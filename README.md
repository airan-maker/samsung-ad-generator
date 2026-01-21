# Samsung Ad Generator (SaiAd)

> AI 기반 삼성전자 제품 광고 영상 자동 생성 플랫폼

[![License](https://img.shields.io/badge/license-Private-red.svg)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)]()
[![Next.js](https://img.shields.io/badge/next.js-14-black.svg)]()
[![FastAPI](https://img.shields.io/badge/fastapi-0.104+-green.svg)]()

## 프로젝트 개요

삼성전자 제품에 특화된 AI 광고 영상 생성 서비스입니다. 제품 이미지와 정보를 입력하면 고품질 광고 영상을 자동으로 생성합니다.

### 핵심 가치
- **속도**: 5분 내 완성된 광고 영상 생성
- **품질**: 삼성 브랜드 가이드라인 준수
- **비용**: 기존 영상 제작 대비 90% 비용 절감

---

## 개발 완료 현황

### Phase 0-1: Foundation & Core MVP ✅

| 기능 | 상태 | 설명 |
|------|------|------|
| 프로젝트 구조 설정 | ✅ 완료 | Next.js 14 + FastAPI 모노레포 구조 |
| 인증 시스템 | ✅ 완료 | Google/Kakao OAuth, JWT 토큰 관리 |
| 제품 관리 | ✅ 완료 | 삼성 제품 DB, 카테고리별 브라우징 |
| 템플릿 시스템 | ✅ 완료 | 영상 템플릿 갤러리, 미리보기 |
| AI 스크립트 생성 | ✅ 완료 | Claude API 기반 자동 스크립트 생성 |
| 영상 생성 파이프라인 | ✅ 완료 | Celery 워커, Runway API 연동 |
| 영상 편집기 | ✅ 완료 | 텍스트 편집, 배경음악 선택 |
| 결제 시스템 | ✅ 완료 | 토스페이먼츠 연동, 구독/크레딧 |

### Phase 2: Enhancement ✅

| 기능 | 상태 | 설명 |
|------|------|------|
| AI 나레이션 | ✅ 완료 | ElevenLabs TTS, 다국어 지원 |
| A/B 테스트 | ✅ 완료 | 다중 버전 생성, 성과 비교 |
| 다국어 지원 | ✅ 완료 | 한국어/영어/중국어 UI 및 스크립트 |
| 브랜드 가이드라인 | ✅ 완료 | 삼성 색상/폰트 자동 적용 |

### Phase 3: B2B & Production ✅

| 기능 | 상태 | 설명 |
|------|------|------|
| B2B Public API | ✅ 완료 | REST API, API 키 인증, Rate Limiting |
| 개발자 포털 | ✅ 완료 | API 문서, 코드 예제 |
| 분석 대시보드 | ✅ 완료 | 사용량 통계, 영상 성과 추적 |
| 관리자 대시보드 | ✅ 완료 | 사용자 관리, 시스템 모니터링 |
| 보안 미들웨어 | ✅ 완료 | Rate Limiting, XSS/SQL Injection 방어 |
| CI/CD 파이프라인 | ✅ 완료 | GitHub Actions, 자동 배포 |
| 프로덕션 인프라 | ✅ 완료 | Docker, Nginx, Terraform (AWS) |

### Phase 4: Post-Launch Enhancements ✅

| 기능 | 상태 | 설명 |
|------|------|------|
| 실시간 협업 | ✅ 완료 | WebSocket, 커서 동기화, 채팅 |
| AI 비디오 최적화 | ✅ 완료 | Claude 기반 제목/스크립트 최적화 |
| 소셜 미디어 통합 | ✅ 완료 | YouTube, Instagram, TikTok 자동 게시 |
| 모바일 편집기 | ✅ 완료 | 반응형 UI, 터치 제스처 지원 |
| 템플릿 커스터마이징 | ✅ 완료 | 색상, 타이포그래피, 레이아웃, 효과 |
| 웹훅 알림 | ✅ 완료 | HMAC 서명, 이벤트 기반 알림 |

---

## 프로젝트 구조

```
samsung-ad-generator/
├── frontend/                     # Next.js 14 프론트엔드
│   ├── src/
│   │   ├── app/                 # App Router 페이지
│   │   │   ├── (auth)/          # 인증 페이지 (로그인, 회원가입)
│   │   │   ├── (dashboard)/     # 대시보드 페이지
│   │   │   ├── create/          # 영상 생성 플로우
│   │   │   └── payment/         # 결제 관련 페이지
│   │   ├── components/          # React 컴포넌트
│   │   │   ├── analytics/       # 분석 컴포넌트
│   │   │   ├── collaboration/   # 협업 컴포넌트
│   │   │   ├── common/          # 공통 컴포넌트
│   │   │   ├── editor/          # 편집기 컴포넌트
│   │   │   ├── templates/       # 템플릿 컴포넌트
│   │   │   └── ui/              # UI 기본 컴포넌트
│   │   ├── hooks/               # Custom Hooks
│   │   ├── i18n/                # 다국어 지원
│   │   ├── lib/                 # 유틸리티
│   │   └── stores/              # Zustand 상태관리
│   └── public/                  # 정적 파일
│
├── backend/                      # FastAPI 백엔드
│   ├── app/
│   │   ├── api/v1/              # API 라우터
│   │   │   ├── auth.py          # 인증 API
│   │   │   ├── users.py         # 사용자 API
│   │   │   ├── products.py      # 제품 API
│   │   │   ├── templates.py     # 템플릿 API
│   │   │   ├── projects.py      # 프로젝트 API
│   │   │   ├── videos.py        # 영상 API
│   │   │   ├── scripts.py       # 스크립트 API
│   │   │   ├── payments.py      # 결제 API
│   │   │   ├── voices.py        # 음성 API
│   │   │   ├── ab_tests.py      # A/B 테스트 API
│   │   │   ├── analytics.py     # 분석 API
│   │   │   ├── collaboration.py # 협업 API
│   │   │   └── public_api.py    # B2B Public API
│   │   ├── agents/              # AI 에이전트
│   │   │   ├── script_agent.py  # 스크립트 생성
│   │   │   ├── video_agent.py   # 영상 생성
│   │   │   ├── audio_agent.py   # 오디오/TTS
│   │   │   ├── music_agent.py   # 배경음악 생성
│   │   │   └── pipeline.py      # 파이프라인 통합
│   │   ├── core/                # 핵심 설정
│   │   │   ├── config.py        # 환경 설정
│   │   │   ├── security.py      # 인증/보안
│   │   │   ├── security_middleware.py  # 보안 미들웨어
│   │   │   └── security_utils.py       # 보안 유틸리티
│   │   ├── models/              # SQLAlchemy 모델
│   │   ├── services/            # 비즈니스 로직
│   │   │   ├── analytics_service.py      # 분석 서비스
│   │   │   ├── collaboration_service.py  # 협업 서비스
│   │   │   ├── ai_optimizer_service.py   # AI 최적화
│   │   │   ├── social_media_service.py   # 소셜 미디어
│   │   │   ├── webhook_service.py        # 웹훅
│   │   │   └── payment_service.py        # 결제 서비스
│   │   ├── tasks/               # Celery 태스크
│   │   └── db/                  # DB 설정
│   └── alembic/                 # DB 마이그레이션
│
├── infrastructure/              # 인프라 설정
│   └── terraform/               # AWS Terraform
│       └── main.tf              # VPC, ECS, RDS, S3, CloudFront
│
├── nginx/                       # Nginx 설정
│   └── nginx.conf               # 리버스 프록시
│
├── .github/                     # GitHub 설정
│   └── workflows/
│       ├── ci.yml               # CI 파이프라인
│       └── deploy.yml           # CD 파이프라인
│
├── docs/                        # 문서
│   ├── PRD.md                   # 제품 요구사항
│   ├── API.md                   # API 명세
│   ├── ARCHITECTURE.md          # 아키텍처
│   └── ROADMAP.md               # 개발 로드맵
│
├── docker-compose.yml           # 개발 환경
├── docker-compose.prod.yml      # 프로덕션 환경
└── .env.example                 # 환경변수 예시
```

---

## 기술 스택

### Frontend
| 기술 | 버전 | 용도 |
|------|------|------|
| Next.js | 14.x | React 프레임워크 (App Router) |
| TypeScript | 5.x | 타입 안정성 |
| Tailwind CSS | 3.x | 스타일링 |
| shadcn/ui | - | UI 컴포넌트 |
| Zustand | 4.x | 상태 관리 |
| Lucide React | - | 아이콘 |

### Backend
| 기술 | 버전 | 용도 |
|------|------|------|
| FastAPI | 0.104+ | REST API 프레임워크 |
| Python | 3.11+ | 백엔드 언어 |
| SQLAlchemy | 2.x | ORM |
| Alembic | - | DB 마이그레이션 |
| Celery | 5.x | 비동기 태스크 큐 |
| Redis | 7.x | 캐시, 메시지 브로커 |
| PostgreSQL | 15.x | 메인 데이터베이스 |

### AI Services
| 서비스 | 용도 |
|--------|------|
| Claude API (Anthropic) | 스크립트 생성, AI 최적화 |
| OpenAI GPT-4 | 대체 스크립트 생성 |
| Runway Gen-3 | AI 영상 생성 |
| ElevenLabs | TTS 나레이션 |
| Suno AI | 배경음악 생성 |

### Infrastructure
| 기술 | 용도 |
|------|------|
| AWS ECS Fargate | 컨테이너 오케스트레이션 |
| AWS RDS | 관리형 PostgreSQL |
| AWS ElastiCache | 관리형 Redis |
| AWS S3 | 파일 스토리지 |
| AWS CloudFront | CDN |
| Docker | 컨테이너화 |
| Terraform | IaC |
| GitHub Actions | CI/CD |

---

## 시작하기

### 필수 요구사항

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### 1. 저장소 클론

```bash
git clone https://github.com/airan-maker/samsung-ad-generator.git
cd samsung-ad-generator
```

### 2. 환경변수 설정

```bash
cp .env.example .env
# .env 파일을 열어 필요한 API 키를 입력
```

### 3. Docker로 실행 (권장)

```bash
# 개발 환경
docker-compose up -d

# 프로덕션 환경
docker-compose -f docker-compose.prod.yml up -d
```

### 4. 로컬 개발 환경

```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend (새 터미널)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Celery Worker (새 터미널)
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

### 5. 접속

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API 문서: http://localhost:8000/docs

---

## 필요한 API 키 및 발급 방법

### 필수 API 키

| API | 용도 | 발급처 | 요금 |
|-----|------|--------|------|
| **Anthropic (Claude)** | AI 스크립트 생성 | [console.anthropic.com](https://console.anthropic.com) | 사용량 기반 (~$3/1M 토큰) |
| **Runway** | AI 영상 생성 | [runwayml.com](https://runwayml.com) | $12/월부터 |
| **ElevenLabs** | AI 음성 합성 (TTS) | [elevenlabs.io](https://elevenlabs.io) | Free 10K자/월, $5/월부터 |

### 인증 관련 API 키

| API | 용도 | 발급처 | 요금 |
|-----|------|--------|------|
| **Google OAuth** | 구글 로그인 | [console.cloud.google.com](https://console.cloud.google.com) | 무료 |
| **Kakao OAuth** | 카카오 로그인 | [developers.kakao.com](https://developers.kakao.com) | 무료 |

### 결제 API 키

| API | 용도 | 발급처 | 요금 |
|-----|------|--------|------|
| **토스페이먼츠** | 결제 처리 | [developers.tosspayments.com](https://developers.tosspayments.com) | 수수료 2.8%~3.4% |

### 인프라 관련

| API | 용도 | 발급처 |
|-----|------|--------|
| **AWS** | 클라우드 인프라 | [aws.amazon.com](https://aws.amazon.com) |

### 선택적 API 키

| API | 용도 | 발급처 |
|-----|------|--------|
| **OpenAI** | 대체 AI 모델 | [platform.openai.com](https://platform.openai.com) |
| **Replicate** | 대체 영상 생성 | [replicate.com](https://replicate.com) |
| **Suno AI** | AI 배경음악 | [suno.ai](https://suno.ai) |

---

## API 키 발급 상세 가이드

### 1. Anthropic (Claude) API - 필수

1. [console.anthropic.com](https://console.anthropic.com) 접속
2. 회원가입 및 로그인
3. "API Keys" 메뉴에서 새 키 생성
4. `.env`의 `ANTHROPIC_API_KEY`에 입력

```env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

### 2. Runway API - 필수

1. [runwayml.com](https://runwayml.com) 접속
2. 회원가입 및 로그인 (유료 플랜 필요)
3. Settings → API에서 API 키 생성
4. `.env`의 `RUNWAY_API_KEY`에 입력

```env
RUNWAY_API_KEY=rw_xxxxx
```

### 3. ElevenLabs API - 필수

1. [elevenlabs.io](https://elevenlabs.io) 접속
2. 회원가입 및 로그인
3. Profile → API Key에서 키 확인
4. `.env`의 `ELEVENLABS_API_KEY`에 입력

```env
ELEVENLABS_API_KEY=xxxxx
```

### 4. Google OAuth - 필수 (로그인용)

1. [console.cloud.google.com](https://console.cloud.google.com) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. "APIs & Services" → "Credentials"
4. "Create Credentials" → "OAuth client ID"
5. Application type: "Web application"
6. Authorized redirect URIs 추가:
   - `http://localhost:3000/auth/callback/google`
   - `https://yourdomain.com/auth/callback/google`
7. Client ID와 Client Secret 복사

```env
GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxx
NEXT_PUBLIC_GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
```

### 5. Kakao OAuth - 필수 (로그인용)

1. [developers.kakao.com](https://developers.kakao.com) 접속
2. 애플리케이션 추가
3. "앱 키"에서 REST API 키 확인
4. "카카오 로그인" 활성화
5. Redirect URI 등록:
   - `http://localhost:3000/auth/callback/kakao`
   - `https://yourdomain.com/auth/callback/kakao`

```env
KAKAO_CLIENT_ID=xxxxx
KAKAO_CLIENT_SECRET=xxxxx
NEXT_PUBLIC_KAKAO_CLIENT_ID=xxxxx
```

### 6. 토스페이먼츠 - 필수 (결제용)

1. [developers.tosspayments.com](https://developers.tosspayments.com) 접속
2. 회원가입 및 사업자 인증
3. "내 개발 정보"에서 API 키 확인
4. 테스트 키 또는 라이브 키 사용

```env
TOSS_CLIENT_KEY=test_ck_xxxxx
TOSS_SECRET_KEY=test_sk_xxxxx
```

### 7. AWS 자격증명 - 프로덕션용

1. [AWS Console](https://aws.amazon.com) 접속
2. IAM → Users → 새 사용자 생성
3. 필요한 권한 부여:
   - AmazonS3FullAccess
   - AmazonECS_FullAccess
   - AmazonRDSFullAccess
   - AmazonElastiCacheFullAccess
4. Access Key 생성

```env
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=xxxxx
AWS_REGION=ap-northeast-2
S3_BUCKET=saiad-assets
```

---

## 환경변수 전체 목록

```env
# App
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-super-secret-key-change-in-production

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/saiad

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# OAuth - Google
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# OAuth - Kakao
KAKAO_CLIENT_ID=your-kakao-client-id
KAKAO_CLIENT_SECRET=your-kakao-client-secret

# AWS
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=ap-northeast-2
S3_BUCKET=saiad-assets
CLOUDFRONT_DOMAIN=cdn.saiad.io

# AI Services - Script Generation
ANTHROPIC_API_KEY=your-anthropic-api-key
OPENAI_API_KEY=your-openai-api-key

# AI Services - Video Generation
RUNWAY_API_KEY=your-runway-api-key
REPLICATE_API_KEY=your-replicate-api-key

# AI Services - Audio/TTS
ELEVENLABS_API_KEY=your-elevenlabs-api-key

# AI Services - Music Generation
SUNO_API_KEY=your-suno-api-key
MUBERT_API_KEY=your-mubert-api-key

# Payment - Toss
TOSS_CLIENT_KEY=your-toss-client-key
TOSS_SECRET_KEY=your-toss-secret-key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
NEXT_PUBLIC_KAKAO_CLIENT_ID=your-kakao-client-id
```

---

## 라이선스

Private - All Rights Reserved

## Repository

- GitHub: [github.com/airan-maker/samsung-ad-generator](https://github.com/airan-maker/samsung-ad-generator)
