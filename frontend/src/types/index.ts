// User Types
export interface User {
  id: string;
  email: string;
  name: string;
  profile_image?: string;
  plan: "free" | "basic" | "pro" | "enterprise";
  credits: number;
  subscription?: Subscription;
  created_at: string;
}

export interface Subscription {
  plan: string;
  status: "active" | "canceled" | "past_due";
  current_period_end: string;
}

// Product Types
export interface Product {
  id: string;
  name: string;
  model_number: string;
  category: ProductCategory;
  subcategory: string;
  description?: string;
  thumbnail: string;
  images?: string[];
  specs?: Record<string, string>;
  features?: string[];
  released_at: string;
}

export type ProductCategory = "smartphone" | "tv" | "appliance" | "wearable";

export interface ProductCategory {
  id: ProductCategory;
  name: string;
  icon: string;
  count: number;
}

// Template Types
export interface Template {
  id: string;
  name: string;
  description: string;
  category: ProductCategory;
  style: TemplateStyle;
  durations: number[];
  thumbnail: string;
  preview_url: string;
  is_premium: boolean;
  scenes?: TemplateScene[];
}

export type TemplateStyle =
  | "unboxing"
  | "lifestyle"
  | "comparison"
  | "feature"
  | "gaming"
  | "smarthome"
  | "interior"
  | "health";

export interface TemplateScene {
  order: number;
  name: string;
  duration_ratio: number;
  description: string;
}

// Project Types
export interface Project {
  id: string;
  name: string;
  product?: Product;
  template?: Template;
  custom_product_image?: string;
  custom_product_name?: string;
  config: ProjectConfig;
  script?: Script;
  videos: Video[];
  status: ProjectStatus;
  created_at: string;
  updated_at: string;
}

export type ProjectStatus = "draft" | "processing" | "completed" | "failed";

export interface ProjectConfig {
  duration: 15 | 30 | 60;
  tone: ToneType;
  language: Language;
  aspect_ratio?: AspectRatio;
  music_id?: string;
  voice_id?: string;
  include_narration?: boolean;
}

export type ToneType = "premium" | "practical" | "mz";
export type Language = "ko" | "en" | "zh";
export type AspectRatio = "16:9" | "9:16" | "1:1";

// Script Types
export interface Script {
  headline: string;
  subline: string;
  narration: string;
  cta: string;
  scenes?: ScriptScene[];
  alternatives?: {
    headline?: string[];
    subline?: string[];
  };
}

export interface ScriptScene {
  order: number;
  text: string;
  narration: string;
}

// Video Types
export interface Video {
  id: string;
  version: number;
  duration: number;
  aspect_ratio: AspectRatio;
  video_url: string;
  thumbnail_url: string;
  file_size?: number;
  render_time?: number;
  created_at: string;
}

// Generation Types
export interface GenerationJob {
  job_id: string;
  project_id: string;
  status: GenerationStatus;
  progress: number;
  current_step?: GenerationStep;
  steps?: GenerationStepStatus[];
  estimated_remaining?: number;
  video?: Video;
  error?: GenerationError;
}

export type GenerationStatus =
  | "queued"
  | "processing"
  | "completed"
  | "failed";

export type GenerationStep =
  | "script_processing"
  | "image_processing"
  | "video_generation"
  | "video_compositing"
  | "audio_mixing";

export interface GenerationStepStatus {
  name: GenerationStep;
  status: "pending" | "in_progress" | "completed" | "failed";
}

export interface GenerationError {
  code: string;
  message: string;
}

// Payment Types
export interface Payment {
  id: string;
  amount: number;
  currency: string;
  plan: string;
  status: PaymentStatus;
  created_at: string;
}

export type PaymentStatus = "pending" | "completed" | "failed" | "refunded";

// API Response Types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}
