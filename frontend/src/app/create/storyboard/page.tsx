"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useDropzone } from "react-dropzone";
import {
  Upload,
  Image as ImageIcon,
  Play,
  RefreshCw,
  Download,
  ChevronRight,
  Loader2,
  Check,
  Wand2,
  Film,
  Grid3X3,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

type StoryboardStyle = "cinematic" | "minimalist" | "dynamic" | "lifestyle" | "tech" | "luxury";

interface Scene {
  scene_number: number;
  title: string;
  description: string;
  camera_angle: string;
  lighting: string;
  duration: number;
  transition: string;
  image_url: string | null;
  video_url: string | null;
  prompt: string;
}

interface StoryboardData {
  storyboard_id: string;
  product_name: string;
  product_category: string;
  style: string;
  total_duration: number;
  status: string;
  grid: Scene[][];
  thumbnail_url: string | null;
}

interface StoryboardResponse {
  storyboard_id: string;
  status: string;
  progress: number;
  message: string;
  storyboard: StoryboardData | null;
}

const STYLES: { value: StoryboardStyle; label: string; description: string }[] = [
  { value: "cinematic", label: "시네마틱", description: "영화같은 드라마틱한 연출" },
  { value: "minimalist", label: "미니멀", description: "깔끔하고 심플한 스타일" },
  { value: "dynamic", label: "다이나믹", description: "역동적이고 에너지 넘치는" },
  { value: "lifestyle", label: "라이프스타일", description: "일상 속 자연스러운 모습" },
  { value: "tech", label: "테크", description: "미래지향적 하이테크 느낌" },
  { value: "luxury", label: "럭셔리", description: "프리미엄 고급스러운 분위기" },
];

const CATEGORIES = [
  { value: "smartphone", label: "스마트폰" },
  { value: "tv", label: "TV" },
  { value: "appliance", label: "가전제품" },
  { value: "wearable", label: "웨어러블" },
];

export default function StoryboardPage() {
  const router = useRouter();
  const [step, setStep] = useState<"upload" | "configure" | "generating" | "preview">("upload");
  const [productImage, setProductImage] = useState<File | null>(null);
  const [productImagePreview, setProductImagePreview] = useState<string | null>(null);
  const [category, setCategory] = useState("smartphone");
  const [style, setStyle] = useState<StoryboardStyle>("cinematic");
  const [duration, setDuration] = useState(15);
  const [storyboardId, setStoryboardId] = useState<string | null>(null);
  const [storyboard, setStoryboard] = useState<StoryboardData | null>(null);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState("");
  const [selectedScene, setSelectedScene] = useState<Scene | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setProductImage(file);
      const reader = new FileReader();
      reader.onload = () => {
        setProductImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
      setStep("configure");
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".png", ".jpg", ".jpeg", ".webp"],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  const handleGenerateStoryboard = async () => {
    if (!productImage) return;

    setStep("generating");
    setIsGenerating(true);
    setProgress(0);
    setStatusMessage("스토리보드 생성 시작...");

    try {
      const formData = new FormData();
      formData.append("product_image", productImage);
      formData.append("product_category", category);
      formData.append("style", style);
      formData.append("target_duration", duration.toString());

      // Start generation
      const response = await fetch("/api/v1/storyboard/generate", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to start storyboard generation");
      }

      const data = await response.json();
      setStoryboardId(data.storyboard_id);

      // Poll for progress
      await pollStoryboardStatus(data.storyboard_id);
    } catch (error) {
      console.error("Storyboard generation error:", error);
      setStatusMessage("오류가 발생했습니다. 다시 시도해주세요.");
      setIsGenerating(false);
    }
  };

  const pollStoryboardStatus = async (id: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/v1/storyboard/${id}`);
        const data: StoryboardResponse = await response.json();

        setProgress(data.progress);
        setStatusMessage(data.message);

        if (data.status === "completed" && data.storyboard) {
          clearInterval(pollInterval);
          setStoryboard(data.storyboard);
          setStep("preview");
          setIsGenerating(false);
        } else if (data.status === "failed") {
          clearInterval(pollInterval);
          setStatusMessage(`생성 실패: ${data.message}`);
          setIsGenerating(false);
        }
      } catch (error) {
        console.error("Polling error:", error);
      }
    }, 2000);

    // Cleanup after 5 minutes
    setTimeout(() => {
      clearInterval(pollInterval);
      if (isGenerating) {
        setStatusMessage("시간 초과. 다시 시도해주세요.");
        setIsGenerating(false);
      }
    }, 5 * 60 * 1000);
  };

  const handleCompileVideo = async () => {
    if (!storyboardId) return;

    try {
      const response = await fetch(`/api/v1/storyboard/${storyboardId}/compile-video`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          include_music: "true",
          include_voiceover: "false",
          transition_style: "fade",
        }),
      });

      if (response.ok) {
        const data = await response.json();
        router.push(`/create/result?video_id=${data.video_id}`);
      }
    } catch (error) {
      console.error("Video compilation error:", error);
    }
  };

  const handleRegenerateScene = async (sceneNumber: number) => {
    if (!storyboardId) return;

    try {
      await fetch(`/api/v1/storyboard/${storyboardId}/regenerate-scene/${sceneNumber}`, {
        method: "POST",
      });
      // Refresh storyboard data
      const response = await fetch(`/api/v1/storyboard/${storyboardId}`);
      const data: StoryboardResponse = await response.json();
      if (data.storyboard) {
        setStoryboard(data.storyboard);
      }
    } catch (error) {
      console.error("Scene regeneration error:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <div className="flex items-center gap-4">
            <Grid3X3 className="h-6 w-6 text-samsung-blue" />
            <h1 className="text-xl font-bold">AI 스토리보드 생성</h1>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <span className={step === "upload" ? "text-samsung-blue font-medium" : ""}>
              1. 이미지 업로드
            </span>
            <ChevronRight className="h-4 w-4" />
            <span className={step === "configure" ? "text-samsung-blue font-medium" : ""}>
              2. 스타일 설정
            </span>
            <ChevronRight className="h-4 w-4" />
            <span className={step === "generating" ? "text-samsung-blue font-medium" : ""}>
              3. 생성 중
            </span>
            <ChevronRight className="h-4 w-4" />
            <span className={step === "preview" ? "text-samsung-blue font-medium" : ""}>
              4. 미리보기
            </span>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8">
        {/* Step 1: Upload */}
        {step === "upload" && (
          <div className="mx-auto max-w-2xl">
            <div className="mb-8 text-center">
              <h2 className="text-2xl font-bold text-gray-900">제품 이미지 업로드</h2>
              <p className="mt-2 text-gray-600">
                제품 이미지를 업로드하면 AI가 자동으로 3x3 스토리보드를 생성합니다
              </p>
            </div>

            <div
              {...getRootProps()}
              className={`cursor-pointer rounded-2xl border-2 border-dashed p-12 text-center transition-colors ${
                isDragActive
                  ? "border-samsung-blue bg-blue-50"
                  : "border-gray-300 hover:border-samsung-blue hover:bg-gray-50"
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-4 text-lg font-medium text-gray-700">
                {isDragActive ? "여기에 놓으세요" : "이미지를 드래그하거나 클릭하여 업로드"}
              </p>
              <p className="mt-2 text-sm text-gray-500">PNG, JPG, WEBP (최대 10MB)</p>
            </div>
          </div>
        )}

        {/* Step 2: Configure */}
        {step === "configure" && productImagePreview && (
          <div className="grid gap-8 lg:grid-cols-2">
            {/* Image Preview */}
            <div className="rounded-2xl bg-white p-6 shadow-sm">
              <h3 className="mb-4 font-semibold text-gray-900">업로드된 이미지</h3>
              <div className="relative aspect-square overflow-hidden rounded-xl bg-gray-100">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={productImagePreview}
                  alt="Product"
                  className="h-full w-full object-contain"
                />
              </div>
              <button
                onClick={() => {
                  setProductImage(null);
                  setProductImagePreview(null);
                  setStep("upload");
                }}
                className="mt-4 text-sm text-gray-500 hover:text-gray-700"
              >
                다른 이미지 선택
              </button>
            </div>

            {/* Configuration */}
            <div className="space-y-6">
              {/* Category */}
              <div className="rounded-2xl bg-white p-6 shadow-sm">
                <h3 className="mb-4 font-semibold text-gray-900">제품 카테고리</h3>
                <div className="grid grid-cols-2 gap-3">
                  {CATEGORIES.map((cat) => (
                    <button
                      key={cat.value}
                      onClick={() => setCategory(cat.value)}
                      className={`rounded-xl border-2 px-4 py-3 text-sm font-medium transition-colors ${
                        category === cat.value
                          ? "border-samsung-blue bg-blue-50 text-samsung-blue"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      {cat.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Style */}
              <div className="rounded-2xl bg-white p-6 shadow-sm">
                <h3 className="mb-4 font-semibold text-gray-900">스토리보드 스타일</h3>
                <div className="grid grid-cols-2 gap-3">
                  {STYLES.map((s) => (
                    <button
                      key={s.value}
                      onClick={() => setStyle(s.value)}
                      className={`rounded-xl border-2 px-4 py-3 text-left transition-colors ${
                        style === s.value
                          ? "border-samsung-blue bg-blue-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <div className={`font-medium ${style === s.value ? "text-samsung-blue" : ""}`}>
                        {s.label}
                      </div>
                      <div className="text-xs text-gray-500">{s.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Duration */}
              <div className="rounded-2xl bg-white p-6 shadow-sm">
                <h3 className="mb-4 font-semibold text-gray-900">영상 길이</h3>
                <div className="flex gap-3">
                  {[15, 30, 60].map((d) => (
                    <button
                      key={d}
                      onClick={() => setDuration(d)}
                      className={`flex-1 rounded-xl border-2 py-3 font-medium transition-colors ${
                        duration === d
                          ? "border-samsung-blue bg-blue-50 text-samsung-blue"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      {d}초
                    </button>
                  ))}
                </div>
                <p className="mt-2 text-xs text-gray-500">
                  9개 장면이 각각 {(duration / 9).toFixed(1)}초씩 재생됩니다
                </p>
              </div>

              {/* Generate Button */}
              <Button
                onClick={handleGenerateStoryboard}
                className="w-full bg-samsung-blue py-6 text-lg hover:bg-blue-700"
              >
                <Wand2 className="mr-2 h-5 w-5" />
                스토리보드 생성하기
              </Button>
            </div>
          </div>
        )}

        {/* Step 3: Generating */}
        {step === "generating" && (
          <div className="mx-auto max-w-xl text-center">
            <div className="rounded-2xl bg-white p-12 shadow-sm">
              <Loader2 className="mx-auto h-16 w-16 animate-spin text-samsung-blue" />
              <h2 className="mt-6 text-xl font-bold text-gray-900">스토리보드 생성 중...</h2>
              <p className="mt-2 text-gray-600">{statusMessage}</p>

              {/* Progress Bar */}
              <div className="mt-8">
                <div className="h-2 overflow-hidden rounded-full bg-gray-200">
                  <div
                    className="h-full bg-samsung-blue transition-all duration-500"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <p className="mt-2 text-sm text-gray-500">{progress}% 완료</p>
              </div>

              {/* Progress Steps */}
              <div className="mt-8 space-y-3 text-left">
                {[
                  { label: "제품 이미지 분석", threshold: 20 },
                  { label: "장면 구성 생성", threshold: 40 },
                  { label: "2K 이미지 생성 (9장)", threshold: 70 },
                  { label: "영상 클립 변환", threshold: 90 },
                  { label: "스토리보드 완성", threshold: 100 },
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-3">
                    {progress >= item.threshold ? (
                      <Check className="h-5 w-5 text-green-500" />
                    ) : progress >= item.threshold - 20 ? (
                      <Loader2 className="h-5 w-5 animate-spin text-samsung-blue" />
                    ) : (
                      <div className="h-5 w-5 rounded-full border-2 border-gray-300" />
                    )}
                    <span
                      className={
                        progress >= item.threshold
                          ? "text-gray-900"
                          : progress >= item.threshold - 20
                          ? "text-samsung-blue"
                          : "text-gray-400"
                      }
                    >
                      {item.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Preview */}
        {step === "preview" && storyboard && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{storyboard.product_name}</h2>
                <p className="text-gray-600">
                  {storyboard.style} 스타일 · {storyboard.total_duration}초
                </p>
              </div>
              <div className="flex gap-3">
                <Button variant="outline" onClick={() => setStep("configure")}>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  다시 생성
                </Button>
                <Button onClick={handleCompileVideo} className="bg-samsung-blue hover:bg-blue-700">
                  <Film className="mr-2 h-4 w-4" />
                  영상으로 만들기
                </Button>
              </div>
            </div>

            {/* 3x3 Grid */}
            <div className="grid grid-cols-3 gap-4">
              {storyboard.grid.flat().map((scene, index) => (
                <div
                  key={index}
                  onClick={() => setSelectedScene(scene)}
                  className={`group cursor-pointer overflow-hidden rounded-xl border-2 bg-white transition-all hover:shadow-lg ${
                    selectedScene?.scene_number === scene.scene_number
                      ? "border-samsung-blue"
                      : "border-transparent"
                  }`}
                >
                  {/* Scene Image/Video */}
                  <div className="relative aspect-square bg-gray-900">
                    {scene.image_url ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={scene.image_url}
                        alt={scene.title}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center">
                        <ImageIcon className="h-12 w-12 text-gray-600" />
                      </div>
                    )}

                    {/* Scene Number Badge */}
                    <div className="absolute left-2 top-2 rounded-full bg-black/70 px-2 py-1 text-xs font-medium text-white">
                      {scene.scene_number}
                    </div>

                    {/* Play Button Overlay */}
                    {scene.video_url && (
                      <div className="absolute inset-0 flex items-center justify-center bg-black/30 opacity-0 transition-opacity group-hover:opacity-100">
                        <Play className="h-12 w-12 text-white" />
                      </div>
                    )}

                    {/* Duration */}
                    <div className="absolute bottom-2 right-2 rounded bg-black/70 px-2 py-1 text-xs text-white">
                      {scene.duration.toFixed(1)}초
                    </div>
                  </div>

                  {/* Scene Info */}
                  <div className="p-3">
                    <h4 className="font-medium text-gray-900">{scene.title}</h4>
                    <p className="mt-1 text-xs text-gray-500">{scene.camera_angle}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Scene Detail Panel */}
            {selectedScene && (
              <div className="rounded-2xl bg-white p-6 shadow-sm">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold">
                      장면 {selectedScene.scene_number}: {selectedScene.title}
                    </h3>
                    <p className="mt-1 text-gray-600">{selectedScene.description}</p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleRegenerateScene(selectedScene.scene_number)}
                  >
                    <RefreshCw className="mr-2 h-4 w-4" />
                    이 장면 다시 생성
                  </Button>
                </div>

                <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">카메라 앵글</span>
                    <p className="font-medium">{selectedScene.camera_angle}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">라이팅</span>
                    <p className="font-medium">{selectedScene.lighting}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">전환 효과</span>
                    <p className="font-medium">{selectedScene.transition}</p>
                  </div>
                </div>

                <div className="mt-4">
                  <span className="text-sm text-gray-500">이미지 생성 프롬프트</span>
                  <p className="mt-1 rounded-lg bg-gray-50 p-3 text-sm text-gray-700">
                    {selectedScene.prompt}
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
