import argparse
import json
import os
import re
import sys
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.taxonomy import (
    TOPICS,
    FAILURE_PATTERNS,
    FRAMEWORKS,
    INTERVIEW_CATEGORIES,
    classify_text,
    get_failure_pattern,
)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

DEFAULT_LOCALE = "en"
DEFAULT_LOCALES = ["en", "es", "fr", "de", "pt-br", "ja", "ko", "zh-cn"]
DEFAULT_RSS_URL = "https://api.substack.com/feed/podcast/10845.rss"

GUEST_ALIASES = {
    "gia laudi": "georgiana laudi",
    "cam adams": "cameron adams",
    "jason m lemkin": "jason lemkin",
    "yuhki yamashata": "yuhki yamashita",
    "alex hardimen": "alex hardiman",
    "benjamin mann": "ben mann",
    "jeanne grosser": "jeanne dewitt grosser",
    "melissa": "melissa perri",
    "shreyas doshi live": "shreyas doshi",
}


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    value = re.sub(r"\s+", "-", value).strip("-")
    value = re.sub(r"-+", "-", value)
    return value


def normalize_title(value: str) -> str:
    value = value.replace("\u2019", "'").replace("\u2018", "'")
    cleaned = re.sub(r"[^a-z0-9\s]", " ", value.lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def fold_accents(value: str) -> str:
    value = value.replace("\u2019", "'").replace("\u2018", "'")
    value = unicodedata.normalize("NFD", value)
    return "".join(char for char in value if unicodedata.category(char) != "Mn")


def norm_key(value: str) -> str:
    return normalize_title(fold_accents(value))


def guest_match_key(value: str) -> str:
    key = norm_key(normalize_guest_name(value))
    key = re.sub(r"\band\b", " ", key)
    return re.sub(r"\s+", " ", key).strip()


def normalize_guest_name(value: str) -> str:
    value = re.sub(r"\s*&\s*", " and ", value)
    value = value.replace("+", " and ")
    return re.sub(r"\s+", " ", value).strip()


def strip_guest_suffix(guest: str) -> str:
    guest = re.sub(r"\([^)]*\)", "", guest)
    if "," in guest:
        guest = guest.split(",", 1)[0].strip()
    return re.sub(r"\s+", " ", guest).strip()


def parse_episode_version(episode_name: str) -> int:
    match = re.search(r"\s+(\d+)\.0\s*$", episode_name)
    return int(match.group(1)) if match else 1


def episode_base_name(episode_name: str) -> str:
    return re.sub(r"\s+\d+\.0\s*$", "", episode_name).strip()


def extract_guest_keys(title: str) -> List[str]:
    title = title.replace("\u2019", "'").replace("\u2018", "'")
    keys: List[str] = []
    if "|" in title:
        guest = strip_guest_suffix(title.split("|")[-1].strip())
        if guest:
            keys.append(guest_match_key(guest))

    prefix_match = re.match(r"^([^|]+?)(?:\s+on\s+|\s+live\b|'s\b)", title.strip())
    if prefix_match:
        guest = strip_guest_suffix(prefix_match.group(1).strip())
        if guest:
            keys.append(guest_match_key(guest))

    embedded_match = re.search(
        r":\s*([^:|]+?)\s+on\s+(?:the|a|an)\b", title, flags=re.IGNORECASE
    )
    if embedded_match:
        guest = strip_guest_suffix(embedded_match.group(1).strip())
        if guest:
            keys.append(guest_match_key(guest))

    from_match = re.search(r"from\s+([^:]+):", title, flags=re.IGNORECASE)
    if from_match:
        guest = strip_guest_suffix(from_match.group(1).strip())
        if guest:
            keys.append(guest_match_key(guest))

    seen = set()
    unique_keys = []
    for key in keys:
        if key and key not in seen:
            seen.add(key)
            unique_keys.append(key)
    return unique_keys


def resolve_guest_lookup_keys(episode_name: str) -> List[str]:
    base_name = normalize_guest_name(episode_base_name(episode_name))
    keys = [guest_match_key(base_name)]

    alias = GUEST_ALIASES.get(norm_key(base_name))
    if alias:
        keys.append(guest_match_key(alias))

    return keys


def read_json(path: Path) -> Dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_transcripts(processed_dir: Path) -> List[Dict]:
    transcripts = []
    for file_path in sorted(processed_dir.glob("*.json")):
        if file_path.name == "index.json":
            continue
        transcripts.append(read_json(file_path))
    return transcripts


def load_rss(rss_source: Optional[str]) -> Optional[ET.Element]:
    if not rss_source:
        return None
    if rss_source.startswith("http://") or rss_source.startswith("https://"):
        user_agent = os.getenv("RSS_USER_AGENT", "LennyPodcastTranscripts/1.0")
        timeout = float(os.getenv("RSS_TIMEOUT", "10"))
        request = urllib.request.Request(rss_source, headers={"User-Agent": user_agent})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read()
    else:
        with open(rss_source, "rb") as file:
            data = file.read()
    return ET.fromstring(data)


def build_rss_index(
    root: Optional[ET.Element],
) -> Tuple[
    Dict[str, List[Dict[str, str]]],
    Dict[str, Dict[str, str]],
    List[Dict[str, str]],
]:
    if root is None:
        return {}, {}, []

    namespace = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}
    guest_index: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    title_index: Dict[str, Dict[str, str]] = {}
    all_entries: List[Dict[str, str]] = []

    def add_title_entry(raw_title: str, entry: Dict[str, str]) -> None:
        trimmed = raw_title.strip()
        if not trimmed:
            return
        title_index.setdefault(trimmed, entry)
        normalized = normalize_title(trimmed)
        if normalized:
            title_index.setdefault(normalized, entry)

    for item in root.findall("./channel/item"):
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        pub_date = item.findtext("pubDate") or ""
        published_at = parsedate_to_datetime(pub_date) if pub_date else None
        enclosure = item.find("enclosure")
        audio_url = enclosure.attrib.get("url", "") if enclosure is not None else ""
        entry = {
            "title": title,
            "episode_url": link.strip(),
            "audio_url": audio_url.strip(),
            "published_at": published_at,
        }
        all_entries.append(entry)

        add_title_entry(title, entry)

        itunes_title = item.findtext("itunes:title", namespaces=namespace) or ""
        add_title_entry(itunes_title, entry)

        for guest_key in extract_guest_keys(title):
            guest_index[guest_key].append(entry)
        for guest_key in extract_guest_keys(itunes_title):
            guest_index[guest_key].append(entry)

    for guest_key, entries in guest_index.items():
        entries.sort(key=lambda item: item["published_at"] or datetime.min)
        deduped: List[Dict[str, str]] = []
        seen_urls = set()
        for entry in entries:
            dedupe_key = entry["episode_url"] or entry["title"]
            if dedupe_key in seen_urls:
                continue
            seen_urls.add(dedupe_key)
            deduped.append(entry)
        guest_index[guest_key] = deduped

    return dict(guest_index), title_index, all_entries


