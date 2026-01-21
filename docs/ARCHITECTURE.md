# System Architecture

## 삼성 광고 제너레이터 - 시스템 아키텍처

---

## 1. 전체 아키텍처

```
                                    ┌─────────────────┐
                                    │   CloudFlare    │
                                    │      CDN        │
                                    └────────┬────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AWS Cloud                                       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Application Layer                            │   │
│  │                                                                      │   │
│  │   ┌──────────────┐          ┌──────────────┐                        │   │
│  │   │   Frontend   │          │   Backend    │                        │   │
│  │   │   (Vercel)   │◄────────►│  (EC2/ECS)   │                        │   │
│  │   │   Next.js    │   API    │   FastAPI    │                        │   │
│  │   └──────────────┘          └──────┬───────┘                        │   │
│  │                                    │                                 │   │
│  └────────────────────────────────────┼─────────────────────────────────┘   │
│                                       │                                     │
│  ┌────────────────────────────────────┼─────────────────────────────────┐   │
│  │                         Service Layer                                │   │
│  │                                    │                                 │   │
│  │   ┌────────────┐    ┌─────────────┴──────────────┐                  │   │
│  │   │   Redis    │    │      Celery Workers        │                  │   │
│  │   │  (Cache)   │    │    (Video Generation)      │                  │   │
│  │   └────────────┘    └─────────────┬──────────────┘                  │   │
│  │                                   │                                  │   │
│  └───────────────────────────────────┼──────────────────────────────────┘   │
│                                      │                                      │
│  ┌───────────────────────────────────┼──────────────────────────────────┐   │
│  │                         Data Layer                                   │   │
│  │                                   │                                  │   │
│  │   ┌────────────┐    ┌────────────┴───┐    ┌──────────────┐          │   │
│  │   │ PostgreSQL │    │       S3       │    │  CloudFront  │          │   │
│  │   │   (RDS)    │    │ (Video/Image)  │    │   (Delivery) │          │   │
│  │   └────────────┘    └────────────────┘    └──────────────┘          │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           External AI Services                               │
│                                                                             │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐               │
│   │  Claude  │   │  Runway  │   │ Eleven   │   │   Suno   │               │
│   │   API    │   │   API    │   │  Labs    │   │    AI    │               │
│   │ (Script) │   │ (Video)  │   │ (Voice)  │   │ (Music)  │               │
│   └──────────┘   └──────────┘   └──────────┘   └──────────┘               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 컴포넌트 상세

### 2.1 Frontend Architecture

```
frontend/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── (auth)/              # 인증 관련 페이지
│   │   │   ├── login/
│   │   │   └── signup/
│   │   ├── (dashboard)/         # 대시보드
│   │   │   ├── projects/
│   │   │   ├── templates/
│   │   │   └── settings/
│   │   ├── create/              # 영상 생성 플로우
│   │   │   ├── product/
│   │   │   ├── template/
│   │   │   ├── customize/
│   │   │   └── result/
│   │   ├── api/                 # API Routes (BFF)
│   │   └── layout.tsx
│   │
│   ├── components/
│   │   ├── ui/                  # shadcn/ui 컴포넌트
│   │   ├── product/             # 제품 관련
│   │   │   ├── ProductSelector.tsx
│   │   │   ├── ProductCard.tsx
│   │   │   └── ImageUploader.tsx
│   │   ├── template/            # 템플릿 관련
│   │   │   ├── TemplateGallery.tsx
│   │   │   ├── TemplatePreview.tsx
│   │   │   └── TemplateCard.tsx
│   │   ├── editor/              # 편집기
│   │   │   ├── VideoEditor.tsx
│   │   │   ├── Timeline.tsx
│   │   │   ├── TextOverlay.tsx
│   │   │   └── MusicSelector.tsx
│   │   └── common/              # 공통
│   │       ├── Header.tsx
│   │       ├── Footer.tsx
│   │       └── Loading.tsx
│   │
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useVideoGeneration.ts
│   │   ├── useProducts.ts
│   │   └── useTemplates.ts
│   │
│   ├── stores/                  # Zustand stores
│   │   ├── authStore.ts
│   │   ├── projectStore.ts
│   │   └── editorStore.ts
│   │
│   ├── lib/
│   │   ├── api.ts              # API 클라이언트
│   │   ├── utils.ts
│   │   └── constants.ts
│   │
│   └── types/
│       ├── product.ts
│       ├── template.ts
│       ├── video.ts
│       └── user.ts
│
├── public/
│   ├── templates/              # 템플릿 썸네일
│   └── products/               # 제품 이미지
│
└── next.config.js
```

### 2.2 Backend Architecture

```
backend/
├── app/
│   ├── main.py                  # FastAPI 앱 진입점
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # 의존성 주입
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py       # 라우터 통합
│   │       ├── auth.py         # 인증 API
│   │       ├── products.py     # 제품 API
│   │       ├── templates.py    # 템플릿 API
│   │       ├── videos.py       # 영상 생성 API
│   │       ├── scripts.py      # 스크립트 API
│   │       └── payments.py     # 결제 API
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # 설정 관리
│   │   ├── security.py         # 인증/보안
│   │   └── exceptions.py       # 커스텀 예외
│   │
│   ├── models/                  # SQLAlchemy 모델
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── template.py
│   │   ├── project.py
│   │   ├── video.py
│   │   └── payment.py
│   │
│   ├── schemas/                 # Pydantic 스키마
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── template.py
│   │   ├── video.py
│   │   └── payment.py
│   │
│   ├── services/                # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── product_service.py
│   │   ├── template_service.py
│   │   ├── video_service.py
│   │   └── payment_service.py
│   │
│   ├── agents/                  # AI 에이전트
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── script_agent.py     # 스크립트 생성
│   │   ├── image_agent.py      # 이미지 처리
│   │   ├── video_agent.py      # 영상 생성
│   │   └── audio_agent.py      # 오디오 생성
│   │
│   ├── tasks/                   # Celery 태스크
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   └── video_tasks.py
│   │
│   └── db/
│       ├── __init__.py
│       ├── session.py          # DB 세션
│       └── init_db.py          # DB 초기화
│
├── alembic/                     # DB 마이그레이션
│   ├── versions/
│   └── env.py
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_products.py
│   └── test_videos.py
│
├── requirements.txt
└── Dockerfile
```

---

## 3. 영상 생성 파이프라인

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Video Generation Pipeline                             │
│                                                                             │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐ │
│   │ Request │───►│ Script  │───►│ Image   │───►│ Video   │───►│ Audio   │ │
│   │ Handler │    │ Agent   │    │ Agent   │    │ Agent   │    │ Agent   │ │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘ │
│        │              │              │              │              │        │
│        ▼              ▼              ▼              ▼              ▼        │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐ │
│   │ Validate│    │ Claude  │    │ SDXL/   │    │ Runway  │    │ Eleven  │ │
│   │ Input   │    │ API     │    │ DALL-E  │    │ Gen-3   │    │ Labs    │ │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘ │
│                       │              │              │              │        │
│                       ▼              ▼              ▼              ▼        │
│                  ┌─────────────────────────────────────────────────────┐   │
│                  │                    Composer                          │   │
│                  │         (FFmpeg - 최종 영상 합성)                     │   │
│                  └─────────────────────────────────────────────────────┘   │
│                                          │                                  │
│                                          ▼                                  │
│                                    ┌─────────┐                             │
│                                    │   S3    │                             │
│                                    │ Upload  │                             │
│                                    └─────────┘                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 각 에이전트 역할

#### Script Agent
```python
# 입력: 제품 정보, 톤앤매너, 템플릿 타입
# 출력: 구조화된 스크립트

