/**
 * Chinese (Simplified) Translations
 */

import type { TranslationKeys } from "./ko";

export const zh: TranslationKeys = {
  // Common
  common: {
    loading: "加载中...",
    error: "发生错误",
    retry: "重试",
    cancel: "取消",
    confirm: "确认",
    save: "保存",
    delete: "删除",
    edit: "编辑",
    close: "关闭",
    search: "搜索",
    filter: "筛选",
    all: "全部",
    back: "返回",
    next: "下一步",
    previous: "上一步",
    submit: "提交",
    download: "下载",
    share: "分享",
    copy: "复制",
  },

  // Navigation
  nav: {
    home: "首页",
    create: "创建视频",
    projects: "我的项目",
    pricing: "定价",
    login: "登录",
    logout: "退出",
    profile: "个人资料",
    settings: "设置",
  },

  // Auth
  auth: {
    login: "登录",
    signup: "注册",
    logout: "退出",
    loginWithGoogle: "使用Google登录",
    loginWithKakao: "使用Kakao登录",
    email: "邮箱",
    password: "密码",
    forgotPassword: "忘记密码？",
    noAccount: "还没有账号？",
    hasAccount: "已有账号？",
    terms: "我同意服务条款",
    privacy: "隐私政策",
  },

  // Landing Page
  landing: {
    hero: {
      title: "三星产品\nAI广告视频生成器",
      subtitle: "只需几次点击即可创建专业广告视频",
      cta: "免费开始",
      demo: "观看演示",
    },
    features: {
      title: "为什么选择SaiAD？",
      ai: {
        title: "AI驱动生成",
        description: "使用最新AI技术自动生成脚本、视频和旁白",
      },
      templates: {
        title: "高级模板",
        description: "专为三星品牌设计的高质量模板",
      },
      export: {
        title: "多平台支持",
        description: "导出到YouTube、Instagram、TikTok等平台",
      },
    },
    howItWorks: {
      title: "使用方法",
      step1: {
        title: "选择产品",
        description: "选择要宣传的三星产品",
      },
      step2: {
        title: "选择模板",
        description: "选择适合您风格的模板",
      },
      step3: {
        title: "AI生成",
        description: "AI自动为您创建视频",
      },
      step4: {
        title: "下载",
        description: "下载完成的视频",
      },
    },
  },

  // Create Flow
  create: {
    title: "创建新视频",
    steps: {
      product: "选择产品",
      template: "选择模板",
      customize: "自定义",
      result: "结果",
    },
    product: {
      title: "选择要宣传的产品",
      search: "按产品名称搜索...",
      categories: {
        all: "全部",
        smartphone: "智能手机",
        tv: "电视",
        appliance: "家电",
        wearable: "穿戴设备",
        tablet: "平板电脑",
        audio: "音频",
      },
      upload: "上传产品图片",
      uploadHint: "AI会自动从图片中识别产品",
    },
    template: {
      title: "选择模板",
      duration: "视频时长",
      styles: {
        unboxing: "开箱",
        feature: "功能介绍",
        lifestyle: "生活方式",
        comparison: "对比",
        review: "评测",
      },
    },
    customize: {
      title: "自定义您的视频",
      script: "脚本",
      regenerate: "重新生成",
      tone: "风格",
      tones: {
        premium: "高端",
        practical: "实用",
        mz: "年轻化",
      },
      voice: "AI配音",
      selectVoice: "选择声音",
      preview: "预览",
      music: "背景音乐",
      selectMusic: "选择音乐",
    },
    result: {
      title: "您的视频已准备好！",
      generating: "正在生成视频...",
      progress: "进度",
      steps: {
        script: "处理脚本",
        audio: "生成旁白",
        music: "选择音乐",
        video: "生成视频",
        composite: "合成",
        export: "最终导出",
      },
      download: "下载",
      formats: {
        youtube: "YouTube",
        instagram: "Instagram",
        tiktok: "TikTok",
        coupang: "Coupang广告",
      },
    },
  },

  // Projects
  projects: {
    title: "我的项目",
    empty: "暂无项目",
    emptyHint: "创建您的第一个视频！",
    createNew: "创建新视频",
    status: {
      draft: "草稿",
      processing: "处理中",
      completed: "已完成",
      failed: "失败",
    },
    actions: {
      edit: "编辑",
      duplicate: "复制",
      delete: "删除",
      download: "下载",
    },
  },

  // Pricing
  pricing: {
    title: "定价",
    subtitle: "选择适合您的方案",
    monthly: "月付",
    yearly: "年付",
    yearlyDiscount: "8折",
    currentPlan: "当前方案",
    upgrade: "升级",
    startFree: "免费开始",
    contactUs: "联系我们",
    features: {
      videos: "每月{count}个视频",
      duration: "{seconds}秒视频",
      resolution: "{resolution}分辨率",
      templates: "模板",
      narration: "AI配音",
      multilingual: "多语言",
      abtest: "A/B测试",
      support: "支持",
    },
    plans: {
      free: {
        name: "免费版",
        description: "体验AI视频广告",
      },
      basic: {
        name: "基础版",
        description: "适合个人创作者",
      },
      pro: {
        name: "专业版",
        description: "适合专业营销人员",
      },
      enterprise: {
        name: "企业版",
        description: "适合企业客户",
      },
    },
  },

  // Errors
  errors: {
    notFound: "页面未找到",
    unauthorized: "请先登录",
    forbidden: "访问被拒绝",
    serverError: "服务器错误",
    networkError: "请检查网络连接",
    paymentFailed: "支付失败",
    insufficientCredits: "积分不足",
  },

  // Success Messages
  success: {
    saved: "保存成功",
    deleted: "删除成功",
    copied: "已复制到剪贴板",
    downloaded: "开始下载",
    paymentComplete: "支付完成",
  },
};
