/**
 * English Translations
 */

import type { TranslationKeys } from "./ko";

export const en: TranslationKeys = {
  // Common
  common: {
    loading: "Loading...",
    error: "An error occurred",
    retry: "Retry",
    cancel: "Cancel",
    confirm: "Confirm",
    save: "Save",
    delete: "Delete",
    edit: "Edit",
    close: "Close",
    search: "Search",
    filter: "Filter",
    all: "All",
    back: "Back",
    next: "Next",
    previous: "Previous",
    submit: "Submit",
    download: "Download",
    share: "Share",
    copy: "Copy",
  },

  // Navigation
  nav: {
    home: "Home",
    create: "Create Video",
    projects: "My Projects",
    pricing: "Pricing",
    login: "Login",
    logout: "Logout",
    profile: "Profile",
    settings: "Settings",
  },

  // Auth
  auth: {
    login: "Login",
    signup: "Sign Up",
    logout: "Logout",
    loginWithGoogle: "Continue with Google",
    loginWithKakao: "Continue with Kakao",
    email: "Email",
    password: "Password",
    forgotPassword: "Forgot Password?",
    noAccount: "Don't have an account?",
    hasAccount: "Already have an account?",
    terms: "I agree to the Terms of Service",
    privacy: "Privacy Policy",
  },

  // Landing Page
  landing: {
    hero: {
      title: "AI Video Ad Generator\nfor Samsung Products",
      subtitle: "Create professional ad videos with just a few clicks",
      cta: "Start for Free",
      demo: "Watch Demo",
    },
    features: {
      title: "Why SaiAD?",
      ai: {
        title: "AI-Powered Generation",
        description: "Automatically generate scripts, videos, and narration with latest AI technology",
      },
      templates: {
        title: "Premium Templates",
        description: "High-quality templates designed for Samsung brand",
      },
      export: {
        title: "Multi-Platform Support",
        description: "Export to YouTube, Instagram, TikTok, and more",
      },
    },
    howItWorks: {
      title: "How It Works",
      step1: {
        title: "Select Product",
        description: "Choose the Samsung product to advertise",
      },
      step2: {
        title: "Choose Template",
        description: "Pick a template that fits your style",
      },
      step3: {
        title: "AI Generates",
        description: "AI automatically creates your video",
      },
      step4: {
        title: "Download",
        description: "Download the finished video",
      },
    },
  },

  // Create Flow
  create: {
    title: "Create New Video",
    steps: {
      product: "Select Product",
      template: "Choose Template",
      customize: "Customize",
      result: "Result",
    },
    product: {
      title: "Select the product to advertise",
      search: "Search by product name...",
      categories: {
        all: "All",
        smartphone: "Smartphones",
        tv: "TVs",
        appliance: "Appliances",
        wearable: "Wearables",
        tablet: "Tablets",
        audio: "Audio",
      },
      upload: "Upload Product Image",
      uploadHint: "AI will automatically recognize the product from your image",
    },
    template: {
      title: "Choose a template",
      duration: "Video Duration",
      styles: {
        unboxing: "Unboxing",
        feature: "Feature Highlight",
        lifestyle: "Lifestyle",
        comparison: "Comparison",
        review: "Review",
      },
    },
    customize: {
      title: "Customize your video",
      script: "Script",
      regenerate: "Regenerate",
      tone: "Tone & Manner",
      tones: {
        premium: "Premium",
        practical: "Practical",
        mz: "Gen Z",
      },
      voice: "AI Voice",
      selectVoice: "Select Voice",
      preview: "Preview",
      music: "Background Music",
      selectMusic: "Select Music",
    },
    result: {
      title: "Your video is ready!",
      generating: "Generating video...",
      progress: "Progress",
      steps: {
        script: "Processing Script",
        audio: "Generating Narration",
        music: "Selecting Music",
        video: "Generating Video",
        composite: "Compositing",
        export: "Final Export",
      },
      download: "Download",
      formats: {
        youtube: "YouTube",
        instagram: "Instagram",
        tiktok: "TikTok",
        coupang: "Coupang Ads",
      },
    },
  },

  // Projects
  projects: {
    title: "My Projects",
    empty: "No projects yet",
    emptyHint: "Create your first video!",
    createNew: "Create New Video",
    status: {
      draft: "Draft",
      processing: "Processing",
      completed: "Completed",
      failed: "Failed",
    },
    actions: {
      edit: "Edit",
      duplicate: "Duplicate",
      delete: "Delete",
      download: "Download",
    },
  },

  // Pricing
  pricing: {
    title: "Pricing",
    subtitle: "Choose the plan that's right for you",
    monthly: "Monthly",
    yearly: "Yearly",
    yearlyDiscount: "20% off",
    currentPlan: "Current Plan",
    upgrade: "Upgrade",
    startFree: "Start Free",
    contactUs: "Contact Us",
    features: {
      videos: "{count} videos per month",
      duration: "{seconds}s videos",
      resolution: "{resolution} resolution",
      templates: "Templates",
      narration: "AI Narration",
      multilingual: "Multi-language",
      abtest: "A/B Testing",
      support: "Support",
    },
    plans: {
      free: {
        name: "Free",
        description: "Try AI video ads",
      },
      basic: {
        name: "Basic",
        description: "For individual creators",
      },
      pro: {
        name: "Pro",
        description: "For professional marketers",
      },
      enterprise: {
        name: "Enterprise",
        description: "For business customers",
      },
    },
  },

  // Errors
  errors: {
    notFound: "Page not found",
    unauthorized: "Please log in",
    forbidden: "Access denied",
    serverError: "Server error occurred",
    networkError: "Please check your network connection",
    paymentFailed: "Payment failed",
    insufficientCredits: "Insufficient credits",
  },

  // Success Messages
  success: {
    saved: "Saved successfully",
    deleted: "Deleted successfully",
    copied: "Copied to clipboard",
    downloaded: "Download started",
    paymentComplete: "Payment completed",
  },
};