{
    "headline": "Galaxy S25 Ultra",
    "subline": "AI로 더 강력해진 카메라",
    "narration": "새로운 갤럭시 S25 울트라를 만나보세요...",
    "cta": "지금 바로 만나보세요",
    "scenes": [
        {"duration": 5, "description": "제품 등장"},
        {"duration": 10, "description": "카메라 기능 시연"},
        {"duration": 10, "description": "야간 모드 비교"},
        {"duration": 5, "description": "CTA 화면"}
    ]
}
```

#### Image Agent
```python
# 입력: 제품 이미지, 씬 설명
# 출력: 처리된 이미지 시퀀스

- 배경 제거/교체
- 제품 각도 조정
- 씬별 이미지 생성
```

#### Video Agent
```python
# 입력: 이미지 시퀀스, 씬 정보
# 출력: 영상 클립들

- Runway API로 이미지 → 영상 변환
- 전환 효과 적용
- 텍스트 오버레이
```

#### Audio Agent
```python
# 입력: 나레이션 스크립트, 음악 선택
# 출력: 오디오 트랙

- TTS 나레이션 생성
- 배경 음악 선택/생성
- 오디오 믹싱
```

---

## 4. 데이터베이스 스키마

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100),
    profile_image VARCHAR(500),
    provider VARCHAR(20), -- google, kakao
    provider_id VARCHAR(255),
    credits INTEGER DEFAULT 3,
    plan VARCHAR(20) DEFAULT 'free', -- free, basic, pro, enterprise
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Products (삼성 제품 DB)
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    model_number VARCHAR(100),
    category VARCHAR(50), -- smartphone, tv, appliance, wearable
    subcategory VARCHAR(50),
    description TEXT,
    specs JSONB, -- 상세 스펙
    images JSONB, -- 이미지 URL 배열
    features JSONB, -- 주요 기능
    released_at DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Templates
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- smartphone, tv, appliance, wearable
    style VARCHAR(50), -- unboxing, lifestyle, comparison, etc.
    durations INTEGER[], -- [15, 30, 60]
    thumbnail_url VARCHAR(500),
    preview_url VARCHAR(500),
    config JSONB, -- 템플릿 설정
    is_premium BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Projects
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200),
    product_id UUID REFERENCES products(id),
    template_id UUID REFERENCES templates(id),
    custom_product_image VARCHAR(500), -- 직접 업로드한 경우
    status VARCHAR(20) DEFAULT 'draft', -- draft, processing, completed, failed
    config JSONB, -- 프로젝트 설정 (톤앤매너, 길이 등)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Videos
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    version INTEGER DEFAULT 1,
    duration INTEGER, -- 초
    resolution VARCHAR(20), -- 1080p, 720p
    aspect_ratio VARCHAR(10), -- 16:9, 9:16, 1:1
    script JSONB, -- 생성된 스크립트
    video_url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    file_size BIGINT,
    render_time INTEGER, -- 렌더링 소요시간 (초)
    created_at TIMESTAMP DEFAULT NOW()
);

-- Payments
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL, -- 원화
    currency VARCHAR(3) DEFAULT 'KRW',
    plan VARCHAR(20),
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255),
    status VARCHAR(20), -- pending, completed, failed, refunded
    created_at TIMESTAMP DEFAULT NOW()
);

-- Usage Logs
CREATE TABLE usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(50), -- video_generated, video_downloaded, etc.
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_videos_project_id ON videos(project_id);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_templates_category ON templates(category);
```

