"""
AI Video Optimizer Service

Uses AI to analyze and optimize video content for better engagement.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import asyncio
import logging
import anthropic

from app.core.config import settings

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    THUMBNAIL = "thumbnail"
    TITLE = "title"
    DESCRIPTION = "description"
    SCRIPT = "script"
    PACING = "pacing"
    MUSIC = "music"
    COLORS = "colors"
    CALL_TO_ACTION = "call_to_action"


class Platform(Enum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    COUPANG = "coupang"
    FACEBOOK = "facebook"


@dataclass
class OptimizationSuggestion:
    type: OptimizationType
    title: str
    description: str
    current_value: Optional[str]
    suggested_value: str
    confidence: float  # 0-1
    expected_improvement: str
    priority: int  # 1-5, 1 being highest


@dataclass
class OptimizationResult:
    project_id: str
    platform: Platform
    overall_score: float  # 0-100
    suggestions: List[OptimizationSuggestion]
    ai_analysis: str
    generated_at: datetime


class AIOptimizerService:
    """
    AI-powered video optimization service.
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)

    async def analyze_video(
        self,
        project_id: str,
        video_data: Dict[str, Any],
        target_platform: Platform = Platform.YOUTUBE,
    ) -> OptimizationResult:
        """
        Analyze a video and provide optimization suggestions.
        """
        # Extract video metadata
        title = video_data.get("title", "")
        description = video_data.get("description", "")
        script = video_data.get("script", {})
        duration = video_data.get("duration", 30)
        product = video_data.get("product", {})
        template = video_data.get("template", {})

        # Get platform-specific analysis
        analysis = await self._get_ai_analysis(
            title=title,
            description=description,
            script=script,
            duration=duration,
            product=product,
            platform=target_platform,
        )

        # Generate suggestions
        suggestions = await self._generate_suggestions(
            video_data=video_data,
            analysis=analysis,
            platform=target_platform,
        )

        # Calculate overall score
        score = self._calculate_optimization_score(suggestions)

        return OptimizationResult(
            project_id=project_id,
            platform=target_platform,
            overall_score=score,
            suggestions=suggestions,
            ai_analysis=analysis.get("summary", ""),
            generated_at=datetime.utcnow(),
        )

    async def optimize_title(
        self,
        product_name: str,
        current_title: str,
        target_platform: Platform,
        keywords: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate optimized title suggestions.
        """
        platform_guidelines = self._get_platform_guidelines(target_platform)

        prompt = f"""제품 광고 영상의 제목을 최적화해주세요.

제품: {product_name}
현재 제목: {current_title}
플랫폼: {target_platform.value}
{f'키워드: {", ".join(keywords)}' if keywords else ''}

플랫폼 가이드라인:
{platform_guidelines['title']}

요구사항:
1. 클릭률을 높일 수 있는 매력적인 제목 5개 생성
2. SEO 최적화 고려
3. 감정적 호소력 포함
4. 적절한 길이 유지

JSON 형식으로 응답:
{{
    "suggestions": [
        {{
            "title": "제목",
            "reason": "이유",
            "estimated_ctr_improvement": "예상 CTR 향상률 (%)"
        }}
    ],
    "best_choice": 0,
    "analysis": "분석 내용"
}}"""

        response = await self._call_claude(prompt)
        return response

    async def optimize_thumbnail(
        self,
        product_info: Dict[str, Any],
        current_thumbnail_url: Optional[str],
        target_platform: Platform,
    ) -> Dict[str, Any]:
        """
        Generate thumbnail optimization suggestions.
        """
        prompt = f"""제품 광고 영상의 썸네일을 최적화해주세요.

제품 정보:
- 이름: {product_info.get('name', '')}
- 카테고리: {product_info.get('category', '')}
- 주요 특징: {product_info.get('features', [])}

플랫폼: {target_platform.value}

요구사항:
1. 시선을 사로잡는 썸네일 컨셉 3개 제안
2. 색상 조합 추천
3. 텍스트 오버레이 제안
4. 구도 가이드

JSON 형식으로 응답:
{{
    "concepts": [
        {{
            "name": "컨셉명",
            "description": "설명",
            "color_palette": ["#색상1", "#색상2", "#색상3"],
            "text_overlay": "텍스트",
            "layout": "구도 설명"
        }}
    ],
    "color_psychology": "색상 심리 분석",
    "best_practices": ["팁1", "팁2"]
}}"""

        response = await self._call_claude(prompt)
        return response

    async def optimize_script(
        self,
        current_script: Dict[str, Any],
        product_info: Dict[str, Any],
        target_audience: str,
        target_platform: Platform,
    ) -> Dict[str, Any]:
        """
        Optimize script for better engagement.
        """
        platform_guidelines = self._get_platform_guidelines(target_platform)

        prompt = f"""광고 영상 스크립트를 최적화해주세요.

현재 스크립트:
{current_script}

제품: {product_info.get('name', '')}
타겟 오디언스: {target_audience}
플랫폼: {target_platform.value}

플랫폼 가이드라인:
{platform_guidelines['content']}

최적화 요구사항:
1. 첫 3초 훅 강화
2. 핵심 메시지 명확화
3. 감정적 연결 강화
4. CTA 최적화
5. 페이싱 조정

JSON 형식으로 응답:
{{
    "optimized_script": {{
        "title": "최적화된 제목",
        "hook": "첫 3초 훅",
        "scenes": [
            {{
                "scene_number": 1,
                "duration": 5,
                "narration": "내레이션",
                "visual_suggestion": "영상 제안"
            }}
        ],
        "cta": "콜투액션"
    }},
    "changes_summary": ["변경사항1", "변경사항2"],
    "expected_improvements": {{
        "engagement": "+X%",
        "watch_time": "+X%",
        "click_through": "+X%"
    }}
}}"""

        response = await self._call_claude(prompt)
        return response

    async def analyze_pacing(
        self,
        script: Dict[str, Any],
        duration: int,
        target_platform: Platform,
    ) -> Dict[str, Any]:
        """
        Analyze and optimize video pacing.
        """
        scenes = script.get("scenes", [])

        prompt = f"""영상의 페이싱을 분석하고 최적화해주세요.

현재 씬 구성:
{scenes}

총 영상 길이: {duration}초
플랫폼: {target_platform.value}

분석 요구사항:
1. 각 씬의 적절성 평가
2. 관심 유지를 위한 페이싱 조정
3. 전환 타이밍 최적화
4. 클라이맥스 위치 확인

JSON 형식으로 응답:
{{
    "current_analysis": {{
        "pacing_score": 75,
        "attention_curve": [씬별 관심도 배열],
        "issues": ["이슈1", "이슈2"]
    }},
    "optimized_pacing": {{
        "scenes": [
            {{
                "scene_number": 1,
                "original_duration": 5,
                "suggested_duration": 4,
                "reason": "이유"
            }}
        ],
        "transitions": ["전환1", "전환2"]
    }},
    "expected_improvement": "예상 시청 유지율 향상"
}}"""

        response = await self._call_claude(prompt)
        return response

    async def suggest_music(
        self,
        video_data: Dict[str, Any],
        mood: str,
        target_platform: Platform,
    ) -> Dict[str, Any]:
        """
        Suggest background music based on content analysis.
        """
        prompt = f"""광고 영상에 적합한 배경 음악을 추천해주세요.

영상 정보:
- 제품: {video_data.get('product', {}).get('name', '')}
- 분위기: {mood}
- 길이: {video_data.get('duration', 30)}초
- 플랫폼: {target_platform.value}

스크립트 톤: {video_data.get('script', {}).get('tone', 'professional')}

요구사항:
1. 브랜드 이미지와 맞는 음악 장르
2. 저작권 프리 음악 카테고리
3. BPM 범위 추천
4. 볼륨 밸런스 가이드

JSON 형식으로 응답:
{{
    "recommendations": [
        {{
            "genre": "장르",
            "mood": "분위기",
            "bpm_range": [120, 140],
            "description": "설명",
            "example_tracks": ["예시1", "예시2"]
        }}
    ],
    "volume_guide": {{
        "music_level": 0.3,
        "narration_level": 1.0,
        "fade_in_duration": 1.5,
        "fade_out_duration": 2.0
    }},
    "timing_suggestions": [
        {{
            "timestamp": 0,
            "action": "음악 시작",
            "note": "메모"
        }}
    ]
}}"""

        response = await self._call_claude(prompt)
        return response

    async def generate_ab_variants(
        self,
        video_data: Dict[str, Any],
        variant_count: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Generate A/B test variants with AI suggestions.
        """
        prompt = f"""광고 영상의 A/B 테스트 변형을 생성해주세요.

원본 영상 정보:
{video_data}

요구사항:
1. {variant_count}개의 서로 다른 변형 생성
2. 각 변형은 특정 타겟 또는 목표에 최적화
3. 테스트 가설 제시

JSON 형식으로 응답:
{{
    "variants": [
        {{
            "name": "변형 A - 감성 호소",
            "target_audience": "25-34 여성",
            "hypothesis": "감성적 메시지가 더 높은 전환율",
            "changes": {{
                "title": "새 제목",
                "hook": "새 훅",
                "tone": "emotional",
                "cta": "새 CTA"
            }},
            "expected_metrics": {{
                "ctr": "+15%",
                "conversion": "+10%"
            }}
        }}
    ],
    "test_recommendations": {{
        "sample_size": 1000,
        "duration_days": 7,
        "success_metric": "conversion_rate"
    }}
}}"""

        response = await self._call_claude(prompt)
        return response.get("variants", [])

    async def _get_ai_analysis(
        self,
        title: str,
        description: str,
        script: Dict[str, Any],
        duration: int,
        product: Dict[str, Any],
        platform: Platform,
    ) -> Dict[str, Any]:
        """Get comprehensive AI analysis of video content."""
        prompt = f"""광고 영상을 종합적으로 분석해주세요.

제목: {title}
설명: {description}
스크립트: {script}
길이: {duration}초
제품: {product}
플랫폼: {platform.value}

다음 항목을 분석해주세요:
1. 타이틀 효과성 (SEO, 클릭 유도)
2. 훅 강도 (첫 3초)
3. 메시지 명확성
4. 감정적 호소력
5. CTA 효과성
6. 플랫폼 최적화 수준

JSON 형식으로 응답:
{{
    "scores": {{
        "title": 0-100,
        "hook": 0-100,
        "message_clarity": 0-100,
        "emotional_appeal": 0-100,
        "cta_effectiveness": 0-100,
        "platform_fit": 0-100
    }},
    "strengths": ["강점1", "강점2"],
    "weaknesses": ["약점1", "약점2"],
    "summary": "종합 분석"
}}"""

        return await self._call_claude(prompt)

    async def _generate_suggestions(
        self,
        video_data: Dict[str, Any],
        analysis: Dict[str, Any],
        platform: Platform,
    ) -> List[OptimizationSuggestion]:
        """Generate specific optimization suggestions based on analysis."""
        suggestions = []
        scores = analysis.get("scores", {})

        # Title optimization
        if scores.get("title", 100) < 80:
            suggestions.append(OptimizationSuggestion(
                type=OptimizationType.TITLE,
                title="제목 최적화 필요",
                description="클릭률을 높이기 위해 제목을 개선하세요",
                current_value=video_data.get("title"),
                suggested_value="[AI 제안 제목]",
                confidence=0.85,
                expected_improvement="+15% CTR",
                priority=1,
            ))

        # Hook optimization
        if scores.get("hook", 100) < 75:
            suggestions.append(OptimizationSuggestion(
                type=OptimizationType.SCRIPT,
                title="첫 3초 훅 강화",
                description="시청자의 주의를 더 효과적으로 끌어야 합니다",
                current_value=str(video_data.get("script", {}).get("hook", "")),
                suggested_value="[AI 제안 훅]",
                confidence=0.9,
                expected_improvement="+20% 시청 유지율",
                priority=1,
            ))

        # CTA optimization
        if scores.get("cta_effectiveness", 100) < 70:
            suggestions.append(OptimizationSuggestion(
                type=OptimizationType.CALL_TO_ACTION,
                title="CTA 강화",
                description="더 명확하고 긴급한 행동 유도 필요",
                current_value=str(video_data.get("script", {}).get("cta", "")),
                suggested_value="[AI 제안 CTA]",
                confidence=0.8,
                expected_improvement="+25% 전환율",
                priority=2,
            ))

        # Platform-specific suggestions
        if scores.get("platform_fit", 100) < 80:
            suggestions.append(OptimizationSuggestion(
                type=OptimizationType.PACING,
                title=f"{platform.value} 플랫폼 최적화",
                description=f"{platform.value}에 맞는 포맷과 페이싱 조정 필요",
                current_value=None,
                suggested_value="[플랫폼별 최적화 제안]",
                confidence=0.75,
                expected_improvement="+10% 참여율",
                priority=2,
            ))

        return sorted(suggestions, key=lambda x: x.priority)

    def _calculate_optimization_score(
        self,
        suggestions: List[OptimizationSuggestion],
    ) -> float:
        """Calculate overall optimization score based on suggestions."""
        if not suggestions:
            return 100.0

        # More high-priority suggestions = lower score
        priority_weights = {1: 15, 2: 10, 3: 5, 4: 3, 5: 1}
        total_deduction = sum(
            priority_weights.get(s.priority, 5) for s in suggestions
        )

        score = max(0, 100 - total_deduction)
        return round(score, 1)

    def _get_platform_guidelines(self, platform: Platform) -> Dict[str, str]:
        """Get platform-specific content guidelines."""
        guidelines = {
            Platform.YOUTUBE: {
                "title": "60자 이내, 키워드 앞부분 배치, 감정적 호소 포함",
                "content": "처음 30초에 핵심 정보, 챕터 마커 활용, 엔드스크린 연결",
                "thumbnail": "밝은 색상, 얼굴 클로즈업, 텍스트 3-4 단어",
            },
            Platform.INSTAGRAM: {
                "title": "30자 이내, 이모지 활용, 해시태그 별도",
                "content": "15초 내 핵심 전달, 세로 영상, 음소거 시청 고려 자막",
                "thumbnail": "정사각형 최적화, 미니멀 디자인",
            },
            Platform.TIKTOK: {
                "title": "트렌드 해시태그, 캐주얼 톤",
                "content": "3초 훅 필수, 빠른 페이싱, 음악 트렌드 활용",
                "thumbnail": "첫 프레임 = 썸네일, 움직임 암시",
            },
            Platform.COUPANG: {
                "title": "제품명 + 핵심 기능, 가격 정보",
                "content": "제품 상세 중심, 사용 시연, 구매 혜택 강조",
                "thumbnail": "제품 이미지 중심, 클린한 배경",
            },
            Platform.FACEBOOK: {
                "title": "40자 이내, 질문형 효과적",
                "content": "처음 3초 훅, 음소거 최적화, 사각형/세로 권장",
                "thumbnail": "텍스트 20% 이하, 밝은 색상",
            },
        }
        return guidelines.get(platform, guidelines[Platform.YOUTUBE])

    async def _call_claude(self, prompt: str) -> Dict[str, Any]:
        """Call Claude API and parse JSON response."""
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )

            response_text = message.content[0].text

            # Extract JSON from response
            import json
            import re

            # Try to find JSON in the response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())

            return {"raw_response": response_text}

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return {"error": str(e)}


# Global instance
ai_optimizer = AIOptimizerService()
