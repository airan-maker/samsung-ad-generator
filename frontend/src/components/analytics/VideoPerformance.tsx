"use client";

import { useState } from "react";
import {
  Eye,
  Heart,
  Share2,
  MousePointer,
  TrendingUp,
  Users,
  Globe,
  Calendar,
} from "lucide-react";

interface VideoPerformanceProps {
  projectId: string;
  videoName: string;
}

// Mock performance data
const mockPerformance = {
  views: {
    total: 53200,
    youtube: 22400,
    instagram: 15600,
    tiktok: 12000,
    coupang: 3200,
  },
  engagement: {
    likes: 3250,
    comments: 189,
    shares: 534,
    saves: 892,
  },
  conversion: {
    clicks: 1890,
    ctr: 0.0355,
    conversions: 145,
    conversionRate: 0.0767,
  },
  demographics: {
    ageGroups: [
      { range: "18-24", percentage: 0.35 },
      { range: "25-34", percentage: 0.42 },
      { range: "35-44", percentage: 0.15 },
      { range: "45+", percentage: 0.08 },
    ],
    gender: {
      male: 0.48,
      female: 0.52,
    },
    topCountries: [
      { code: "KR", name: "대한민국", percentage: 0.72 },
      { code: "US", name: "미국", percentage: 0.12 },
      { code: "JP", name: "일본", percentage: 0.08 },
      { code: "CN", name: "중국", percentage: 0.05 },
      { code: "TW", name: "대만", percentage: 0.03 },
    ],
  },
  dailyViews: [
    { date: "01/15", views: 4200 },
    { date: "01/16", views: 6800 },
    { date: "01/17", views: 8100 },
    { date: "01/18", views: 7400 },
    { date: "01/19", views: 9200 },
    { date: "01/20", views: 8500 },
    { date: "01/21", views: 9000 },
  ],
};

