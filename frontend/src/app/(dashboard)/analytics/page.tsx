"use client";

import { useState } from "react";
import {
  BarChart3,
  TrendingUp,
  Video,
  Users,
  Clock,
  Download,
  Calendar,
  ArrowUpRight,
  ArrowDownRight,
  Play,
  Eye,
  Heart,
  Share2,
  MousePointer,
} from "lucide-react";

type TimeRange = "7d" | "30d" | "90d" | "year";

// Mock data
const mockMetrics = {
  totalVideos: 45,
  completedVideos: 42,
  totalViews: 125000,
  totalEngagement: 8500,
  avgGenerationTime: 120,
  creditsUsed: 45,
  creditsRemaining: 55,
};

const mockTrends = [
  { date: "01/15", videos: 3, views: 4200 },
  { date: "01/16", videos: 5, views: 6800 },
  { date: "01/17", videos: 2, views: 3100 },
  { date: "01/18", videos: 4, views: 5400 },
  { date: "01/19", videos: 6, views: 8900 },
  { date: "01/20", videos: 3, views: 4500 },
  { date: "01/21", videos: 7, views: 9200 },
];

const mockTopVideos = [
  {
    id: "1",
    name: "Galaxy S25 Ultra - 언박싱",
    views: 25600,
    engagement: 2100,
    ctr: 0.082,
    platform: "YouTube",
  },
  {
    id: "2",
    name: "Galaxy Z Fold 6 - 기능 하이라이트",
    views: 18300,
    engagement: 1450,
    ctr: 0.079,
    platform: "Instagram",
  },
  {
    id: "3",
    name: "Galaxy Buds 3 Pro - MZ 리뷰",
    views: 15200,
    engagement: 1280,
    ctr: 0.084,
    platform: "TikTok",
  },
  {
    id: "4",
    name: "Galaxy Watch 7 - 라이프스타일",
    views: 12400,
    engagement: 980,
    ctr: 0.079,
    platform: "YouTube",
  },
  {
    id: "5",
    name: "Galaxy Ring - 신제품 소개",
    views: 9800,
    engagement: 720,
    ctr: 0.073,
    platform: "Coupang",
  },
];

