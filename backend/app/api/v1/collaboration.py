"""
Collaboration API Endpoints

Real-time collaboration for video projects.
"""

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any

from app.db import get_db
from app.core.security import get_current_user_id
from app.services.collaboration_service import (
    collaboration_service,
    CollaboratorRole,
    ActionType,
)

router = APIRouter()


class CreateSessionRequest(BaseModel):
    project_id: str


class JoinSessionRequest(BaseModel):
    session_id: str


class InviteRequest(BaseModel):
    session_id: str
    email: EmailStr
    role: str = "editor"


class ActionRequest(BaseModel):
    session_id: str
    action_type: str
    data: Dict[str, Any]
    base_version: int


class ChatMessageRequest(BaseModel):
    session_id: str
    message: str


class CursorUpdateRequest(BaseModel):
    session_id: str
    position: Dict[str, Any]


class SelectionUpdateRequest(BaseModel):
    session_id: str
    selection: Dict[str, Any]


class CollaboratorResponse(BaseModel):
    user_id: str
    email: str
    name: str
    role: str
    color: str
    avatar_url: Optional[str]
    cursor_position: Optional[Dict[str, Any]]
    current_selection: Optional[Dict[str, Any]]
    last_active: str


class SessionResponse(BaseModel):
    session_id: str
    project_id: str
    current_version: int
    collaborators: List[CollaboratorResponse]
    recent_chat: List[Dict[str, Any]]


@router.post("/sessions", response_model=SessionResponse)
async def create_collaboration_session(
    request: CreateSessionRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new collaboration session for a project.

    Only the project owner can create a session.
    """
    # In production, verify user owns the project
    # For now, use mock user data
    session = await collaboration_service.create_session(
        project_id=request.project_id,
        owner_id=user_id,
        owner_email="user@example.com",
        owner_name="Project Owner",
    )

    state = collaboration_service.get_session_state(session.session_id)
    return SessionResponse(**state)


@router.post("/sessions/join", response_model=CollaboratorResponse)
async def join_collaboration_session(
    request: JoinSessionRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Join an existing collaboration session.
    """
    collaborator = await collaboration_service.join_session(
        session_id=request.session_id,
        user_id=user_id,
        user_email="collaborator@example.com",
        user_name="Collaborator",
        role=CollaboratorRole.EDITOR,
    )

    if not collaborator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return CollaboratorResponse(
        user_id=collaborator.user_id,
        email=collaborator.email,
        name=collaborator.name,
        role=collaborator.role.value,
        color=collaborator.color,
        avatar_url=collaborator.avatar_url,
        cursor_position=collaborator.cursor_position,
        current_selection=collaborator.current_selection,
        last_active=collaborator.last_active.isoformat(),
    )


@router.post("/sessions/leave")
async def leave_collaboration_session(
    request: JoinSessionRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Leave a collaboration session.
    """
    success = await collaboration_service.leave_session(
        session_id=request.session_id,
        user_id=user_id,
    )

    return {"success": success}


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session_state(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Get the current state of a collaboration session.
    """
    state = collaboration_service.get_session_state(session_id)

    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return SessionResponse(**state)


@router.get("/sessions/{session_id}/collaborators")
async def get_active_collaborators(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Get list of active collaborators in a session.
    """
    collaborators = collaboration_service.get_active_collaborators(session_id)
    return {"collaborators": collaborators}


@router.post("/invite")
async def invite_collaborator(
    request: InviteRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Invite a new collaborator to a session.
    """
    try:
        role = CollaboratorRole(request.role)
    except ValueError:
        role = CollaboratorRole.EDITOR

    result = await collaboration_service.invite_collaborator(
        session_id=request.session_id,
        inviter_id=user_id,
        invitee_email=request.email,
        role=role,
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to create invitation"),
        )

    return result


@router.post("/actions")
async def apply_action(
    request: ActionRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Apply an action to the collaboration session.

    Uses operational transformation for conflict resolution.
    """
    try:
        action_type = ActionType(request.action_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action type: {request.action_type}",
        )

    action = await collaboration_service.apply_action(
        session_id=request.session_id,
        user_id=user_id,
        action_type=action_type,
        data=request.data,
        base_version=request.base_version,
    )

    if not action:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to apply action",
        )

    return {
        "action_id": action.action_id,
        "version": action.version,
    }


@router.post("/cursor")
async def update_cursor(
    request: CursorUpdateRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Update cursor position for presence awareness.
    """
    success = await collaboration_service.update_cursor(
        session_id=request.session_id,
        user_id=user_id,
        position=request.position,
    )

    return {"success": success}


@router.post("/selection")
async def update_selection(
    request: SelectionUpdateRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Update selection for presence awareness.
    """
    success = await collaboration_service.update_selection(
        session_id=request.session_id,
        user_id=user_id,
        selection=request.selection,
    )

    return {"success": success}


@router.post("/chat")
async def send_chat_message(
    request: ChatMessageRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Send a chat message in the collaboration session.
    """
    message = await collaboration_service.send_chat_message(
        session_id=request.session_id,
        user_id=user_id,
        message=request.message,
    )

    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to send message",
        )

    return message


@router.websocket("/ws/{session_id}")
async def collaboration_websocket(
    websocket: WebSocket,
    session_id: str,
):
    """
    WebSocket endpoint for real-time collaboration.
    """
    await websocket.accept()

    # Get user_id from token (simplified for demo)
    user_id = None

    try:
        # Wait for authentication message
        auth_data = await websocket.receive_json()
        user_id = auth_data.get("user_id")

        if not user_id:
            await websocket.close(code=4001, reason="Authentication required")
            return

        # Register connection
        if session_id not in collaboration_service.websocket_connections:
            collaboration_service.websocket_connections[session_id] = {}
        collaboration_service.websocket_connections[session_id][user_id] = websocket

        # Send current state
        state = collaboration_service.get_session_state(session_id)
        if state:
            await websocket.send_json({
                "type": "session_state",
                "data": state,
            })

        # Listen for messages
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "cursor":
                await collaboration_service.update_cursor(
                    session_id=session_id,
                    user_id=user_id,
                    position=data.get("position", {}),
                )

            elif message_type == "selection":
                await collaboration_service.update_selection(
                    session_id=session_id,
                    user_id=user_id,
                    selection=data.get("selection", {}),
                )

            elif message_type == "action":
                try:
                    action_type = ActionType(data.get("action_type"))
                    await collaboration_service.apply_action(
                        session_id=session_id,
                        user_id=user_id,
                        action_type=action_type,
                        data=data.get("data", {}),
                        base_version=data.get("base_version", 0),
                    )
                except ValueError:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Invalid action type: {data.get('action_type')}",
                    })

            elif message_type == "chat":
                await collaboration_service.send_chat_message(
                    session_id=session_id,
                    user_id=user_id,
                    message=data.get("message", ""),
                )

            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        pass
    finally:
        # Cleanup
        if user_id and session_id in collaboration_service.websocket_connections:
            collaboration_service.websocket_connections[session_id].pop(user_id, None)
            await collaboration_service.leave_session(session_id, user_id)
