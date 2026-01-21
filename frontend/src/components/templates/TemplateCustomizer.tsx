"use client";

import { useState } from "react";
import {
  Palette,
  Type,
  Layout,
  Image,
  Music,
  Sliders,
  RotateCcw,
  Save,
  Eye,
  ChevronRight,
  Check,
} from "lucide-react";

export interface TemplateCustomizerProps {
  templateId: string;
  templateName?: string;
  initialConfig?: TemplateConfig;
  onConfigChange?: (config: TemplateConfig) => void;
  onSave?: (customizations: TemplateConfig) => void;
  onPreview?: () => void;
}

export interface TemplateConfig {
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    text: string;
    background: string;
  };
  typography: {
    headlineFont: string;
    bodyFont: string;
    headlineSize: "small" | "medium" | "large";
    bodySize: "small" | "medium" | "large";
  };
  layout: {
    logoPosition: string;
    textPosition: string;
    productPosition: string;
    ctaPosition: string;
  };
  effects: {
    transition: string;
    animation: string;
    filterStyle: string;
  };
  branding: {
    showLogo: boolean;
    logoUrl: string;
    watermark: boolean;
  };
}

const defaultCustomizations: TemplateConfig = {
  colors: {
    primary: "#1428A0",
    secondary: "#000000",
    accent: "#FF6B6B",
    text: "#FFFFFF",
    background: "#000000",
  },
  typography: {
    headlineFont: "Samsung One",
    bodyFont: "Pretendard",
    headlineSize: "large",
    bodySize: "medium",
  },
  layout: {
    logoPosition: "top-right",
    textPosition: "bottom-left",
    productPosition: "center",
    ctaPosition: "bottom-center",
  },
  effects: {
    transition: "fade",
    animation: "zoom-in",
    filterStyle: "none",
  },
  branding: {
    showLogo: true,
    logoUrl: "",
    watermark: true,
  },
};

const presetThemes = [
  {
    name: "Samsung Blue",
    colors: { primary: "#1428A0", secondary: "#000000", accent: "#00A9E0", text: "#FFFFFF", background: "#000000" },
  },
  {
    name: "Minimal White",
    colors: { primary: "#000000", secondary: "#333333", accent: "#1428A0", text: "#000000", background: "#FFFFFF" },
  },
  {
    name: "Premium Gold",
    colors: { primary: "#B8860B", secondary: "#000000", accent: "#FFD700", text: "#FFFFFF", background: "#1A1A1A" },
  },
  {
    name: "Tech Neon",
    colors: { primary: "#00FF88", secondary: "#0A0A0A", accent: "#FF00FF", text: "#FFFFFF", background: "#0A0A0A" },
  },
];

const fonts = [
  "Samsung One",
  "Pretendard",
  "Noto Sans KR",
  "Spoqa Han Sans Neo",
  "IBM Plex Sans KR",
];

const transitions = [
  { id: "fade", name: "페이드" },
  { id: "slide-left", name: "슬라이드 (왼쪽)" },
  { id: "slide-right", name: "슬라이드 (오른쪽)" },
  { id: "zoom", name: "줌" },
  { id: "dissolve", name: "디졸브" },
  { id: "wipe", name: "와이프" },
];

const animations = [
  { id: "none", name: "없음" },
  { id: "zoom-in", name: "줌 인" },
  { id: "zoom-out", name: "줌 아웃" },
  { id: "pan-left", name: "팬 (왼쪽)" },
  { id: "pan-right", name: "팬 (오른쪽)" },
  { id: "ken-burns", name: "켄 번즈" },
];

const filters = [
  { id: "none", name: "없음" },
  { id: "cinematic", name: "시네마틱" },
  { id: "vintage", name: "빈티지" },
  { id: "bright", name: "밝은" },
  { id: "moody", name: "무디" },
  { id: "black-white", name: "흑백" },
];

