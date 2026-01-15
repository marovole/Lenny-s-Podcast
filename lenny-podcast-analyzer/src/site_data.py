import argparse
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

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


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    value = re.sub(r"\s+", "-", value).strip("-")
    value = re.sub(r"-+", "-", value)
    return value


def normalize_title(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", value.lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


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


def build_rss_map(root: Optional[ET.Element]) -> Dict[str, Dict[str, str]]:
    if root is None:
        return {}

    namespace = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}
    items = root.findall("./channel/item")
    rss_map: Dict[str, Dict[str, str]] = {}

    def add_entry(raw_title: str, link: str, audio_url: str) -> None:
        if not raw_title:
            return
        trimmed = raw_title.strip()
        if not trimmed:
            return
        entry = {"episode_url": link.strip(), "audio_url": audio_url.strip()}
        rss_map.setdefault(trimmed, entry)
        normalized = normalize_title(trimmed)
        if normalized:
            rss_map.setdefault(normalized, entry)

    for item in items:
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        enclosure = item.find("enclosure")
        audio_url = ""
        if enclosure is not None:
            audio_url = enclosure.attrib.get("url", "")

        add_entry(title, link, audio_url)

        itunes_title = item.findtext("itunes:title", namespaces=namespace) or ""
        add_entry(itunes_title, link, audio_url)

    return rss_map


def apply_rss_metadata(
    episode: Dict, rss_map: Dict[str, Dict[str, str]], overrides: Dict
) -> Dict:
    title_override = overrides.get("title_overrides", {}).get(episode["episode_name"])
    target_title = title_override or episode["episode_name"]

    rss_entry = rss_map.get(target_title) or rss_map.get(
        normalize_title(target_title), {}
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
    for episode in episodes:
        for segment in episode["segments"]:
            search_text = f"{segment['speaker']} {segment['content']}".lower()
            documents.append(
                {
                    "slug": episode["slug"],
                    "title": episode["title"],
                    "speaker": segment["speaker"],
                    "timestamp": segment["timestamp"],
                    "content": segment["content"],
                    "search_text": search_text,
                }
            )
    return {"documents": documents}


def write_locale_payload(
    locale_dir: Path, public_dir: Path, locale: str, episodes: List[Dict]
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

    search_payload = build_search_index(episodes)
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
    rss_map = build_rss_map(rss_root)

    base_dataset = build_base_dataset(transcripts)
    base_dataset = [
        apply_rss_metadata(episode, rss_map, overrides) for episode in base_dataset
    ]

    client = init_translator()
    model = translation_model or os.getenv(
        "TRANSLATION_MODEL", "anthropic/claude-3-5-sonnet"
    )

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

        write_locale_payload(locale_dir, public_dir, locale, locale_dataset)

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
        default=os.getenv("RSS_URL"),
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
