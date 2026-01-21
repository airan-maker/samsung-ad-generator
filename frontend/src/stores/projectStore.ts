import { create } from "zustand";
import { persist } from "zustand/middleware";
import type {
  Product,
  Template,
  ProjectConfig,
  Script,
  ToneType,
  Language,
} from "@/types";

interface ProjectState {
  // Current project state
  selectedProduct: Product | null;
  customProductImage: string | null;
  customProductName: string | null;
  selectedTemplate: Template | null;
  config: ProjectConfig;
  script: Script | null;

  // Actions
  setProduct: (product: Product | null) => void;
  setCustomProduct: (image: string, name: string) => void;
  clearProduct: () => void;
  setTemplate: (template: Template | null) => void;
  setConfig: (config: Partial<ProjectConfig>) => void;
  setScript: (script: Script | null) => void;
  updateScript: (updates: Partial<Script>) => void;
  reset: () => void;
}

const defaultConfig: ProjectConfig = {
  duration: 30,
  tone: "premium",
  language: "ko",
  aspect_ratio: "16:9",
  include_narration: true,
};

export const useProjectStore = create<ProjectState>()(
  persist(
    (set, get) => ({
      // Initial state
      selectedProduct: null,
      customProductImage: null,
      customProductName: null,
      selectedTemplate: null,
      config: defaultConfig,
      script: null,

      // Actions
      setProduct: (product) =>
        set({
          selectedProduct: product,
          customProductImage: null,
          customProductName: null,
        }),

      setCustomProduct: (image, name) =>
        set({
          selectedProduct: null,
          customProductImage: image,
          customProductName: name,
        }),

      clearProduct: () =>
        set({
          selectedProduct: null,
          customProductImage: null,
          customProductName: null,
        }),

      setTemplate: (template) => set({ selectedTemplate: template }),

      setConfig: (newConfig) =>
        set((state) => ({
          config: { ...state.config, ...newConfig },
        })),

      setScript: (script) => set({ script }),

      updateScript: (updates) =>
        set((state) => ({
          script: state.script ? { ...state.script, ...updates } : null,
        })),

      reset: () =>
        set({
          selectedProduct: null,
          customProductImage: null,
          customProductName: null,
          selectedTemplate: null,
          config: defaultConfig,
          script: null,
        }),
    }),
    {
      name: "saiad-project",
      partialize: (state) => ({
        selectedProduct: state.selectedProduct,
        customProductImage: state.customProductImage,
        customProductName: state.customProductName,
        selectedTemplate: state.selectedTemplate,
        config: state.config,
      }),
    }
  )
);