def lookup_rss_entry(
    episode_name: str,
    guest_index: Dict[str, List[Dict[str, str]]],
    title_index: Dict[str, Dict[str, str]],
    overrides: Dict,
    all_entries: List[Dict[str, str]],
) -> Dict[str, str]:
    title_override = overrides.get("title_overrides", {}).get(episode_name)
    if title_override:
        return title_index.get(title_override) or title_index.get(
            normalize_title(title_override), {}
        )

    version = parse_episode_version(episode_name)
    for guest_key in resolve_guest_lookup_keys(episode_name):
        entries = guest_index.get(guest_key, [])
        if version <= len(entries):
            return entries[version - 1]

    base_key = guest_match_key(episode_base_name(episode_name))
    if base_key:
        title_matches = []
        for entry in all_entries:
            title_key = guest_match_key(entry["title"])
            if base_key in title_key:
                title_matches.append(entry)
        if title_matches:
            title_matches.sort(key=lambda item: item["published_at"] or datetime.min)
            deduped = []
            seen_urls = set()
            for entry in title_matches:
                dedupe_key = entry["episode_url"] or entry["title"]
                if dedupe_key in seen_urls:
                    continue
                seen_urls.add(dedupe_key)
                deduped.append(entry)
            if version <= len(deduped):
                return deduped[version - 1]

    partial_matches = [
        guest_key
        for guest_key in guest_index
        if base_key and (base_key in guest_key or guest_key in base_key)
    ]
    if len(partial_matches) == 1:
        entries = guest_index[partial_matches[0]]
        if version <= len(entries):
            return entries[version - 1]

    return {}


