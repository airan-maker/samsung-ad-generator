"""
Samsung Brand Guidelines Service

Enforces Samsung brand compliance for generated content.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class BrandCheckSeverity(Enum):
    ERROR = "error"      # Must fix before publishing
    WARNING = "warning"  # Should review
    INFO = "info"        # Suggestion


@dataclass
class BrandCheckResult:
    passed: bool
    severity: BrandCheckSeverity
    rule_id: str
    rule_name: str
    message: str
    suggestion: Optional[str] = None
    location: Optional[str] = None


@dataclass
class BrandComplianceReport:
    compliant: bool
    score: int  # 0-100
    checks: List[BrandCheckResult]
    errors: int
    warnings: int


# Samsung Brand Colors (Official)
SAMSUNG_COLORS = {
    "primary": {
        "samsung_blue": "#1428A0",
        "white": "#FFFFFF",
        "black": "#000000",
    },
    "secondary": {
        "gray_100": "#F4F4F4",
        "gray_200": "#E8E8E8",
        "gray_300": "#CCCCCC",
        "gray_500": "#888888",
        "gray_700": "#555555",
        "gray_900": "#222222",
    },
    "accent": {
        "light_blue": "#4A90D9",
        "success_green": "#00A651",
        "warning_orange": "#FF9500",
        "error_red": "#E60012",
    },
}

# Samsung Typography Guidelines
SAMSUNG_FONTS = {
    "primary": ["Samsung One", "SamsungOne"],
    "fallback": ["Noto Sans KR", "Roboto", "Arial", "sans-serif"],
    "weights": {
        "regular": 400,
        "medium": 500,
        "bold": 700,
    },
}

# Logo Usage Rules
LOGO_RULES = {
    "min_clear_space": 20,  # pixels
    "min_size": 40,  # pixels height
    "position": ["bottom_right", "bottom_left", "top_right"],
    "background_contrast": 0.4,  # minimum contrast ratio difference
}

# Prohibited Terms and Phrases
PROHIBITED_TERMS = [
    r"\b(최고|최상|최대|최초|세계 최초)\b",  # Superlatives requiring proof
    r"\b(무료|공짜|0원)\b",  # Free claims in ads
    r"\b(보장|보증)\b",  # Guarantee claims
    r"\b(경쟁사|삼성 vs|애플|LG|소니)\b",  # Competitor mentions
]

# Required Elements
REQUIRED_ELEMENTS = {
    "logo": True,
    "product_name": True,
    "call_to_action": True,
}


class BrandGuidelinesService:
    """Service for checking Samsung brand compliance."""

    def __init__(self):
        pass

    def check_script_compliance(
        self,
        script: Dict[str, Any],
    ) -> BrandComplianceReport:
        """
        Check script content for brand compliance.

        Args:
            script: Generated script to check

        Returns:
            BrandComplianceReport with all checks
        """
        checks = []

        # Extract all text from script
        all_text = self._extract_script_text(script)

        # Check for prohibited terms
        checks.extend(self._check_prohibited_terms(all_text))

        # Check for required elements
        checks.extend(self._check_required_elements(script))

        # Check tone and messaging
        checks.extend(self._check_tone(script))

        # Calculate compliance score
        errors = sum(1 for c in checks if c.severity == BrandCheckSeverity.ERROR)
        warnings = sum(1 for c in checks if c.severity == BrandCheckSeverity.WARNING)

        # Score: start at 100, -20 per error, -5 per warning
        score = max(0, 100 - (errors * 20) - (warnings * 5))

        return BrandComplianceReport(
            compliant=errors == 0,
            score=score,
            checks=checks,
            errors=errors,
            warnings=warnings,
        )

    def check_video_compliance(
        self,
        video_config: Dict[str, Any],
    ) -> BrandComplianceReport:
        """
        Check video configuration for brand compliance.

        Args:
            video_config: Video generation config

        Returns:
            BrandComplianceReport
        """
        checks = []

        # Check colors
        checks.extend(self._check_colors(video_config.get("colors", {})))

        # Check fonts
        checks.extend(self._check_fonts(video_config.get("fonts", {})))

        # Check logo usage
        checks.extend(self._check_logo(video_config.get("logo", {})))

        # Calculate score
        errors = sum(1 for c in checks if c.severity == BrandCheckSeverity.ERROR)
        warnings = sum(1 for c in checks if c.severity == BrandCheckSeverity.WARNING)
        score = max(0, 100 - (errors * 20) - (warnings * 5))

        return BrandComplianceReport(
            compliant=errors == 0,
            score=score,
            checks=checks,
            errors=errors,
            warnings=warnings,
        )

    def _extract_script_text(self, script: Dict[str, Any]) -> str:
        """Extract all text content from script."""
        texts = []

        if script.get("title"):
            texts.append(script["title"])

        if script.get("headline"):
            texts.append(script["headline"])

        if script.get("subheadline"):
            texts.append(script["subheadline"])

        for scene in script.get("scenes", []):
            if scene.get("narration"):
                texts.append(scene["narration"])
            if scene.get("visual_description"):
                texts.append(scene["visual_description"])

        return " ".join(texts)

    def _check_prohibited_terms(self, text: str) -> List[BrandCheckResult]:
        """Check for prohibited terms in text."""
        checks = []

        for pattern in PROHIBITED_TERMS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                checks.append(
                    BrandCheckResult(
                        passed=False,
                        severity=BrandCheckSeverity.WARNING,
                        rule_id="prohibited_term",
                        rule_name="금지어 검사",
                        message=f"주의가 필요한 표현이 발견되었습니다: {', '.join(set(matches))}",
                        suggestion="광고법상 입증이 필요한 표현입니다. 객관적인 표현으로 수정을 권장합니다.",
                    )
                )

        if not checks:
            checks.append(
                BrandCheckResult(
                    passed=True,
                    severity=BrandCheckSeverity.INFO,
                    rule_id="prohibited_term",
                    rule_name="금지어 검사",
                    message="금지어가 발견되지 않았습니다.",
                )
            )

        return checks

    def _check_required_elements(
        self,
        script: Dict[str, Any],
    ) -> List[BrandCheckResult]:
        """Check for required elements in script."""
        checks = []

        # Check for product name mention
        title = script.get("title", "")
        has_product_name = any(
            keyword in title.lower()
            for keyword in ["galaxy", "samsung", "비스포크", "bespoke"]
        )

        if not has_product_name:
            checks.append(
                BrandCheckResult(
                    passed=False,
                    severity=BrandCheckSeverity.WARNING,
                    rule_id="product_name",
                    rule_name="제품명 포함",
                    message="제목에 제품명 또는 브랜드명이 포함되지 않았습니다.",
                    suggestion="Galaxy, Samsung 등의 브랜드 키워드를 제목에 포함시키세요.",
                )
            )

        # Check for call to action
        all_text = self._extract_script_text(script).lower()
        cta_keywords = ["지금", "만나보세요", "경험하세요", "확인하세요", "구매", "바로"]
        has_cta = any(kw in all_text for kw in cta_keywords)

        if not has_cta:
            checks.append(
                BrandCheckResult(
                    passed=False,
                    severity=BrandCheckSeverity.INFO,
                    rule_id="call_to_action",
                    rule_name="행동 유도 문구",
                    message="명확한 행동 유도 문구(CTA)가 포함되지 않았습니다.",
                    suggestion="'지금 만나보세요', '자세히 알아보기' 등의 CTA를 추가하세요.",
                )
            )

        return checks

    def _check_tone(self, script: Dict[str, Any]) -> List[BrandCheckResult]:
        """Check script tone matches Samsung brand voice."""
        checks = []

        # Samsung brand voice should be:
        # - Professional but approachable
        # - Innovative and forward-thinking
        # - Premium without being elitist

        all_text = self._extract_script_text(script).lower()

        # Check for overly casual language
        casual_patterns = [
            r"\b(ㅋㅋ|ㅎㅎ|헐|대박|쩐다)\b",
            r"[!?]{2,}",  # Multiple exclamation/question marks
        ]

        for pattern in casual_patterns:
            if re.search(pattern, all_text):
                checks.append(
                    BrandCheckResult(
                        passed=False,
                        severity=BrandCheckSeverity.INFO,
                        rule_id="tone_casual",
                        rule_name="톤앤매너 검사",
                        message="비격식적인 표현이 발견되었습니다.",
                        suggestion="삼성 브랜드 가이드라인에 맞는 전문적인 톤을 유지하세요.",
                    )
                )
                break

        return checks

    def _check_colors(self, colors: Dict[str, str]) -> List[BrandCheckResult]:
        """Check color compliance with Samsung brand."""
        checks = []

        primary_color = colors.get("primary", "").lower()

        # Check if primary color is Samsung Blue
        if primary_color and primary_color != "#1428a0":
            checks.append(
                BrandCheckResult(
                    passed=False,
                    severity=BrandCheckSeverity.WARNING,
                    rule_id="color_primary",
                    rule_name="브랜드 컬러",
                    message=f"기본 색상({primary_color})이 삼성 블루(#1428A0)와 다릅니다.",
                    suggestion="삼성 브랜드 컬러 가이드라인을 확인하세요.",
                )
            )

        return checks

    def _check_fonts(self, fonts: Dict[str, str]) -> List[BrandCheckResult]:
        """Check font compliance with Samsung brand."""
        checks = []

        primary_font = fonts.get("primary", "")

        if primary_font and primary_font not in SAMSUNG_FONTS["primary"]:
            checks.append(
                BrandCheckResult(
                    passed=False,
                    severity=BrandCheckSeverity.INFO,
                    rule_id="font_primary",
                    rule_name="브랜드 폰트",
                    message=f"사용된 폰트({primary_font})가 삼성 공식 폰트가 아닙니다.",
                    suggestion="Samsung One 폰트 사용을 권장합니다.",
                )
            )

        return checks

    def _check_logo(self, logo_config: Dict[str, Any]) -> List[BrandCheckResult]:
        """Check logo usage compliance."""
        checks = []

        position = logo_config.get("position", "")
        if position and position not in LOGO_RULES["position"]:
            checks.append(
                BrandCheckResult(
                    passed=False,
                    severity=BrandCheckSeverity.WARNING,
                    rule_id="logo_position",
                    rule_name="로고 위치",
                    message=f"로고 위치({position})가 가이드라인과 다릅니다.",
                    suggestion="로고는 하단 우측, 하단 좌측, 또는 상단 우측에 배치하세요.",
                )
            )

        size = logo_config.get("size", 0)
        if size and size < LOGO_RULES["min_size"]:
            checks.append(
                BrandCheckResult(
                    passed=False,
                    severity=BrandCheckSeverity.ERROR,
                    rule_id="logo_size",
                    rule_name="로고 크기",
                    message=f"로고 크기({size}px)가 최소 기준({LOGO_RULES['min_size']}px) 미만입니다.",
                    suggestion=f"로고 높이를 최소 {LOGO_RULES['min_size']}px 이상으로 설정하세요.",
                )
            )

        return checks

    def get_brand_config(self) -> Dict[str, Any]:
        """Get Samsung brand configuration for video generation."""
        return {
            "colors": SAMSUNG_COLORS,
            "fonts": SAMSUNG_FONTS,
            "logo": {
                "rules": LOGO_RULES,
                "default_position": "bottom_right",
                "watermark_opacity": 0.8,
            },
            "guidelines_url": "https://www.samsung.com/global/brand/guidelines/",
        }


def check_brand_compliance(
    script: Optional[Dict[str, Any]] = None,
    video_config: Optional[Dict[str, Any]] = None,
) -> BrandComplianceReport:
    """
    Convenience function to check brand compliance.

    Args:
        script: Script to check
        video_config: Video config to check

    Returns:
        Combined BrandComplianceReport
    """
    service = BrandGuidelinesService()
    all_checks = []

    if script:
        report = service.check_script_compliance(script)
        all_checks.extend(report.checks)

    if video_config:
        report = service.check_video_compliance(video_config)
        all_checks.extend(report.checks)

    errors = sum(1 for c in all_checks if c.severity == BrandCheckSeverity.ERROR)
    warnings = sum(1 for c in all_checks if c.severity == BrandCheckSeverity.WARNING)
    score = max(0, 100 - (errors * 20) - (warnings * 5))

    return BrandComplianceReport(
        compliant=errors == 0,
        score=score,
        checks=all_checks,
        errors=errors,
        warnings=warnings,
    )
