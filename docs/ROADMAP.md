# Development Roadmap

## 삼성 광고 제너레이터 - 개발 로드맵

---

## 타임라인 개요

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Development Timeline                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 0        Phase 1           Phase 2           Phase 3                 │
│  Foundation     Core MVP          Enhancement       Scale                   │
│  ──────────     ────────          ───────────       ─────                   │
│  Week 1-2       Week 3-8          Week 9-14         Week 15-20              │
│                                                                             │
│  ▓▓▓▓           ▓▓▓▓▓▓▓▓▓▓▓▓      ▓▓▓▓▓▓▓▓▓▓▓▓      ▓▓▓▓▓▓▓▓▓▓▓▓           │
│                                                                             │
│  • 환경 설정     • 인증 시스템      • AI 나레이션      • B2B API              │
│  • 프로젝트      • 제품/템플릿      • A/B 테스트       • 분석 대시보드         │
│    구조 설정     • 영상 생성        • 다국어 지원      • 성능 최적화           │
│  • CI/CD        • 편집기           • 브랜드 체크      • 확장                  │
│                 • 결제 시스템                                                │
│                                                                             │
│           ▲                  ▲                  ▲                           │
│           │                  │                  │                           │
│       MVP Alpha          MVP Beta           Public Launch                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 0: Foundation (Week 1-2)

### 목표
프로젝트 기반 환경 구축 및 개발 인프라 설정

### Week 1: 환경 설정

