"use client";

import { useState } from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Header } from "@/components/common/Header";
import { Footer } from "@/components/common/Footer";
import {
  Plus,
  Search,
  MoreVertical,
  Play,
  Download,
  Trash2,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
} from "lucide-react";
import type { ProjectStatus } from "@/types";

// Mock data - will be replaced with API call
const mockProjects = [
  {
    id: "proj_1",
    name: "S25 Ultra 프로모션 영상",
    product_name: "Galaxy S25 Ultra",
    template_name: "언박싱 시퀀스",
    status: "completed" as ProjectStatus,
    thumbnail: null,
    duration: 30,
    created_at: "2025-01-20T10:30:00Z",
    updated_at: "2025-01-20T10:35:00Z",
  },
  {
    id: "proj_2",
    name: "Z Fold 6 카메라 하이라이트",
    product_name: "Galaxy Z Fold 6",
    template_name: "카메라 하이라이트",
    status: "completed" as ProjectStatus,
    thumbnail: null,
    duration: 60,
    created_at: "2025-01-19T14:00:00Z",
    updated_at: "2025-01-19T14:10:00Z",
  },
  {
    id: "proj_3",
    name: "비스포크 냉장고 광고",
    product_name: "비스포크 냉장고 4도어",
    template_name: "비스포크 인테리어",
    status: "processing" as ProjectStatus,
    thumbnail: null,
    duration: 30,
    created_at: "2025-01-21T09:00:00Z",
    updated_at: "2025-01-21T09:00:00Z",
  },
  {
    id: "proj_4",
    name: "Galaxy Watch 헬스 광고",
    product_name: "Galaxy Watch 7",
    template_name: "헬스 트래킹",
    status: "draft" as ProjectStatus,
    thumbnail: null,
    duration: 15,
    created_at: "2025-01-18T16:00:00Z",
    updated_at: "2025-01-18T16:00:00Z",
  },
];

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

export default function ProjectsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<ProjectStatus | "all">("all");
  const [isLoading] = useState(false);

  const filteredProjects = mockProjects.filter((project) => {
    const matchesSearch =
      project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.product_name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || project.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("ko-KR", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">내 프로젝트</h1>
            <p className="mt-1 text-gray-600">
              총 {filteredProjects.length}개의 프로젝트
            </p>
          </div>
          <Link href="/create">
            <Button variant="samsung" size="lg">
              <Plus className="mr-2 h-5 w-5" />
              새 영상 만들기
            </Button>
          </Link>
        </div>

        {/* Filters */}
        <div className="mt-6 flex flex-col gap-4 sm:flex-row sm:items-center">
          {/* Search */}
          <div className="relative flex-1 sm:max-w-xs">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <Input
              placeholder="프로젝트 검색..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Status Filter */}
          <div className="flex gap-2">
            <button
              onClick={() => setStatusFilter("all")}
              className={cn(
                "rounded-full px-4 py-2 text-sm font-medium transition-colors",
                statusFilter === "all"
                  ? "bg-samsung-blue text-white"
                  : "bg-white text-gray-600 hover:bg-gray-100"
              )}
            >
              전체
            </button>
            {(Object.keys(statusConfig) as ProjectStatus[]).map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={cn(
                  "rounded-full px-4 py-2 text-sm font-medium transition-colors",
                  statusFilter === status
                    ? "bg-samsung-blue text-white"
                    : "bg-white text-gray-600 hover:bg-gray-100"
                )}
              >
                {statusConfig[status].label}
              </button>
            ))}
          </div>
        </div>

        {/* Projects Grid */}
        {isLoading ? (
          <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {[...Array(6)].map((_, i) => (
              <Card key={i}>
                <Skeleton className="aspect-video w-full" />
                <CardContent className="p-4">
                  <Skeleton className="h-5 w-3/4" />
                  <Skeleton className="mt-2 h-4 w-1/2" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="mt-8 flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-200 py-16">
            <div className="rounded-full bg-gray-100 p-4">
              <Plus className="h-8 w-8 text-gray-400" />
            </div>
            <h3 className="mt-4 text-lg font-medium text-gray-900">
              프로젝트가 없습니다
            </h3>
            <p className="mt-1 text-gray-500">
              새 영상을 만들어보세요!
            </p>
            <Link href="/create" className="mt-4">
              <Button variant="samsung">
                <Plus className="mr-2 h-5 w-5" />
                새 영상 만들기
              </Button>
            </Link>
          </div>
        ) : (
          <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filteredProjects.map((project) => {
              const status = statusConfig[project.status];
              const StatusIcon = status.icon;

              return (
                <Card
                  key={project.id}
                  className="group overflow-hidden transition-all hover:shadow-lg"
                >
                  {/* Thumbnail */}
                  <div className="relative aspect-video bg-gradient-to-br from-gray-800 to-gray-900">
                    {/* Placeholder content */}
                    <div className="absolute inset-0 flex items-center justify-center text-4xl text-white/20">
                      📱
                    </div>

                    {/* Status Badge */}
                    <div className="absolute left-2 top-2">
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

                    {/* Duration */}
                    <div className="absolute bottom-2 right-2">
                      <Badge variant="secondary" className="bg-black/60 text-white">
                        {project.duration}초
                      </Badge>
                    </div>

                    {/* Hover overlay */}
                    {project.status === "completed" && (
                      <div className="absolute inset-0 flex items-center justify-center gap-2 bg-black/50 opacity-0 transition-opacity group-hover:opacity-100">
                        <Button size="sm" variant="secondary">
                          <Play className="mr-1 h-4 w-4" />
                          재생
                        </Button>
                        <Button size="sm" variant="secondary">
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    )}
                  </div>

                  {/* Info */}
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="min-w-0 flex-1">
                        <Link
                          href={`/projects/${project.id}`}
                          className="font-semibold text-gray-900 hover:text-samsung-blue"
                        >
                          {project.name}
                        </Link>
                        <p className="mt-1 truncate text-sm text-gray-500">
                          {project.product_name} · {project.template_name}
                        </p>
                        <p className="mt-1 text-xs text-gray-400">
                          {formatDate(project.updated_at)}
                        </p>
                      </div>

                      {/* Actions Menu */}
                      <button className="rounded-full p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
                        <MoreVertical className="h-5 w-5" />
                      </button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
