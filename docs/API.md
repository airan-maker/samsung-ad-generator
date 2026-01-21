# API Specification

## 삼성 광고 제너레이터 - API 명세

**Base URL**: `https://api.saiad.io/v1`
**Version**: v1
**Format**: JSON

---

## 인증

모든 API 요청은 Bearer 토큰이 필요합니다 (공개 엔드포인트 제외).

```
Authorization: Bearer <access_token>
```

### 토큰 구조
- **Access Token**: 15분 유효
- **Refresh Token**: 7일 유효 (HttpOnly Cookie)

---

## 1. 인증 API

### 1.1 Google OAuth 로그인

```http
POST /auth/google
```

**Request Body**
```json
{
  "code": "4/0AX4XfWh...",  // Google OAuth authorization code
  "redirect_uri": "https://saiad.io/auth/callback"
}
```

**Response** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 900,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@gmail.com",
    "name": "홍길동",
    "profile_image": "https://lh3.googleusercontent.com/...",
    "plan": "free",
    "credits": 3
  }
}
```

### 1.2 Kakao OAuth 로그인

```http
POST /auth/kakao
```

**Request Body**
```json
{
  "code": "abc123...",
  "redirect_uri": "https://saiad.io/auth/callback"
}
```

**Response** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 900,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@kakao.com",
    "name": "홍길동",
    "profile_image": "https://k.kakaocdn.net/...",
    "plan": "free",
    "credits": 3
  }
}
```

### 1.3 토큰 갱신

```http
POST /auth/refresh
```

**Request**: Refresh Token이 HttpOnly Cookie로 전송됨

**Response** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

### 1.4 로그아웃

```http
DELETE /auth/logout
```

**Response** `204 No Content`

---

## 2. 사용자 API

### 2.1 현재 사용자 정보

```http
GET /users/me
```

**Response** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@gmail.com",
  "name": "홍길동",
  "profile_image": "https://lh3.googleusercontent.com/...",
  "plan": "basic",
  "credits": 25,
  "subscription": {
    "plan": "basic",
    "status": "active",
    "current_period_end": "2025-02-21T00:00:00Z"
  },
  "created_at": "2025-01-15T10:30:00Z"
}
```

### 2.2 사용자 정보 수정

```http
PATCH /users/me
```

**Request Body**
```json
{
  "name": "김철수"
}
```

**Response** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "김철수",
  ...
}
```

---

## 3. 제품 API

### 3.1 제품 목록 조회

```http
GET /products
```

**Query Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| category | string | 카테고리 필터 (smartphone, tv, appliance, wearable) |
| search | string | 검색어 |
| page | int | 페이지 번호 (기본: 1) |
| limit | int | 페이지 크기 (기본: 20, 최대: 50) |

**Response** `200 OK`
```json
{
  "items": [
    {
      "id": "prod_001",
      "name": "Galaxy S25 Ultra",
      "model_number": "SM-S928N",
      "category": "smartphone",
      "subcategory": "flagship",
      "thumbnail": "https://cdn.saiad.io/products/s25-ultra-thumb.jpg",
      "released_at": "2025-01-22"
    },
    {
      "id": "prod_002",
      "name": "Galaxy Z Fold 6",
      "model_number": "SM-F956N",
      "category": "smartphone",
      "subcategory": "foldable",
      "thumbnail": "https://cdn.saiad.io/products/z-fold6-thumb.jpg",
      "released_at": "2024-07-10"
    }
  ],
  "total": 50,
  "page": 1,
  "limit": 20,
  "total_pages": 3
}
```

### 3.2 제품 상세 조회

```http
GET /products/{product_id}
```

