"use client";

import { useState } from "react";
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Volume2,
  VolumeX,
  Type,
  Music,
  Palette,
  Layers,
  Download,
  Share2,
  ChevronUp,
  ChevronDown,
  Edit3,
  Trash2,
  Plus,
  Clock,
  Smartphone,
  Monitor,
  Square,
} from "lucide-react";

interface Scene {
  id: string;
  order: number;
  duration: number;
  narration: string;
  visualType: "image" | "video";
  visualUrl: string;
  textOverlay?: string;
}

interface MobileVideoEditorProps {
  projectId: string;
  videoUrl?: string;
  scenes: Scene[];
  onSceneUpdate: (scenes: Scene[]) => void;
  onExport: (format: string) => void;
}

type AspectRatio = "16:9" | "9:16" | "1:1" | "4:5";

export function MobileVideoEditor({
  projectId,
  videoUrl,
  scenes,
  onSceneUpdate,
  onExport,
}: MobileVideoEditorProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [activePanel, setActivePanel] = useState<"scenes" | "text" | "music" | "style" | null>(
    "scenes"
  );
  const [selectedScene, setSelectedScene] = useState<string | null>(null);
  const [aspectRatio, setAspectRatio] = useState<AspectRatio>("16:9");

  const totalDuration = scenes.reduce((sum, s) => sum + s.duration, 0);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const getAspectRatioClass = () => {
    switch (aspectRatio) {
      case "9:16":
        return "aspect-[9/16] max-h-[50vh]";
      case "1:1":
        return "aspect-square max-h-[40vh]";
      case "4:5":
        return "aspect-[4/5] max-h-[50vh]";
      default:
        return "aspect-video";
    }
  };

  const panelConfig = [
    { id: "scenes", icon: Layers, label: "씬" },
    { id: "text", icon: Type, label: "텍스트" },
    { id: "music", icon: Music, label: "음악" },
    { id: "style", icon: Palette, label: "스타일" },
  ] as const;

  return (
    <div className="flex h-screen flex-col bg-black">
      {/* Video Preview */}
      <div className="flex flex-1 items-center justify-center bg-gray-900 p-4">
        <div className={`relative w-full ${getAspectRatioClass()} bg-black rounded-lg overflow-hidden`}>
          {videoUrl ? (
            <video
              src={videoUrl}
              className="h-full w-full object-contain"
              autoPlay={isPlaying}
              muted={isMuted}
            />
          ) : (
            <div className="flex h-full items-center justify-center text-gray-500">
              <div className="text-center">
                <Play className="mx-auto h-12 w-12 mb-2" />
                <p>미리보기</p>
              </div>
            </div>
          )}

          {/* Aspect Ratio Selector */}
          <div className="absolute right-2 top-2 flex gap-1 rounded-lg bg-black/50 p-1">
            <button
              onClick={() => setAspectRatio("16:9")}
              className={`rounded p-1.5 ${aspectRatio === "16:9" ? "bg-white/20" : ""}`}
              title="YouTube (16:9)"
            >
              <Monitor className="h-4 w-4 text-white" />
            </button>
            <button
              onClick={() => setAspectRatio("9:16")}
              className={`rounded p-1.5 ${aspectRatio === "9:16" ? "bg-white/20" : ""}`}
              title="TikTok/Reels (9:16)"
            >
              <Smartphone className="h-4 w-4 text-white" />
            </button>
            <button
              onClick={() => setAspectRatio("1:1")}
              className={`rounded p-1.5 ${aspectRatio === "1:1" ? "bg-white/20" : ""}`}
              title="Instagram (1:1)"
            >
              <Square className="h-4 w-4 text-white" />
            </button>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="bg-gray-800 px-4 py-2">
        {/* Progress Bar */}
        <div className="mb-2">
          <input
            type="range"
            min={0}
            max={totalDuration}
            value={currentTime}
            onChange={(e) => setCurrentTime(Number(e.target.value))}
            className="w-full h-1 rounded-full appearance-none bg-gray-600 cursor-pointer
              [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3
              [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full
              [&::-webkit-slider-thumb]:bg-samsung-blue"
          />
        </div>

        {/* Controls */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1">
            <button
              onClick={() => setCurrentTime(Math.max(0, currentTime - 5))}
              className="rounded-full p-2 text-white hover:bg-white/10"
            >
              <SkipBack className="h-5 w-5" />
            </button>
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="rounded-full bg-samsung-blue p-3 text-white"
            >
              {isPlaying ? (
                <Pause className="h-6 w-6" />
              ) : (
                <Play className="h-6 w-6 ml-0.5" />
              )}
            </button>
            <button
              onClick={() => setCurrentTime(Math.min(totalDuration, currentTime + 5))}
              className="rounded-full p-2 text-white hover:bg-white/10"
            >
              <SkipForward className="h-5 w-5" />
            </button>
          </div>

          <div className="flex items-center gap-3 text-sm text-white">
            <span>
              {formatTime(currentTime)} / {formatTime(totalDuration)}
            </span>
            <button
              onClick={() => setIsMuted(!isMuted)}
              className="rounded p-1.5 hover:bg-white/10"
            >
              {isMuted ? (
                <VolumeX className="h-5 w-5" />
              ) : (
                <Volume2 className="h-5 w-5" />
              )}
            </button>
          </div>
        </div>

        {/* Scene Thumbnails */}
        <div className="mt-3 flex gap-1 overflow-x-auto pb-2">
          {scenes.map((scene, index) => (
            <button
              key={scene.id}
              onClick={() => setSelectedScene(scene.id)}
              className={`relative flex-shrink-0 rounded overflow-hidden transition-all ${
                selectedScene === scene.id
                  ? "ring-2 ring-samsung-blue"
                  : "opacity-70 hover:opacity-100"
              }`}
              style={{ width: `${(scene.duration / totalDuration) * 200}px`, minWidth: 40 }}
            >
              <div className="aspect-video bg-gray-700">
                {scene.visualUrl && (
                  <img
                    src={scene.visualUrl}
                    alt={`Scene ${index + 1}`}
                    className="h-full w-full object-cover"
                  />
                )}
              </div>
              <div className="absolute bottom-0 left-0 right-0 bg-black/60 px-1 py-0.5 text-xs text-white">
                {scene.duration}s
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Bottom Panel Tabs */}
      <div className="flex border-t border-gray-700 bg-gray-900">
        {panelConfig.map((panel) => (
          <button
            key={panel.id}
            onClick={() => setActivePanel(activePanel === panel.id ? null : panel.id)}
            className={`flex flex-1 flex-col items-center gap-1 py-3 text-xs transition-colors ${
              activePanel === panel.id
                ? "bg-gray-800 text-samsung-blue"
                : "text-gray-400 hover:text-white"
            }`}
          >
            <panel.icon className="h-5 w-5" />
            {panel.label}
          </button>
        ))}
      </div>

      {/* Active Panel Content */}
      {activePanel && (
        <div className="border-t border-gray-700 bg-gray-900 p-4 max-h-64 overflow-y-auto">
          {activePanel === "scenes" && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="font-medium text-white">씬 편집</h3>
                <button className="flex items-center gap-1 rounded-lg bg-samsung-blue px-3 py-1.5 text-sm text-white">
                  <Plus className="h-4 w-4" />
                  씬 추가
                </button>
              </div>
              {scenes.map((scene, index) => (
                <div
                  key={scene.id}
                  className={`rounded-lg border p-3 ${
                    selectedScene === scene.id
                      ? "border-samsung-blue bg-gray-800"
                      : "border-gray-700"
                  }`}
                  onClick={() => setSelectedScene(scene.id)}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="text-sm font-medium text-white">
                        씬 {index + 1}
                      </div>
                      <div className="mt-1 text-xs text-gray-400 line-clamp-2">
                        {scene.narration || "나레이션 없음"}
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="flex items-center gap-1 text-xs text-gray-400">
                        <Clock className="h-3 w-3" />
                        {scene.duration}초
                      </span>
                      <button className="p-1 text-gray-400 hover:text-white">
                        <Edit3 className="h-4 w-4" />
                      </button>
                      <button className="p-1 text-gray-400 hover:text-red-400">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activePanel === "text" && (
            <div className="space-y-4">
              <h3 className="font-medium text-white">텍스트 오버레이</h3>
              <div>
                <label className="block text-sm text-gray-400 mb-1">헤드라인</label>
                <input
                  type="text"
                  placeholder="헤드라인 입력..."
                  className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-white placeholder-gray-500 focus:border-samsung-blue focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">서브 텍스트</label>
                <input
                  type="text"
                  placeholder="서브 텍스트 입력..."
                  className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-white placeholder-gray-500 focus:border-samsung-blue focus:outline-none"
                />
              </div>
              <div className="flex gap-2">
                <div className="flex-1">
                  <label className="block text-sm text-gray-400 mb-1">폰트</label>
                  <select className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-white">
                    <option>Samsung One</option>
                    <option>Pretendard</option>
                    <option>Noto Sans KR</option>
                  </select>
                </div>
                <div className="flex-1">
                  <label className="block text-sm text-gray-400 mb-1">크기</label>
                  <select className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-white">
                    <option>Small</option>
                    <option>Medium</option>
                    <option>Large</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {activePanel === "music" && (
            <div className="space-y-3">
              <h3 className="font-medium text-white">배경 음악</h3>
              {[
                { name: "Upbeat Corporate", duration: "2:30", mood: "에너지틱" },
                { name: "Soft & Elegant", duration: "3:15", mood: "고급스러운" },
                { name: "Tech Innovation", duration: "2:45", mood: "미래지향적" },
                { name: "Emotional Journey", duration: "3:00", mood: "감성적" },
              ].map((track) => (
                <div
                  key={track.name}
                  className="flex items-center justify-between rounded-lg border border-gray-700 p-3 hover:border-samsung-blue cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <button className="rounded-full bg-samsung-blue p-2">
                      <Play className="h-4 w-4 text-white ml-0.5" />
                    </button>
                    <div>
                      <div className="text-sm font-medium text-white">{track.name}</div>
                      <div className="text-xs text-gray-400">{track.mood} · {track.duration}</div>
                    </div>
                  </div>
                  <button className="rounded bg-gray-700 px-2 py-1 text-xs text-white hover:bg-gray-600">
                    선택
                  </button>
                </div>
              ))}
            </div>
          )}

          {activePanel === "style" && (
            <div className="space-y-4">
              <h3 className="font-medium text-white">스타일 설정</h3>
              <div>
                <label className="block text-sm text-gray-400 mb-2">컬러 테마</label>
                <div className="flex gap-2">
                  {["#1428A0", "#000000", "#FFFFFF", "#FF6B6B", "#4ECDC4"].map((color) => (
                    <button
                      key={color}
                      className="h-10 w-10 rounded-lg border-2 border-gray-600 hover:border-samsung-blue"
                      style={{ backgroundColor: color }}
                    />
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">전환 효과</label>
                <select className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-white">
                  <option>페이드</option>
                  <option>슬라이드</option>
                  <option>줌</option>
                  <option>디졸브</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">로고 위치</label>
                <div className="grid grid-cols-3 gap-2">
                  {["좌상단", "중앙 상단", "우상단", "좌하단", "중앙 하단", "우하단"].map((pos) => (
                    <button
                      key={pos}
                      className="rounded border border-gray-700 py-2 text-xs text-gray-300 hover:border-samsung-blue hover:text-white"
                    >
                      {pos}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Export Button */}
      <div className="flex gap-2 border-t border-gray-700 bg-gray-900 p-4">
        <button
          onClick={() => onExport("all")}
          className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-samsung-blue py-3 font-medium text-white"
        >
          <Download className="h-5 w-5" />
          내보내기
        </button>
        <button className="rounded-lg border border-gray-700 p-3 text-white hover:bg-gray-800">
          <Share2 className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}
