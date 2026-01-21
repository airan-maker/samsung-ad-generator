"use client";

import { useState } from "react";
import {
  Users,
  Video,
  DollarSign,
  Activity,
  Server,
  AlertTriangle,
  TrendingUp,
  Shield,
  Database,
  Cpu,
  HardDrive,
  RefreshCw,
  Search,
  MoreVertical,
  Ban,
  Mail,
  Eye,
} from "lucide-react";

type TimeRange = "7d" | "30d" | "90d";

// Mock admin data
const mockAdminMetrics = {
  users: {
    total: 2847,
    active: 1234,
    new: 156,
    growth: 0.12,
  },
  videos: {
    total: 15420,
    today: 234,
    completionRate: 0.95,
    avgGenerationTime: 118,
  },
  revenue: {
    total: 45000000, // 45M KRW
    subscriptions: 38000000,
    oneTime: 7000000,
    growth: 0.18,
  },
  system: {
    apiLatency: 145,
    queueSize: 23,
    errorRate: 0.02,
    uptime: 0.999,
    storageUsed: 2.5,
    storageLimit: 10,
    cpuUsage: 0.45,
    memoryUsage: 0.62,
  },
};

const mockRecentUsers = [
  {
    id: "1",
    email: "enterprise@samsung.com",
    name: "삼성전자",
    plan: "enterprise",
    videos: 234,
    lastActive: "2025-01-21T10:30:00Z",
    status: "active",
  },
  {
    id: "2",
    email: "marketing@lg.com",
    name: "LG전자",
    plan: "pro",
    videos: 156,
    lastActive: "2025-01-21T09:15:00Z",
    status: "active",
  },
  {
    id: "3",
    email: "ad@coupang.com",
    name: "쿠팡",
    plan: "pro",
    videos: 89,
    lastActive: "2025-01-20T18:45:00Z",
    status: "active",
  },
  {
    id: "4",
    email: "content@naver.com",
    name: "네이버",
    plan: "basic",
    videos: 45,
    lastActive: "2025-01-20T14:20:00Z",
    status: "active",
  },
  {
    id: "5",
    email: "test@example.com",
    name: "테스트 유저",
    plan: "free",
    videos: 3,
    lastActive: "2025-01-19T11:00:00Z",
    status: "suspended",
  },
];

const mockAlerts = [
  {
    id: "1",
    type: "warning",
    message: "API 응답 시간이 평균보다 20% 증가했습니다",
    time: "10분 전",
  },
  {
    id: "2",
    type: "info",
    message: "새로운 Enterprise 고객이 가입했습니다",
    time: "25분 전",
  },
  {
    id: "3",
    type: "error",
    message: "Runway API 연동 오류 발생 (3건)",
    time: "1시간 전",
  },
  {
    id: "4",
    type: "success",
    message: "일일 백업 완료",
    time: "3시간 전",
  },
];

