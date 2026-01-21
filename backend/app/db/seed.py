"""
Seed data for Samsung Ad Generator
Run with: python -m app.db.seed
"""

import asyncio
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.product import Product, ProductCategory
from app.models.template import Template, TemplateStyle


# Samsung Products Data
PRODUCTS_DATA = [
    # Smartphones
    {
        "name": "Galaxy S25 Ultra",
        "model_number": "SM-S928N",
        "category": ProductCategory.SMARTPHONE,
        "subcategory": "flagship",
        "description": "AI로 더 강력해진 갤럭시 S25 울트라",
        "specs": {
            "display": "6.9인치 Dynamic AMOLED 2X",
            "processor": "Snapdragon 8 Elite",
            "camera": "200MP 광각 + 50MP 초광각 + 10MP 망원 + 50MP 망원",
            "battery": "5000mAh",
            "storage": "256GB / 512GB / 1TB",
        },
        "features": ["Galaxy AI", "S Pen 내장", "45W 초고속 충전", "IP68 방수방진"],
        "images": [
            "https://cdn.saiad.io/products/s25-ultra-1.jpg",
            "https://cdn.saiad.io/products/s25-ultra-2.jpg",
        ],
        "released_at": date(2025, 1, 22),
    },
    {
        "name": "Galaxy S25+",
        "model_number": "SM-S926N",
        "category": ProductCategory.SMARTPHONE,
        "subcategory": "flagship",
        "description": "완벽한 밸런스의 프리미엄 스마트폰",
        "specs": {
            "display": "6.7인치 Dynamic AMOLED 2X",
            "processor": "Snapdragon 8 Elite",
            "camera": "50MP 광각 + 12MP 초광각 + 10MP 망원",
            "battery": "4900mAh",
        },
        "features": ["Galaxy AI", "45W 초고속 충전", "IP68 방수방진"],
        "images": ["https://cdn.saiad.io/products/s25-plus-1.jpg"],
        "released_at": date(2025, 1, 22),
    },
    {
        "name": "Galaxy S25",
        "model_number": "SM-S921N",
        "category": ProductCategory.SMARTPHONE,
        "subcategory": "flagship",
        "description": "컴팩트한 사이즈에 담긴 플래그십 성능",
        "specs": {
            "display": "6.2인치 Dynamic AMOLED 2X",
            "processor": "Snapdragon 8 Elite",
            "camera": "50MP 광각 + 12MP 초광각 + 10MP 망원",
            "battery": "4000mAh",
        },
        "features": ["Galaxy AI", "25W 초고속 충전", "IP68 방수방진"],
        "images": ["https://cdn.saiad.io/products/s25-1.jpg"],
        "released_at": date(2025, 1, 22),
    },
    {
        "name": "Galaxy Z Fold 6",
        "model_number": "SM-F956N",
        "category": ProductCategory.SMARTPHONE,
        "subcategory": "foldable",
        "description": "펼치면 태블릿, 접으면 스마트폰",
        "specs": {
            "main_display": "7.6인치 Dynamic AMOLED 2X",
            "cover_display": "6.3인치 Dynamic AMOLED 2X",
            "processor": "Snapdragon 8 Gen 3",
            "camera": "50MP 광각 + 12MP 초광각 + 10MP 망원",
            "battery": "4400mAh",
        },
        "features": ["Flex Mode", "S Pen 지원", "IPX8 방수"],
        "images": ["https://cdn.saiad.io/products/z-fold6-1.jpg"],
        "released_at": date(2024, 7, 10),
    },
    {
        "name": "Galaxy Z Flip 6",
        "model_number": "SM-F741N",
        "category": ProductCategory.SMARTPHONE,
        "subcategory": "foldable",
        "description": "스타일을 접다",
        "specs": {
            "main_display": "6.7인치 Dynamic AMOLED 2X",
            "cover_display": "3.4인치 Super AMOLED",
            "processor": "Snapdragon 8 Gen 3",
            "camera": "50MP 광각 + 12MP 초광각",
            "battery": "4000mAh",
        },
        "features": ["Flex Mode", "FlexCam", "IPX8 방수"],
        "images": ["https://cdn.saiad.io/products/z-flip6-1.jpg"],
        "released_at": date(2024, 7, 10),
    },
    {
        "name": "Galaxy A55 5G",
        "model_number": "SM-A556N",
        "category": ProductCategory.SMARTPHONE,
        "subcategory": "mid-range",
        "description": "합리적인 가격의 5G 스마트폰",
        "specs": {
            "display": "6.6인치 Super AMOLED",
            "processor": "Exynos 1480",
            "camera": "50MP 광각 + 12MP 초광각 + 5MP 매크로",
            "battery": "5000mAh",
        },
        "features": ["One UI 6", "25W 고속 충전", "IP67 방수방진"],
        "images": ["https://cdn.saiad.io/products/a55-1.jpg"],
        "released_at": date(2024, 3, 11),
    },
    # TVs
    {
        "name": "Neo QLED 8K QN900D",
        "model_number": "QN85QN900D",
        "category": ProductCategory.TV,
        "subcategory": "neo-qled",
        "description": "8K 해상도의 압도적인 화질",
        "specs": {
            "screen_size": "85인치",
            "resolution": "8K (7680 x 4320)",
            "panel": "Neo QLED",
            "hdr": "HDR10+, HLG",
            "refresh_rate": "120Hz",
        },
        "features": ["Neural Quantum 프로세서 8K", "Infinity Screen", "Object Tracking Sound Pro"],
        "images": ["https://cdn.saiad.io/products/qn900d-1.jpg"],
        "released_at": date(2024, 3, 1),
    },
    {
        "name": "Neo QLED 4K QN90D",
        "model_number": "QN65QN90D",
        "category": ProductCategory.TV,
        "subcategory": "neo-qled",
        "description": "선명한 4K Neo QLED",
        "specs": {
            "screen_size": "65인치",
            "resolution": "4K (3840 x 2160)",
            "panel": "Neo QLED",
            "hdr": "HDR10+, HLG",
            "refresh_rate": "144Hz",
        },
        "features": ["Neural Quantum 프로세서 4K", "Anti-Reflection", "Gaming Hub"],
        "images": ["https://cdn.saiad.io/products/qn90d-1.jpg"],
        "released_at": date(2024, 3, 1),
    },
    {
        "name": "OLED S95D",
        "model_number": "QN65S95D",
        "category": ProductCategory.TV,
        "subcategory": "oled",
        "description": "완벽한 블랙과 생생한 컬러",
        "specs": {
            "screen_size": "65인치",
            "resolution": "4K (3840 x 2160)",
            "panel": "QD-OLED",
            "hdr": "HDR10+, HLG",
            "refresh_rate": "144Hz",
        },
        "features": ["Neural Quantum 프로세서 4K", "Dolby Atmos", "4K Gaming"],
        "images": ["https://cdn.saiad.io/products/s95d-1.jpg"],
        "released_at": date(2024, 3, 1),
    },
    {
        "name": "The Frame",
        "model_number": "QN65LS03D",
        "category": ProductCategory.TV,
        "subcategory": "lifestyle",
        "description": "TV가 예술 작품이 되다",
        "specs": {
            "screen_size": "65인치",
            "resolution": "4K (3840 x 2160)",
            "panel": "QLED",
            "hdr": "HDR10+, HLG",
        },
        "features": ["Art Mode", "Matte Display", "커스터마이징 베젤"],
        "images": ["https://cdn.saiad.io/products/frame-1.jpg"],
        "released_at": date(2024, 3, 1),
    },
    # Appliances
    {
        "name": "비스포크 냉장고 4도어",
        "model_number": "RF85B9121AP",
        "category": ProductCategory.APPLIANCE,
        "subcategory": "refrigerator",
        "description": "당신의 주방에 맞춘 맞춤형 냉장고",
        "specs": {
            "capacity": "848L",
            "type": "4도어",
            "energy_grade": "1등급",
            "color_options": "새틴 스카이블루, 코타 화이트 등 20가지",
        },
        "features": ["비스포크 디자인", "메탈쿨링", "정온냉동", "AI 절전"],
        "images": ["https://cdn.saiad.io/products/bespoke-ref-1.jpg"],
        "released_at": date(2024, 1, 15),
    },
    {
        "name": "비스포크 그랑데 세탁기 AI",
        "model_number": "WF24B9600KE",
        "category": ProductCategory.APPLIANCE,
        "subcategory": "washer",
        "description": "AI가 알아서 세탁하는 스마트 세탁기",
        "specs": {
            "capacity": "24kg",
            "motor": "DD 인버터",
            "energy_grade": "1등급",
        },
        "features": ["AI 맞춤세탁", "버블워시", "무세제 통세척", "SmartThings 연동"],
        "images": ["https://cdn.saiad.io/products/bespoke-washer-1.jpg"],
        "released_at": date(2024, 2, 1),
    },
    {
        "name": "비스포크 무풍에어컨 갤러리",
        "model_number": "AF19B9970GFS",
        "category": ProductCategory.APPLIANCE,
        "subcategory": "air-conditioner",
        "description": "바람 없이 시원하게, 그리고 아름답게",
        "specs": {
            "cooling_capacity": "19평형",
            "energy_grade": "1등급",
            "noise_level": "22dB",
        },
        "features": ["무풍냉방", "AI 자동운전", "공기청정 기능", "갤러리 디자인"],
        "images": ["https://cdn.saiad.io/products/bespoke-ac-1.jpg"],
        "released_at": date(2024, 4, 1),
    },
    {
        "name": "비스포크 큐브 냉장고",
        "model_number": "CRS25T9500",
        "category": ProductCategory.APPLIANCE,
        "subcategory": "refrigerator",
        "description": "나만의 공간에 맞는 작은 냉장고",
        "specs": {
            "capacity": "25L",
            "type": "미니 냉장고",
            "color_options": "8가지 컬러",
        },
        "features": ["비스포크 디자인", "무소음", "스탠드 설치 가능"],
        "images": ["https://cdn.saiad.io/products/cube-1.jpg"],
        "released_at": date(2024, 1, 1),
    },
    # Wearables
    {
        "name": "Galaxy Watch 7",
        "model_number": "SM-R960",
        "category": ProductCategory.WEARABLE,
        "subcategory": "watch",
        "description": "건강을 더 스마트하게 관리하세요",
        "specs": {
            "display": "1.5인치 Super AMOLED",
            "processor": "Exynos W1000",
            "battery": "425mAh",
            "os": "Wear OS 5",
        },
        "features": ["심박수 모니터링", "수면 추적", "체성분 분석", "GPS"],
        "images": ["https://cdn.saiad.io/products/watch7-1.jpg"],
        "released_at": date(2024, 7, 10),
    },
    {
        "name": "Galaxy Watch Ultra",
        "model_number": "SM-R950",
        "category": ProductCategory.WEARABLE,
        "subcategory": "watch",
        "description": "극한의 환경에서도 당신과 함께",
        "specs": {
            "display": "1.5인치 Super AMOLED",
            "processor": "Exynos W1000",
            "battery": "590mAh",
            "durability": "10ATM, MIL-STD-810H",
        },
        "features": ["듀얼 GPS", "100시간 배터리", "티타늄 프레임", "긴급 사이렌"],
        "images": ["https://cdn.saiad.io/products/watch-ultra-1.jpg"],
        "released_at": date(2024, 7, 10),
    },
    {
        "name": "Galaxy Buds 3 Pro",
        "model_number": "SM-R630",
        "category": ProductCategory.WEARABLE,
        "subcategory": "earbuds",
        "description": "프리미엄 사운드의 완성",
        "specs": {
            "driver": "듀얼 드라이버",
            "anc": "인텔리전트 ANC",
            "battery": "총 30시간",
            "codec": "SSC, AAC, SBC",
        },
        "features": ["360 오디오", "통역 기능", "IP57 방수"],
        "images": ["https://cdn.saiad.io/products/buds3-pro-1.jpg"],
        "released_at": date(2024, 7, 10),
    },
    {
        "name": "Galaxy Ring",
        "model_number": "SM-Q500",
        "category": ProductCategory.WEARABLE,
        "subcategory": "ring",
        "description": "손가락에서 시작되는 건강 관리",
        "specs": {
            "material": "티타늄",
            "battery": "최대 7일",
            "weight": "2.3g (Size 5)",
            "sizes": "5-13",
        },
        "features": ["심박수 모니터링", "수면 추적", "생체 인증", "방수"],
        "images": ["https://cdn.saiad.io/products/ring-1.jpg"],
        "released_at": date(2024, 7, 10),
    },
]

