"use client";

import Link from "next/link";
import { FileText, Grid3X3, Wand2, ArrowRight } from "lucide-react";

export default function CreatePage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="mx-auto max-w-4xl px-4">
        <div className="mb-10 text-center">
          <h1 className="text-3xl font-bold text-gray-900">광고 영상 만들기</h1>
          <p className="mt-2 text-gray-600">원하는 방식을 선택하세요</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Option 1: Template-based */}
          <Link
            href="/create/product"
            className="group rounded-2xl border-2 border-transparent bg-white p-8 shadow-sm transition-all hover:border-samsung-blue hover:shadow-lg"
          >
            <div className="mb-4 inline-flex rounded-xl bg-blue-100 p-3">
              <FileText className="h-8 w-8 text-samsung-blue" />
            </div>
            <h2 className="text-xl font-bold text-gray-900">템플릿 기반 생성</h2>
            <p className="mt-2 text-gray-600">
              제품을 선택하고 준비된 템플릿으로 빠르게 광고 영상을 만드세요
            </p>
            <ul className="mt-4 space-y-2 text-sm text-gray-500">
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-samsung-blue" />
                제품 카탈로그에서 선택
              </li>
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-samsung-blue" />
                다양한 스타일 템플릿
              </li>
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-samsung-blue" />
                AI 스크립트 자동 생성
              </li>
            </ul>
            <div className="mt-6 flex items-center gap-2 text-samsung-blue group-hover:underline">
              시작하기 <ArrowRight className="h-4 w-4" />
            </div>
          </Link>

          {/* Option 2: Storyboard-based (New!) */}
          <Link
            href="/create/storyboard"
            className="group relative rounded-2xl border-2 border-transparent bg-white p-8 shadow-sm transition-all hover:border-samsung-blue hover:shadow-lg"
          >
            {/* New Badge */}
            <div className="absolute right-4 top-4 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 px-3 py-1 text-xs font-bold text-white">
              NEW
            </div>

            <div className="mb-4 inline-flex rounded-xl bg-purple-100 p-3">
              <Grid3X3 className="h-8 w-8 text-purple-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900">AI 스토리보드 생성</h2>
            <p className="mt-2 text-gray-600">
              제품 이미지만 업로드하면 AI가 3x3 스토리보드와 영상을 자동 생성합니다
            </p>
            <ul className="mt-4 space-y-2 text-sm text-gray-500">
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-purple-500" />
                제품 이미지 업로드
              </li>
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-purple-500" />
                9개 장면 2K 이미지 자동 생성
              </li>
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-purple-500" />
                장면별 1-2초 영상 클립 변환
              </li>
            </ul>
            <div className="mt-6 flex items-center gap-2 text-purple-600 group-hover:underline">
              시작하기 <ArrowRight className="h-4 w-4" />
            </div>
          </Link>
        </div>

        {/* Quick Start Tip */}
        <div className="mt-8 rounded-xl bg-gradient-to-r from-samsung-blue/10 to-purple-500/10 p-6">
          <div className="flex items-start gap-4">
            <Wand2 className="h-6 w-6 text-samsung-blue" />
            <div>
              <h3 className="font-semibold text-gray-900">어떤 방식이 좋을까요?</h3>
              <p className="mt-1 text-sm text-gray-600">
                <strong>템플릿 기반</strong>은 빠르고 일관된 품질의 영상을 원할 때,{" "}
                <strong>AI 스토리보드</strong>는 특정 제품 이미지를 최대한 활용한 맞춤형 영상을 원할 때 추천합니다.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
