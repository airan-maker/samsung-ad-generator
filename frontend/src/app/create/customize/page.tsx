"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useProjectStore } from "@/stores/projectStore";
import {
  ArrowLeft,
  ArrowRight,
  RefreshCw,
  Play,
  Pause,
  Volume2,
  VolumeX,
  Sparkles,
  Music,
  Mic,
} from "lucide-react";
import type { ToneType } from "@/types";

const toneOptions: { value: ToneType; label: string; description: string }[] = [
  {
    value: "premium",
    label: "프리미엄",
    description: "고급스럽고 세련된 톤",
  },
  {
    value: "practical",
    label: "실용적",
    description: "기능과 가성비 강조",
  },
  {
    value: "mz",
    label: "MZ",
    description: "트렌디하고 캐주얼한 톤",
  },
];

const musicOptions = [
  { id: "music_1", name: "Upbeat Electronic", mood: "역동적" },
  { id: "music_2", name: "Cinematic Strings", mood: "감성적" },
  { id: "music_3", name: "Modern Pop", mood: "트렌디" },
  { id: "music_4", name: "Minimal Piano", mood: "차분한" },
  { id: "music_5", name: "Tech Future", mood: "미래적" },
];

const voiceOptions = [
  { id: "voice_ko_m_1", name: "민준", language: "한국어", gender: "남성" },
  { id: "voice_ko_f_1", name: "서연", language: "한국어", gender: "여성" },
  { id: "voice_ko_m_2", name: "준서", language: "한국어", gender: "남성" },
  { id: "voice_en_f_1", name: "Emily", language: "English", gender: "Female" },
  { id: "voice_en_m_1", name: "James", language: "English", gender: "Male" },
];

