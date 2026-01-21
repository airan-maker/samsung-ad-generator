"use client";

import { useState, useEffect, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Header } from "@/components/common/Header";
import { Footer } from "@/components/common/Footer";
import {
  ArrowLeft,
  Play,
  Pause,
  Download,
  Share2,
  RefreshCw,
  Edit3,
  CheckCircle,
  Clock,
  AlertCircle,
  Loader2,
  Volume2,
  VolumeX,
  Maximize,
  SkipBack,
  SkipForward,
  Copy,
  Instagram,
  Youtube,
} from "lucide-react";
import type { ProjectStatus } from "@/types";

// Mock project data
const mockProject = {
  id: "proj_1",
  name: "S25 Ultra 프로모션 영상",
  product: {
    id: "prod_1",
    name: "Galaxy S25 Ultra",
    category: "smartphone",
  },
  template: {
    id: "tmpl_1",
    name: "언박싱 시퀀스",
    style: "unboxing",
  },
  status: "completed" as ProjectStatus,
  duration: 30,
  video_url: null,
  thumbnail_url: null,
  script: {
    title: "Galaxy S25 Ultra - 혁신의 시작",
    scenes: [
      {
        scene_number: 1,
        duration: 5,
        narration: "새로운 차원의 스마트폰 경험",
        visual_description: "Galaxy S25 Ultra 박스가 서서히 열리는 장면",
      },
      {
        scene_number: 2,
        duration: 8,
        narration: "200MP 카메라로 포착하는 완벽한 순간",
        visual_description: "카메라 렌즈 클로즈업, 빛 반사 효과",
      },
      {
        scene_number: 3,
        duration: 7,
        narration: "Galaxy AI가 만드는 새로운 가능성",
        visual_description: "AI 기능 사용 화면, 미래적인 인터페이스",
      },
      {
        scene_number: 4,
        duration: 5,
        narration: "S펜과 함께하는 창의적인 작업",
        visual_description: "S펜으로 그림 그리는 손 클로즈업",
      },
      {
        scene_number: 5,
        duration: 5,
        narration: "Galaxy S25 Ultra, 지금 만나보세요",
        visual_description: "제품 전체 샷, Samsung 로고",
      },
    ],
  },
  created_at: "2025-01-20T10:30:00Z",
  updated_at: "2025-01-20T10:35:00Z",
};

const statusConfig = {
  draft: {
    label: "초안",
    icon: Clock,
    color: "bg-gray-100 text-gray-600",
  },
  processing: {
    label: "생성 중",
    icon: Loader2,
    color: "bg-blue-100 text-blue-600",
  },
  completed: {
    label: "완료",
    icon: CheckCircle,
    color: "bg-green-100 text-green-600",
  },
  failed: {
    label: "실패",
    icon: AlertCircle,
    color: "bg-red-100 text-red-600",
  },
};

