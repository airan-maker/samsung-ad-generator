"use client";

import { useState } from "react";
import { useTranslation } from "@/hooks/useTranslation";
import {
  Key,
  Copy,
  Eye,
  EyeOff,
  Plus,
  Trash2,
  RefreshCw,
  ExternalLink,
  Code,
  Book,
  Zap,
  Shield,
} from "lucide-react";

interface APIKey {
  id: string;
  name: string;
  keyPrefix: string;
  createdAt: string;
  lastUsed: string | null;
  scopes: string[];
  status: "active" | "revoked";
}

// Mock data for demonstration
const mockAPIKeys: APIKey[] = [
  {
    id: "key_1",
    name: "Production Key",
    keyPrefix: "saiad_prod_xxxxx",
    createdAt: "2025-01-15T10:00:00Z",
    lastUsed: "2025-01-21T09:30:00Z",
    scopes: ["videos:create", "videos:read", "products:read", "templates:read"],
    status: "active",
  },
  {
    id: "key_2",
    name: "Development Key",
    keyPrefix: "saiad_dev_xxxxx",
    createdAt: "2025-01-10T14:00:00Z",
    lastUsed: "2025-01-20T16:45:00Z",
    scopes: ["videos:read", "products:read"],
    status: "active",
  },
];

const codeExamples = {
  curl: `curl -X POST https://api.saiad.io/api/v1/public/videos \\
  -H "X-API-Key: your_api_key" \\
  -H "Content-Type: application/json" \\
  -d '{
    "product_id": "galaxy-s25-ultra",
    "template_id": "unboxing-premium",
    "duration": 30,
    "tone": "professional",
    "language": "ko"
  }'`,
  python: `import requests

api_key = "your_api_key"
url = "https://api.saiad.io/api/v1/public/videos"

response = requests.post(
    url,
    headers={
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    },
    json={
        "product_id": "galaxy-s25-ultra",
        "template_id": "unboxing-premium",
        "duration": 30,
        "tone": "professional",
        "language": "ko"
    }
)

print(response.json())`,
  javascript: `const response = await fetch(
  "https://api.saiad.io/api/v1/public/videos",
  {
    method: "POST",
    headers: {
      "X-API-Key": "your_api_key",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      product_id: "galaxy-s25-ultra",
      template_id: "unboxing-premium",
      duration: 30,
      tone: "professional",
      language: "ko",
    }),
  }
);

const data = await response.json();
console.log(data);`,
};

