# Samsung Ad Generator (사이아드)

> AI 기반 삼성전자 제품 광고 영상 자동 생성 플랫폼

## 🎯 프로젝트 개요

삼성전자 제품에 특화된 AI 광고 영상 생성 서비스입니다. 제품 이미지와 정보를 입력하면 고품질 광고 영상을 자동으로 생성합니다.

### 핵심 가치
- **속도**: 5분 내 완성된 광고 영상 생성
- **품질**: 삼성 브랜드 가이드라인 준수
- **비용**: 기존 영상 제작 대비 90% 비용 절감

## 🏗️ 프로젝트 구조

```
samsung-ad-generator/
├── frontend/                 # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/             # App Router 페이지
│   │   ├── components/      # React 컴포넌트
│   │   ├── hooks/           # Custom Hooks
│   │   ├── lib/             # 유틸리티
│   │   ├── stores/          # Zustand 상태관리
│   │   └── types/           # TypeScript 타입
│   └── public/              # 정적 파일
│
├── backend/                  # FastAPI 백엔드
│   ├── app/
│   │   ├── api/             # API 라우터
│   │   ├── core/            # 설정, 보안
│   │   ├── models/          # DB 모델
│   │   ├── schemas/         # Pydantic 스키마
│   │   ├── services/        # 비즈니스 로직
│   │   └── agents/          # AI 에이전트
│   └── tests/               # 테스트
│
├── shared/                   # 공유 리소스
│   ├── templates/           # 영상 템플릿
│   ├── products/            # 삼성 제품 DB
│   └── assets/              # 공용 에셋
│
├── docs/                     # 문서
│   ├── PRD.md               # 제품 요구사항
│   ├── API.md               # API 명세
│   ├── ARCHITECTURE.md      # 아키텍처
│   └── ROADMAP.md           # 개발 로드맵
│
├── docker-compose.yml        # 도커 설정
└── .env.example             # 환경변수 예시
```

## 🛠️ 기술 스택

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State**: Zustand
- **Video**: React Player, FFmpeg.wasm

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL + Redis
- **ORM**: SQLAlchemy + Alembic
- **Task Queue**: Celery

### AI Services
- **Script**: Claude API / GPT-4
- **Video**: Runway Gen-3 / Pika Labs
- **Voice**: ElevenLabs
- **Music**: Suno AI

### Infrastructure
- **Cloud**: AWS (EC2, S3, CloudFront)
- **Container**: Docker
- **CI/CD**: GitHub Actions

## 🚀 시작하기

### 필수 요구사항
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### 설치

```bash
# 저장소 클론
git clone https://github.com/your-org/samsung-ad-generator.git
cd samsung-ad-generator

# 환경변수 설정
cp .env.example .env

# Docker로 실행
docker-compose up -d

# 또는 로컬 개발 환경
# Frontend
cd frontend && npm install && npm run dev

# Backend
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload
```

## 📋 주요 기능

### MVP (Phase 1)
- [ ] 사용자 인증 (Google/Kakao OAuth)
- [ ] 삼성 제품 선택 및 이미지 업로드
- [ ] 템플릿 기반 영상 생성
- [ ] AI 스크립트 자동 생성
- [ ] 기본 영상 편집기
- [ ] 결제 시스템

### Phase 2
- [ ] AI 나레이션 (다국어)
- [ ] A/B 테스트 다중 버전
- [ ] 브랜드 가이드라인 자동 적용
- [ ] 플랫폼별 자동 최적화

## 📄 라이선스

Private - All Rights Reserved

## 👥 팀

- Product Owner: TBD
- Tech Lead: TBD
- Frontend: TBD
- Backend: TBD
- AI/ML: TBD