def apply_rss_metadata(
    episode: Dict,
    guest_index: Dict[str, List[Dict[str, str]]],
    title_index: Dict[str, Dict[str, str]],
    overrides: Dict,
    all_entries: List[Dict[str, str]],
) -> Dict:
    rss_entry = lookup_rss_entry(
        episode["episode_name"],
        guest_index,
        title_index,
        overrides,
        all_entries,
    )
    episode_override = overrides.get("episode_overrides", {}).get(
        episode["episode_name"], {}
    )

    episode["episode_url"] = episode_override.get("episode_url") or rss_entry.get(
        "episode_url"
    )
    episode["audio_url"] = episode_override.get("audio_url") or rss_entry.get(
        "audio_url"
    )
    return episode


def build_base_dataset(transcripts: List[Dict]) -> List[Dict]:
    dataset = []
    for transcript in transcripts:
        topics = classify_text(transcript.get("full_text", ""))
        failure_patterns = get_failure_pattern(transcript.get("full_text", ""))

        dataset.append(
            {
                "episode_name": transcript["episode_name"],
                "title": transcript["episode_name"],
                "slug": slugify(transcript["episode_name"]),
                "num_segments": transcript.get("num_segments", 0),
                "segments": transcript.get("segments", []),
                "full_text": transcript.get("full_text", ""),
                "companies": transcript.get("companies", []),
                "topics": topics,
                "failure_patterns": failure_patterns,
            }
        )
    return dataset


def init_translator() -> Optional[Any]:
    if OpenAI is None:
        return None
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    api_key = openrouter_key or openai_key
    if not api_key:
        return None
    if openrouter_key:
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        return OpenAI(api_key=api_key, base_url=base_url)
    return OpenAI(api_key=api_key)


def translate_batch(
    client: Any, model: str, texts: List[str], locale: str
) -> List[str]:
    payload = json.dumps(texts, ensure_ascii=False)
    prompt = (
        "Translate the JSON array of strings into the target language. "
        "Return a JSON array of the same length. "
        f"Target language: {locale}.\n\n{payload}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a translation engine. Output JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=4000,
    )

    content = response.choices[0].message.content
    if content is None:
        raise ValueError("Translation response was empty")
    content = content.replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", content, re.DOTALL)
        if not match:
            raise
        parsed = json.loads(match.group(0))

    if not isinstance(parsed, list) or len(parsed) != len(texts):
        raise ValueError("Translation response had unexpected length")

    return parsed


def translate_episode(client: Any, model: str, episode: Dict, locale: str) -> Dict:
    translated = dict(episode)
    translated["title"] = translate_batch(client, model, [episode["title"]], locale)[0]

    segments = episode["segments"]
    translated_segments = []
    batch_size = int(os.getenv("TRANSLATION_BATCH_SIZE", "12"))
    for i in range(0, len(segments), batch_size):
        batch = segments[i : i + batch_size]
        texts = [seg["content"] for seg in batch]
        translated_texts = translate_batch(client, model, texts, locale)
        for seg, content in zip(batch, translated_texts):
            translated_segments.append({**seg, "content": content})
    translated["segments"] = translated_segments
    translated["full_text"] = "\n".join([seg["content"] for seg in translated_segments])
    return translated


