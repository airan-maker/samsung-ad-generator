"""
Storyboard API Endpoints

Handles storyboard generation from product images.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from typing import Optional, List
from pydantic import BaseModel
import uuid
import asyncio

from app.agents.storyboard_agent import (
    storyboard_agent,
    StoryboardStyle,
    Storyboard,
)

router = APIRouter(prefix="/storyboard", tags=["storyboard"])


# In-memory storage for storyboards (use database in production)
storyboard_storage: dict[str, dict] = {}


class StoryboardRequest(BaseModel):
    product_category: str = "smartphone"
    style: str = "cinematic"
    target_duration: float = 15.0
    custom_prompts: Optional[List[str]] = None


class StoryboardResponse(BaseModel):
    storyboard_id: str
    status: str
    message: str


class SceneResponse(BaseModel):
    scene_number: int
    title: str
    description: str
    camera_angle: str
    lighting: str
    duration: float
    transition: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    prompt: str


class StoryboardDetailResponse(BaseModel):
    storyboard_id: str
    product_name: str
    product_category: str
    style: str
    total_duration: float
    status: str
    grid: List[List[dict]]
    thumbnail_url: Optional[str] = None


@router.post("/generate", response_model=StoryboardResponse)
async def generate_storyboard(
    background_tasks: BackgroundTasks,
    product_image: UploadFile = File(...),
    product_category: str = Form("smartphone"),
    style: str = Form("cinematic"),
    target_duration: float = Form(15.0),
):
    """
    Generate a 3x3 storyboard from a product image.

    - Analyzes the product image using Gemini Vision
    - Creates 9 scene descriptions optimized for the product
    - Returns storyboard ID for tracking progress
    """

    # Validate inputs
    valid_categories = ["smartphone", "tv", "appliance", "wearable"]
    if product_category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {valid_categories}"
        )

    try:
        storyboard_style = StoryboardStyle(style)
    except ValueError:
        valid_styles = [s.value for s in StoryboardStyle]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid style. Must be one of: {valid_styles}"
        )

    # Read image data
    image_data = await product_image.read()

    if len(image_data) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="Image size exceeds 10MB limit")

    # Generate storyboard ID
    storyboard_id = str(uuid.uuid4())

    # Store initial status
    storyboard_storage[storyboard_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Analyzing product image...",
        "storyboard": None,
    }

    # Start background processing
    background_tasks.add_task(
        process_storyboard,
        storyboard_id=storyboard_id,
        image_data=image_data,
        product_category=product_category,
        style=storyboard_style,
        target_duration=target_duration,
    )

    return StoryboardResponse(
        storyboard_id=storyboard_id,
        status="processing",
        message="Storyboard generation started. Use GET /storyboard/{id} to check progress."
    )


async def process_storyboard(
    storyboard_id: str,
    image_data: bytes,
    product_category: str,
    style: StoryboardStyle,
    target_duration: float,
):
    """Background task to process storyboard generation"""

    try:
        # Step 1: Generate storyboard with scene descriptions
        storyboard_storage[storyboard_id]["message"] = "Generating scene descriptions..."
        storyboard_storage[storyboard_id]["progress"] = 20

        storyboard = await storyboard_agent.generate_storyboard(
            product_image=image_data,
            product_category=product_category,
            style=style,
            target_duration=target_duration,
        )

        # Step 2: Generate 2K images for each scene
        storyboard_storage[storyboard_id]["message"] = "Generating scene images (2K)..."
        storyboard_storage[storyboard_id]["progress"] = 40

        storyboard = await storyboard_agent.generate_scene_images(
            storyboard=storyboard,
            resolution="2048x2048"
        )

        # Step 3: Generate video clips for each scene
        storyboard_storage[storyboard_id]["message"] = "Converting images to video clips..."
        storyboard_storage[storyboard_id]["progress"] = 70

        storyboard = await storyboard_agent.generate_scene_videos(
            storyboard=storyboard,
            video_duration=1.5
        )

        # Export grid format
        storyboard_storage[storyboard_id]["message"] = "Finalizing storyboard..."
        storyboard_storage[storyboard_id]["progress"] = 90

        grid_data = storyboard_agent.export_storyboard_grid(storyboard)

        # Store completed storyboard
        storyboard_storage[storyboard_id] = {
            "status": "completed",
            "progress": 100,
            "message": "Storyboard generation completed",
            "storyboard": grid_data,
        }

    except Exception as e:
        storyboard_storage[storyboard_id] = {
            "status": "failed",
            "progress": 0,
            "message": f"Error: {str(e)}",
            "storyboard": None,
        }


@router.get("/{storyboard_id}", response_model=dict)
async def get_storyboard(storyboard_id: str):
    """
    Get storyboard status and data.

    Returns current progress during generation,
    or complete storyboard data when finished.
    """

    if storyboard_id not in storyboard_storage:
        raise HTTPException(status_code=404, detail="Storyboard not found")

    data = storyboard_storage[storyboard_id]

    return {
        "storyboard_id": storyboard_id,
        "status": data["status"],
        "progress": data["progress"],
        "message": data["message"],
        "storyboard": data["storyboard"],
    }


@router.get("/{storyboard_id}/scenes", response_model=List[dict])
async def get_storyboard_scenes(storyboard_id: str):
    """Get all scenes from a storyboard as a flat list"""

    if storyboard_id not in storyboard_storage:
        raise HTTPException(status_code=404, detail="Storyboard not found")

    data = storyboard_storage[storyboard_id]

    if data["status"] != "completed" or not data["storyboard"]:
        raise HTTPException(
            status_code=400,
            detail=f"Storyboard not ready. Status: {data['status']}"
        )

    # Flatten grid to list
    scenes = []
    for row in data["storyboard"]["grid"]:
        scenes.extend(row)

    return scenes


@router.post("/{storyboard_id}/regenerate-scene/{scene_number}")
async def regenerate_scene(
    storyboard_id: str,
    scene_number: int,
    custom_prompt: Optional[str] = Form(None),
):
    """Regenerate a specific scene with an optional custom prompt"""

    if storyboard_id not in storyboard_storage:
        raise HTTPException(status_code=404, detail="Storyboard not found")

    if scene_number < 1 or scene_number > 9:
        raise HTTPException(status_code=400, detail="Scene number must be between 1 and 9")

    data = storyboard_storage[storyboard_id]

    if data["status"] != "completed" or not data["storyboard"]:
        raise HTTPException(
            status_code=400,
            detail="Storyboard must be completed before regenerating scenes"
        )

    # TODO: Implement scene regeneration with custom prompt
    # This would update just one scene in the storyboard

    return {
        "message": f"Scene {scene_number} regeneration started",
        "storyboard_id": storyboard_id,
    }


@router.post("/{storyboard_id}/compile-video")
async def compile_video(
    storyboard_id: str,
    background_tasks: BackgroundTasks,
    include_music: bool = Form(True),
    include_voiceover: bool = Form(False),
    transition_style: str = Form("fade"),
):
    """
    Compile all scene videos into a final advertisement video.

    Combines the 9 scene clips (1-2 seconds each) into a cohesive ad.
    """

    if storyboard_id not in storyboard_storage:
        raise HTTPException(status_code=404, detail="Storyboard not found")

    data = storyboard_storage[storyboard_id]

    if data["status"] != "completed" or not data["storyboard"]:
        raise HTTPException(
            status_code=400,
            detail="Storyboard must be completed before compiling video"
        )

    # Start video compilation in background
    video_id = str(uuid.uuid4())

    # TODO: Implement video compilation
    # - Collect all scene video URLs
    # - Add transitions between scenes
    # - Add background music (optional)
    # - Add voiceover (optional)
    # - Render final video

    return {
        "message": "Video compilation started",
        "video_id": video_id,
        "storyboard_id": storyboard_id,
        "estimated_duration": data["storyboard"]["total_duration"],
    }


@router.delete("/{storyboard_id}")
async def delete_storyboard(storyboard_id: str):
    """Delete a storyboard and its associated assets"""

    if storyboard_id not in storyboard_storage:
        raise HTTPException(status_code=404, detail="Storyboard not found")

    del storyboard_storage[storyboard_id]

    return {"message": "Storyboard deleted successfully"}