**Response** `200 OK`
```json
{
  "id": "prod_001",
  "name": "Galaxy S25 Ultra",
  "model_number": "SM-S928N",
  "category": "smartphone",
  "subcategory": "flagship",
  "description": "AI로 더 강력해진 갤럭시 S25 울트라",
  "images": [
    "https://cdn.saiad.io/products/s25-ultra-1.jpg",
    "https://cdn.saiad.io/products/s25-ultra-2.jpg",
    "https://cdn.saiad.io/products/s25-ultra-3.jpg"
  ],
  "specs": {
    "display": "6.9인치 Dynamic AMOLED 2X",
    "processor": "Snapdragon 8 Elite",
    "camera": "200MP 광각 + 50MP 초광각 + 10MP 망원 + 50MP 망원",
    "battery": "5000mAh",
    "storage": "256GB / 512GB / 1TB"
  },
  "features": [
    "Galaxy AI",
    "S Pen 내장",
    "45W 초고속 충전",
    "IP68 방수방진"
  ],
  "released_at": "2025-01-22"
}
```

### 3.3 카테고리 목록

```http
GET /products/categories
```

**Response** `200 OK`
```json
{
  "categories": [
    {
      "id": "smartphone",
      "name": "스마트폰",
      "icon": "📱",
      "count": 15
    },
    {
      "id": "tv",
      "name": "TV",
      "icon": "📺",
      "count": 12
    },
    {
      "id": "appliance",
      "name": "가전",
      "icon": "🏠",
      "count": 18
    },
    {
      "id": "wearable",
      "name": "웨어러블",
      "icon": "⌚",
      "count": 5
    }
  ]
}
```

### 3.4 이미지로 제품 인식

```http
POST /products/recognize
Content-Type: multipart/form-data
```

**Request Body**
| Field | Type | Description |
|-------|------|-------------|
| image | file | 제품 이미지 (jpg, png, webp) |

**Response** `200 OK`
```json
{
  "recognized": true,
  "confidence": 0.95,
  "product": {
    "id": "prod_001",
    "name": "Galaxy S25 Ultra",
    "category": "smartphone"
  },
  "suggestions": [
    {
      "id": "prod_002",
      "name": "Galaxy S25+",
      "confidence": 0.72
    }
  ]
}
```

**Response** `200 OK` (인식 실패)
```json
{
  "recognized": false,
  "message": "제품을 인식하지 못했습니다. 직접 선택해주세요.",
  "suggestions": []
}
```

---

## 4. 템플릿 API

### 4.1 템플릿 목록 조회

```http
GET /templates
```

**Query Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| category | string | 카테고리 필터 |
| style | string | 스타일 필터 (unboxing, lifestyle, comparison 등) |

**Response** `200 OK`
```json
{
  "items": [
    {
      "id": "tpl_001",
      "name": "언박싱 시퀀스",
      "description": "제품 개봉의 설렘을 담은 프리미엄 언박싱 영상",
      "category": "smartphone",
      "style": "unboxing",
      "durations": [15, 30, 60],
      "thumbnail": "https://cdn.saiad.io/templates/unboxing-thumb.jpg",
      "preview_url": "https://cdn.saiad.io/templates/unboxing-preview.mp4",
      "is_premium": false
    },
    {
      "id": "tpl_002",
      "name": "카메라 하이라이트",
      "description": "카메라 성능을 극대화하는 시네마틱 영상",
      "category": "smartphone",
      "style": "feature",
      "durations": [15, 30, 60],
      "thumbnail": "https://cdn.saiad.io/templates/camera-thumb.jpg",
      "preview_url": "https://cdn.saiad.io/templates/camera-preview.mp4",
      "is_premium": false
    }
  ],
  "total": 12
}
```

### 4.2 템플릿 상세 조회

```http
GET /templates/{template_id}
```