# Templates Data
TEMPLATES_DATA = [
    # Smartphone Templates
    {
        "name": "언박싱 시퀀스",
        "description": "제품 개봉의 설렘을 담은 프리미엄 언박싱 영상",
        "category": ProductCategory.SMARTPHONE,
        "style": TemplateStyle.UNBOXING,
        "durations": [15, 30, 60],
        "thumbnail_url": "https://cdn.saiad.io/templates/unboxing-thumb.jpg",
        "preview_url": "https://cdn.saiad.io/templates/unboxing-preview.mp4",
        "is_premium": False,
        "config": {
            "scenes": [
                {"order": 1, "name": "박스 등장", "duration_ratio": 0.2},
                {"order": 2, "name": "개봉", "duration_ratio": 0.3},
                {"order": 3, "name": "제품 클로즈업", "duration_ratio": 0.3},
                {"order": 4, "name": "CTA", "duration_ratio": 0.2},
            ]
        },
    },
    {
        "name": "카메라 하이라이트",
        "description": "카메라 성능을 극대화하는 시네마틱 영상",
        "category": ProductCategory.SMARTPHONE,
        "style": TemplateStyle.FEATURE,
        "durations": [15, 30, 60],
        "thumbnail_url": "https://cdn.saiad.io/templates/camera-thumb.jpg",
        "preview_url": "https://cdn.saiad.io/templates/camera-preview.mp4",
        "is_premium": False,
        "config": {
            "scenes": [
                {"order": 1, "name": "제품 등장", "duration_ratio": 0.15},
                {"order": 2, "name": "카메라 기능 시연", "duration_ratio": 0.4},
                {"order": 3, "name": "촬영 결과물", "duration_ratio": 0.3},
                {"order": 4, "name": "CTA", "duration_ratio": 0.15},
            ]
        },
    },
    {
        "name": "일상 라이프스타일",
        "description": "제품과 함께하는 일상을 자연스럽게 담은 영상",
        "category": ProductCategory.SMARTPHONE,
        "style": TemplateStyle.LIFESTYLE,
        "durations": [15, 30, 60],
        "thumbnail_url": "https://cdn.saiad.io/templates/lifestyle-thumb.jpg",
        "preview_url": "https://cdn.saiad.io/templates/lifestyle-preview.mp4",
        "is_premium": False,
        "config": {
            "scenes": [
                {"order": 1, "name": "일상 장면", "duration_ratio": 0.35},
                {"order": 2, "name": "제품 사용", "duration_ratio": 0.35},
                {"order": 3, "name": "제품 클로즈업", "duration_ratio": 0.15},
                {"order": 4, "name": "CTA", "duration_ratio": 0.15},
            ]
        },
    },
    {
        "name": "스펙 비교",
        "description": "경쟁 제품과의 비교를 통한 강점 부각",
        "category": ProductCategory.SMARTPHONE,
        "style": TemplateStyle.COMPARISON,
        "durations": [30, 60],
        "thumbnail_url": "https://cdn.saiad.io/templates/comparison-thumb.jpg",
        "preview_url": "https://cdn.saiad.io/templates/comparison-preview.mp4",
        "is_premium": True,
        "config": {
            "scenes": [
                {"order": 1, "name": "비교 인트로", "duration_ratio": 0.15},
                {"order": 2, "name": "스펙 비교", "duration_ratio": 0.5},
                {"order": 3, "name": "결론", "duration_ratio": 0.2},
                {"order": 4, "name": "CTA", "duration_ratio": 0.15},
            ]
        },
    },
    # TV Templates
    {
        "name": "거실 시네마틱",
        "description": "TV가 있는 거실의 프리미엄 분위기를 연출",
        "category": ProductCategory.TV,
        "style": TemplateStyle.LIFESTYLE,
        "durations": [15, 30, 60],
        "thumbnail_url": "https://cdn.saiad.io/templates/living-thumb.jpg",
        "preview_url": "https://cdn.saiad.io/templates/living-preview.mp4",
        "is_premium": False,
        "config": {
            "scenes": [
                {"order": 1, "name": "거실 전경", "duration_ratio": 0.3},
                {"order": 2, "name": "TV 화면", "duration_ratio": 0.4},
                {"order": 3, "name": "제품 디테일", "duration_ratio": 0.15},
                {"order": 4, "name": "CTA", "duration_ratio": 0.15},
            ]
        },
    },
    {
        "name": "게이밍 모드",
        "description": "게이밍 TV의 성능을 극대화한 역동적인 영상",
        "category": ProductCategory.TV,
        "style": TemplateStyle.GAMING,
        "durations": [15, 30],
        "thumbnail_url": "https://cdn.saiad.io/templates/gaming-thumb.jpg",
        "preview_url": "https://cdn.saiad.io/templates/gaming-preview.mp4",
        "is_premium": False,
        "config": {
            "scenes": [
                {"order": 1, "name": "게임 시작", "duration_ratio": 0.2},
                {"order": 2, "name": "게임 플레이", "duration_ratio": 0.5},
                {"order": 3, "name": "성능 스펙", "duration_ratio": 0.15},
                {"order": 4, "name": "CTA", "duration_ratio": 0.15},
            ]
        },
    },
    {
        "name": "화질 비교",
        "description": "압도적인 화질을 보여주는 비교 영상",
        "category": ProductCategory.TV,
        "style": TemplateStyle.COMPARISON,
        "durations": [30, 60],
        "thumbnail_url": "https://cdn.saiad.io/templates/quality-thumb.jpg",
        "preview_url": "https://cdn.saiad.io/templates/quality-preview.mp4",
        "is_premium": True,
        "config": {
            "scenes": [
                {"order": 1, "name": "일반 화질", "duration_ratio": 0.25},
                {"order": 2, "name": "고화질 전환", "duration_ratio": 0.4},
                {"order": 3, "name": "스펙 설명", "duration_ratio": 0.2},
                {"order": 4, "name": "CTA", "duration_ratio": 0.15},
            ]
        },
    },
    # Appliance Templates
    {
        "name": "비스포크 인테리어",
        "description": "주방과 어우러지는 비스포크 가전의 아름다움",
        "category": ProductCategory.APPLIANCE,
        "style": TemplateStyle.INTERIOR,
        "durations": [15, 30, 60],
        "thumbnail_url": "https://cdn.saiad.io/templates/bespoke-thumb.jpg",
        "preview_url": "https://cdn.saiad.io/templates/bespoke-preview.mp4",
        "is_premium": False,
        "config": {
            "scenes": [
                {"order": 1, "name": "주방 전경", "duration_ratio": 0.3},
                {"order": 2, "name": "제품 포커스", "duration_ratio": 0.35},
                {"order": 3, "name": "컬러 옵션", "duration_ratio": 0.2},
                {"order": 4, "name": "CTA", "duration_ratio": 0.15},
            ]
        },
    },
    {
        "name": "기능 시연",
        "description": "제품의 핵심 기능을 명확하게 보여주는 영상",
        "category": ProductCategory.APPLIANCE,
        "style": TemplateStyle.FEATURE,
        "durations": [30, 60],
        "thumbnail_url": "https://cdn.saiad.io/templates/demo-thumb.jpg",
        "preview_url": "https://cdn.saiad.io/templates/demo-preview.mp4",
        "is_premium": False,
        "config": {
            "scenes": [
                {"order": 1, "name": "제품 소개", "duration_ratio": 0.2},
                {"order": 2, "name": "기능 시연 1", "duration_ratio": 0.25},
                {"order": 3, "name": "기능 시연 2", "duration_ratio": 0.25},
                {"order": 4, "name": "스펙 요약", "duration_ratio": 0.15},
                {"order": 5, "name": "CTA", "duration_ratio": 0.15},
            ]
        },
    },
    # Wearable Templates
    {
        "name": "헬스 트래킹",
        "description": "건강 관리 기능을 중심으로 한 역동적인 영상",
        "category": ProductCategory.WEARABLE,
        "style": TemplateStyle.HEALTH,
        "durations": [15, 30],
        "thumbnail_url": "https://cdn.saiad.io/templates/health-thumb.jpg",
        "preview_url": "https://cdn.saiad.io/templates/health-preview.mp4",
        "is_premium": False,
        "config": {
            "scenes": [
                {"order": 1, "name": "운동 장면", "duration_ratio": 0.3},
                {"order": 2, "name": "헬스 데이터", "duration_ratio": 0.35},
                {"order": 3, "name": "제품 클로즈업", "duration_ratio": 0.2},
                {"order": 4, "name": "CTA", "duration_ratio": 0.15},
            ]
        },
    },
    {
        "name": "에코시스템 연동",
        "description": "갤럭시 생태계와의 완벽한 연동",
        "category": ProductCategory.WEARABLE,
        "style": TemplateStyle.FEATURE,
        "durations": [30, 60],
        "thumbnail_url": "https://cdn.saiad.io/templates/ecosystem-thumb.jpg",
        "preview_url": "https://cdn.saiad.io/templates/ecosystem-preview.mp4",
        "is_premium": False,
        "config": {
            "scenes": [
                {"order": 1, "name": "기기들 소개", "duration_ratio": 0.2},
                {"order": 2, "name": "연동 시연", "duration_ratio": 0.45},
                {"order": 3, "name": "편의성 강조", "duration_ratio": 0.2},
                {"order": 4, "name": "CTA", "duration_ratio": 0.15},
            ]
        },
    },
]


async def seed_products(db: AsyncSession) -> None:
    """Seed products data."""
    print("Seeding products...")
    for data in PRODUCTS_DATA:
        product = Product(**data)
        db.add(product)
    await db.commit()
    print(f"  Added {len(PRODUCTS_DATA)} products")


async def seed_templates(db: AsyncSession) -> None:
    """Seed templates data."""
    print("Seeding templates...")
    for data in TEMPLATES_DATA:
        template = Template(**data)
        db.add(template)
    await db.commit()
    print(f"  Added {len(TEMPLATES_DATA)} templates")


async def main() -> None:
    """Run all seed functions."""
    print("Starting database seed...")

    async with AsyncSessionLocal() as db:
        try:
            await seed_products(db)
            await seed_templates(db)
            print("\nDatabase seed completed successfully!")
        except Exception as e:
            print(f"\nError during seed: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
