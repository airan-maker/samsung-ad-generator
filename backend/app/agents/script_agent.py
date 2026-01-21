from typing import List, Optional, Dict, Any
import anthropic
from app.core.config import settings


class ScriptAgent:
    """AI Agent for generating advertising scripts."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    async def generate(
        self,
        product_name: str,
        product_features: List[str],
        product_specs: Dict[str, str],
        template_style: Optional[str],
        tone: str,
        language: str,
        duration: int,
        custom_keywords: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate advertising script for a product."""

        tone_descriptions = {
            "premium": "고급스럽고 세련된 톤. 프리미엄 가치와 품격을 강조합니다.",
            "practical": "실용적이고 합리적인 톤. 기능과 가성비를 강조합니다.",
            "mz": "트렌디하고 캐주얼한 톤. MZ세대에 맞는 친근하고 재미있는 표현을 사용합니다.",
        }

        language_instructions = {
            "ko": "한국어로 작성해주세요.",
            "en": "Write in English.",
            "zh": "请用中文写作。",
        }

        features_text = "\n".join([f"- {f}" for f in product_features]) if product_features else "제품 특성 정보 없음"
        specs_text = "\n".join([f"- {k}: {v}" for k, v in product_specs.items()]) if product_specs else "스펙 정보 없음"
        keywords_text = ", ".join(custom_keywords) if custom_keywords else "없음"

        prompt = f"""당신은 삼성전자 제품 광고 카피라이터입니다. 다음 정보를 바탕으로 {duration}초 광고 영상용 스크립트를 작성해주세요.

## 제품 정보
- 제품명: {product_name}
- 주요 기능:
{features_text}
- 스펙:
{specs_text}

## 요구사항
- 톤앤매너: {tone} - {tone_descriptions.get(tone, '')}
- 템플릿 스타일: {template_style or '일반'}
- 영상 길이: {duration}초
- 강조 키워드: {keywords_text}
- {language_instructions.get(language, '한국어로 작성해주세요.')}

## 출력 형식
다음 JSON 형식으로 출력해주세요:

{{
    "headline": "메인 헤드라인 (5자 이내, 제품명 또는 핵심 메시지)",
    "subline": "서브 카피 (15자 이내, 핵심 가치 전달)",
    "narration": "나레이션 스크립트 ({duration}초 기준, 약 {duration * 2.5}자)",
    "cta": "CTA 문구 (행동 유도, 10자 이내)",
    "scenes": [
        {{"order": 1, "text": "화면에 표시될 텍스트", "narration": "해당 씬의 나레이션"}},
        ...
    ],
    "alternatives": {{
        "headline": ["대안1", "대안2"],
        "subline": ["대안1", "대안2"]
    }}
}}
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse response
            content = response.content[0].text

            # Extract JSON from response
            import json
            import re

            # Try to find JSON in the response
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                script = json.loads(json_match.group())
                return script

            # Fallback if JSON parsing fails
            return self._generate_fallback_script(product_name, tone, duration)

        except Exception as e:
            print(f"Script generation error: {e}")
            return self._generate_fallback_script(product_name, tone, duration)

    async def regenerate_field(
        self,
        field: str,
        current_value: str,
        instruction: Optional[str],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Regenerate a specific field of the script."""

        field_descriptions = {
            "headline": "메인 헤드라인 (5자 이내)",
            "subline": "서브 카피 (15자 이내)",
            "narration": "나레이션 스크립트",
            "cta": "CTA 문구 (10자 이내)",
        }

        prompt = f"""당신은 삼성전자 제품 광고 카피라이터입니다.

## 현재 값
- 필드: {field} ({field_descriptions.get(field, '')})
- 현재 내용: {current_value}

## 제품 정보
- 제품명: {context.get('product_name', '')}

## 요청
{instruction or '다른 버전으로 다시 작성해주세요.'}

## 출력 형식
다음 JSON 형식으로 출력해주세요:
{{
    "field": "{field}",
    "value": "새로운 내용",
    "alternatives": ["대안1", "대안2"]
}}
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text

            import json
            import re

            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                result = json.loads(json_match.group())
                return result

            # Fallback
            return {
                "field": field,
                "value": current_value,
                "alternatives": [],
            }

        except Exception as e:
            print(f"Script regeneration error: {e}")
            return {
                "field": field,
                "value": current_value,
                "alternatives": [],
            }

    def _generate_fallback_script(
        self,
        product_name: str,
        tone: str,
        duration: int,
    ) -> Dict[str, Any]:
        """Generate a fallback script if AI fails."""

        fallback_scripts = {
            "premium": {
                "headline": product_name,
                "subline": "새로운 기준을 제시합니다",
                "narration": f"새로운 {product_name}을 만나보세요. 혁신적인 기술과 세련된 디자인이 만나 완벽한 조화를 이룹니다.",
                "cta": "지금 만나보세요",
            },
            "practical": {
                "headline": product_name,
                "subline": "똑똑한 선택",
                "narration": f"{product_name}과 함께라면 일상이 더 편리해집니다. 합리적인 가격에 최고의 성능을 경험하세요.",
                "cta": "자세히 보기",
            },
            "mz": {
                "headline": product_name,
                "subline": "이건 진짜임",
                "narration": f"요즘 핫한 {product_name}, 직접 써보면 알게 됨. 이 정도면 갓성비 아님?",
                "cta": "지금 확인",
            },
        }

        script = fallback_scripts.get(tone, fallback_scripts["premium"])

        return {
            **script,
            "scenes": [
                {"order": 1, "text": script["headline"], "narration": script["narration"][:30]},
                {"order": 2, "text": script["subline"], "narration": script["narration"][30:60]},
                {"order": 3, "text": script["cta"], "narration": ""},
            ],
            "alternatives": {
                "headline": [product_name],
                "subline": [script["subline"]],
            },
        }