export default function CustomizePage() {
  const router = useRouter();
  const {
    selectedProduct,
    customProductName,
    selectedTemplate,
    config,
    setConfig,
    script,
    setScript,
    updateScript,
  } = useProjectStore();

  const [selectedTone, setSelectedTone] = useState<ToneType>(config.tone || "premium");
  const [selectedMusic, setSelectedMusic] = useState(musicOptions[0].id);
  const [selectedVoice, setSelectedVoice] = useState(voiceOptions[0].id);
  const [includeNarration, setIncludeNarration] = useState(config.include_narration ?? true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);

  // Local script state for editing
  const [localScript, setLocalScript] = useState({
    headline: script?.headline || "Galaxy S25 Ultra",
    subline: script?.subline || "AI로 더 강력해진 카메라",
    narration:
      script?.narration ||
      "새로운 갤럭시 S25 울트라를 만나보세요. AI가 만들어내는 놀라운 사진과 영상을 경험하세요. 프로급 촬영이 일상이 됩니다.",
    cta: script?.cta || "지금 바로 만나보세요",
  });

  const productName = selectedProduct?.name || customProductName || "제품";

  const handleToneChange = (tone: ToneType) => {
    setSelectedTone(tone);
    setConfig({ tone });
  };

  const handleGenerateScript = async () => {
    setIsGenerating(true);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Mock generated script based on tone
    const scripts = {
      premium: {
        headline: productName,
        subline: "새로운 기준을 제시합니다",
        narration: `새로운 ${productName}을 만나보세요. 혁신적인 기술과 세련된 디자인이 만나 완벽한 조화를 이룹니다. 당신의 일상에 특별함을 더합니다.`,
        cta: "지금 경험하세요",
      },
      practical: {
        headline: productName,
        subline: "똑똑한 선택, 확실한 만족",
        narration: `${productName}과 함께라면 일상이 더 편리해집니다. 뛰어난 성능과 합리적인 가격. 지금 바로 확인해 보세요.`,
        cta: "자세히 보기",
      },
      mz: {
        headline: productName,
        subline: "이건 진짜 다름 ✨",
        narration: `요즘 핫한 ${productName}, 직접 써보면 알게 됨! 이 정도면 갓성비 아님? 지금 바로 찜해두세요.`,
        cta: "바로 확인",
      },
    };

    setLocalScript(scripts[selectedTone]);
    setIsGenerating(false);
  };

  const handleRegenerateField = async (field: keyof typeof localScript) => {
    setIsGenerating(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // Mock regeneration
    const alternatives: Record<string, string[]> = {
      headline: [productName, `새로운 ${productName}`, `The ${productName}`],
      subline: ["혁신의 시작", "한 차원 높은 경험", "상상 그 이상"],
      cta: ["지금 만나보세요", "더 알아보기", "구매하기"],
    };

    if (alternatives[field]) {
      const randomIndex = Math.floor(Math.random() * alternatives[field].length);
      setLocalScript((prev) => ({
        ...prev,
        [field]: alternatives[field][randomIndex],
      }));
    }

    setIsGenerating(false);
  };

  const handleNext = () => {
    setScript(localScript);
    setConfig({
      tone: selectedTone,
      include_narration: includeNarration,
    });
    router.push("/create/result");
  };

  const handleBack = () => {
    router.push("/create/template");
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">커스터마이징</h1>
        <p className="mt-2 text-gray-600">
          광고 스크립트와 스타일을 설정하세요
        </p>
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Left: Preview */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Play className="h-5 w-5" />
                미리보기
              </CardTitle>
            </CardHeader>
            <CardContent>
              {/* Video Preview Placeholder */}
              <div className="relative aspect-video overflow-hidden rounded-lg bg-gradient-to-br from-gray-800 to-gray-900">
                {/* Preview content */}
                <div className="absolute inset-0 flex flex-col items-center justify-center p-8 text-center text-white">
                  <h2 className="text-2xl font-bold">{localScript.headline}</h2>
                  <p className="mt-2 text-lg text-gray-300">{localScript.subline}</p>
                  <p className="mt-4 text-sm text-gray-400">{localScript.narration}</p>
                  <Button variant="outline" className="mt-6" size="sm">
                    {localScript.cta}
                  </Button>
                </div>

                {/* Video Controls */}
                <div className="absolute bottom-0 left-0 right-0 flex items-center justify-between bg-black/50 p-3">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setIsPlaying(!isPlaying)}
                      className="rounded-full bg-white/20 p-2 hover:bg-white/30"
                    >
                      {isPlaying ? (
                        <Pause className="h-4 w-4 text-white" />
                      ) : (
                        <Play className="h-4 w-4 text-white" />
                      )}
                    </button>
                    <span className="text-sm text-white">0:00 / 0:{config.duration}</span>
                  </div>
                  <button
                    onClick={() => setIsMuted(!isMuted)}
                    className="rounded-full bg-white/20 p-2 hover:bg-white/30"
                  >
                    {isMuted ? (
                      <VolumeX className="h-4 w-4 text-white" />
                    ) : (
                      <Volume2 className="h-4 w-4 text-white" />
                    )}
                  </button>
                </div>
              </div>

              {/* Template info */}
              <div className="mt-4 flex items-center justify-between text-sm">
                <span className="text-gray-500">
                  템플릿: <span className="font-medium">{selectedTemplate?.name}</span>
                </span>
                <Badge>{config.duration}초</Badge>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right: Settings */}
        <div className="space-y-6">
          {/* Tone Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5" />
                톤앤매너
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-3">
                {toneOptions.map((tone) => (
                  <button
                    key={tone.value}
                    onClick={() => handleToneChange(tone.value)}
                    className={cn(
                      "rounded-lg border-2 p-3 text-left transition-all",
                      selectedTone === tone.value
                        ? "border-samsung-blue bg-samsung-blue/5"
                        : "border-gray-200 hover:border-gray-300"
                    )}
                  >
                    <p className="font-medium">{tone.label}</p>
                    <p className="mt-1 text-xs text-gray-500">{tone.description}</p>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Script Editor */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>스크립트</CardTitle>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleGenerateScript}
                  disabled={isGenerating}
                >
                  {isGenerating ? (
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Sparkles className="mr-2 h-4 w-4" />
                  )}
                  AI 생성
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Headline */}
              <div>
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium">헤드라인</label>
                  <button
                    onClick={() => handleRegenerateField("headline")}
                    className="text-xs text-samsung-blue hover:underline"
                  >
                    <RefreshCw className="mr-1 inline h-3 w-3" />
                    재생성
                  </button>
                </div>
                <Input
                  value={localScript.headline}
                  onChange={(e) =>
                    setLocalScript((prev) => ({ ...prev, headline: e.target.value }))
                  }
                  className="mt-1"
                  maxLength={20}
                />
              </div>

              {/* Subline */}
              <div>
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium">서브 카피</label>
                  <button
                    onClick={() => handleRegenerateField("subline")}
                    className="text-xs text-samsung-blue hover:underline"
                  >
                    <RefreshCw className="mr-1 inline h-3 w-3" />
                    재생성
                  </button>
                </div>
                <Input
                  value={localScript.subline}
                  onChange={(e) =>
                    setLocalScript((prev) => ({ ...prev, subline: e.target.value }))
                  }
                  className="mt-1"
                  maxLength={30}
                />
              </div>

              {/* Narration */}
              <div>
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium">나레이션</label>
                </div>
                <textarea
                  value={localScript.narration}
                  onChange={(e) =>
                    setLocalScript((prev) => ({ ...prev, narration: e.target.value }))
                  }
                  className="mt-1 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
                  rows={3}
                  maxLength={200}
                />
                <p className="mt-1 text-right text-xs text-gray-500">
                  {localScript.narration.length}/200
                </p>
              </div>

              {/* CTA */}
              <div>
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium">CTA 문구</label>
                  <button
                    onClick={() => handleRegenerateField("cta")}
                    className="text-xs text-samsung-blue hover:underline"
                  >
                    <RefreshCw className="mr-1 inline h-3 w-3" />
                    재생성
                  </button>
                </div>
                <Input
                  value={localScript.cta}
                  onChange={(e) =>
                    setLocalScript((prev) => ({ ...prev, cta: e.target.value }))
                  }
                  className="mt-1"
                  maxLength={15}
                />
              </div>
            </CardContent>
          </Card>

          {/* Audio Settings */}
          <Card>
            <CardHeader>
              <CardTitle>오디오</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="music">
                <TabsList className="w-full">
                  <TabsTrigger value="music" className="flex-1">
                    <Music className="mr-2 h-4 w-4" />
                    배경 음악
                  </TabsTrigger>
                  <TabsTrigger value="voice" className="flex-1">
                    <Mic className="mr-2 h-4 w-4" />
                    나레이션
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="music" className="mt-4 space-y-2">
                  {musicOptions.map((music) => (
                    <button
                      key={music.id}
                      onClick={() => setSelectedMusic(music.id)}
                      className={cn(
                        "flex w-full items-center justify-between rounded-lg border p-3 transition-all",
                        selectedMusic === music.id
                          ? "border-samsung-blue bg-samsung-blue/5"
                          : "border-gray-200 hover:border-gray-300"
                      )}
                    >
                      <span className="font-medium">{music.name}</span>
                      <Badge variant="secondary">{music.mood}</Badge>
                    </button>
                  ))}
                </TabsContent>

                <TabsContent value="voice" className="mt-4 space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">나레이션 포함</span>
                    <button
                      onClick={() => setIncludeNarration(!includeNarration)}
                      className={cn(
                        "relative h-6 w-11 rounded-full transition-colors",
                        includeNarration ? "bg-samsung-blue" : "bg-gray-200"
                      )}
                    >
                      <span
                        className={cn(
                          "absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform",
                          includeNarration ? "left-5" : "left-0.5"
                        )}
                      />
                    </button>
                  </div>

                  {includeNarration && (
                    <div className="space-y-2">
                      {voiceOptions.map((voice) => (
                        <button
                          key={voice.id}
                          onClick={() => setSelectedVoice(voice.id)}
                          className={cn(
                            "flex w-full items-center justify-between rounded-lg border p-3 transition-all",
                            selectedVoice === voice.id
                              ? "border-samsung-blue bg-samsung-blue/5"
                              : "border-gray-200 hover:border-gray-300"
                          )}
                        >
                          <div>
                            <span className="font-medium">{voice.name}</span>
                            <span className="ml-2 text-sm text-gray-500">
                              {voice.language} · {voice.gender}
                            </span>
                          </div>
                          <Play className="h-4 w-4 text-gray-400" />
                        </button>
                      ))}
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Bottom Actions */}
      <div className="flex justify-between border-t pt-6">
        <Button variant="outline" size="lg" onClick={handleBack}>
          <ArrowLeft className="mr-2 h-5 w-5" />
          이전 단계
        </Button>
        <Button variant="samsung" size="lg" onClick={handleNext}>
          영상 생성하기
          <ArrowRight className="ml-2 h-5 w-5" />
        </Button>
      </div>
    </div>
  );
}
