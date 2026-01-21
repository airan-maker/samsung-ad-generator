"""
A/B Testing Service

Manages multi-version video generation for A/B testing.
"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import uuid
import logging

from app.agents.script_agent import ScriptAgent
from app.agents.pipeline import run_video_pipeline, PipelineResult

logger = logging.getLogger(__name__)


class VersionTone(Enum):
    PREMIUM = "premium"
    PRACTICAL = "practical"
    MZ = "mz"  # Gen Z / Millennial


@dataclass
class VersionConfig:
    tone: VersionTone
    name: str
    description: str


# A/B test version configurations
VERSION_CONFIGS = {
    VersionTone.PREMIUM: VersionConfig(
        tone=VersionTone.PREMIUM,
        name="프리미엄",
        description="고급스럽고 세련된 톤으로 제품의 프리미엄 가치를 강조",
    ),
    VersionTone.PRACTICAL: VersionConfig(
        tone=VersionTone.PRACTICAL,
        name="실용적",
        description="제품의 실용적인 기능과 가성비를 강조",
    ),
    VersionTone.MZ: VersionConfig(
        tone=VersionTone.MZ,
        name="MZ세대",
        description="트렌디하고 캐주얼한 톤으로 젊은 세대에 어필",
    ),
}


@dataclass
class ABTestVersion:
    version_id: str
    tone: VersionTone
    name: str
    script: Optional[Dict[str, Any]] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    status: str = "pending"
    error: Optional[str] = None


@dataclass
class ABTestResult:
    test_id: str
    project_id: str
    versions: List[ABTestVersion]
    created_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "pending"


class ABTestingService:
    """Service for managing A/B test video generation."""

    def __init__(self):
        self.script_agent = ScriptAgent()

    async def create_ab_test(
        self,
        project_id: str,
        product: Dict[str, Any],
        template: Dict[str, Any],
        config: Dict[str, Any],
        tones: Optional[List[str]] = None,
    ) -> ABTestResult:
        """
        Create an A/B test with multiple video versions.

        Args:
            project_id: Project ID
            product: Product information
            template: Template configuration
            config: Base generation config
            tones: List of tones to test (default: all 3)

        Returns:
            ABTestResult with version information
        """
        test_id = str(uuid.uuid4())

        # Default to all tones if not specified
        if tones is None:
            tones = [t.value for t in VersionTone]

        # Create version entries
        versions = []
        for tone in tones:
            try:
                tone_enum = VersionTone(tone)
                version_config = VERSION_CONFIGS[tone_enum]
                versions.append(
                    ABTestVersion(
                        version_id=str(uuid.uuid4()),
                        tone=tone_enum,
                        name=version_config.name,
                    )
                )
            except ValueError:
                logger.warning(f"Invalid tone: {tone}")
                continue

        result = ABTestResult(
            test_id=test_id,
            project_id=project_id,
            versions=versions,
            created_at=datetime.utcnow(),
        )

        return result

    async def generate_scripts(
        self,
        ab_test: ABTestResult,
        product: Dict[str, Any],
        template: Dict[str, Any],
        duration: int = 30,
    ) -> ABTestResult:
        """
        Generate scripts for all A/B test versions in parallel.

        Args:
            ab_test: A/B test result to update
            product: Product information
            template: Template configuration
            duration: Video duration

        Returns:
            Updated ABTestResult with scripts
        """
        tasks = []

        for version in ab_test.versions:
            task = asyncio.create_task(
                self._generate_version_script(
                    product=product,
                    template=template,
                    tone=version.tone.value,
                    duration=duration,
                )
            )
            tasks.append((version, task))

        # Wait for all scripts to complete
        for version, task in tasks:
            try:
                script = await task
                version.script = script
                version.status = "script_ready"
            except Exception as e:
                logger.error(f"Script generation failed for {version.tone}: {e}")
                version.status = "failed"
                version.error = str(e)

        return ab_test

    async def _generate_version_script(
        self,
        product: Dict[str, Any],
        template: Dict[str, Any],
        tone: str,
        duration: int,
    ) -> Dict[str, Any]:
        """Generate script for a specific tone."""
        return await self.script_agent.generate_script(
            product_info=product,
            template_type=template.get("style", "unboxing"),
            duration=duration,
            tone=tone,
        )

    async def generate_videos(
        self,
        ab_test: ABTestResult,
        product: Dict[str, Any],
        template: Dict[str, Any],
        config: Dict[str, Any],
        on_version_complete: Optional[callable] = None,
    ) -> ABTestResult:
        """
        Generate videos for all A/B test versions.

        Videos are generated sequentially to manage API costs.

        Args:
            ab_test: A/B test result to update
            product: Product information
            template: Template configuration
            config: Generation config
            on_version_complete: Callback when a version completes

        Returns:
            Updated ABTestResult with video URLs
        """
        ab_test.status = "generating"

        for version in ab_test.versions:
            if version.status == "failed":
                continue

            if not version.script:
                version.status = "failed"
                version.error = "No script available"
                continue

            try:
                version.status = "generating"

                # Generate video for this version
                result = await run_video_pipeline(
                    project_id=f"{ab_test.project_id}_{version.version_id}",
                    product=product,
                    template=template,
                    config={**config, "tone": version.tone.value},
                    existing_script=version.script,
                )

                if result.success:
                    version.video_url = result.video_url
                    version.thumbnail_url = result.thumbnail_url
                    version.status = "completed"
                else:
                    version.status = "failed"
                    version.error = result.error

                if on_version_complete:
                    on_version_complete(version)

            except Exception as e:
                logger.error(f"Video generation failed for {version.tone}: {e}")
                version.status = "failed"
                version.error = str(e)

        # Check if all versions are done
        all_done = all(
            v.status in ["completed", "failed"] for v in ab_test.versions
        )
        if all_done:
            ab_test.status = "completed"
            ab_test.completed_at = datetime.utcnow()

        return ab_test

    async def get_version_comparison(
        self,
        ab_test: ABTestResult,
    ) -> Dict[str, Any]:
        """
        Get comparison data for all versions.

        Returns summary and comparison metrics.
        """
        versions_data = []

        for version in ab_test.versions:
            config = VERSION_CONFIGS[version.tone]
            versions_data.append({
                "version_id": version.version_id,
                "tone": version.tone.value,
                "name": config.name,
                "description": config.description,
                "script_title": version.script.get("title") if version.script else None,
                "video_url": version.video_url,
                "thumbnail_url": version.thumbnail_url,
                "status": version.status,
            })

        return {
            "test_id": ab_test.test_id,
            "project_id": ab_test.project_id,
            "status": ab_test.status,
            "versions": versions_data,
            "created_at": ab_test.created_at.isoformat(),
            "completed_at": ab_test.completed_at.isoformat() if ab_test.completed_at else None,
            "total_versions": len(ab_test.versions),
            "completed_versions": sum(1 for v in ab_test.versions if v.status == "completed"),
        }


def get_available_tones() -> List[Dict[str, str]]:
    """Get list of available tones for A/B testing."""
    return [
        {
            "id": config.tone.value,
            "name": config.name,
            "description": config.description,
        }
        for config in VERSION_CONFIGS.values()
    ]
