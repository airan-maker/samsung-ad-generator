"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Search,
  Filter,
  Grid,
  List,
  Star,
  Clock,
  Play,
  Smartphone,
  Tv,
  Monitor,
  Laptop,
  Watch,
  Headphones,
  Palette,
} from "lucide-react";

interface Template {
  id: string;
  name: string;
  description: string;
  thumbnail: string;
  category: string;
  duration: number;
  aspectRatio: string;
  rating: number;
  uses: number;
  tags: string[];
  isNew?: boolean;
  isPremium?: boolean;
}

const templates: Template[] = [
  {
    id: "1",
    name: "Galaxy S 시리즈 프리미엄",
    description: "Galaxy S 시리즈를 위한 프리미엄 광고 템플릿. 세련된 애니메이션과 역동적인 전환 효과.",
    thumbnail: "/templates/galaxy-s.jpg",
    category: "smartphone",
    duration: 30,
    aspectRatio: "16:9",
    rating: 4.9,
    uses: 2340,
    tags: ["프리미엄", "역동적", "모던"],
    isNew: true,
  },
  {
    id: "2",
    name: "Galaxy Z 폴드/플립",
    description: "폴더블 폰의 혁신적인 기능을 강조하는 템플릿",
    thumbnail: "/templates/galaxy-z.jpg",
    category: "smartphone",
    duration: 15,
    aspectRatio: "9:16",
    rating: 4.8,
    uses: 1850,
    tags: ["폴더블", "혁신", "세로형"],
  },
  {
    id: "3",
    name: "가전제품 라이프스타일",
    description: "삼성 가전제품을 위한 라이프스타일 템플릿. 일상의 편리함을 강조.",
    thumbnail: "/templates/appliance.jpg",
    category: "appliance",
    duration: 15,
    aspectRatio: "16:9",
    rating: 4.7,
    uses: 1520,
    tags: ["라이프스타일", "가전", "일상"],
  },
  {
    id: "4",
    name: "Neo QLED TV 시네마틱",
    description: "대화면 TV의 압도적인 화질을 보여주는 시네마틱 템플릿",
    thumbnail: "/templates/tv.jpg",
    category: "tv",
    duration: 45,
    aspectRatio: "21:9",
    rating: 4.9,
    uses: 980,
    tags: ["시네마틱", "프리미엄", "와이드"],
    isPremium: true,
  },
  {
    id: "5",
    name: "Galaxy Book 프로덕티비티",
    description: "노트북의 생산성 기능을 강조하는 비즈니스 템플릿",
    thumbnail: "/templates/laptop.jpg",
    category: "laptop",
    duration: 30,
    aspectRatio: "16:9",
    rating: 4.6,
    uses: 720,
    tags: ["비즈니스", "생산성", "전문가"],
  },
  {
    id: "6",
    name: "Galaxy Watch 피트니스",
    description: "스마트워치의 헬스케어 기능을 강조하는 활동적인 템플릿",
    thumbnail: "/templates/watch.jpg",
    category: "wearable",
    duration: 15,
    aspectRatio: "1:1",
    rating: 4.7,
    uses: 1100,
    tags: ["피트니스", "건강", "스포티"],
  },
  {
    id: "7",
    name: "Galaxy Buds 음악",
    description: "이어버드의 사운드 품질을 감각적으로 표현하는 템플릿",
    thumbnail: "/templates/buds.jpg",
    category: "wearable",
    duration: 15,
    aspectRatio: "9:16",
    rating: 4.5,
    uses: 890,
    tags: ["음악", "사운드", "감각적"],
  },
  {
    id: "8",
    name: "B2B 기업 솔루션",
    description: "기업용 솔루션 홍보를 위한 전문적인 템플릿",
    thumbnail: "/templates/b2b.jpg",
    category: "b2b",
    duration: 60,
    aspectRatio: "16:9",
    rating: 4.8,
    uses: 450,
    tags: ["B2B", "기업", "전문가"],
    isPremium: true,
  },
  {
    id: "9",
    name: "소셜미디어 숏폼",
    description: "Instagram/TikTok용 짧고 임팩트 있는 템플릿",
    thumbnail: "/templates/social.jpg",
    category: "social",
    duration: 6,
    aspectRatio: "9:16",
    rating: 4.9,
    uses: 3200,
    tags: ["소셜미디어", "숏폼", "바이럴"],
    isNew: true,
  },
];