export default function DevelopersPage() {
  const { t } = useTranslation();
  const [apiKeys, setApiKeys] = useState<APIKey[]>(mockAPIKeys);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState<keyof typeof codeExamples>("curl");
  const [copiedCode, setCopiedCode] = useState(false);
  const [visibleKeys, setVisibleKeys] = useState<Set<string>>(new Set());

  const toggleKeyVisibility = (keyId: string) => {
    const newVisible = new Set(visibleKeys);
    if (newVisible.has(keyId)) {
      newVisible.delete(keyId);
    } else {
      newVisible.add(keyId);
    }
    setVisibleKeys(newVisible);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("ko-KR", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Developer Portal</h1>
          <p className="mt-2 text-gray-600">
            API 키를 관리하고 SaiAd API를 통합하세요
          </p>
        </div>

        {/* Quick Links */}
        <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <a
            href="/api/v1/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 rounded-lg border bg-white p-4 transition-shadow hover:shadow-md"
          >
            <div className="rounded-lg bg-blue-100 p-2">
              <Book className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <div className="font-medium text-gray-900">API 문서</div>
              <div className="text-sm text-gray-500">Swagger UI</div>
            </div>
            <ExternalLink className="ml-auto h-4 w-4 text-gray-400" />
          </a>

          <a
            href="/api/v1/redoc"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 rounded-lg border bg-white p-4 transition-shadow hover:shadow-md"
          >
            <div className="rounded-lg bg-purple-100 p-2">
              <Code className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <div className="font-medium text-gray-900">ReDoc</div>
              <div className="text-sm text-gray-500">상세 문서</div>
            </div>
            <ExternalLink className="ml-auto h-4 w-4 text-gray-400" />
          </a>

          <a
            href="https://status.saiad.io"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 rounded-lg border bg-white p-4 transition-shadow hover:shadow-md"
          >
            <div className="rounded-lg bg-green-100 p-2">
              <Zap className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <div className="font-medium text-gray-900">API 상태</div>
              <div className="text-sm text-gray-500">실시간 모니터링</div>
            </div>
            <ExternalLink className="ml-auto h-4 w-4 text-gray-400" />
          </a>

          <a
            href="mailto:support@saiad.io"
            className="flex items-center gap-3 rounded-lg border bg-white p-4 transition-shadow hover:shadow-md"
          >
            <div className="rounded-lg bg-orange-100 p-2">
              <Shield className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <div className="font-medium text-gray-900">기술 지원</div>
              <div className="text-sm text-gray-500">문의하기</div>
            </div>
            <ExternalLink className="ml-auto h-4 w-4 text-gray-400" />
          </a>
        </div>

        {/* API Keys Section */}
        <div className="mb-8 rounded-xl border bg-white shadow-sm">
          <div className="flex items-center justify-between border-b p-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">API 키</h2>
              <p className="mt-1 text-sm text-gray-500">
                API 요청 인증에 사용되는 키를 관리합니다
              </p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 rounded-lg bg-samsung-blue px-4 py-2 text-white transition-colors hover:bg-blue-700"
            >
              <Plus className="h-4 w-4" />
              새 API 키 생성
            </button>
          </div>

          <div className="divide-y">
            {apiKeys.map((key) => (
              <div key={key.id} className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className="rounded-lg bg-gray-100 p-2">
                      <Key className="h-5 w-5 text-gray-600" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900">
                          {key.name}
                        </span>
                        <span
                          className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                            key.status === "active"
                              ? "bg-green-100 text-green-700"
                              : "bg-red-100 text-red-700"
                          }`}
                        >
                          {key.status === "active" ? "활성" : "비활성"}
                        </span>
                      </div>
                      <div className="mt-1 flex items-center gap-2">
                        <code className="rounded bg-gray-100 px-2 py-1 text-sm font-mono text-gray-700">
                          {visibleKeys.has(key.id)
                            ? `saiad_prod_abc123def456`
                            : key.keyPrefix}
                        </code>
                        <button
                          onClick={() => toggleKeyVisibility(key.id)}
                          className="p-1 text-gray-400 hover:text-gray-600"
                        >
                          {visibleKeys.has(key.id) ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </button>
                        <button
                          onClick={() => copyToClipboard("saiad_prod_abc123def456")}
                          className="p-1 text-gray-400 hover:text-gray-600"
                        >
                          <Copy className="h-4 w-4" />
                        </button>
                      </div>
                      <div className="mt-2 flex flex-wrap gap-1">
                        {key.scopes.map((scope) => (
                          <span
                            key={scope}
                            className="rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700"
                          >
                            {scope}
                          </span>
                        ))}
                      </div>
                      <div className="mt-2 text-xs text-gray-500">
                        생성일: {formatDate(key.createdAt)}
                        {key.lastUsed && (
                          <> · 마지막 사용: {formatDate(key.lastUsed)}</>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
                      <RefreshCw className="h-4 w-4" />
                    </button>
                    <button className="rounded-lg p-2 text-gray-400 hover:bg-red-50 hover:text-red-600">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}

            {apiKeys.length === 0 && (
              <div className="p-12 text-center">
                <Key className="mx-auto h-12 w-12 text-gray-300" />
                <h3 className="mt-4 text-lg font-medium text-gray-900">
                  API 키가 없습니다
                </h3>
                <p className="mt-2 text-gray-500">
                  새 API 키를 생성하여 SaiAd API를 사용하세요
                </p>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="mt-4 rounded-lg bg-samsung-blue px-4 py-2 text-white transition-colors hover:bg-blue-700"
                >
                  API 키 생성
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Quick Start Code Examples */}
        <div className="rounded-xl border bg-white shadow-sm">
          <div className="border-b p-6">
            <h2 className="text-xl font-semibold text-gray-900">빠른 시작</h2>
            <p className="mt-1 text-sm text-gray-500">
              아래 코드 예제로 바로 시작하세요
            </p>
          </div>

          <div className="p-6">
            {/* Language tabs */}
            <div className="mb-4 flex gap-2">
              {(["curl", "python", "javascript"] as const).map((lang) => (
                <button
                  key={lang}
                  onClick={() => setSelectedLanguage(lang)}
                  className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                    selectedLanguage === lang
                      ? "bg-samsung-blue text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  {lang === "curl"
                    ? "cURL"
                    : lang === "python"
                    ? "Python"
                    : "JavaScript"}
                </button>
              ))}
            </div>

            {/* Code block */}
            <div className="relative">
              <pre className="overflow-x-auto rounded-lg bg-gray-900 p-4 text-sm text-gray-100">
                <code>{codeExamples[selectedLanguage]}</code>
              </pre>
              <button
                onClick={() => copyToClipboard(codeExamples[selectedLanguage])}
                className="absolute right-3 top-3 rounded-md bg-gray-700 p-2 text-gray-300 transition-colors hover:bg-gray-600"
              >
                {copiedCode ? (
                  <span className="text-xs text-green-400">복사됨!</span>
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </button>
            </div>

            {/* Response example */}
            <div className="mt-4">
              <h3 className="mb-2 text-sm font-medium text-gray-700">
                응답 예시
              </h3>
              <pre className="overflow-x-auto rounded-lg bg-gray-100 p-4 text-sm text-gray-700">
                <code>{`{
  "job_id": "job_abc123",
  "project_id": "proj_xyz789",
  "status": "queued",
  "estimated_seconds": 180,
  "created_at": "2025-01-21T10:30:00Z"
}`}</code>
              </pre>
            </div>
          </div>
        </div>

        {/* API Usage Stats */}
        <div className="mt-8 rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-gray-900">이번 달 사용량</h2>
          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-lg bg-gray-50 p-4">
              <div className="text-sm text-gray-500">API 요청</div>
              <div className="mt-1 text-2xl font-bold text-gray-900">
                1,250 <span className="text-sm font-normal text-gray-500">/ 10,000</span>
              </div>
              <div className="mt-2 h-2 rounded-full bg-gray-200">
                <div className="h-full w-[12.5%] rounded-full bg-samsung-blue" />
              </div>
            </div>

            <div className="rounded-lg bg-gray-50 p-4">
              <div className="text-sm text-gray-500">영상 생성</div>
              <div className="mt-1 text-2xl font-bold text-gray-900">
                45 <span className="text-sm font-normal text-gray-500">/ 100</span>
              </div>
              <div className="mt-2 h-2 rounded-full bg-gray-200">
                <div className="h-full w-[45%] rounded-full bg-green-500" />
              </div>
            </div>

            <div className="rounded-lg bg-gray-50 p-4">
              <div className="text-sm text-gray-500">남은 크레딧</div>
              <div className="mt-1 text-2xl font-bold text-gray-900">55</div>
              <div className="mt-2 text-sm text-gray-500">
                다음 갱신: 2025년 2월 1일
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Create API Key Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-gray-900">
              새 API 키 생성
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              API 키의 이름과 권한을 설정하세요
            </p>

            <div className="mt-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  키 이름
                </label>
                <input
                  type="text"
                  placeholder="예: Production Key"
                  className="mt-1 w-full rounded-lg border px-3 py-2 focus:border-samsung-blue focus:outline-none focus:ring-1 focus:ring-samsung-blue"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  권한 범위
                </label>
                <div className="mt-2 space-y-2">
                  {[
                    { id: "products:read", label: "제품 조회" },
                    { id: "templates:read", label: "템플릿 조회" },
                    { id: "videos:read", label: "영상 조회" },
                    { id: "videos:create", label: "영상 생성" },
                  ].map((scope) => (
                    <label key={scope.id} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        defaultChecked
                        className="rounded border-gray-300 text-samsung-blue focus:ring-samsung-blue"
                      />
                      <span className="text-sm text-gray-700">{scope.label}</span>
                      <code className="ml-auto text-xs text-gray-500">
                        {scope.id}
                      </code>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setShowCreateModal(false)}
                className="rounded-lg border px-4 py-2 text-gray-700 transition-colors hover:bg-gray-50"
              >
                취소
              </button>
              <button
                onClick={() => {
                  // In production, call API to create key
                  setShowCreateModal(false);
                }}
                className="rounded-lg bg-samsung-blue px-4 py-2 text-white transition-colors hover:bg-blue-700"
              >
                생성하기
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