---

## 5. API 설계

### 5.1 인증

```
POST   /api/v1/auth/google          # Google OAuth
POST   /api/v1/auth/kakao           # Kakao OAuth
POST   /api/v1/auth/refresh         # 토큰 갱신
DELETE /api/v1/auth/logout          # 로그아웃
```

### 5.2 제품

```
GET    /api/v1/products             # 제품 목록
GET    /api/v1/products/:id         # 제품 상세
GET    /api/v1/products/categories  # 카테고리 목록
POST   /api/v1/products/recognize   # 이미지로 제품 인식
```

### 5.3 템플릿

```
GET    /api/v1/templates            # 템플릿 목록
GET    /api/v1/templates/:id        # 템플릿 상세
GET    /api/v1/templates/:id/preview # 템플릿 미리보기
```

### 5.4 프로젝트

```
POST   /api/v1/projects             # 프로젝트 생성
GET    /api/v1/projects             # 내 프로젝트 목록
GET    /api/v1/projects/:id         # 프로젝트 상세
PATCH  /api/v1/projects/:id         # 프로젝트 수정
DELETE /api/v1/projects/:id         # 프로젝트 삭제
```

### 5.5 영상 생성

```
POST   /api/v1/videos/generate      # 영상 생성 시작
GET    /api/v1/videos/:id/status    # 생성 상태 확인
GET    /api/v1/videos/:id           # 영상 정보
GET    /api/v1/videos/:id/download  # 다운로드 URL
```

### 5.6 스크립트

```
POST   /api/v1/scripts/generate     # 스크립트 생성
POST   /api/v1/scripts/regenerate   # 스크립트 재생성
```

### 5.7 결제

```
POST   /api/v1/payments/subscribe   # 구독 결제
POST   /api/v1/payments/cancel      # 구독 취소
GET    /api/v1/payments/history     # 결제 내역
```

---

## 6. 배포 환경

### 6.1 Development
```yaml
# docker-compose.dev.yml
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    volumes: ["./frontend:/app"]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    volumes: ["./backend:/app"]

  postgres:
    image: postgres:15
    ports: ["5432:5432"]

  redis:
    image: redis:7
    ports: ["6379:6379"]
```

### 6.2 Production
```
Frontend: Vercel (자동 배포)
Backend: AWS ECS Fargate
Database: AWS RDS PostgreSQL
Cache: AWS ElastiCache Redis
Storage: AWS S3 + CloudFront
Queue: AWS SQS + Celery
```

---

## 7. 보안 고려사항

### 7.1 인증/인가
- JWT 기반 인증 (Access Token: 15분, Refresh Token: 7일)
- OAuth 2.0 (Google, Kakao)
- API Rate Limiting (100 req/min per user)

### 7.2 데이터 보안
- 모든 통신 HTTPS
- DB 암호화 (at rest)
- 민감 정보 환경변수 관리 (AWS Secrets Manager)

### 7.3 파일 업로드
- 허용 확장자 제한 (jpg, png, webp)
- 파일 크기 제한 (10MB)
- 바이러스 스캔