**Response** `200 OK`
```json
{
  "id": "tpl_001",
  "name": "언박싱 시퀀스",
  "description": "제품 개봉의 설렘을 담은 프리미엄 언박싱 영상",
  "category": "smartphone",
  "style": "unboxing",
  "durations": [15, 30, 60],
  "thumbnail": "https://cdn.saiad.io/templates/unboxing-thumb.jpg",
  "preview_url": "https://cdn.saiad.io/templates/unboxing-preview.mp4",
  "is_premium": false,
  "scenes": [
    {
      "order": 1,
      "name": "박스 등장",
      "duration_ratio": 0.2,
      "description": "제품 박스가 화면에 등장"
    },
    {
      "order": 2,
      "name": "개봉",
      "duration_ratio": 0.3,
      "description": "박스를 열고 제품 공개"
    },
    {
      "order": 3,
      "name": "제품 클로즈업",
      "duration_ratio": 0.3,
      "description": "제품 디테일 샷"
    },
    {
      "order": 4,
      "name": "CTA",
      "duration_ratio": 0.2,
      "description": "구매 유도 화면"
    }
  ]
}
```

---

## 5. 프로젝트 API

### 5.1 프로젝트 생성

```http
POST /projects
```

**Request Body**
```json
{
  "name": "S25 Ultra 프로모션 영상",
  "product_id": "prod_001",
  "template_id": "tpl_001",
  "config": {
    "duration": 30,
    "tone": "premium",
    "language": "ko"
  }
}
```

**또는 직접 업로드 이미지 사용**
```json
{
  "name": "신제품 프로모션",
  "custom_product_image": "https://s3.../uploads/my-product.jpg",
  "custom_product_name": "Galaxy S25 Ultra",
  "template_id": "tpl_001",
  "config": {
    "duration": 30,
    "tone": "premium",
    "language": "ko"
  }
}
```

**Response** `201 Created`
```json
{
  "id": "proj_001",
  "name": "S25 Ultra 프로모션 영상",
  "product": {
    "id": "prod_001",
    "name": "Galaxy S25 Ultra"
  },
  "template": {
    "id": "tpl_001",
    "name": "언박싱 시퀀스"
  },
  "config": {
    "duration": 30,
    "tone": "premium",
    "language": "ko"
  },
  "status": "draft",
  "created_at": "2025-01-21T15:30:00Z"
}
```

### 5.2 내 프로젝트 목록

```http
GET /projects
```

**Query Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | 상태 필터 (draft, processing, completed, failed) |
| page | int | 페이지 번호 |
| limit | int | 페이지 크기 |

**Response** `200 OK`
```json
{
  "items": [
    {
      "id": "proj_001",
      "name": "S25 Ultra 프로모션 영상",
      "product_name": "Galaxy S25 Ultra",
      "template_name": "언박싱 시퀀스",
      "status": "completed",
      "thumbnail": "https://cdn.saiad.io/projects/proj_001/thumb.jpg",
      "created_at": "2025-01-21T15:30:00Z",
      "updated_at": "2025-01-21T15:35:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "limit": 20
}
```

### 5.3 프로젝트 상세

```http
GET /projects/{project_id}
```

**Response** `200 OK`
```json
{
  "id": "proj_001",
  "name": "S25 Ultra 프로모션 영상",
  "product": {
    "id": "prod_001",
    "name": "Galaxy S25 Ultra",
    "thumbnail": "https://cdn.saiad.io/products/s25-ultra-thumb.jpg"
  },
  "template": {
    "id": "tpl_001",
    "name": "언박싱 시퀀스"
  },
  "config": {
    "duration": 30,
    "tone": "premium",
    "language": "ko"
  },
  "script": {
    "headline": "Galaxy S25 Ultra",
    "subline": "AI로 더 강력해진 카메라",
    "narration": "새로운 갤럭시 S25 울트라를 만나보세요. AI가 만들어내는 놀라운 사진과 영상을 경험하세요.",
    "cta": "지금 바로 만나보세요"
  },
  "videos": [
    {
      "id": "vid_001",
      "version": 1,
      "duration": 30,
      "aspect_ratio": "16:9",
      "video_url": "https://cdn.saiad.io/videos/vid_001.mp4",
      "thumbnail_url": "https://cdn.saiad.io/videos/vid_001-thumb.jpg",
      "created_at": "2025-01-21T15:35:00Z"
    }
  ],
  "status": "completed",
  "created_at": "2025-01-21T15:30:00Z",
  "updated_at": "2025-01-21T15:35:00Z"
}
```

