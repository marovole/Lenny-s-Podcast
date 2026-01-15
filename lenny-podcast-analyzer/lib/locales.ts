export type LocaleConfig = {
  code: string;
  label: string;
};

export const DEFAULT_LOCALE = "en";

export const LOCALES: LocaleConfig[] = [
  { code: "en", label: "English" },
  { code: "es", label: "Español" },
  { code: "fr", label: "Français" },
  { code: "de", label: "Deutsch" },
  { code: "pt-br", label: "Português (Brasil)" },
  { code: "ja", label: "日本語" },
  { code: "ko", label: "한국어" },
  { code: "zh-cn", label: "简体中文" }
];

export const LOCALE_CODES = LOCALES.map((locale) => locale.code);