export function TemplateCustomizer({
  templateId,
  templateName,
  initialConfig,
  onConfigChange,
  onSave,
  onPreview,
}: TemplateCustomizerProps) {
  const [customizations, setCustomizations] = useState<TemplateConfig>(
    initialConfig || defaultCustomizations
  );
  const [activeSection, setActiveSection] = useState<string>("colors");
  const [hasChanges, setHasChanges] = useState(false);

  const updateCustomization = <K extends keyof TemplateConfig>(
    section: K,
    key: keyof TemplateConfig[K],
    value: any
  ) => {
    setCustomizations((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value,
      },
    }));
    setHasChanges(true);
  };

  const applyPreset = (preset: typeof presetThemes[0]) => {
    setCustomizations((prev) => ({
      ...prev,
      colors: preset.colors,
    }));
    setHasChanges(true);
  };

  const resetToDefault = () => {
    setCustomizations(defaultCustomizations);
    setHasChanges(false);
  };

  const sections = [
    { id: "colors", icon: Palette, label: "컬러" },
    { id: "typography", icon: Type, label: "타이포그래피" },
    { id: "layout", icon: Layout, label: "레이아웃" },
    { id: "effects", icon: Sliders, label: "효과" },
    { id: "branding", icon: Image, label: "브랜딩" },
  ];

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <div className="w-64 border-r bg-gray-50">
        <div className="p-4 border-b">
          <h2 className="font-semibold text-gray-900">템플릿 커스터마이징</h2>
          <p className="text-sm text-gray-500 mt-1">{templateName}</p>
        </div>

        <nav className="p-2">
          {sections.map((section) => (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left transition-colors ${
                activeSection === section.id
                  ? "bg-samsung-blue text-white"
                  : "text-gray-700 hover:bg-gray-100"
              }`}
            >
              <section.icon className="h-5 w-5" />
              <span>{section.label}</span>
              <ChevronRight className="ml-auto h-4 w-4" />
            </button>
          ))}
        </nav>

        <div className="absolute bottom-0 left-0 w-64 border-t bg-white p-4">
          <div className="flex gap-2">
            <button
              onClick={resetToDefault}
              className="flex flex-1 items-center justify-center gap-2 rounded-lg border py-2 text-gray-600 hover:bg-gray-50"
            >
              <RotateCcw className="h-4 w-4" />
              초기화
            </button>
            <button
              onClick={onPreview}
              className="flex flex-1 items-center justify-center gap-2 rounded-lg border py-2 text-gray-600 hover:bg-gray-50"
            >
              <Eye className="h-4 w-4" />
              미리보기
            </button>
          </div>
          <button
            onClick={() => onSave?.(customizations)}
            disabled={!hasChanges}
            className={`mt-2 flex w-full items-center justify-center gap-2 rounded-lg py-2.5 font-medium transition-colors ${
              hasChanges
                ? "bg-samsung-blue text-white hover:bg-blue-700"
                : "bg-gray-100 text-gray-400"
            }`}
          >
            <Save className="h-4 w-4" />
            저장하기
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {/* Colors Section */}
        {activeSection === "colors" && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">컬러 테마</h3>

              {/* Presets */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  프리셋 테마
                </label>
                <div className="grid grid-cols-4 gap-3">
                  {presetThemes.map((preset) => (
                    <button
                      key={preset.name}
                      onClick={() => applyPreset(preset)}
                      className="rounded-lg border p-3 hover:border-samsung-blue transition-colors"
                    >
                      <div className="flex gap-1 mb-2">
                        {Object.values(preset.colors).slice(0, 3).map((color, i) => (
                          <div
                            key={i}
                            className="h-4 flex-1 rounded"
                            style={{ backgroundColor: color }}
                          />
                        ))}
                      </div>
                      <div className="text-xs text-gray-600">{preset.name}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Individual Colors */}
              <div className="grid grid-cols-2 gap-4">
                {[
                  { key: "primary", label: "주요 색상" },
                  { key: "secondary", label: "보조 색상" },
                  { key: "accent", label: "강조 색상" },
                  { key: "text", label: "텍스트 색상" },
                  { key: "background", label: "배경 색상" },
                ].map(({ key, label }) => (
                  <div key={key}>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {label}
                    </label>
                    <div className="flex items-center gap-2">
                      <input
                        type="color"
                        value={customizations.colors[key as keyof typeof customizations.colors]}
                        onChange={(e) =>
                          updateCustomization("colors", key as any, e.target.value)
                        }
                        className="h-10 w-14 rounded border cursor-pointer"
                      />
                      <input
                        type="text"
                        value={customizations.colors[key as keyof typeof customizations.colors]}
                        onChange={(e) =>
                          updateCustomization("colors", key as any, e.target.value)
                        }
                        className="flex-1 rounded-lg border px-3 py-2 text-sm font-mono uppercase"
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Typography Section */}
        {activeSection === "typography" && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">타이포그래피</h3>

            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  헤드라인 폰트
                </label>
                <select
                  value={customizations.typography.headlineFont}
                  onChange={(e) =>
                    updateCustomization("typography", "headlineFont", e.target.value)
                  }
                  className="w-full rounded-lg border px-3 py-2"
                >
                  {fonts.map((font) => (
                    <option key={font} value={font}>
                      {font}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  본문 폰트
                </label>
                <select
                  value={customizations.typography.bodyFont}
                  onChange={(e) =>
                    updateCustomization("typography", "bodyFont", e.target.value)
                  }
                  className="w-full rounded-lg border px-3 py-2"
                >
                  {fonts.map((font) => (
                    <option key={font} value={font}>
                      {font}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  헤드라인 크기
                </label>
                <div className="flex gap-2">
                  {["small", "medium", "large"].map((size) => (
                    <button
                      key={size}
                      onClick={() =>
                        updateCustomization("typography", "headlineSize", size as any)
                      }
                      className={`flex-1 rounded-lg border py-2 text-sm capitalize transition-colors ${
                        customizations.typography.headlineSize === size
                          ? "border-samsung-blue bg-blue-50 text-samsung-blue"
                          : "text-gray-600 hover:bg-gray-50"
                      }`}
                    >
                      {size === "small" ? "작게" : size === "medium" ? "보통" : "크게"}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  본문 크기
                </label>
                <div className="flex gap-2">
                  {["small", "medium", "large"].map((size) => (
                    <button
                      key={size}
                      onClick={() =>
                        updateCustomization("typography", "bodySize", size as any)
                      }
                      className={`flex-1 rounded-lg border py-2 text-sm capitalize transition-colors ${
                        customizations.typography.bodySize === size
                          ? "border-samsung-blue bg-blue-50 text-samsung-blue"
                          : "text-gray-600 hover:bg-gray-50"
                      }`}
                    >
                      {size === "small" ? "작게" : size === "medium" ? "보통" : "크게"}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Preview */}
            <div
              className="rounded-lg border p-6 mt-6"
              style={{ backgroundColor: customizations.colors.background }}
            >
              <h4
                className="mb-2"
                style={{
                  fontFamily: customizations.typography.headlineFont,
                  color: customizations.colors.text,
                  fontSize:
                    customizations.typography.headlineSize === "small"
                      ? "1.5rem"
                      : customizations.typography.headlineSize === "medium"
                      ? "2rem"
                      : "2.5rem",
                }}
              >
                Galaxy S25 Ultra
              </h4>
              <p
                style={{
                  fontFamily: customizations.typography.bodyFont,
                  color: customizations.colors.text,
                  fontSize:
                    customizations.typography.bodySize === "small"
                      ? "0.875rem"
                      : customizations.typography.bodySize === "medium"
                      ? "1rem"
                      : "1.125rem",
                }}
              >
                혁신적인 AI 기술이 만들어가는 새로운 경험
              </p>
            </div>
          </div>
        )}

        {/* Layout Section */}
        {activeSection === "layout" && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">레이아웃</h3>

            {[
              { key: "logoPosition", label: "로고 위치" },
              { key: "textPosition", label: "텍스트 위치" },
              { key: "productPosition", label: "제품 위치" },
              { key: "ctaPosition", label: "CTA 위치" },
            ].map(({ key, label }) => (
              <div key={key}>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {label}
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    "top-left",
                    "top-center",
                    "top-right",
                    "center-left",
                    "center",
                    "center-right",
                    "bottom-left",
                    "bottom-center",
                    "bottom-right",
                  ].map((pos) => (
                    <button
                      key={pos}
                      onClick={() =>
                        updateCustomization("layout", key as any, pos)
                      }
                      className={`rounded border py-2 text-xs transition-colors ${
                        customizations.layout[key as keyof typeof customizations.layout] ===
                        pos
                          ? "border-samsung-blue bg-blue-50 text-samsung-blue"
                          : "text-gray-600 hover:bg-gray-50"
                      }`}
                    >
                      {pos
                        .replace("-", " ")
                        .replace("top", "상단")
                        .replace("bottom", "하단")
                        .replace("left", "좌")
                        .replace("right", "우")
                        .replace("center", "중앙")}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Effects Section */}
        {activeSection === "effects" && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">효과</h3>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                씬 전환 효과
              </label>
              <div className="grid grid-cols-3 gap-2">
                {transitions.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => updateCustomization("effects", "transition", t.id)}
                    className={`rounded-lg border py-3 text-sm transition-colors ${
                      customizations.effects.transition === t.id
                        ? "border-samsung-blue bg-blue-50 text-samsung-blue"
                        : "text-gray-600 hover:bg-gray-50"
                    }`}
                  >
                    {t.name}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                애니메이션
              </label>
              <div className="grid grid-cols-3 gap-2">
                {animations.map((a) => (
                  <button
                    key={a.id}
                    onClick={() => updateCustomization("effects", "animation", a.id)}
                    className={`rounded-lg border py-3 text-sm transition-colors ${
                      customizations.effects.animation === a.id
                        ? "border-samsung-blue bg-blue-50 text-samsung-blue"
                        : "text-gray-600 hover:bg-gray-50"
                    }`}
                  >
                    {a.name}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                필터 스타일
              </label>
              <div className="grid grid-cols-3 gap-2">
                {filters.map((f) => (
                  <button
                    key={f.id}
                    onClick={() => updateCustomization("effects", "filterStyle", f.id)}
                    className={`rounded-lg border py-3 text-sm transition-colors ${
                      customizations.effects.filterStyle === f.id
                        ? "border-samsung-blue bg-blue-50 text-samsung-blue"
                        : "text-gray-600 hover:bg-gray-50"
                    }`}
                  >
                    {f.name}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Branding Section */}
        {activeSection === "branding" && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">브랜딩</h3>

            <div className="flex items-center justify-between rounded-lg border p-4">
              <div>
                <div className="font-medium text-gray-900">로고 표시</div>
                <div className="text-sm text-gray-500">영상에 브랜드 로고 표시</div>
              </div>
              <button
                onClick={() =>
                  updateCustomization("branding", "showLogo", !customizations.branding.showLogo)
                }
                className={`relative h-6 w-11 rounded-full transition-colors ${
                  customizations.branding.showLogo ? "bg-samsung-blue" : "bg-gray-200"
                }`}
              >
                <span
                  className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${
                    customizations.branding.showLogo ? "left-5" : "left-0.5"
                  }`}
                />
              </button>
            </div>

            {customizations.branding.showLogo && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  로고 업로드
                </label>
                <div className="rounded-lg border-2 border-dashed p-6 text-center">
                  <Image className="mx-auto h-10 w-10 text-gray-400" />
                  <p className="mt-2 text-sm text-gray-500">
                    클릭하여 로고 업로드 또는 드래그 앤 드롭
                  </p>
                  <p className="text-xs text-gray-400 mt-1">PNG, SVG (최대 2MB)</p>
                </div>
              </div>
            )}

            <div className="flex items-center justify-between rounded-lg border p-4">
              <div>
                <div className="font-medium text-gray-900">워터마크</div>
                <div className="text-sm text-gray-500">SaiAd 워터마크 표시</div>
              </div>
              <button
                onClick={() =>
                  updateCustomization("branding", "watermark", !customizations.branding.watermark)
                }
                className={`relative h-6 w-11 rounded-full transition-colors ${
                  customizations.branding.watermark ? "bg-samsung-blue" : "bg-gray-200"
                }`}
              >
                <span
                  className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${
                    customizations.branding.watermark ? "left-5" : "left-0.5"
                  }`}
                />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