const categories = [
  { id: "all", name: "전체", icon: Grid },
  { id: "smartphone", name: "스마트폰", icon: Smartphone },
  { id: "tv", name: "TV", icon: Tv },
  { id: "laptop", name: "노트북", icon: Laptop },
  { id: "appliance", name: "가전", icon: Monitor },
  { id: "wearable", name: "웨어러블", icon: Watch },
  { id: "b2b", name: "B2B", icon: Headphones },
];

export default function TemplatesPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [sortBy, setSortBy] = useState<"popular" | "rating" | "newest">("popular");

  const filteredTemplates = templates
    .filter((template) => {
      const matchesSearch =
        template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()));
      const matchesCategory =
        selectedCategory === "all" || template.category === selectedCategory;
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      if (sortBy === "popular") return b.uses - a.uses;
      if (sortBy === "rating") return b.rating - a.rating;
      return 0; // newest would sort by date
    });

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "smartphone":
        return <Smartphone className="h-4 w-4" />;
      case "tv":
        return <Tv className="h-4 w-4" />;
      case "laptop":
        return <Laptop className="h-4 w-4" />;
      case "appliance":
        return <Monitor className="h-4 w-4" />;
      case "wearable":
        return <Watch className="h-4 w-4" />;
      default:
        return <Grid className="h-4 w-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="border-b bg-white">
        <div className="mx-auto max-w-7xl px-6 py-8">
          <h1 className="text-3xl font-bold text-gray-900">템플릿 갤러리</h1>
          <p className="mt-2 text-gray-600">
            삼성 제품을 위한 다양한 광고 템플릿을 선택하고 커스터마이징하세요
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="border-b bg-white">
        <div className="mx-auto max-w-7xl px-6 py-4">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="템플릿 검색..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full rounded-lg border py-2 pl-10 pr-4 focus:border-samsung-blue focus:outline-none focus:ring-1 focus:ring-samsung-blue"
              />
            </div>

            {/* Controls */}
            <div className="flex items-center gap-4">
              {/* Sort */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
                className="rounded-lg border px-3 py-2 text-sm focus:border-samsung-blue focus:outline-none focus:ring-1 focus:ring-samsung-blue"
              >
                <option value="popular">인기순</option>
                <option value="rating">평점순</option>
                <option value="newest">최신순</option>
              </select>

              {/* View Mode */}
              <div className="flex rounded-lg border">
                <button
                  onClick={() => setViewMode("grid")}
                  className={`p-2 ${
                    viewMode === "grid" ? "bg-samsung-blue text-white" : "text-gray-500"
                  }`}
                >
                  <Grid className="h-5 w-5" />
                </button>
                <button
                  onClick={() => setViewMode("list")}
                  className={`p-2 ${
                    viewMode === "list" ? "bg-samsung-blue text-white" : "text-gray-500"
                  }`}
                >
                  <List className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>

          {/* Categories */}
          <div className="mt-4 flex flex-wrap gap-2">
            {categories.map((category) => {
              const Icon = category.icon;
              return (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                    selectedCategory === category.id
                      ? "bg-samsung-blue text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {category.name}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Templates Grid/List */}
      <div className="mx-auto max-w-7xl px-6 py-8">
        {filteredTemplates.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <Search className="h-12 w-12 text-gray-300" />
            <h3 className="mt-4 text-lg font-medium text-gray-900">검색 결과 없음</h3>
            <p className="mt-2 text-gray-500">
              다른 검색어나 카테고리를 선택해 보세요.
            </p>
          </div>
        ) : viewMode === "grid" ? (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filteredTemplates.map((template) => (
              <Link
                key={template.id}
                href={`/templates/customize?id=${template.id}`}
                className="group overflow-hidden rounded-xl border bg-white shadow-sm transition-all hover:shadow-lg"
              >
                {/* Thumbnail */}
                <div className="relative aspect-video bg-gray-100">
                  <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-samsung-blue/20 to-purple-600/20">
                    <Play className="h-12 w-12 text-white opacity-0 transition-opacity group-hover:opacity-100" />
                  </div>

                  {/* Badges */}
                  <div className="absolute left-3 top-3 flex gap-2">
                    {template.isNew && (
                      <span className="rounded-full bg-green-500 px-2 py-0.5 text-xs font-medium text-white">
                        NEW
                      </span>
                    )}
                    {template.isPremium && (
                      <span className="rounded-full bg-gradient-to-r from-yellow-500 to-orange-500 px-2 py-0.5 text-xs font-medium text-white">
                        PREMIUM
                      </span>
                    )}
                  </div>

                  {/* Duration */}
                  <div className="absolute bottom-3 right-3 flex items-center gap-1 rounded bg-black/70 px-2 py-1 text-xs text-white">
                    <Clock className="h-3 w-3" />
                    {template.duration}초
                  </div>

                  {/* Aspect Ratio */}
                  <div className="absolute bottom-3 left-3 rounded bg-black/70 px-2 py-1 text-xs text-white">
                    {template.aspectRatio}
                  </div>
                </div>

                {/* Content */}
                <div className="p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900 group-hover:text-samsung-blue">
                        {template.name}
                      </h3>
                      <p className="mt-1 line-clamp-2 text-sm text-gray-500">
                        {template.description}
                      </p>
                    </div>
                    {getCategoryIcon(template.category)}
                  </div>

                  {/* Tags */}
                  <div className="mt-3 flex flex-wrap gap-1">
                    {template.tags.slice(0, 3).map((tag) => (
                      <span
                        key={tag}
                        className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  {/* Stats */}
                  <div className="mt-3 flex items-center justify-between border-t pt-3 text-sm">
                    <div className="flex items-center gap-1 text-yellow-500">
                      <Star className="h-4 w-4 fill-current" />
                      <span className="font-medium">{template.rating}</span>
                    </div>
                    <span className="text-gray-500">{template.uses.toLocaleString()}회 사용</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {filteredTemplates.map((template) => (
              <Link
                key={template.id}
                href={`/templates/customize?id=${template.id}`}
                className="group flex gap-4 rounded-xl border bg-white p-4 shadow-sm transition-all hover:shadow-lg"
              >
                {/* Thumbnail */}
                <div className="relative h-24 w-40 flex-shrink-0 overflow-hidden rounded-lg bg-gray-100">
                  <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-samsung-blue/20 to-purple-600/20">
                    <Play className="h-8 w-8 text-white opacity-0 transition-opacity group-hover:opacity-100" />
                  </div>
                </div>

                {/* Content */}
                <div className="flex flex-1 flex-col justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-gray-900 group-hover:text-samsung-blue">
                        {template.name}
                      </h3>
                      {template.isNew && (
                        <span className="rounded-full bg-green-500 px-2 py-0.5 text-xs font-medium text-white">
                          NEW
                        </span>
                      )}
                      {template.isPremium && (
                        <span className="rounded-full bg-gradient-to-r from-yellow-500 to-orange-500 px-2 py-0.5 text-xs font-medium text-white">
                          PREMIUM
                        </span>
                      )}
                    </div>
                    <p className="mt-1 text-sm text-gray-500">{template.description}</p>
                  </div>

                  <div className="flex items-center gap-4 text-sm">
                    <span className="flex items-center gap-1 text-gray-500">
                      <Clock className="h-4 w-4" />
                      {template.duration}초
                    </span>
                    <span className="text-gray-500">{template.aspectRatio}</span>
                    <span className="flex items-center gap-1 text-yellow-500">
                      <Star className="h-4 w-4 fill-current" />
                      {template.rating}
                    </span>
                    <span className="text-gray-500">{template.uses.toLocaleString()}회 사용</span>
                  </div>
                </div>

                {/* Customize Button */}
                <div className="flex items-center">
                  <span className="flex items-center gap-2 rounded-lg bg-samsung-blue px-4 py-2 text-sm font-medium text-white opacity-0 transition-opacity group-hover:opacity-100">
                    <Palette className="h-4 w-4" />
                    커스터마이즈
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
