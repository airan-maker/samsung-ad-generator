import axios, { AxiosError, AxiosInstance } from "axios";
import type {
  User,
  Product,
  Template,
  Project,
  Script,
  GenerationJob,
  PaginatedResponse,
  ApiError,
  ProductCategory,
} from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/v1";

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Request interceptor for auth token
    this.client.interceptors.request.use((config) => {
      const token = this.getAccessToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError<ApiError>) => {
        if (error.response?.status === 401) {
          // Try to refresh token
          try {
            await this.refreshToken();
            // Retry the original request
            return this.client.request(error.config!);
          } catch {
            // Redirect to login
            if (typeof window !== "undefined") {
              window.location.href = "/login";
            }
          }
        }
        return Promise.reject(error);
      }
    );
  }

  private getAccessToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  }

  private setAccessToken(token: string): void {
    if (typeof window !== "undefined") {
      localStorage.setItem("access_token", token);
    }
  }

  // Auth
  async loginWithGoogle(code: string, redirectUri: string) {
    const response = await this.client.post("/auth/google", {
      code,
      redirect_uri: redirectUri,
    });
    this.setAccessToken(response.data.access_token);
    return response.data;
  }

  async loginWithKakao(code: string, redirectUri: string) {
    const response = await this.client.post("/auth/kakao", {
      code,
      redirect_uri: redirectUri,
    });
    this.setAccessToken(response.data.access_token);
    return response.data;
  }

  async refreshToken() {
    const response = await this.client.post("/auth/refresh");
    this.setAccessToken(response.data.access_token);
    return response.data;
  }

  async logout() {
    await this.client.delete("/auth/logout");
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
    }
  }

  // Users
  async getCurrentUser(): Promise<User> {
    const response = await this.client.get("/users/me");
    return response.data;
  }

  async updateUser(data: Partial<User>): Promise<User> {
    const response = await this.client.patch("/users/me", data);
    return response.data;
  }

  // Products
  async getProducts(params?: {
    category?: string;
    search?: string;
    page?: number;
    limit?: number;
  }): Promise<PaginatedResponse<Product>> {
    const response = await this.client.get("/products", { params });
    return response.data;
  }

  async getProduct(id: string): Promise<Product> {
    const response = await this.client.get(`/products/${id}`);
    return response.data;
  }

  async getCategories(): Promise<{ categories: ProductCategory[] }> {
    const response = await this.client.get("/products/categories");
    return response.data;
  }

  async recognizeProduct(image: File): Promise<{
    recognized: boolean;
    confidence?: number;
    product?: Product;
    suggestions?: Array<{ id: string; name: string; confidence: number }>;
  }> {
    const formData = new FormData();
    formData.append("image", image);
    const response = await this.client.post("/products/recognize", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  }

  // Templates
  async getTemplates(params?: {
    category?: string;
    style?: string;
  }): Promise<{ items: Template[]; total: number }> {
    const response = await this.client.get("/templates", { params });
    return response.data;
  }

  async getTemplate(id: string): Promise<Template> {
    const response = await this.client.get(`/templates/${id}`);
    return response.data;
  }

  // Projects
  async createProject(data: {
    name: string;
    product_id?: string;
    custom_product_image?: string;
    custom_product_name?: string;
    template_id: string;
    config: {
      duration: number;
      tone: string;
      language: string;
    };
  }): Promise<Project> {
    const response = await this.client.post("/projects", data);
    return response.data;
  }

  async getProjects(params?: {
    status?: string;
    page?: number;
    limit?: number;
  }): Promise<PaginatedResponse<Project>> {
    const response = await this.client.get("/projects", { params });
    return response.data;
  }

  async getProject(id: string): Promise<Project> {
    const response = await this.client.get(`/projects/${id}`);
    return response.data;
  }

  async updateProject(id: string, data: Partial<Project>): Promise<Project> {
    const response = await this.client.patch(`/projects/${id}`, data);
    return response.data;
  }

  async deleteProject(id: string): Promise<void> {
    await this.client.delete(`/projects/${id}`);
  }

  // Scripts
  async generateScript(data: {
    project_id: string;
    tone: string;
    language: string;
    custom_keywords?: string[];
  }): Promise<Script> {
    const response = await this.client.post("/scripts/generate", data);
    return response.data;
  }

  async regenerateScript(data: {
    project_id: string;
    field: string;
    current_value: string;
    instruction?: string;
  }): Promise<{ field: string; value: string; alternatives: string[] }> {
    const response = await this.client.post("/scripts/regenerate", data);
    return response.data;
  }

  // Videos
  async generateVideo(data: {
    project_id: string;
    script: Script;
    config: {
      duration: number;
      aspect_ratio: string;
      music_id?: string;
      voice_id?: string;
      include_narration?: boolean;
    };
  }): Promise<GenerationJob> {
    const response = await this.client.post("/videos/generate", data);
    return response.data;
  }

  async getVideoStatus(jobId: string): Promise<GenerationJob> {
    const response = await this.client.get(`/videos/${jobId}/status`);
    return response.data;
  }

  async getDownloadUrl(
    videoId: string,
    format?: string
  ): Promise<{
    download_url: string;
    expires_at: string;
    format: { name: string; aspect_ratio: string; resolution: string };
  }> {
    const response = await this.client.get(`/videos/${videoId}/download`, {
      params: { format },
    });
    return response.data;
  }

  // Payments
  async subscribe(data: {
    plan: string;
    payment_method: string;
  }): Promise<{ payment_url: string; order_id: string }> {
    const response = await this.client.post("/payments/subscribe", data);
    return response.data;
  }

  async cancelSubscription(): Promise<{ message: string; effective_date: string }> {
    const response = await this.client.post("/payments/cancel");
    return response.data;
  }

  async getPaymentHistory(): Promise<{
    items: Array<{
      id: string;
      amount: number;
      currency: string;
      plan: string;
      status: string;
      created_at: string;
    }>;
    total: number;
  }> {
    const response = await this.client.get("/payments/history");
    return response.data;
  }

  // File Upload
  async uploadFile(file: File, type: "product" | "asset"): Promise<{ url: string }> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("type", type);
    const response = await this.client.post("/uploads", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  }
}

export const api = new ApiClient();