export default function AdminDashboardPage() {
  const [timeRange, setTimeRange] = useState<TimeRange>("30d");
  const [searchQuery, setSearchQuery] = useState("");

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
    if (num >= 1000) return (num / 1000).toFixed(1) + "K";
    return num.toString();
  };

  const formatCurrency = (num: number) => {
    return new Intl.NumberFormat("ko-KR", {
      style: "currency",
      currency: "KRW",
      maximumFractionDigits: 0,
    }).format(num);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));

    if (hours < 1) return "방금 전";
    if (hours < 24) return `${hours}시간 전`;
    return date.toLocaleDateString("ko-KR");
  };

  const getPlanBadgeColor = (plan: string) => {
    switch (plan) {
      case "enterprise":
        return "bg-purple-100 text-purple-700";
      case "pro":
        return "bg-blue-100 text-blue-700";
      case "basic":
        return "bg-green-100 text-green-700";
      default:
        return "bg-gray-100 text-gray-700";
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">관리자 대시보드</h1>
            <p className="mt-1 text-gray-600">
              시스템 현황과 사용자를 관리합니다
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex rounded-lg border bg-white p-1">
              {(["7d", "30d", "90d"] as const).map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                    timeRange === range
                      ? "bg-samsung-blue text-white"
                      : "text-gray-600 hover:text-gray-900"
                  }`}
                >
                  {range === "7d" ? "7일" : range === "30d" ? "30일" : "90일"}
                </button>
              ))}
            </div>
            <button className="rounded-lg border bg-white p-2 text-gray-600 hover:bg-gray-50">
              <RefreshCw className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="rounded-lg bg-blue-100 p-2">
                <Users className="h-5 w-5 text-blue-600" />
              </div>
              <span className="flex items-center gap-1 text-sm font-medium text-green-600">
                +{(mockAdminMetrics.users.growth * 100).toFixed(0)}%
              </span>
            </div>
            <div className="mt-4">
              <div className="text-2xl font-bold text-gray-900">
                {formatNumber(mockAdminMetrics.users.total)}
              </div>
              <div className="text-sm text-gray-500">총 사용자</div>
              <div className="mt-1 text-xs text-gray-400">
                활성: {formatNumber(mockAdminMetrics.users.active)} · 신규:{" "}
                {mockAdminMetrics.users.new}
              </div>
            </div>
          </div>

          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="rounded-lg bg-green-100 p-2">
                <Video className="h-5 w-5 text-green-600" />
              </div>
              <span className="text-sm text-gray-500">오늘 +{mockAdminMetrics.videos.today}</span>
            </div>
            <div className="mt-4">
              <div className="text-2xl font-bold text-gray-900">
                {formatNumber(mockAdminMetrics.videos.total)}
              </div>
              <div className="text-sm text-gray-500">총 영상</div>
              <div className="mt-1 text-xs text-gray-400">
                완료율: {(mockAdminMetrics.videos.completionRate * 100).toFixed(0)}%
              </div>
            </div>
          </div>

          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="rounded-lg bg-purple-100 p-2">
                <DollarSign className="h-5 w-5 text-purple-600" />
              </div>
              <span className="flex items-center gap-1 text-sm font-medium text-green-600">
                +{(mockAdminMetrics.revenue.growth * 100).toFixed(0)}%
              </span>
            </div>
            <div className="mt-4">
              <div className="text-2xl font-bold text-gray-900">
                {formatCurrency(mockAdminMetrics.revenue.total)}
              </div>
              <div className="text-sm text-gray-500">이번 달 매출</div>
              <div className="mt-1 text-xs text-gray-400">
                구독: {formatCurrency(mockAdminMetrics.revenue.subscriptions)}
              </div>
            </div>
          </div>

          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="rounded-lg bg-orange-100 p-2">
                <Activity className="h-5 w-5 text-orange-600" />
              </div>
              <span
                className={`text-sm font-medium ${
                  mockAdminMetrics.system.uptime >= 0.99
                    ? "text-green-600"
                    : "text-yellow-600"
                }`}
              >
                {(mockAdminMetrics.system.uptime * 100).toFixed(1)}%
              </span>
            </div>
            <div className="mt-4">
              <div className="text-2xl font-bold text-gray-900">
                {mockAdminMetrics.system.apiLatency}ms
              </div>
              <div className="text-sm text-gray-500">API 응답 시간</div>
              <div className="mt-1 text-xs text-gray-400">
                에러율: {(mockAdminMetrics.system.errorRate * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* User Management */}
          <div className="lg:col-span-2 rounded-xl border bg-white shadow-sm">
            <div className="flex items-center justify-between border-b p-6">
              <h2 className="text-lg font-semibold text-gray-900">사용자 관리</h2>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="검색..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-48 rounded-lg border py-2 pl-9 pr-3 text-sm focus:border-samsung-blue focus:outline-none focus:ring-1 focus:ring-samsung-blue"
                />
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 text-sm text-gray-500">
                  <tr>
                    <th className="px-6 py-3 text-left font-medium">사용자</th>
                    <th className="px-6 py-3 text-left font-medium">플랜</th>
                    <th className="px-6 py-3 text-left font-medium">영상</th>
                    <th className="px-6 py-3 text-left font-medium">마지막 활동</th>
                    <th className="px-6 py-3 text-left font-medium">상태</th>
                    <th className="px-6 py-3 text-right font-medium">액션</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {mockRecentUsers.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div>
                          <div className="font-medium text-gray-900">
                            {user.name}
                          </div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`rounded-full px-2 py-1 text-xs font-medium ${getPlanBadgeColor(
                            user.plan
                          )}`}
                        >
                          {user.plan.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-gray-900">{user.videos}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {formatDate(user.lastActive)}
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`rounded-full px-2 py-1 text-xs font-medium ${
                            user.status === "active"
                              ? "bg-green-100 text-green-700"
                              : "bg-red-100 text-red-700"
                          }`}
                        >
                          {user.status === "active" ? "활성" : "정지"}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex justify-end gap-1">
                          <button className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
                            <Eye className="h-4 w-4" />
                          </button>
                          <button className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
                            <Mail className="h-4 w-4" />
                          </button>
                          <button className="rounded p-1 text-gray-400 hover:bg-red-50 hover:text-red-600">
                            <Ban className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Alerts & System Health */}
          <div className="space-y-6">
            {/* Alerts */}
            <div className="rounded-xl border bg-white shadow-sm">
              <div className="flex items-center justify-between border-b p-4">
                <h2 className="font-semibold text-gray-900">알림</h2>
                <AlertTriangle className="h-5 w-5 text-yellow-500" />
              </div>
              <div className="divide-y">
                {mockAlerts.map((alert) => (
                  <div key={alert.id} className="p-4">
                    <div className="flex items-start gap-3">
                      <div
                        className={`mt-0.5 h-2 w-2 rounded-full ${
                          alert.type === "error"
                            ? "bg-red-500"
                            : alert.type === "warning"
                            ? "bg-yellow-500"
                            : alert.type === "success"
                            ? "bg-green-500"
                            : "bg-blue-500"
                        }`}
                      />
                      <div className="flex-1">
                        <p className="text-sm text-gray-900">{alert.message}</p>
                        <p className="mt-1 text-xs text-gray-500">{alert.time}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* System Health */}
            <div className="rounded-xl border bg-white shadow-sm">
              <div className="flex items-center justify-between border-b p-4">
                <h2 className="font-semibold text-gray-900">시스템 상태</h2>
                <Server className="h-5 w-5 text-gray-400" />
              </div>
              <div className="p-4 space-y-4">
                {/* CPU */}
                <div>
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <Cpu className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-600">CPU</span>
                    </div>
                    <span className="font-medium text-gray-900">
                      {(mockAdminMetrics.system.cpuUsage * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="mt-1 h-2 rounded-full bg-gray-100">
                    <div
                      className={`h-full rounded-full ${
                        mockAdminMetrics.system.cpuUsage > 0.8
                          ? "bg-red-500"
                          : mockAdminMetrics.system.cpuUsage > 0.6
                          ? "bg-yellow-500"
                          : "bg-green-500"
                      }`}
                      style={{ width: `${mockAdminMetrics.system.cpuUsage * 100}%` }}
                    />
                  </div>
                </div>

                {/* Memory */}
                <div>
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <Database className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-600">메모리</span>
                    </div>
                    <span className="font-medium text-gray-900">
                      {(mockAdminMetrics.system.memoryUsage * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="mt-1 h-2 rounded-full bg-gray-100">
                    <div
                      className={`h-full rounded-full ${
                        mockAdminMetrics.system.memoryUsage > 0.8
                          ? "bg-red-500"
                          : mockAdminMetrics.system.memoryUsage > 0.6
                          ? "bg-yellow-500"
                          : "bg-green-500"
                      }`}
                      style={{ width: `${mockAdminMetrics.system.memoryUsage * 100}%` }}
                    />
                  </div>
                </div>

                {/* Storage */}
                <div>
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <HardDrive className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-600">스토리지</span>
                    </div>
                    <span className="font-medium text-gray-900">
                      {mockAdminMetrics.system.storageUsed}TB /{" "}
                      {mockAdminMetrics.system.storageLimit}TB
                    </span>
                  </div>
                  <div className="mt-1 h-2 rounded-full bg-gray-100">
                    <div
                      className="h-full rounded-full bg-samsung-blue"
                      style={{
                        width: `${
                          (mockAdminMetrics.system.storageUsed /
                            mockAdminMetrics.system.storageLimit) *
                          100
                        }%`,
                      }}
                    />
                  </div>
                </div>

                {/* Queue */}
                <div className="flex items-center justify-between rounded-lg bg-gray-50 p-3 text-sm">
                  <span className="text-gray-600">대기열 크기</span>
                  <span className="font-medium text-gray-900">
                    {mockAdminMetrics.system.queueSize} 작업
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
