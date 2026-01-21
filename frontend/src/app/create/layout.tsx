"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Check } from "lucide-react";

const steps = [
  { id: "product", name: "제품 선택", href: "/create/product" },
  { id: "template", name: "템플릿 선택", href: "/create/template" },
  { id: "customize", name: "커스터마이징", href: "/create/customize" },
  { id: "result", name: "완료", href: "/create/result" },
];

export default function CreateLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  const currentStepIndex = steps.findIndex((step) => pathname.includes(step.id));

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <Link href="/" className="text-2xl font-bold text-samsung-blue">
              SaiAd
            </Link>
            <Link
              href="/"
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              나가기
            </Link>
          </div>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="border-b bg-white">
        <div className="mx-auto max-w-3xl px-4 py-6 sm:px-6 lg:px-8">
          <nav aria-label="Progress">
            <ol className="flex items-center justify-between">
              {steps.map((step, index) => {
                const isCompleted = index < currentStepIndex;
                const isCurrent = index === currentStepIndex;

                return (
                  <li key={step.id} className="relative flex-1">
                    {index !== 0 && (
                      <div
                        className={cn(
                          "absolute left-0 top-4 -ml-px h-0.5 w-full -translate-x-1/2",
                          isCompleted ? "bg-samsung-blue" : "bg-gray-200"
                        )}
                        style={{ width: "calc(100% - 2rem)", left: "-50%" }}
                      />
                    )}
                    <div className="relative flex flex-col items-center">
                      <span
                        className={cn(
                          "flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium",
                          isCompleted
                            ? "bg-samsung-blue text-white"
                            : isCurrent
                            ? "border-2 border-samsung-blue bg-white text-samsung-blue"
                            : "border-2 border-gray-300 bg-white text-gray-500"
                        )}
                      >
                        {isCompleted ? (
                          <Check className="h-5 w-5" />
                        ) : (
                          index + 1
                        )}
                      </span>
                      <span
                        className={cn(
                          "mt-2 text-xs font-medium",
                          isCurrent ? "text-samsung-blue" : "text-gray-500"
                        )}
                      >
                        {step.name}
                      </span>
                    </div>
                  </li>
                );
              })}
            </ol>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
