"""
Storyboard Generation Agent - Google AI Studio Integration

Analyzes product images and generates 3x3 storyboard with 9 scenes,
then creates 2K images for each scene using Imagen.
"""

import httpx
import asyncio
import base64
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


class StoryboardStyle(Enum):
    CINEMATIC = "cinematic"
    MINIMALIST = "minimalist"
    DYNAMIC = "dynamic"
    LIFESTYLE = "lifestyle"
    TECH = "tech"
    LUXURY = "luxury"


class SceneType(Enum):
    PRODUCT_HERO = "product_hero"  # Main product shot
    FEATURE_HIGHLIGHT = "feature_highlight"  # Specific feature focus
    LIFESTYLE = "lifestyle"  # Product in use context
    DETAIL = "detail"  # Close-up detail shot
    ENVIRONMENT = "environment"  # Product in environment
    COMPARISON = "comparison"  # Before/after or comparison
    ACTION = "action"  # Dynamic action shot
    EMOTION = "emotion"  # Emotional appeal shot
    BRANDING = "branding"  # Logo/brand shot


@dataclass
class SceneDescription:
    """Description for a single storyboard scene"""
    scene_number: int
    scene_type: SceneType
    title: str
    description: str
    camera_angle: str
    lighting: str
    mood: str
    duration_seconds: float = 1.5
    transition: str = "fade"
    image_prompt: str = ""
    generated_image_url: Optional[str] = None
    video_url: Optional[str] = None


@dataclass
class Storyboard:
    """Complete storyboard with 9 scenes (3x3 grid)"""
    id: str
    product_name: str
    product_category: str
    style: StoryboardStyle
    total_duration: float
    scenes: List[SceneDescription] = field(default_factory=list)
    thumbnail_url: Optional[str] = None
    status: str = "pending"
    error: Optional[str] = None