def build_search_index(episodes: List[Dict]) -> Dict:
    documents = []
    max_documents = os.getenv("SEARCH_MAX_DOCUMENTS", "20000")
    max_chars = os.getenv("SEARCH_CONTENT_MAX_CHARS", "280")

    try:
        max_documents_value = int(max_documents) if max_documents else None
    except ValueError:
        max_documents_value = None

    try:
        max_chars_value = int(max_chars) if max_chars else None
    except ValueError:
        max_chars_value = None

    for episode in episodes:
        for segment in episode["segments"]:
            content = segment["content"]
            if (
                max_chars_value
                and max_chars_value > 0
                and len(content) > max_chars_value
            ):
                content = f"{content[:max_chars_value].rstrip()}..."
            search_text = f"{segment['speaker']} {content}".lower()
            documents.append(
                {
                    "slug": episode["slug"],
                    "title": episode["title"],
                    "speaker": segment["speaker"],
                    "timestamp": segment["timestamp"],
                    "content": content,
                    "search_text": search_text,
                }
            )
            if max_documents_value and len(documents) >= max_documents_value:
                return {"documents": documents}
    return {"documents": documents}


def write_locale_payload(
    locale_dir: Path,
    public_dir: Path,
    locale: str,
    episodes: List[Dict],
    search_payload: Dict,
):
    episodes_dir = locale_dir / "episodes"
    episodes_dir.mkdir(parents=True, exist_ok=True)

    episodes_index = []
    for episode in episodes:
        episodes_index.append(
            {
                "slug": episode["slug"],
                "title": episode["title"],
                "num_segments": episode["num_segments"],
                "topics": episode["topics"],
                "failure_patterns": episode["failure_patterns"],
                "companies": episode["companies"],
            }
        )
        with open(
            episodes_dir / f"{episode['slug']}.json", "w", encoding="utf-8"
        ) as file:
            json.dump(episode, file, ensure_ascii=False, indent=2)

    with open(episodes_dir / "index.json", "w", encoding="utf-8") as file:
        json.dump(episodes_index, file, ensure_ascii=False, indent=2)

    guests = [
        {
            "name": episode["title"],
            "slug": episode["slug"],
            "episode_slug": episode["slug"],
        }
        for episode in episodes
    ]
    with open(locale_dir / "guests.json", "w", encoding="utf-8") as file:
        json.dump(guests, file, ensure_ascii=False, indent=2)

    topics_payload = []
    for topic_id, topic_info in TOPICS.items():
        topics_payload.append(
            {
                "id": topic_id,
                "name": topic_info["name"],
                "episodes": [
                    episode["slug"]
                    for episode in episodes
                    if topic_id in episode["topics"]
                ],
            }
        )
    with open(locale_dir / "topics.json", "w", encoding="utf-8") as file:
        json.dump(topics_payload, file, ensure_ascii=False, indent=2)

    frameworks_payload = []
    for framework_id, framework in FRAMEWORKS.items():
        frameworks_payload.append(
            {
                "id": framework_id,
                "name": framework["name"],
                "description": framework["description"],
                "source": framework["source"],
            }
        )
    with open(locale_dir / "frameworks.json", "w", encoding="utf-8") as file:
        json.dump(frameworks_payload, file, ensure_ascii=False, indent=2)

    failure_payload = []
    for pattern_id, pattern in FAILURE_PATTERNS.items():
        failure_payload.append(
            {
                "id": pattern_id,
                "name": pattern["name"],
                "examples": pattern["examples"],
                "episodes": [
                    episode["slug"]
                    for episode in episodes
                    if pattern_id in episode["failure_patterns"]
                ],
            }
        )
    with open(locale_dir / "failure.json", "w", encoding="utf-8") as file:
        json.dump(failure_payload, file, ensure_ascii=False, indent=2)

    interviews_payload = []
    for category_id, category in INTERVIEW_CATEGORIES.items():
        interviews_payload.append(
            {
                "id": category_id,
                "name": category["name"],
                "questions": category["questions"],
            }
        )
    with open(locale_dir / "interviews.json", "w", encoding="utf-8") as file:
        json.dump(interviews_payload, file, ensure_ascii=False, indent=2)

    with open(locale_dir / "search.json", "w", encoding="utf-8") as file:
        json.dump(search_payload, file, ensure_ascii=False, indent=2)

    public_locale_dir = public_dir / locale
    public_locale_dir.mkdir(parents=True, exist_ok=True)
    with open(public_locale_dir / "search.json", "w", encoding="utf-8") as file:
        json.dump(search_payload, file, ensure_ascii=False, indent=2)