### 5.4 프로젝트 수정

```http
PATCH /projects/{project_id}
```

**Request Body**
```json
{
  "name": "S25 Ultra 신년 프로모션",
  "config": {
    "duration": 60,
    "tone": "mz"
  }
}
```

**Response** `200 OK`

### 5.5 프로젝트 삭제

```http
DELETE /projects/{project_id}
```

**Response** `204 No Content`

---

## 6. 스크립트 API

### 6.1 스크립트 생성

```http
POST /scripts/generate
```

**Request Body**
```json
{
  "project_id": "proj_001",
  "tone": "premium",
  "language": "ko",
  "custom_keywords": ["AI 카메라", "야간 모드", "프로급 촬영"]
}
```

**Response** `200 OK`
```json
{
  "headline": "Galaxy S25 Ultra",
  "subline": "AI로 더 강력해진 카메라",
  "narration": "새로운 갤럭시 S25 울트라를 만나보세요. AI가 만들어내는 놀라운 사진과 영상을 경험하세요. 프로급 촬영이 일상이 됩니다.",
  "cta": "지금 바로 만나보세요",
  "scenes": [
    {
      "order": 1,
      "text": "Galaxy S25 Ultra",
      "narration": "새로운 갤럭시 S25 울트라를 만나보세요."
    },
    {
      "order": 2,
      "text": "AI 카메라",
      "narration": "AI가 만들어내는 놀라운 사진과 영상을 경험하세요."
    },
    {
      "order": 3,
      "text": "프로급 촬영",
      "narration": "프로급 촬영이 일상이 됩니다."
    },
    {
      "order": 4,
      "text": "지금 바로 만나보세요",
      "narration": ""
    }
  ],
  "alternatives": {
    "headline": ["S25 Ultra", "갤럭시 S25 울트라"],
    "subline": ["카메라의 새로운 기준", "AI 시대의 스마트폰"]
  }
}
```

### 6.2 스크립트 재생성

```http
POST /scripts/regenerate
```

**Request Body**
```json
{
  "project_id": "proj_001",
  "field": "narration",
  "current_value": "새로운 갤럭시 S25 울트라를 만나보세요...",
  "instruction": "더 짧고 임팩트 있게"
}
```

**Response** `200 OK`
```json
{
  "field": "narration",
  "value": "AI 카메라의 새로운 기준. 갤럭시 S25 울트라.",
  "alternatives": [
    "프로급 촬영, 이제 누구나. S25 울트라.",
    "카메라가 달라졌다. 갤럭시 S25 울트라."
  ]
}
```

---

## 7. 영상 생성 API

### 7.1 영상 생성 시작

```http
POST /videos/generate
```

**Request Body**
```json
{
  "project_id": "proj_001",
  "script": {
    "headline": "Galaxy S25 Ultra",
    "subline": "AI로 더 강력해진 카메라",
    "narration": "새로운 갤럭시 S25 울트라를 만나보세요.",
    "cta": "지금 바로 만나보세요"
  },
  "config": {
    "duration": 30,
    "aspect_ratio": "16:9",
    "music_id": "music_001",
    "voice_id": "voice_ko_female_01",
    "include_narration": true
  }
}
```

**Response** `202 Accepted`
```json
{
  "job_id": "job_abc123",
  "project_id": "proj_001",
  "status": "queued",
  "estimated_time": 180,
  "created_at": "2025-01-21T15:30:00Z"
}
```

### 7.2 생성 상태 확인

```http
GET /videos/{job_id}/status
```

**Response** `200 OK` (진행 중)
```json
{
  "job_id": "job_abc123",
  "status": "processing",
  "progress": 65,
  "current_step": "video_compositing",
  "steps": [
    { "name": "script_processing", "status": "completed" },
    { "name": "image_processing", "status": "completed" },
    { "name": "video_generation", "status": "completed" },
    { "name": "video_compositing", "status": "in_progress" },
    { "name": "audio_mixing", "status": "pending" }
  ],
  "estimated_remaining": 60
}
```