export function VideoPerformance({ projectId, videoName }: VideoPerformanceProps) {
  const [selectedPlatform, setSelectedPlatform] = useState<string>("all");

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
    if (num >= 1000) return (num / 1000).toFixed(1) + "K";
    return num.toString();
  };

  const platforms = [
    { id: "all", name: "전체", views: mockPerformance.views.total },
    { id: "youtube", name: "YouTube", views: mockPerformance.views.youtube },
    { id: "instagram", name: "Instagram", views: mockPerformance.views.instagram },
    { id: "tiktok", name: "TikTok", views: mockPerformance.views.tiktok },
    { id: "coupang", name: "Coupang", views: mockPerformance.views.coupang },
  ];

  const maxViews = Math.max(...mockPerformance.dailyViews.map((d) => d.views));

  return (
    <div className="space-y-6">
      {/* Platform Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {platforms.map((platform) => (
          <button
            key={platform.id}
            onClick={() => setSelectedPlatform(platform.id)}
            className={`flex-shrink-0 rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              selectedPlatform === platform.id
                ? "bg-samsung-blue text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            {platform.name}
            <span className="ml-2 text-xs opacity-75">
              {formatNumber(platform.views)}
            </span>
          </button>
        ))}
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="rounded-lg border bg-white p-4">
          <div className="flex items-center gap-2 text-gray-500">
            <Eye className="h-4 w-4" />
            <span className="text-sm">조회수</span>
          </div>
          <div className="mt-2 text-2xl font-bold text-gray-900">
            {formatNumber(mockPerformance.views.total)}
          </div>
        </div>

        <div className="rounded-lg border bg-white p-4">
          <div className="flex items-center gap-2 text-gray-500">
            <Heart className="h-4 w-4" />
            <span className="text-sm">좋아요</span>
          </div>
          <div className="mt-2 text-2xl font-bold text-gray-900">
            {formatNumber(mockPerformance.engagement.likes)}
          </div>
        </div>

        <div className="rounded-lg border bg-white p-4">
          <div className="flex items-center gap-2 text-gray-500">
            <MousePointer className="h-4 w-4" />
            <span className="text-sm">CTR</span>
          </div>
          <div className="mt-2 text-2xl font-bold text-gray-900">
            {(mockPerformance.conversion.ctr * 100).toFixed(2)}%
          </div>
        </div>

        <div className="rounded-lg border bg-white p-4">
          <div className="flex items-center gap-2 text-gray-500">
            <TrendingUp className="h-4 w-4" />
            <span className="text-sm">전환율</span>
          </div>
          <div className="mt-2 text-2xl font-bold text-gray-900">
            {(mockPerformance.conversion.conversionRate * 100).toFixed(2)}%
          </div>
        </div>
      </div>

      {/* Views Chart */}
      <div className="rounded-lg border bg-white p-6">
        <h3 className="mb-4 font-semibold text-gray-900">일별 조회수</h3>
        <div className="flex h-40 items-end justify-between gap-2">
          {mockPerformance.dailyViews.map((day, i) => (
            <div key={i} className="flex flex-1 flex-col items-center gap-1">
              <div className="w-full">
                <div
                  className="mx-auto w-full max-w-8 rounded-t bg-samsung-blue transition-all hover:bg-blue-700"
                  style={{
                    height: `${(day.views / maxViews) * 100}%`,
                    minHeight: "4px",
                  }}
                />
              </div>
              <span className="text-xs text-gray-500">{day.date}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Engagement & Demographics */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Engagement Breakdown */}
        <div className="rounded-lg border bg-white p-6">
          <h3 className="mb-4 font-semibold text-gray-900">참여도 상세</h3>
          <div className="space-y-4">
            {[
              { label: "좋아요", value: mockPerformance.engagement.likes, icon: Heart },
              { label: "댓글", value: mockPerformance.engagement.comments, icon: Users },
              { label: "공유", value: mockPerformance.engagement.shares, icon: Share2 },
              { label: "저장", value: mockPerformance.engagement.saves, icon: Calendar },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <item.icon className="h-4 w-4 text-gray-400" />
                  <span className="text-gray-600">{item.label}</span>
                </div>
                <span className="font-medium text-gray-900">
                  {formatNumber(item.value)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Age Distribution */}
        <div className="rounded-lg border bg-white p-6">
          <h3 className="mb-4 font-semibold text-gray-900">연령대 분포</h3>
          <div className="space-y-3">
            {mockPerformance.demographics.ageGroups.map((group) => (
              <div key={group.range}>
                <div className="mb-1 flex items-center justify-between text-sm">
                  <span className="text-gray-600">{group.range}세</span>
                  <span className="font-medium text-gray-900">
                    {(group.percentage * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="h-2 rounded-full bg-gray-100">
                  <div
                    className="h-full rounded-full bg-samsung-blue"
                    style={{ width: `${group.percentage * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Gender Split */}
          <div className="mt-6">
            <h4 className="mb-2 text-sm font-medium text-gray-700">성별 비율</h4>
            <div className="flex h-4 overflow-hidden rounded-full">
              <div
                className="bg-blue-500"
                style={{
                  width: `${mockPerformance.demographics.gender.male * 100}%`,
                }}
              />
              <div
                className="bg-pink-500"
                style={{
                  width: `${mockPerformance.demographics.gender.female * 100}%`,
                }}
              />
            </div>
            <div className="mt-2 flex justify-between text-xs">
              <span className="text-blue-600">
                남성 {(mockPerformance.demographics.gender.male * 100).toFixed(0)}%
              </span>
              <span className="text-pink-600">
                여성 {(mockPerformance.demographics.gender.female * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Geographic Distribution */}
      <div className="rounded-lg border bg-white p-6">
        <h3 className="mb-4 flex items-center gap-2 font-semibold text-gray-900">
          <Globe className="h-5 w-5" />
          지역별 분포
        </h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-5">
          {mockPerformance.demographics.topCountries.map((country, i) => (
            <div
              key={country.code}
              className="flex items-center gap-3 rounded-lg bg-gray-50 p-3"
            >
              <span className="text-2xl">
                {country.code === "KR"
                  ? "🇰🇷"
                  : country.code === "US"
                  ? "🇺🇸"
                  : country.code === "JP"
                  ? "🇯🇵"
                  : country.code === "CN"
                  ? "🇨🇳"
                  : "🇹🇼"}
              </span>
              <div>
                <div className="font-medium text-gray-900">{country.name}</div>
                <div className="text-sm text-gray-500">
                  {(country.percentage * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