# Scene templates for different product categories
SCENE_TEMPLATES = {
    "smartphone": [
        {"type": SceneType.PRODUCT_HERO, "title": "제품 등장", "camera": "dramatic low angle", "lighting": "rim lighting"},
        {"type": SceneType.DETAIL, "title": "디스플레이 클로즈업", "camera": "macro close-up", "lighting": "soft diffused"},
        {"type": SceneType.FEATURE_HIGHLIGHT, "title": "카메라 시스템", "camera": "45 degree angle", "lighting": "studio lighting"},
        {"type": SceneType.ACTION, "title": "고속 촬영", "camera": "tracking shot", "lighting": "natural daylight"},
        {"type": SceneType.LIFESTYLE, "title": "일상 속 사용", "camera": "over-the-shoulder", "lighting": "warm ambient"},
        {"type": SceneType.DETAIL, "title": "디자인 디테일", "camera": "rotating product shot", "lighting": "gradient background"},
        {"type": SceneType.FEATURE_HIGHLIGHT, "title": "성능 시연", "camera": "screen recording style", "lighting": "dark mode aesthetic"},
        {"type": SceneType.EMOTION, "title": "사용자 반응", "camera": "medium close-up", "lighting": "soft natural"},
        {"type": SceneType.BRANDING, "title": "브랜드 마무리", "camera": "centered product shot", "lighting": "Samsung blue accent"},
    ],
    "tv": [
        {"type": SceneType.ENVIRONMENT, "title": "거실 공간", "camera": "wide establishing shot", "lighting": "warm living room"},
        {"type": SceneType.PRODUCT_HERO, "title": "TV 전면", "camera": "straight-on hero shot", "lighting": "screen glow"},
        {"type": SceneType.DETAIL, "title": "베젤리스 디자인", "camera": "edge detail shot", "lighting": "side lighting"},
        {"type": SceneType.FEATURE_HIGHLIGHT, "title": "화질 시연", "camera": "screen focus", "lighting": "HDR content display"},
        {"type": SceneType.LIFESTYLE, "title": "가족 시청", "camera": "behind sofa angle", "lighting": "cozy evening"},
        {"type": SceneType.ACTION, "title": "스포츠/게임", "camera": "dynamic content", "lighting": "vibrant colors"},
        {"type": SceneType.DETAIL, "title": "슬림 프로필", "camera": "side profile", "lighting": "minimalist white"},
        {"type": SceneType.FEATURE_HIGHLIGHT, "title": "스마트 기능", "camera": "UI showcase", "lighting": "soft ambient"},
        {"type": SceneType.BRANDING, "title": "브랜드 엔딩", "camera": "beauty shot", "lighting": "Samsung signature"},
    ],
    "appliance": [
        {"type": SceneType.ENVIRONMENT, "title": "주방/공간", "camera": "wide kitchen shot", "lighting": "bright natural"},
        {"type": SceneType.PRODUCT_HERO, "title": "제품 전체", "camera": "three-quarter angle", "lighting": "clean studio"},
        {"type": SceneType.DETAIL, "title": "패널/컨트롤", "camera": "close-up interface", "lighting": "soft focused"},
        {"type": SceneType.ACTION, "title": "작동 모습", "camera": "medium shot", "lighting": "natural daylight"},
        {"type": SceneType.LIFESTYLE, "title": "요리/사용", "camera": "lifestyle angle", "lighting": "warm kitchen"},
        {"type": SceneType.FEATURE_HIGHLIGHT, "title": "내부 공간", "camera": "interior shot", "lighting": "internal LED"},
        {"type": SceneType.DETAIL, "title": "마감 디테일", "camera": "texture close-up", "lighting": "reflective surface"},
        {"type": SceneType.EMOTION, "title": "만족스러운 결과", "camera": "result showcase", "lighting": "appetizing warm"},
        {"type": SceneType.BRANDING, "title": "브랜드 마무리", "camera": "product beauty shot", "lighting": "premium finish"},
    ],
    "wearable": [
        {"type": SceneType.PRODUCT_HERO, "title": "워치 등장", "camera": "dramatic close-up", "lighting": "spotlight"},
        {"type": SceneType.DETAIL, "title": "디스플레이", "camera": "face close-up", "lighting": "AMOLED glow"},
        {"type": SceneType.LIFESTYLE, "title": "착용 모습", "camera": "wrist shot", "lighting": "natural outdoor"},
        {"type": SceneType.ACTION, "title": "운동 중", "camera": "action tracking", "lighting": "dynamic outdoor"},
        {"type": SceneType.FEATURE_HIGHLIGHT, "title": "건강 기능", "camera": "screen UI", "lighting": "clean interface"},
        {"type": SceneType.DETAIL, "title": "밴드/디자인", "camera": "material close-up", "lighting": "studio macro"},
        {"type": SceneType.LIFESTYLE, "title": "일상 활용", "camera": "daily life shot", "lighting": "casual ambient"},
        {"type": SceneType.FEATURE_HIGHLIGHT, "title": "연결성", "camera": "phone pairing", "lighting": "tech aesthetic"},
        {"type": SceneType.BRANDING, "title": "브랜드 엔딩", "camera": "floating product", "lighting": "Samsung blue"},
    ],
}


class StoryboardAgent:
    """Agent for generating storyboards using Google AI Studio (Gemini + Imagen)"""

    def __init__(self):
        self.gemini_api_key = settings.GOOGLE_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.imagen_url = "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict"

    async def analyze_product_image(
        self,
        image_data: bytes,
        product_category: str = "smartphone"
    ) -> Dict[str, Any]:
        """Analyze product image using Gemini Vision to extract key features"""

        if not self.gemini_api_key:
            logger.warning("Google API key not configured, using mock analysis")
            return self._mock_product_analysis(product_category)

        # Encode image to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        prompt = f"""Analyze this Samsung {product_category} product image and extract:
1. Product name/model (if visible)
2. Key visual features (color, design elements, materials)
3. Distinguishing characteristics
4. Suggested mood/style for advertising
5. Key selling points visible in the image