**Response** `200 OK` (완료)
```json
{
  "job_id": "job_abc123",
  "status": "completed",
  "progress": 100,
  "video": {
    "id": "vid_001",
    "video_url": "https://cdn.saiad.io/videos/vid_001.mp4",
    "thumbnail_url": "https://cdn.saiad.io/videos/vid_001-thumb.jpg",
    "duration": 30,
    "file_size": 15728640,
    "render_time": 145
  }
}
```

### 7.3 영상 다운로드 URL

```http
GET /videos/{video_id}/download
```

**Query Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| format | string | 플랫폼별 포맷 (youtube, instagram, tiktok, coupang) |

**Response** `200 OK`
```json
{
  "download_url": "https://cdn.saiad.io/videos/vid_001.mp4?token=abc...",
  "expires_at": "2025-01-21T16:30:00Z",
  "format": {
    "name": "youtube",
    "aspect_ratio": "16:9",
    "resolution": "1080p"
  }
}
```

---

## 8. 결제 API

### 8.1 구독 결제

```http
POST /payments/subscribe
```

**Request Body**
```json
{
  "plan": "basic",
  "payment_method": "card"
}
```

**Response** `200 OK`
```json
{
  "payment_url": "https://pay.tosspayments.com/...",
  "order_id": "order_abc123"
}
```

### 8.2 결제 확인 (Webhook)

```http
POST /payments/confirm
```

(토스페이먼츠 웹훅으로 호출됨)

### 8.3 구독 취소

```http
POST /payments/cancel
```

**Response** `200 OK`
```json
{
  "message": "구독이 취소되었습니다.",
  "effective_date": "2025-02-21T00:00:00Z"
}
```

### 8.4 결제 내역

```http
GET /payments/history
```

**Response** `200 OK`
```json
{
  "items": [
    {
      "id": "pay_001",
      "amount": 19900,
      "currency": "KRW",
      "plan": "basic",
      "status": "completed",
      "created_at": "2025-01-21T10:00:00Z"
    }
  ],
  "total": 3
}
```

---

## 에러 응답

### 표준 에러 형식

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "요청이 올바르지 않습니다.",
    "details": {
      "field": "duration",
      "reason": "15, 30, 60 중 하나를 선택해주세요."
    }
  }
}
```

### 에러 코드

| HTTP Status | Code | Description |
|-------------|------|-------------|
| 400 | INVALID_REQUEST | 잘못된 요청 |
| 401 | UNAUTHORIZED | 인증 필요 |
| 403 | FORBIDDEN | 권한 없음 |
| 404 | NOT_FOUND | 리소스 없음 |
| 409 | CONFLICT | 충돌 (중복 등) |
| 422 | VALIDATION_ERROR | 유효성 검증 실패 |
| 429 | RATE_LIMITED | 요청 한도 초과 |
| 500 | INTERNAL_ERROR | 서버 오류 |
| 503 | SERVICE_UNAVAILABLE | 서비스 일시 중단 |

---

## Rate Limiting

| Plan | Limit |
|------|-------|
| Free | 60 req/min |
| Basic | 120 req/min |
| Pro | 300 req/min |
| Enterprise | Custom |

**Rate Limit Headers**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705847400
```

---

## WebSocket API

### 영상 생성 진행률 실시간 업데이트

```
wss://api.saiad.io/ws/videos/{job_id}
```

**Message Format**
```json
{
  "type": "progress",
  "data": {
    "progress": 65,
    "current_step": "video_compositing",
    "message": "영상을 합성하고 있습니다..."
  }
}
```

```json
{
  "type": "completed",
  "data": {
    "video_id": "vid_001",
    "video_url": "https://cdn.saiad.io/videos/vid_001.mp4"
  }
}
```

```json
{
  "type": "error",
  "data": {
    "code": "GENERATION_FAILED",
    "message": "영상 생성에 실패했습니다. 다시 시도해주세요."
  }
}
```
