/**
 * i18n Module
 *
 * Provides internationalization utilities and hooks.
 */

export * from "./config";
export * from "./translations/ko";
export { en } from "./translations/en";
export { zh } from "./translations/zh";

import { ko, type TranslationKeys } from "./translations/ko";
import { en } from "./translations/en";
import { zh } from "./translations/zh";
import { type Locale, defaultLocale } from "./config";

// All translations
const translations: Record<Locale, TranslationKeys> = {
  ko,
  en,
  zh,
};

/**
 * Get translations for a specific locale
 */
export function getTranslations(locale: Locale = defaultLocale): TranslationKeys {
  return translations[locale] || translations[defaultLocale];
}

/**
 * Get a specific translation key with optional interpolation
 */
export function t(
  locale: Locale,
  key: string,
  params?: Record<string, string | number>
): string {
  const trans = getTranslations(locale);

  // Navigate nested keys like "common.loading"
  const keys = key.split(".");
  let value: any = trans;

  for (const k of keys) {
    if (value && typeof value === "object" && k in value) {
      value = value[k];
    } else {
      console.warn(`Translation key not found: ${key}`);
      return key;
    }
  }

  if (typeof value !== "string") {
    console.warn(`Translation key is not a string: ${key}`);
    return key;
  }

  // Interpolate params like {count}
  if (params) {
    return value.replace(/\{(\w+)\}/g, (_, param) => {
      return params[param]?.toString() || `{${param}}`;
    });
  }

  return value;
}