Respond in JSON format:
{{
    "product_name": "string",
    "color": "string",
    "design_features": ["list of features"],
    "materials": ["list of materials"],
    "mood_suggestions": ["list of moods"],
    "selling_points": ["list of points"],
    "background_suggestion": "string"
}}"""

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/models/gemini-1.5-flash:generateContent",
                    params={"key": self.gemini_api_key},
                    json={
                        "contents": [{
                            "parts": [
                                {"text": prompt},
                                {
                                    "inline_data": {
                                        "mime_type": "image/jpeg",
                                        "data": image_base64
                                    }
                                }
                            ]
                        }],
                        "generationConfig": {
                            "temperature": 0.4,
                            "topK": 32,
                            "topP": 1,
                            "maxOutputTokens": 1024,
                        }
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    text = result["candidates"][0]["content"]["parts"][0]["text"]
                    # Parse JSON from response
                    json_start = text.find('{')
                    json_end = text.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        return json.loads(text[json_start:json_end])
                    return self._mock_product_analysis(product_category)
                else:
                    logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                    return self._mock_product_analysis(product_category)

            except Exception as e:
                logger.error(f"Error analyzing product image: {e}")
                return self._mock_product_analysis(product_category)

    def _mock_product_analysis(self, category: str) -> Dict[str, Any]:
        """Return mock analysis for testing"""
        return {
            "product_name": f"Samsung Galaxy {category.title()}",
            "color": "Phantom Black",
            "design_features": ["sleek design", "premium finish", "minimalist aesthetic"],
            "materials": ["glass", "aluminum", "ceramic"],
            "mood_suggestions": ["premium", "innovative", "sophisticated"],
            "selling_points": ["cutting-edge technology", "beautiful design", "powerful performance"],
            "background_suggestion": "dark gradient with subtle blue accents"
        }

    async def generate_storyboard(
        self,
        product_image: bytes,
        product_category: str,
        style: StoryboardStyle = StoryboardStyle.CINEMATIC,
        target_duration: float = 15.0,
        custom_prompts: Optional[List[str]] = None
    ) -> Storyboard:
        """Generate a complete 3x3 storyboard for the product"""

        import uuid
        storyboard_id = str(uuid.uuid4())

        # Step 1: Analyze the product image
        logger.info(f"Analyzing product image for storyboard {storyboard_id}")
        product_analysis = await self.analyze_product_image(product_image, product_category)

        # Step 2: Get scene templates for this category
        templates = SCENE_TEMPLATES.get(product_category, SCENE_TEMPLATES["smartphone"])

        # Step 3: Generate detailed scene descriptions using Gemini
        scenes = await self._generate_scene_descriptions(
            product_analysis=product_analysis,
            templates=templates,
            style=style,
            target_duration=target_duration,
            custom_prompts=custom_prompts
        )

        storyboard = Storyboard(
            id=storyboard_id,
            product_name=product_analysis.get("product_name", "Samsung Product"),
            product_category=product_category,
            style=style,
            total_duration=target_duration,
            scenes=scenes,
            status="scenes_generated"
        )

        return storyboard

    async def _generate_scene_descriptions(
        self,
        product_analysis: Dict[str, Any],
        templates: List[Dict],
        style: StoryboardStyle,
        target_duration: float,
        custom_prompts: Optional[List[str]] = None
    ) -> List[SceneDescription]:
        """Generate detailed descriptions for each scene"""

        scenes = []
        scene_duration = target_duration / 9  # 9 scenes

        for i, template in enumerate(templates[:9]):
            scene_type = template["type"]

            # Build image generation prompt
            image_prompt = self._build_imagen_prompt(
                product_analysis=product_analysis,
                scene_type=scene_type,
                template=template,
                style=style,
                custom_prompt=custom_prompts[i] if custom_prompts and i < len(custom_prompts) else None
            )

            scene = SceneDescription(
                scene_number=i + 1,
                scene_type=scene_type,
                title=template["title"],
                description=f"{template['title']} - {style.value} style",
                camera_angle=template["camera"],
                lighting=template["lighting"],
                mood=style.value,
                duration_seconds=scene_duration,
                transition="fade" if i < 8 else "none",
                image_prompt=image_prompt
            )
            scenes.append(scene)

        return scenes

    def _build_imagen_prompt(
        self,
        product_analysis: Dict[str, Any],
        scene_type: SceneType,
        template: Dict,
        style: StoryboardStyle,
        custom_prompt: Optional[str] = None
    ) -> str:
        """Build a detailed prompt for Imagen image generation"""

        product_name = product_analysis.get("product_name", "Samsung product")
        color = product_analysis.get("color", "black")
        features = product_analysis.get("design_features", [])

        base_prompt = f"Professional advertising photography of {product_name} in {color}"

        style_modifiers = {
            StoryboardStyle.CINEMATIC: "cinematic lighting, dramatic shadows, movie-quality, 8K resolution",
            StoryboardStyle.MINIMALIST: "clean white background, minimalist composition, soft shadows",
            StoryboardStyle.DYNAMIC: "motion blur, energetic composition, vibrant colors",
            StoryboardStyle.LIFESTYLE: "lifestyle photography, natural environment, authentic moment",
            StoryboardStyle.TECH: "futuristic aesthetic, blue accent lighting, high-tech atmosphere",
            StoryboardStyle.LUXURY: "luxury setting, premium materials, elegant composition",
        }

        scene_modifiers = {
            SceneType.PRODUCT_HERO: "hero shot, centered composition, dramatic presentation",
            SceneType.FEATURE_HIGHLIGHT: "feature focus, detailed view, informative angle",
            SceneType.LIFESTYLE: "in-use scenario, realistic setting, human element",
            SceneType.DETAIL: "macro photography, extreme close-up, texture detail",
            SceneType.ENVIRONMENT: "environmental context, wide shot, atmosphere",
            SceneType.COMPARISON: "side-by-side comparison, clear difference",
            SceneType.ACTION: "dynamic movement, action freeze, energy",
            SceneType.EMOTION: "emotional connection, human reaction, warmth",
            SceneType.BRANDING: "brand identity, logo visible, signature style",
        }

        prompt_parts = [
            base_prompt,
            f"Camera: {template['camera']}",
            f"Lighting: {template['lighting']}",
            style_modifiers.get(style, ""),
            scene_modifiers.get(scene_type, ""),
            f"Design features: {', '.join(features[:3])}" if features else "",
            "Samsung brand aesthetic, premium quality, professional advertisement",
            "2K resolution, sharp focus, perfect exposure",
        ]

        if custom_prompt:
            prompt_parts.append(custom_prompt)

        return ", ".join(filter(None, prompt_parts))

    async def generate_scene_images(
        self,
        storyboard: Storyboard,
        resolution: str = "2048x2048"
    ) -> Storyboard:
        """Generate 2K images for each scene using Imagen"""

        if not self.gemini_api_key:
            logger.warning("Google API key not configured, skipping image generation")
            storyboard.status = "images_skipped"
            return storyboard

        logger.info(f"Generating {len(storyboard.scenes)} scene images for storyboard {storyboard.id}")

        async with httpx.AsyncClient(timeout=120.0) as client:
            tasks = []
            for scene in storyboard.scenes:
                task = self._generate_single_image(client, scene, resolution)
                tasks.append(task)

            # Generate images concurrently (but respect rate limits)
            results = await asyncio.gather(*tasks, return_exceptions=True)

            success_count = 0
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to generate image for scene {i+1}: {result}")
                    storyboard.scenes[i].generated_image_url = None
                elif result:
                    storyboard.scenes[i].generated_image_url = result
                    success_count += 1

            storyboard.status = "images_generated" if success_count == 9 else "images_partial"
            logger.info(f"Generated {success_count}/9 images for storyboard {storyboard.id}")

        return storyboard

    async def _generate_single_image(
        self,
        client: httpx.AsyncClient,
        scene: SceneDescription,
        resolution: str
    ) -> Optional[str]:
        """Generate a single image using Imagen 3"""

        try:
            # Parse resolution
            width, height = map(int, resolution.split('x'))

            response = await client.post(
                self.imagen_url,
                params={"key": self.gemini_api_key},
                json={
                    "instances": [{"prompt": scene.image_prompt}],
                    "parameters": {
                        "sampleCount": 1,
                        "aspectRatio": "1:1",
                        "outputOptions": {
                            "mimeType": "image/png"
                        }
                    }
                }
            )

            if response.status_code == 200:
                result = response.json()
                # Extract image data and save/upload
                if "predictions" in result and len(result["predictions"]) > 0:
                    image_data = result["predictions"][0].get("bytesBase64Encoded")
                    if image_data:
                        # In production, upload to cloud storage and return URL
                        # For now, return a data URL or save locally
                        return f"data:image/png;base64,{image_data[:100]}..."  # Truncated for logging
            else:
                logger.error(f"Imagen API error: {response.status_code} - {response.text}")

        except Exception as e:
            logger.error(f"Error generating image: {e}")

        return None

    async def generate_scene_videos(
        self,
        storyboard: Storyboard,
        video_duration: float = 1.5
    ) -> Storyboard:
        """Convert scene images to short video clips using Runway"""

        # Import Runway agent
        from app.agents.video_agent import VideoAgent

        video_agent = VideoAgent()

        logger.info(f"Generating video clips for storyboard {storyboard.id}")

        for i, scene in enumerate(storyboard.scenes):
            if not scene.generated_image_url:
                logger.warning(f"Skipping scene {i+1}: no image generated")
                continue

            try:
                # Generate video from image using Runway
                video_result = await video_agent.generate_from_image(
                    image_url=scene.generated_image_url,
                    prompt=f"Subtle motion, {scene.camera_angle}, {scene.mood} mood, Samsung advertisement style",
                    duration=video_duration
                )

                if video_result and video_result.video_url:
                    scene.video_url = video_result.video_url
                    scene.duration_seconds = video_duration

            except Exception as e:
                logger.error(f"Error generating video for scene {i+1}: {e}")

        # Count successful video generations
        video_count = sum(1 for s in storyboard.scenes if s.video_url)
        storyboard.status = "videos_generated" if video_count == 9 else "videos_partial"
        logger.info(f"Generated {video_count}/9 video clips for storyboard {storyboard.id}")

        return storyboard

    def export_storyboard_grid(self, storyboard: Storyboard) -> Dict[str, Any]:
        """Export storyboard as a 3x3 grid structure for frontend display"""

        grid = []
        for row in range(3):
            row_scenes = []
            for col in range(3):
                scene_idx = row * 3 + col
                if scene_idx < len(storyboard.scenes):
                    scene = storyboard.scenes[scene_idx]
                    row_scenes.append({
                        "scene_number": scene.scene_number,
                        "title": scene.title,
                        "description": scene.description,
                        "camera_angle": scene.camera_angle,
                        "lighting": scene.lighting,
                        "duration": scene.duration_seconds,
                        "transition": scene.transition,
                        "image_url": scene.generated_image_url,
                        "video_url": scene.video_url,
                        "prompt": scene.image_prompt,
                    })
            grid.append(row_scenes)

        return {
            "storyboard_id": storyboard.id,
            "product_name": storyboard.product_name,
            "product_category": storyboard.product_category,
            "style": storyboard.style.value,
            "total_duration": storyboard.total_duration,
            "status": storyboard.status,
            "grid": grid,
            "thumbnail_url": storyboard.thumbnail_url,
        }


# Singleton instance
storyboard_agent = StoryboardAgent()