const exportFormats = [
  {
    id: "youtube",
    name: "YouTube",
    icon: Youtube,
    aspect: "16:9",
    resolution: "1920x1080",
  },
  {
    id: "instagram",
    name: "Instagram Reels",
    icon: Instagram,
    aspect: "9:16",
    resolution: "1080x1920",
  },
  {
    id: "tiktok",
    name: "TikTok",
    icon: Play,
    aspect: "9:16",
    resolution: "1080x1920",
  },
  {
    id: "coupang",
    name: "쿠팡 광고",
    icon: Play,
    aspect: "1:1",
    resolution: "720x720",
  },
];

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const videoRef = useRef<HTMLVideoElement>(null);

  const [project] = useState(mockProject);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [activeTab, setActiveTab] = useState("preview");
  const [selectedFormat, setSelectedFormat] = useState("youtube");

  const status = statusConfig[project.status];
  const StatusIcon = status.icon;

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("ko-KR", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  };

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    if (videoRef.current) {
      videoRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  const getCurrentScene = () => {
    let accumulatedTime = 0;
    for (const scene of project.script.scenes) {
      accumulatedTime += scene.duration;
      if (currentTime < accumulatedTime) {
        return scene;
      }
    }
    return project.script.scenes[project.script.scenes.length - 1];
  };

  const currentScene = getCurrentScene();

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Back Navigation */}
        <div className="mb-6">
          <Link
            href="/projects"
            className="inline-flex items-center text-sm text-gray-600 hover:text-samsung-blue"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            프로젝트 목록
          </Link>
        </div>

        {/* Project Header */}
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
              <Badge className={cn("gap-1", status.color)}>
                <StatusIcon
                  className={cn(
                    "h-3 w-3",
                    project.status === "processing" && "animate-spin"
                  )}
                />
                {status.label}
              </Badge>
            </div>
            <p className="mt-1 text-gray-600">
              {project.product.name} · {project.template.name}
            </p>
          </div>

          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <Edit3 className="mr-2 h-4 w-4" />
              편집
            </Button>
            <Button variant="outline" size="sm">
              <Share2 className="mr-2 h-4 w-4" />
              공유
            </Button>
            {project.status === "failed" && (
              <Button variant="samsung" size="sm">
                <RefreshCw className="mr-2 h-4 w-4" />
                재생성
              </Button>
            )}
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Video Preview Section */}
          <div className="lg:col-span-2">
            <Card>
              <CardContent className="p-0">
                {/* Video Player */}
                <div className="relative aspect-video bg-gray-900">
                  {project.video_url ? (
                    <video
                      ref={videoRef}
                      className="h-full w-full"
                      onTimeUpdate={handleTimeUpdate}
                      onEnded={() => setIsPlaying(false)}
                    >
                      <source src={project.video_url} type="video/mp4" />
                    </video>
                  ) : (
                    <div className="flex h-full items-center justify-center">
                      <div className="text-center text-white">
                        <div className="mb-4 text-6xl">🎬</div>
                        <p className="text-lg font-medium">미리보기</p>
                        <p className="text-sm text-gray-400">
                          {project.status === "processing"
                            ? "영상 생성 중..."
                            : "영상이 준비되면 여기에 표시됩니다"}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Video Controls Overlay */}
                  <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/80 to-transparent p-4">
                    {/* Progress Bar */}
                    <div className="mb-3">
                      <input
                        type="range"
                        min={0}
                        max={project.duration}
                        value={currentTime}
                        onChange={handleSeek}
                        className="h-1 w-full cursor-pointer appearance-none rounded-full bg-white/30"
                        style={{
                          background: `linear-gradient(to right, #1428A0 ${
                            (currentTime / project.duration) * 100
                          }%, rgba(255,255,255,0.3) ${
                            (currentTime / project.duration) * 100
                          }%)`,
                        }}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={togglePlay}
                          className="rounded-full bg-white p-2 text-gray-900 transition hover:bg-gray-100"
                        >
                          {isPlaying ? (
                            <Pause className="h-5 w-5" />
                          ) : (
                            <Play className="h-5 w-5" />
                          )}
                        </button>
                        <button className="p-2 text-white hover:text-gray-300">
                          <SkipBack className="h-4 w-4" />
                        </button>
                        <button className="p-2 text-white hover:text-gray-300">
                          <SkipForward className="h-4 w-4" />
                        </button>
                        <button
                          onClick={toggleMute}
                          className="p-2 text-white hover:text-gray-300"
                        >
                          {isMuted ? (
                            <VolumeX className="h-4 w-4" />
                          ) : (
                            <Volume2 className="h-4 w-4" />
                          )}
                        </button>
                        <span className="text-sm text-white">
                          {formatTime(currentTime)} / {formatTime(project.duration)}
                        </span>
                      </div>

                      <button className="p-2 text-white hover:text-gray-300">
                        <Maximize className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>

                {/* Tabs */}
                <Tabs value={activeTab} onValueChange={setActiveTab} className="p-4">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="preview">미리보기</TabsTrigger>
                    <TabsTrigger value="script">스크립트</TabsTrigger>
                    <TabsTrigger value="export">내보내기</TabsTrigger>
                  </TabsList>

                  <TabsContent value="preview" className="mt-4">
                    {/* Current Scene Info */}
                    <div className="rounded-lg bg-gray-50 p-4">
                      <div className="mb-2 flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-500">
                          Scene {currentScene?.scene_number || 1}
                        </span>
                        <span className="text-sm text-gray-400">
                          {currentScene?.duration}초
                        </span>
                      </div>
                      <p className="text-lg font-medium text-gray-900">
                        {currentScene?.narration || "나레이션 없음"}
                      </p>
                      <p className="mt-2 text-sm text-gray-500">
                        {currentScene?.visual_description || "설명 없음"}
                      </p>
                    </div>
                  </TabsContent>

                  <TabsContent value="script" className="mt-4">
                    <div className="space-y-3">
                      {project.script.scenes.map((scene, index) => (
                        <div
                          key={index}
                          className={cn(
                            "rounded-lg border p-4 transition",
                            currentScene?.scene_number === scene.scene_number
                              ? "border-samsung-blue bg-blue-50"
                              : "border-gray-200 hover:border-gray-300"
                          )}
                        >
                          <div className="mb-2 flex items-center justify-between">
                            <span className="font-medium text-gray-900">
                              Scene {scene.scene_number}
                            </span>
                            <span className="text-sm text-gray-500">
                              {scene.duration}초
                            </span>
                          </div>
                          <p className="text-gray-700">{scene.narration}</p>
                          <p className="mt-2 text-sm text-gray-500">
                            {scene.visual_description}
                          </p>
                        </div>
                      ))}
                    </div>
                  </TabsContent>

                  <TabsContent value="export" className="mt-4">
                    <div className="space-y-4">
                      <p className="text-sm text-gray-600">
                        다양한 플랫폼에 맞는 형식으로 영상을 다운로드하세요.
                      </p>

                      <div className="grid gap-3 sm:grid-cols-2">
                        {exportFormats.map((format) => {
                          const FormatIcon = format.icon;
                          return (
                            <button
                              key={format.id}
                              onClick={() => setSelectedFormat(format.id)}
                              className={cn(
                                "flex items-center gap-3 rounded-lg border p-4 text-left transition",
                                selectedFormat === format.id
                                  ? "border-samsung-blue bg-blue-50"
                                  : "border-gray-200 hover:border-gray-300"
                              )}
                            >
                              <div
                                className={cn(
                                  "flex h-10 w-10 items-center justify-center rounded-lg",
                                  selectedFormat === format.id
                                    ? "bg-samsung-blue text-white"
                                    : "bg-gray-100 text-gray-600"
                                )}
                              >
                                <FormatIcon className="h-5 w-5" />
                              </div>
                              <div>
                                <p className="font-medium text-gray-900">
                                  {format.name}
                                </p>
                                <p className="text-sm text-gray-500">
                                  {format.aspect} · {format.resolution}
                                </p>
                              </div>
                            </button>
                          );
                        })}
                      </div>

                      <Button
                        variant="samsung"
                        className="w-full"
                        disabled={project.status !== "completed"}
                      >
                        <Download className="mr-2 h-5 w-5" />
                        다운로드
                      </Button>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Project Info */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">프로젝트 정보</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-gray-500">제품</p>
                  <p className="font-medium">{project.product.name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">템플릿</p>
                  <p className="font-medium">{project.template.name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">영상 길이</p>
                  <p className="font-medium">{project.duration}초</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">생성일</p>
                  <p className="font-medium">{formatDate(project.created_at)}</p>
                </div>
              </CardContent>
            </Card>

            {/* Script Summary */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-lg">스크립트</CardTitle>
                <Button variant="ghost" size="sm">
                  <Copy className="mr-2 h-4 w-4" />
                  복사
                </Button>
              </CardHeader>
              <CardContent>
                <h3 className="mb-2 font-semibold">{project.script.title}</h3>
                <p className="text-sm text-gray-600">
                  {project.script.scenes.length}개 씬 · 총 {project.duration}초
                </p>
              </CardContent>
            </Card>

            {/* Processing Status (if processing) */}
            {project.status === "processing" && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">생성 진행 상황</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Progress value={65} className="h-2" />
                  <div className="space-y-2">
                    {[
                      { name: "스크립트 처리", status: "completed" },
                      { name: "나레이션 생성", status: "completed" },
                      { name: "영상 생성", status: "in_progress" },
                      { name: "영상 합성", status: "pending" },
                      { name: "최종 내보내기", status: "pending" },
                    ].map((step, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between text-sm"
                      >
                        <span
                          className={cn(
                            step.status === "completed"
                              ? "text-green-600"
                              : step.status === "in_progress"
                              ? "text-samsung-blue"
                              : "text-gray-400"
                          )}
                        >
                          {step.name}
                        </span>
                        {step.status === "completed" && (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        )}
                        {step.status === "in_progress" && (
                          <Loader2 className="h-4 w-4 animate-spin text-samsung-blue" />
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">빠른 작업</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" className="w-full justify-start">
                  <Edit3 className="mr-2 h-4 w-4" />
                  스크립트 수정
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <RefreshCw className="mr-2 h-4 w-4" />
                  다른 템플릿으로 재생성
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Copy className="mr-2 h-4 w-4" />
                  프로젝트 복제
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
