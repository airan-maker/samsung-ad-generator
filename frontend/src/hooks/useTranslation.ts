/**
 * useTranslation Hook
 *
 * React hook for accessing translations in components.
 */

import { useState, useEffect, useCallback } from "react";
import {
  type Locale,
  defaultLocale,
  getPreferredLocale,
  setLocale as saveLocale,
} from "@/i18n/config";
import { getTranslations, t, type TranslationKeys } from "@/i18n";

interface UseTranslationReturn {
  locale: Locale;
  t: (key: string, params?: Record<string, string | number>) => string;
  setLocale: (locale: Locale) => void;
  translations: TranslationKeys;
}

export function useTranslation(): UseTranslationReturn {
  const [locale, setLocaleState] = useState<Locale>(defaultLocale);

  // Initialize locale from preferences on mount
  useEffect(() => {
    const preferred = getPreferredLocale();
    setLocaleState(preferred);
  }, []);

  // Set locale and save preference
  const setLocale = useCallback((newLocale: Locale) => {
    setLocaleState(newLocale);
    saveLocale(newLocale);

    // Update HTML lang attribute
    if (typeof document !== "undefined") {
      document.documentElement.lang = newLocale;
    }
  }, []);

  // Translation function
  const translate = useCallback(
    (key: string, params?: Record<string, string | number>) => {
      return t(locale, key, params);
    },
    [locale]
  );

  // Get current translations object
  const translations = getTranslations(locale);

  return {
    locale,
    t: translate,
    setLocale,
    translations,
  };
}

// Export type for the hook
export type { UseTranslationReturn };