const mockPlatformStats = [
  { platform: "YouTube", views: 52000, percentage: 0.42, color: "bg-red-500" },
  { platform: "Instagram", views: 31000, percentage: 0.25, color: "bg-pink-500" },
  { platform: "TikTok", views: 28000, percentage: 0.22, color: "bg-black" },
  { platform: "Coupang", views: 14000, percentage: 0.11, color: "bg-orange-500" },
];

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState<TimeRange>("30d");

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
    if (num >= 1000) return (num / 1000).toFixed(1) + "K";
    return num.toString();
  };

  const getMaxValue = (data: typeof mockTrends, key: "videos" | "views") => {
    return Math.max(...data.map((d) => d[key]));
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">분석 대시보드</h1>
            <p className="mt-1 text-gray-600">
              영상 성과와 사용량을 한눈에 확인하세요
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Time Range Selector */}
            <div className="flex rounded-lg border bg-white p-1">
              {(["7d", "30d", "90d", "year"] as const).map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                    timeRange === range
                      ? "bg-samsung-blue text-white"
                      : "text-gray-600 hover:text-gray-900"
                  }`}
                >
                  {range === "7d"
                    ? "7일"
                    : range === "30d"
                    ? "30일"
                    : range === "90d"
                    ? "90일"
                    : "올해"}
                </button>
              ))}
            </div>

            <button className="flex items-center gap-2 rounded-lg border bg-white px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50">
              <Download className="h-4 w-4" />
              내보내기
            </button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="rounded-lg bg-blue-100 p-2">
                <Video className="h-5 w-5 text-blue-600" />
              </div>
              <span className="flex items-center gap-1 text-sm font-medium text-green-600">
                <ArrowUpRight className="h-4 w-4" />
                +12%
              </span>
            </div>
            <div className="mt-4">
              <div className="text-2xl font-bold text-gray-900">
                {mockMetrics.totalVideos}
              </div>
              <div className="text-sm text-gray-500">총 생성 영상</div>
            </div>
          </div>

          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="rounded-lg bg-green-100 p-2">
                <Eye className="h-5 w-5 text-green-600" />
              </div>
              <span className="flex items-center gap-1 text-sm font-medium text-green-600">
                <ArrowUpRight className="h-4 w-4" />
                +25%
              </span>
            </div>
            <div className="mt-4">
              <div className="text-2xl font-bold text-gray-900">
                {formatNumber(mockMetrics.totalViews)}
              </div>
              <div className="text-sm text-gray-500">총 조회수</div>
            </div>
          </div>

          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="rounded-lg bg-purple-100 p-2">
                <Heart className="h-5 w-5 text-purple-600" />
              </div>
              <span className="flex items-center gap-1 text-sm font-medium text-green-600">
                <ArrowUpRight className="h-4 w-4" />
                +18%
              </span>
            </div>
            <div className="mt-4">
              <div className="text-2xl font-bold text-gray-900">
                {formatNumber(mockMetrics.totalEngagement)}
              </div>
              <div className="text-sm text-gray-500">총 참여</div>
            </div>
          </div>

          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="rounded-lg bg-orange-100 p-2">
                <Clock className="h-5 w-5 text-orange-600" />
              </div>
              <span className="flex items-center gap-1 text-sm font-medium text-red-600">
                <ArrowDownRight className="h-4 w-4" />
                -8%
              </span>
            </div>
            <div className="mt-4">
              <div className="text-2xl font-bold text-gray-900">
                {mockMetrics.avgGenerationTime}초
              </div>
              <div className="text-sm text-gray-500">평균 생성 시간</div>
            </div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Video Generation Trend */}
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">영상 생성 추이</h2>
              <BarChart3 className="h-5 w-5 text-gray-400" />
            </div>
            <div className="flex h-48 items-end justify-between gap-2">
              {mockTrends.map((day, i) => (
                <div key={i} className="flex flex-1 flex-col items-center gap-1">
                  <div
                    className="w-full rounded-t bg-samsung-blue transition-all hover:bg-blue-700"
                    style={{
                      height: `${(day.videos / getMaxValue(mockTrends, "videos")) * 100}%`,
                      minHeight: "4px",
                    }}
                  />
                  <span className="text-xs text-gray-500">{day.date}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Views Trend */}
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">조회수 추이</h2>
              <TrendingUp className="h-5 w-5 text-gray-400" />
            </div>
            <div className="flex h-48 items-end justify-between gap-2">
              {mockTrends.map((day, i) => (
                <div key={i} className="flex flex-1 flex-col items-center gap-1">
                  <div
                    className="w-full rounded-t bg-green-500 transition-all hover:bg-green-600"
                    style={{
                      height: `${(day.views / getMaxValue(mockTrends, "views")) * 100}%`,
                      minHeight: "4px",
                    }}
                  />
                  <span className="text-xs text-gray-500">{day.date}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom Row */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Top Videos */}
          <div className="lg:col-span-2 rounded-xl border bg-white shadow-sm">
            <div className="border-b p-6">
              <h2 className="text-lg font-semibold text-gray-900">
                인기 영상 TOP 5
              </h2>
            </div>
            <div className="divide-y">
              {mockTopVideos.map((video, i) => (
                <div
                  key={video.id}
                  className="flex items-center justify-between p-4 hover:bg-gray-50"
                >
                  <div className="flex items-center gap-4">
                    <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-sm font-medium text-gray-600">
                      {i + 1}
                    </span>
                    <div>
                      <div className="font-medium text-gray-900">
                        {video.name}
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs">
                          {video.platform}
                        </span>
                        <span>CTR {(video.ctr * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-6 text-sm">
                    <div className="text-right">
                      <div className="font-medium text-gray-900">
                        {formatNumber(video.views)}
                      </div>
                      <div className="text-gray-500">조회수</div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium text-gray-900">
                        {formatNumber(video.engagement)}
                      </div>
                      <div className="text-gray-500">참여</div>
                    </div>
                    <button className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
                      <Play className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Platform Distribution */}
          <div className="rounded-xl border bg-white shadow-sm">
            <div className="border-b p-6">
              <h2 className="text-lg font-semibold text-gray-900">
                플랫폼별 분포
              </h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {mockPlatformStats.map((platform) => (
                  <div key={platform.platform}>
                    <div className="mb-1 flex items-center justify-between text-sm">
                      <span className="font-medium text-gray-700">
                        {platform.platform}
                      </span>
                      <span className="text-gray-500">
                        {formatNumber(platform.views)} (
                        {(platform.percentage * 100).toFixed(0)}%)
                      </span>
                    </div>
                    <div className="h-2 rounded-full bg-gray-100">
                      <div
                        className={`h-full rounded-full ${platform.color}`}
                        style={{ width: `${platform.percentage * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Usage Summary */}
              <div className="mt-6 rounded-lg bg-gray-50 p-4">
                <h3 className="mb-3 text-sm font-medium text-gray-700">
                  크레딧 사용량
                </h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-gray-900">
                    {mockMetrics.creditsUsed}
                  </span>
                  <span className="text-sm text-gray-500">
                    / {mockMetrics.creditsUsed + mockMetrics.creditsRemaining} 크레딧
                  </span>
                </div>
                <div className="mt-2 h-2 rounded-full bg-gray-200">
                  <div
                    className="h-full rounded-full bg-samsung-blue"
                    style={{
                      width: `${
                        (mockMetrics.creditsUsed /
                          (mockMetrics.creditsUsed + mockMetrics.creditsRemaining)) *
                        100
                      }%`,
                    }}
                  />
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  남은 크레딧: {mockMetrics.creditsRemaining}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* AI Insights */}
        <div className="mt-8 rounded-xl border bg-gradient-to-r from-blue-50 to-purple-50 p-6 shadow-sm">
          <div className="flex items-start gap-4">
            <div className="rounded-lg bg-white p-2 shadow-sm">
              <TrendingUp className="h-6 w-6 text-samsung-blue" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">AI 인사이트</h2>
              <ul className="mt-2 space-y-1 text-gray-600">
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-samsung-blue" />
                  MZ세대 톤의 영상이 평균 대비 23% 높은 참여율을 보입니다
                </li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-samsung-blue" />
                  15초 숏폼 영상이 TikTok에서 가장 좋은 성과를 보입니다
                </li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-samsung-blue" />
                  Galaxy S25 Ultra 관련 콘텐츠의 수요가 증가하고 있습니다
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
