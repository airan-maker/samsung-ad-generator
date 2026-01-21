/**
 * Korean Translations
 */

export const ko = {
  // Common
  common: {
    loading: "로딩 중...",
    error: "오류가 발생했습니다",
    retry: "다시 시도",
    cancel: "취소",
    confirm: "확인",
    save: "저장",
    delete: "삭제",
    edit: "편집",
    close: "닫기",
    search: "검색",
    filter: "필터",
    all: "전체",
    back: "뒤로",
    next: "다음",
    previous: "이전",
    submit: "제출",
    download: "다운로드",
    share: "공유",
    copy: "복사",
  },

  // Navigation
  nav: {
    home: "홈",
    create: "영상 만들기",
    projects: "내 프로젝트",
    pricing: "요금제",
    login: "로그인",
    logout: "로그아웃",
    profile: "프로필",
    settings: "설정",
  },

  // Auth
  auth: {
    login: "로그인",
    signup: "회원가입",
    logout: "로그아웃",
    loginWithGoogle: "Google로 로그인",
    loginWithKakao: "카카오로 로그인",
    email: "이메일",
    password: "비밀번호",
    forgotPassword: "비밀번호 찾기",
    noAccount: "계정이 없으신가요?",
    hasAccount: "이미 계정이 있으신가요?",
    terms: "이용약관에 동의합니다",
    privacy: "개인정보처리방침",
  },

  // Landing Page
  landing: {
    hero: {
      title: "삼성 제품을 위한\nAI 광고 영상 생성기",
      subtitle: "몇 번의 클릭만으로 프로페셔널한 광고 영상을 만드세요",
      cta: "무료로 시작하기",
      demo: "데모 보기",
    },
    features: {
      title: "왜 SaiAD인가요?",
      ai: {
        title: "AI 기반 자동 생성",
        description: "최신 AI 기술로 스크립트, 영상, 나레이션을 자동 생성합니다",
      },
      templates: {
        title: "프리미엄 템플릿",
        description: "삼성 브랜드에 맞는 고품질 템플릿을 제공합니다",
      },
      export: {
        title: "다양한 플랫폼 지원",
        description: "유튜브, 인스타그램, 틱톡 등 다양한 형식으로 내보내기",
      },
    },
    howItWorks: {
      title: "이렇게 사용하세요",
      step1: {
        title: "제품 선택",
        description: "광고할 삼성 제품을 선택하세요",
      },
      step2: {
        title: "템플릿 선택",
        description: "스타일에 맞는 템플릿을 고르세요",
      },
      step3: {
        title: "AI가 생성",
        description: "AI가 자동으로 영상을 만들어줍니다",
      },
      step4: {
        title: "다운로드",
        description: "완성된 영상을 다운로드하세요",
      },
    },
  },

  // Create Flow
  create: {
    title: "새 영상 만들기",
    steps: {
      product: "제품 선택",
      template: "템플릿 선택",
      customize: "커스터마이징",
      result: "결과",
    },
    product: {
      title: "광고할 제품을 선택하세요",
      search: "제품명으로 검색...",
      categories: {
        all: "전체",
        smartphone: "스마트폰",
        tv: "TV",
        appliance: "가전",
        wearable: "웨어러블",
        tablet: "태블릿",
        audio: "오디오",
      },
      upload: "제품 이미지 업로드",
      uploadHint: "이미지를 업로드하면 AI가 자동으로 제품을 인식합니다",
    },
    template: {
      title: "템플릿을 선택하세요",
      duration: "영상 길이",
      styles: {
        unboxing: "언박싱",
        feature: "기능 소개",
        lifestyle: "라이프스타일",
        comparison: "비교",
        review: "리뷰",
      },
    },
    customize: {
      title: "영상을 커스터마이징하세요",
      script: "스크립트",
      regenerate: "다시 생성",
      tone: "톤앤매너",
      tones: {
        premium: "프리미엄",
        practical: "실용적",
        mz: "MZ세대",
      },
      voice: "AI 음성",
      selectVoice: "음성 선택",
      preview: "미리듣기",
      music: "배경음악",
      selectMusic: "음악 선택",
    },
    result: {
      title: "영상이 생성되었습니다!",
      generating: "영상 생성 중...",
      progress: "진행률",
      steps: {
        script: "스크립트 처리",
        audio: "나레이션 생성",
        music: "배경음악 선택",
        video: "영상 생성",
        composite: "영상 합성",
        export: "최종 내보내기",
      },
      download: "다운로드",
      formats: {
        youtube: "YouTube",
        instagram: "Instagram",
        tiktok: "TikTok",
        coupang: "쿠팡 광고",
      },
    },
  },

  // Projects
  projects: {
    title: "내 프로젝트",
    empty: "프로젝트가 없습니다",
    emptyHint: "새 영상을 만들어보세요!",
    createNew: "새 영상 만들기",
    status: {
      draft: "초안",
      processing: "생성 중",
      completed: "완료",
      failed: "실패",
    },
    actions: {
      edit: "편집",
      duplicate: "복제",
      delete: "삭제",
      download: "다운로드",
    },
  },

  // Pricing
  pricing: {
    title: "요금제",
    subtitle: "당신에게 맞는 플랜을 선택하세요",
    monthly: "월간 결제",
    yearly: "연간 결제",
    yearlyDiscount: "20% 할인",
    currentPlan: "현재 플랜",
    upgrade: "업그레이드",
    startFree: "무료로 시작",
    contactUs: "문의하기",
    features: {
      videos: "월 {count}회 영상 생성",
      duration: "{seconds}초 영상",
      resolution: "{resolution} 해상도",
      templates: "템플릿",
      narration: "AI 나레이션",
      multilingual: "다국어 지원",
      abtest: "A/B 테스트",
      support: "지원",
    },
    plans: {
      free: {
        name: "무료",
        description: "AI 광고 영상 체험하기",
      },
      basic: {
        name: "Basic",
        description: "개인 크리에이터를 위한",
      },
      pro: {
        name: "Pro",
        description: "전문 마케터를 위한",
      },
      enterprise: {
        name: "Enterprise",
        description: "기업 고객을 위한",
      },
    },
  },

  // Errors
  errors: {
    notFound: "페이지를 찾을 수 없습니다",
    unauthorized: "로그인이 필요합니다",
    forbidden: "접근 권한이 없습니다",
    serverError: "서버 오류가 발생했습니다",
    networkError: "네트워크 연결을 확인해주세요",
    paymentFailed: "결제에 실패했습니다",
    insufficientCredits: "크레딧이 부족합니다",
  },

  // Success Messages
  success: {
    saved: "저장되었습니다",
    deleted: "삭제되었습니다",
    copied: "복사되었습니다",
    downloaded: "다운로드가 시작됩니다",
    paymentComplete: "결제가 완료되었습니다",
  },
};

export type TranslationKeys = typeof ko;