def build_site(
    locales: List[str],
    rss_source: Optional[str],
    allow_fallback: bool,
    max_episodes: Optional[int],
    translation_model: Optional[str],
):
    processed_dir = Path("data/processed")
    output_dir = Path("data/site")
    public_dir = Path("public/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    public_dir.mkdir(parents=True, exist_ok=True)

    transcripts = load_transcripts(processed_dir)
    if max_episodes:
        transcripts = transcripts[:max_episodes]

    overrides_path = Path("data/rss_overrides.json")
    overrides = read_json(overrides_path) if overrides_path.exists() else {}

    rss_root = load_rss(rss_source)
    guest_index, title_index, all_entries = build_rss_index(rss_root)

    base_dataset = build_base_dataset(transcripts)
    base_dataset = [
        apply_rss_metadata(
            episode, guest_index, title_index, overrides, all_entries
        )
        for episode in base_dataset
    ]

    client = init_translator()
    model = translation_model or os.getenv(
        "TRANSLATION_MODEL", "anthropic/claude-3-5-sonnet"
    )

    search_index_locales = {
        locale.strip()
        for locale in os.getenv("SEARCH_INDEX_LOCALES", DEFAULT_LOCALE).split(",")
        if locale.strip()
    }

    for locale in locales:
        locale_dir = output_dir / locale
        locale_dir.mkdir(parents=True, exist_ok=True)

        if locale == DEFAULT_LOCALE:
            locale_dataset = base_dataset
        else:
            if client is None:
                if allow_fallback:
                    locale_dataset = base_dataset
                else:
                    raise RuntimeError(
                        "Translation client unavailable. Set OPENROUTER_API_KEY/OPENAI_API_KEY "
                        "or pass --allow-fallback."
                    )
            else:
                locale_dataset = [
                    translate_episode(client, model, episode, locale)
                    for episode in base_dataset
                ]

        if locale in search_index_locales:
            search_payload = build_search_index(locale_dataset)
        else:
            search_payload = {"documents": [], "fallback_locale": DEFAULT_LOCALE}

        write_locale_payload(
            locale_dir, public_dir, locale, locale_dataset, search_payload
        )

        site_metadata = {
            "locale": locale,
            "updated_at": datetime.utcnow().isoformat(),
            "total_episodes": len(locale_dataset),
            "topics": [
                {"id": topic_id, "name": topic_info["name"]}
                for topic_id, topic_info in TOPICS.items()
            ],
            "locales": [{"code": code, "label": code} for code in locales],
        }

        with open(locale_dir / "site.json", "w", encoding="utf-8") as file:
            json.dump(site_metadata, file, ensure_ascii=False, indent=2)

    print(f"Generated site data for locales: {', '.join(locales)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate site data for transcript site"
    )
    parser.add_argument(
        "--rss",
        dest="rss_source",
        default=os.getenv("RSS_URL", DEFAULT_RSS_URL),
        help="RSS feed URL or local file path",
    )
    parser.add_argument("--locales", help="Comma-separated locale codes")
    parser.add_argument("--allow-fallback", action="store_true")
    parser.add_argument("--max-episodes", type=int, default=None)
    parser.add_argument(
        "--translation-model",
        dest="translation_model",
        help="Override translation model",
    )
    args = parser.parse_args()

    locales = DEFAULT_LOCALES
    if args.locales:
        locales = [
            locale.strip() for locale in args.locales.split(",") if locale.strip()
        ]

    build_site(
        locales,
        args.rss_source,
        args.allow_fallback,
        args.max_episodes,
        args.translation_model,
    )
