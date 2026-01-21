"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useDropzone } from "react-dropzone";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useProjectStore } from "@/stores/projectStore";
import { Search, Upload, Smartphone, Tv, Home, Watch, ArrowRight, X } from "lucide-react";
import type { Product, ProductCategory } from "@/types";

// Mock data - will be replaced with API call
const mockProducts: Product[] = [
  {
    id: "1",
    name: "Galaxy S25 Ultra",
    model_number: "SM-S928N",
    category: "smartphone",
    subcategory: "flagship",
    thumbnail: "/products/s25-ultra.jpg",
    released_at: "2025-01-22",
  },
  {
    id: "2",
    name: "Galaxy Z Fold 6",
    model_number: "SM-F956N",
    category: "smartphone",
    subcategory: "foldable",
    thumbnail: "/products/z-fold6.jpg",
    released_at: "2024-07-10",
  },
  {
    id: "3",
    name: "Galaxy Z Flip 6",
    model_number: "SM-F741N",
    category: "smartphone",
    subcategory: "foldable",
    thumbnail: "/products/z-flip6.jpg",
    released_at: "2024-07-10",
  },
  {
    id: "4",
    name: "Neo QLED 8K QN900D",
    model_number: "QN85QN900D",
    category: "tv",
    subcategory: "neo-qled",
    thumbnail: "/products/qn900d.jpg",
    released_at: "2024-03-01",
  },
  {
    id: "5",
    name: "비스포크 냉장고 4도어",
    model_number: "RF85B9121AP",
    category: "appliance",
    subcategory: "refrigerator",
    thumbnail: "/products/bespoke-ref.jpg",
    released_at: "2024-01-15",
  },
  {
    id: "6",
    name: "Galaxy Watch 7",
    model_number: "SM-R960",
    category: "wearable",
    subcategory: "watch",
    thumbnail: "/products/watch7.jpg",
    released_at: "2024-07-10",
  },
] as Product[];

const categories = [
  { id: "all", name: "전체", icon: null },
  { id: "smartphone", name: "스마트폰", icon: Smartphone },
  { id: "tv", name: "TV", icon: Tv },
  { id: "appliance", name: "가전", icon: Home },
  { id: "wearable", name: "웨어러블", icon: Watch },
];

export default function ProductSelectionPage() {
  const router = useRouter();
  const { setProduct, setCustomProduct, selectedProduct, customProductImage } = useProjectStore();

  const [selectedCategory, setSelectedCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [uploadedImage, setUploadedImage] = useState<string | null>(customProductImage);
  const [customName, setCustomName] = useState("");

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      "image/*": [".jpeg", ".jpg", ".png", ".webp"],
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      const file = acceptedFiles[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = () => {
          setUploadedImage(reader.result as string);
          setProduct(null); // Clear selected product when uploading
        };
        reader.readAsDataURL(file);
      }
    },
  });

  const filteredProducts = mockProducts.filter((product) => {
    const matchesCategory =
      selectedCategory === "all" || product.category === selectedCategory;
    const matchesSearch =
      product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      product.model_number.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const handleProductSelect = (product: Product) => {
    setProduct(product);
    setUploadedImage(null);
  };

  const handleClearUpload = () => {
    setUploadedImage(null);
    setCustomName("");
  };

  const handleNext = () => {
    if (uploadedImage && customName) {
      setCustomProduct(uploadedImage, customName);
    }
    router.push("/create/template");
  };

  const canProceed = selectedProduct || (uploadedImage && customName);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">제품 선택</h1>
        <p className="mt-2 text-gray-600">
          광고를 만들 삼성 제품을 선택하거나 이미지를 직접 업로드하세요
        </p>
      </div>

      <Tabs defaultValue="select" className="w-full">
        <TabsList className="mx-auto grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="select">제품 선택</TabsTrigger>
          <TabsTrigger value="upload">직접 업로드</TabsTrigger>
        </TabsList>

        {/* Product Selection Tab */}
        <TabsContent value="select" className="mt-6">
          {/* Search and Filter */}
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            {/* Category Filter */}
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={cn(
                    "inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-colors",
                    selectedCategory === category.id
                      ? "bg-samsung-blue text-white"
                      : "bg-white text-gray-600 hover:bg-gray-100"
                  )}
                >
                  {category.icon && <category.icon className="h-4 w-4" />}
                  {category.name}
                </button>
              ))}
            </div>

            {/* Search */}
            <div className="relative w-full sm:w-64">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <Input
                placeholder="제품명 또는 모델명 검색"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* Product Grid */}
          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filteredProducts.map((product) => (
              <Card
                key={product.id}
                className={cn(
                  "cursor-pointer overflow-hidden transition-all hover:shadow-lg",
                  selectedProduct?.id === product.id &&
                    "ring-2 ring-samsung-blue"
                )}
                onClick={() => handleProductSelect(product)}
              >
                <div className="aspect-square bg-gray-100 relative">
                  {/* Placeholder for product image */}
                  <div className="absolute inset-0 flex items-center justify-center text-6xl">
                    {product.category === "smartphone" && "📱"}
                    {product.category === "tv" && "📺"}
                    {product.category === "appliance" && "🏠"}
                    {product.category === "wearable" && "⌚"}
                  </div>
                  {selectedProduct?.id === product.id && (
                    <div className="absolute right-2 top-2">
                      <Badge variant="default">선택됨</Badge>
                    </div>
                  )}
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-gray-900">{product.name}</h3>
                  <p className="text-sm text-gray-500">{product.model_number}</p>
                </div>
              </Card>
            ))}
          </div>

          {filteredProducts.length === 0 && (
            <div className="py-12 text-center">
              <p className="text-gray-500">검색 결과가 없습니다</p>
            </div>
          )}
        </TabsContent>

        {/* Upload Tab */}
        <TabsContent value="upload" className="mt-6">
          <div className="mx-auto max-w-xl">
            {!uploadedImage ? (
              <div
                {...getRootProps()}
                className={cn(
                  "flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-12 transition-colors",
                  isDragActive
                    ? "border-samsung-blue bg-samsung-blue/5"
                    : "border-gray-300 hover:border-samsung-blue"
                )}
              >
                <input {...getInputProps()} />
                <Upload className="h-12 w-12 text-gray-400" />
                <p className="mt-4 text-center text-gray-600">
                  {isDragActive ? (
                    "여기에 드롭하세요"
                  ) : (
                    <>
                      이미지를 드래그하거나{" "}
                      <span className="text-samsung-blue">클릭하여 업로드</span>
                    </>
                  )}
                </p>
                <p className="mt-2 text-sm text-gray-500">
                  JPG, PNG, WebP (최대 10MB)
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="relative aspect-square overflow-hidden rounded-xl bg-gray-100">
                  <Image
                    src={uploadedImage}
                    alt="업로드된 이미지"
                    fill
                    className="object-contain"
                  />
                  <button
                    onClick={handleClearUpload}
                    className="absolute right-2 top-2 rounded-full bg-black/50 p-1 text-white hover:bg-black/70"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    제품명 입력 *
                  </label>
                  <Input
                    placeholder="예: Galaxy S25 Ultra"
                    value={customName}
                    onChange={(e) => setCustomName(e.target.value)}
                    className="mt-1"
                  />
                </div>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>

      {/* Bottom Action */}
      <div className="flex justify-end border-t pt-6">
        <Button
          variant="samsung"
          size="lg"
          disabled={!canProceed}
          onClick={handleNext}
        >
          다음 단계
          <ArrowRight className="ml-2 h-5 w-5" />
        </Button>
      </div>
    </div>
  );
}