| Task | 담당 | 완료 기준 |
|------|------|----------|
| 저장소 생성 및 브랜치 전략 수립 | DevOps | main, develop, feature/* 브랜치 구조 |
| Frontend 프로젝트 초기화 | Frontend | Next.js 14 + TypeScript + Tailwind 설정 |
| Backend 프로젝트 초기화 | Backend | FastAPI + Poetry 설정 |
| Docker 환경 구성 | DevOps | docker-compose 로컬 개발 환경 |
| CI/CD 파이프라인 | DevOps | GitHub Actions 기본 설정 |

```bash
# Week 1 체크리스트
□ GitHub 저장소 생성
□ Branch protection rules 설정
□ PR 템플릿 작성
□ Frontend boilerplate 완성
□ Backend boilerplate 완성
□ Docker Compose 로컬 환경
□ ESLint/Prettier/Black 설정
□ Pre-commit hooks 설정
```

### Week 2: 개발 인프라

| Task | 담당 | 완료 기준 |
|------|------|----------|
| AWS 인프라 초기 설정 | DevOps | VPC, 보안그룹 설정 |
| 데이터베이스 설정 | Backend | PostgreSQL + Alembic 마이그레이션 |
| 스테이징 환경 구축 | DevOps | dev.saiad.io 접속 가능 |
| 외부 API 계정 생성 | Tech Lead | Claude, Runway, ElevenLabs API 키 확보 |
| 디자인 시스템 기초 | Frontend | shadcn/ui 컴포넌트 설정 |

```bash
# Week 2 체크리스트
□ AWS 계정 및 IAM 설정
□ RDS PostgreSQL 인스턴스
□ S3 버킷 생성
□ Vercel 프로젝트 연결
□ 환경변수 관리 체계
□ 기본 DB 스키마 마이그레이션
□ API 키 Secrets Manager 등록
□ 스테이징 배포 확인
```

### Deliverables
- [ ] 동작하는 개발 환경
- [ ] CI/CD 파이프라인
- [ ] 스테이징 URL 접속 가능
- [ ] 모든 외부 API 연동 테스트 완료

---

## Phase 1: Core MVP (Week 3-8)

### 목표
핵심 기능이 동작하는 MVP 완성

### Sprint 1 (Week 3-4): 인증 & 제품

#### Week 3: 인증 시스템

| Task | 담당 | Story Points |
|------|------|-------------|
| Google OAuth 연동 | Backend | 5 |
| Kakao OAuth 연동 | Backend | 5 |
| JWT 토큰 관리 | Backend | 3 |
| 로그인/회원가입 UI | Frontend | 5 |
| 사용자 프로필 페이지 | Frontend | 3 |

```bash
# Week 3 체크리스트
□ POST /api/v1/auth/google 구현
□ POST /api/v1/auth/kakao 구현
□ 토큰 갱신 로직
□ 로그인 페이지 UI
□ 회원가입 플로우
□ 로그인 상태 유지 (Zustand)
□ 프로필 페이지
□ 로그아웃 기능
```

#### Week 4: 제품 시스템

| Task | 담당 | Story Points |
|------|------|-------------|
| 삼성 제품 DB 구축 (50개) | Backend | 8 |
| 제품 API 구현 | Backend | 5 |
| 제품 선택 UI | Frontend | 8 |
| 이미지 업로드 | Frontend | 5 |
| 제품 인식 API 연동 | Backend | 5 |

```bash
# Week 4 체크리스트
□ products 테이블 시드 데이터
□ GET /api/v1/products 구현
□ 카테고리별 제품 브라우징 UI
□ 제품 검색 기능
□ 이미지 업로드 (S3)
□ Vision API 제품 인식
□ 제품 상세 모달
□ 제품 선택 상태 관리
```

### Sprint 2 (Week 5-6): 템플릿 & 스크립트

#### Week 5: 템플릿 시스템

| Task | 담당 | Story Points |
|------|------|-------------|
| 템플릿 DB 설계 및 시드 | Backend | 5 |
| 템플릿 API 구현 | Backend | 3 |
| 템플릿 갤러리 UI | Frontend | 8 |
| 템플릿 미리보기 | Frontend | 5 |
| 영상 길이 선택 | Frontend | 2 |

```bash
# Week 5 체크리스트
□ templates 테이블 시드 (12개)
□ GET /api/v1/templates 구현
□ 템플릿 카드 컴포넌트
□ 카테고리 필터
□ 템플릿 미리보기 비디오
□ 15/30/60초 선택 UI
□ 템플릿 상세 정보 표시
□ 선택 상태 관리
```

#### Week 6: AI 스크립트 생성

| Task | 담당 | Story Points |
|------|------|-------------|
| Script Agent 구현 | Backend | 8 |
| Claude API 연동 | Backend | 5 |
| 스크립트 생성 API | Backend | 3 |
| 커스터마이징 UI | Frontend | 8 |
| 톤앤매너 선택 | Frontend | 3 |
| 스크립트 편집 | Frontend | 5 |

```bash
# Week 6 체크리스트
□ Script Agent 클래스 구현
□ Claude API 프롬프트 엔지니어링
□ POST /api/v1/scripts/generate
□ 톤앤매너 3종 (프리미엄/실용/MZ)
□ 헤드라인/서브카피 생성
□ 나레이션 스크립트 생성
□ 스크립트 재생성 버튼
□ 수동 편집 기능
```

### Sprint 3 (Week 7-8): 영상 생성 & 편집기

#### Week 7: 영상 생성 파이프라인

| Task | 담당 | Story Points |
|------|------|-------------|
| Celery 워커 설정 | Backend | 5 |
| Video Agent 구현 | Backend | 13 |
| Runway API 연동 | Backend | 8 |
| FFmpeg 합성 로직 | Backend | 8 |
| 생성 상태 실시간 업데이트 | Full Stack | 5 |

```bash
# Week 7 체크리스트
□ Celery + Redis 설정
□ Video Agent 클래스
□ Runway Gen-3 API 연동
□ 이미지 → 영상 변환
□ 씬 전환 효과
□ 텍스트 오버레이 (FFmpeg)
□ WebSocket 진행률 전송
□ 생성 상태 UI
```

#### Week 8: 편집기 & 완성

| Task | 담당 | Story Points |
|------|------|-------------|
| 영상 편집기 UI | Frontend | 13 |
| 텍스트 편집 기능 | Frontend | 5 |
| 배경 음악 선택 | Frontend | 5 |
| 다운로드 기능 | Full Stack | 5 |
| 플랫폼별 내보내기 | Backend | 8 |

```bash
# Week 8 체크리스트
□ VideoEditor 컴포넌트
□ 텍스트 위치/스타일 수정
□ 배경 음악 5종 프리셋
□ 실시간 미리보기
□ Undo/Redo
□ MP4 다운로드
□ 유튜브/인스타/틱톡/쿠팡 규격
□ 최종 QA 및 버그 수정
```

### MVP Alpha Deliverables
- [ ] 회원가입/로그인 동작
- [ ] 제품 선택 → 템플릿 선택 → 영상 생성 전체 플로우
- [ ] 30초 영상 생성 (3분 이내)
- [ ] 기본 편집 및 다운로드
- [ ] 내부 테스트 가능한 상태

---

## Phase 2: Enhancement (Week 9-14)

### 목표
사용자 경험 개선 및 프리미엄 기능 추가

### Sprint 4 (Week 9-10): 결제 & 나레이션

#### Week 9: 결제 시스템

| Task | 담당 | Story Points |
|------|------|-------------|
| 토스페이먼츠 연동 | Backend | 8 |
| 구독 결제 로직 | Backend | 5 |
| 크레딧 시스템 | Backend | 5 |
| 결제 UI | Frontend | 8 |
| 플랜 선택 페이지 | Frontend | 5 |

```bash
# Week 9 체크리스트
□ 토스페이먼츠 SDK 연동
□ 구독 결제 API
□ 크레딧 차감 로직
□ 결제 페이지 UI
□ 플랜 비교 테이블
□ 결제 완료 화면
□ 영수증 발행
□ 결제 실패 처리
```

#### Week 10: AI 나레이션

| Task | 담당 | Story Points |
|------|------|-------------|
| Audio Agent 구현 | Backend | 8 |
| ElevenLabs API 연동 | Backend | 5 |
| 음성 선택 UI | Frontend | 5 |
| 음성 미리듣기 | Frontend | 3 |
| 오디오 믹싱 | Backend | 5 |

```bash
# Week 10 체크리스트
□ Audio Agent 클래스
□ ElevenLabs TTS 연동
□ 한국어 음성 3종
□ 영어 음성 2종
□ 음성 선택 UI
□ 미리듣기 기능
□ 나레이션 + 배경음악 믹싱
□ 볼륨 조절
```

### Sprint 5 (Week 11-12): 다국어 & A/B 테스트

#### Week 11: 다국어 지원

| Task | 담당 | Story Points |
|------|------|-------------|
| i18n 설정 | Frontend | 5 |
| 한국어/영어/중국어 번역 | - | 8 |
| 다국어 스크립트 생성 | Backend | 5 |
| 언어 선택 UI | Frontend | 3 |

```bash
# Week 11 체크리스트
□ next-intl 설정
□ 한국어 번역 파일
□ 영어 번역 파일
□ 중국어 번역 파일
□ 언어 선택 드롭다운
□ 스크립트 다국어 생성
□ 나레이션 다국어
□ 언어 자동 감지
```

#### Week 12: A/B 테스트 다중 버전

| Task | 담당 | Story Points |
|------|------|-------------|
| 다중 버전 생성 로직 | Backend | 8 |
| 버전 비교 UI | Frontend | 8 |
| 버전 관리 시스템 | Full Stack | 5 |

```bash
# Week 12 체크리스트
□ 3가지 톤으로 동시 생성
□ 버전 비교 뷰
□ 나란히 보기
□ 버전별 다운로드
□ 버전 히스토리
□ 최적 버전 추천 (향후)
```

### Sprint 6 (Week 13-14): 품질 & 안정화

#### Week 13: 브랜드 가이드라인

| Task | 담당 | Story Points |
|------|------|-------------|
| 삼성 브랜드 색상 자동 적용 | Backend | 5 |
| 로고 워터마크 자동 삽입 | Backend | 3 |
| 폰트 가이드라인 적용 | Frontend | 5 |
| 브랜드 체크리스트 | Full Stack | 5 |

```bash
# Week 13 체크리스트
□ 삼성 공식 색상 팔레트
□ 로고 자동 배치
□ Samsung One 폰트 적용
□ 브랜드 가이드라인 체커
□ 위반 시 경고 표시
```

#### Week 14: 안정화 & 최적화

| Task | 담당 | Story Points |
|------|------|-------------|
| 성능 최적화 | Full Stack | 8 |
| 에러 처리 강화 | Full Stack | 5 |
| 로깅 및 모니터링 | DevOps | 5 |
| QA 및 버그 수정 | All | 8 |

```bash
# Week 14 체크리스트
□ 영상 생성 시간 최적화
□ 프론트엔드 번들 최적화
□ 에러 바운더리
□ Sentry 에러 트래킹
□ CloudWatch 대시보드
□ 부하 테스트
□ 베타 테스터 피드백 반영
□ 크리티컬 버그 수정
```

### MVP Beta Deliverables
- [ ] 결제 시스템 동작
- [ ] AI 나레이션 (한/영/중)
- [ ] A/B 테스트 다중 버전
- [ ] 브랜드 가이드라인 적용
- [ ] 베타 테스트 준비 완료

---

## Phase 3: Scale (Week 15-20)

### 목표
프로덕션 배포 및 확장성 확보

### Sprint 7 (Week 15-16): B2B & API

| Task | 담당 | Story Points |
|------|------|-------------|
| Public API 설계 | Backend | 8 |
| API 문서화 (OpenAPI) | Backend | 5 |
| API 키 관리 | Backend | 5 |
| Rate Limiting | Backend | 3 |
| 개발자 포털 | Frontend | 8 |

### Sprint 8 (Week 17-18): 분석 & 대시보드

| Task | 담당 | Story Points |
|------|------|-------------|
| 사용자 분석 대시보드 | Full Stack | 13 |
| 영상 성과 추적 | Backend | 8 |
| 리포트 생성 | Backend | 5 |
| 관리자 대시보드 | Frontend | 8 |

### Sprint 9 (Week 19-20): 런칭 준비

| Task | 담당 | Story Points |
|------|------|-------------|
| 프로덕션 인프라 최종화 | DevOps | 8 |
| 보안 감사 | DevOps | 8 |
| 성능 튜닝 | Full Stack | 8 |
| 런칭 마케팅 준비 | Marketing | - |
| 고객 지원 체계 | Support | - |

### Public Launch Deliverables
- [ ] B2B API 제공
- [ ] 분석 대시보드
- [ ] 프로덕션 안정성 확보
- [ ] SLA 99.9% 준비
- [ ] 고객 지원 체계

---

## 리소스 계획

### 팀 구성 (권장)

| 역할 | 인원 | 주요 책임 |
|------|------|----------|
| Tech Lead | 1 | 아키텍처, 코드 리뷰, 기술 의사결정 |
| Frontend | 2 | Next.js, UI/UX 구현 |
| Backend | 2 | FastAPI, AI 에이전트, 영상 파이프라인 |
| DevOps | 1 | 인프라, CI/CD, 모니터링 |
| Designer | 1 | UI/UX 디자인, 템플릿 제작 |
| PM | 1 | 일정 관리, 스프린트 진행 |

### 예상 비용 (월)

| 항목 | MVP Phase | Scale Phase |
|------|-----------|-------------|
| AWS 인프라 | $500 | $2,000 |
| AI API (Runway, Claude 등) | $1,000 | $5,000 |
| 도메인/SSL | $50 | $50 |
| 모니터링 도구 | $100 | $300 |
| **총계** | **$1,650** | **$7,350** |

---

## 리스크 관리

| 리스크 | 확률 | 영향 | 대응 |
|--------|------|------|------|
| AI API 비용 초과 | 높음 | 중간 | 캐싱, 사용량 제한, 대체 API |
| Runway API 장애 | 중간 | 높음 | Pika Labs 백업, 재시도 로직 |
| 영상 품질 미달 | 중간 | 높음 | 템플릿 품질 관리, QA 강화 |
| 일정 지연 | 중간 | 중간 | 스코프 조정, MVP 기능 축소 |
| 보안 이슈 | 낮음 | 높음 | 정기 보안 감사, 펜테스트 |

---

## 마일스톤 체크포인트

```
Week 2  ──── Foundation Complete ────────────────────────────────────────────
              □ 개발 환경 완성
              □ 스테이징 배포 가능

Week 8  ──── MVP Alpha ──────────────────────────────────────────────────────
              □ 전체 플로우 동작
              □ 내부 테스트 시작

Week 14 ──── MVP Beta ───────────────────────────────────────────────────────
              □ 결제 시스템 완성
              □ 베타 테스터 모집

Week 20 ──── Public Launch ──────────────────────────────────────────────────
              □ 프로덕션 배포
              □ 마케팅 시작
```

---

## 다음 단계

1. **즉시**: Phase 0 시작 - 저장소 생성, 환경 설정
2. **이번 주**: 팀 구성 확정, 역할 배분
3. **다음 주**: Sprint 1 킥오프, 일일 스탠드업 시작
