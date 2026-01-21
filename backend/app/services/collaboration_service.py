"""
Real-time Collaboration Service

Enables multiple users to collaborate on video projects in real-time.
"""

from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import json
import logging
import uuid

logger = logging.getLogger(__name__)


class CollaboratorRole(Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"
    COMMENTER = "commenter"


class ActionType(Enum):
    # Project actions
    PROJECT_UPDATE = "project_update"

    # Script actions
    SCRIPT_EDIT = "script_edit"
    SCRIPT_COMMENT = "script_comment"

    # Timeline actions
    TIMELINE_ADD_SCENE = "timeline_add_scene"
    TIMELINE_REMOVE_SCENE = "timeline_remove_scene"
    TIMELINE_REORDER = "timeline_reorder"

    # Style actions
    STYLE_UPDATE = "style_update"

    # Cursor/presence actions
    CURSOR_MOVE = "cursor_move"
    SELECTION_CHANGE = "selection_change"

    # Chat
    CHAT_MESSAGE = "chat_message"


@dataclass
class Collaborator:
    user_id: str
    email: str
    name: str
    role: CollaboratorRole
    color: str  # Unique color for cursor/selection
    avatar_url: Optional[str] = None
    joined_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    cursor_position: Optional[Dict[str, Any]] = None
    current_selection: Optional[Dict[str, Any]] = None


@dataclass
class CollaborationAction:
    action_id: str
    action_type: ActionType
    user_id: str
    timestamp: datetime
    data: Dict[str, Any]
    version: int


@dataclass
class CollaborationSession:
    session_id: str
    project_id: str
    created_at: datetime
    collaborators: Dict[str, Collaborator] = field(default_factory=dict)
    action_history: List[CollaborationAction] = field(default_factory=list)
    current_version: int = 0
    chat_messages: List[Dict[str, Any]] = field(default_factory=list)


class CollaborationService:
    """
    Manages real-time collaboration sessions for video projects.
    """

    # Color palette for collaborators
    COLLABORATOR_COLORS = [
        "#3B82F6",  # Blue
        "#10B981",  # Green
        "#F59E0B",  # Amber
        "#EF4444",  # Red
        "#8B5CF6",  # Purple
        "#EC4899",  # Pink
        "#06B6D4",  # Cyan
        "#F97316",  # Orange
    ]

    def __init__(self):
        self.sessions: Dict[str, CollaborationSession] = {}
        self.user_sessions: Dict[str, Set[str]] = {}  # user_id -> session_ids
        self.websocket_connections: Dict[str, Dict[str, Any]] = {}  # session_id -> {user_id: websocket}

    async def create_session(
        self,
        project_id: str,
        owner_id: str,
        owner_email: str,
        owner_name: str,
    ) -> CollaborationSession:
        """Create a new collaboration session for a project."""
        session_id = str(uuid.uuid4())

        owner = Collaborator(
            user_id=owner_id,
            email=owner_email,
            name=owner_name,
            role=CollaboratorRole.OWNER,
            color=self.COLLABORATOR_COLORS[0],
        )

        session = CollaborationSession(
            session_id=session_id,
            project_id=project_id,
            created_at=datetime.utcnow(),
            collaborators={owner_id: owner},
        )

        self.sessions[session_id] = session

        if owner_id not in self.user_sessions:
            self.user_sessions[owner_id] = set()
        self.user_sessions[owner_id].add(session_id)

        logger.info(f"Created collaboration session {session_id} for project {project_id}")
        return session

    async def join_session(
        self,
        session_id: str,
        user_id: str,
        user_email: str,
        user_name: str,
        role: CollaboratorRole = CollaboratorRole.EDITOR,
    ) -> Optional[Collaborator]:
        """Add a user to a collaboration session."""
        session = self.sessions.get(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found")
            return None

        if user_id in session.collaborators:
            # User already in session, update last_active
            session.collaborators[user_id].last_active = datetime.utcnow()
            return session.collaborators[user_id]

        # Assign unique color
        used_colors = {c.color for c in session.collaborators.values()}
        available_colors = [c for c in self.COLLABORATOR_COLORS if c not in used_colors]
        color = available_colors[0] if available_colors else self.COLLABORATOR_COLORS[len(session.collaborators) % len(self.COLLABORATOR_COLORS)]

        collaborator = Collaborator(
            user_id=user_id,
            email=user_email,
            name=user_name,
            role=role,
            color=color,
        )

        session.collaborators[user_id] = collaborator

        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = set()
        self.user_sessions[user_id].add(session_id)

        # Broadcast join event to other collaborators
        await self._broadcast_to_session(
            session_id,
            {
                "type": "collaborator_joined",
                "collaborator": self._collaborator_to_dict(collaborator),
            },
            exclude_user=user_id,
        )

        logger.info(f"User {user_id} joined session {session_id}")
        return collaborator

    async def leave_session(self, session_id: str, user_id: str) -> bool:
        """Remove a user from a collaboration session."""
        session = self.sessions.get(session_id)
        if not session or user_id not in session.collaborators:
            return False

        collaborator = session.collaborators[user_id]

        # Don't remove owner, just mark as inactive
        if collaborator.role == CollaboratorRole.OWNER:
            collaborator.last_active = datetime.utcnow()
        else:
            del session.collaborators[user_id]

        if user_id in self.user_sessions:
            self.user_sessions[user_id].discard(session_id)

        # Broadcast leave event
        await self._broadcast_to_session(
            session_id,
            {
                "type": "collaborator_left",
                "user_id": user_id,
            },
            exclude_user=user_id,
        )

        logger.info(f"User {user_id} left session {session_id}")
        return True

    async def apply_action(
        self,
        session_id: str,
        user_id: str,
        action_type: ActionType,
        data: Dict[str, Any],
        base_version: int,
    ) -> Optional[CollaborationAction]:
        """
        Apply an action to the session with operational transformation.
        """
        session = self.sessions.get(session_id)
        if not session:
            return None

        collaborator = session.collaborators.get(user_id)
        if not collaborator:
            return None

        # Check permissions
        if not self._can_perform_action(collaborator.role, action_type):
            logger.warning(f"User {user_id} not authorized for {action_type}")
            return None

        # Handle version conflicts (basic OT)
        if base_version < session.current_version:
            # Transform action based on intervening actions
            data = self._transform_action(
                data,
                action_type,
                session.action_history[base_version:],
            )

        # Create action
        session.current_version += 1
        action = CollaborationAction(
            action_id=str(uuid.uuid4()),
            action_type=action_type,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            data=data,
            version=session.current_version,
        )

        session.action_history.append(action)

        # Keep only last 1000 actions
        if len(session.action_history) > 1000:
            session.action_history = session.action_history[-1000:]

        # Update collaborator activity
        collaborator.last_active = datetime.utcnow()

        # Broadcast action to other collaborators
        await self._broadcast_to_session(
            session_id,
            {
                "type": "action",
                "action": self._action_to_dict(action),
            },
            exclude_user=user_id,
        )

        return action

    async def update_cursor(
        self,
        session_id: str,
        user_id: str,
        position: Dict[str, Any],
    ) -> bool:
        """Update a user's cursor position."""
        session = self.sessions.get(session_id)
        if not session or user_id not in session.collaborators:
            return False

        session.collaborators[user_id].cursor_position = position
        session.collaborators[user_id].last_active = datetime.utcnow()

        # Broadcast cursor update
        await self._broadcast_to_session(
            session_id,
            {
                "type": "cursor_update",
                "user_id": user_id,
                "position": position,
                "color": session.collaborators[user_id].color,
            },
            exclude_user=user_id,
        )

        return True

    async def update_selection(
        self,
        session_id: str,
        user_id: str,
        selection: Dict[str, Any],
    ) -> bool:
        """Update a user's selection."""
        session = self.sessions.get(session_id)
        if not session or user_id not in session.collaborators:
            return False

        session.collaborators[user_id].current_selection = selection

        # Broadcast selection update
        await self._broadcast_to_session(
            session_id,
            {
                "type": "selection_update",
                "user_id": user_id,
                "selection": selection,
                "color": session.collaborators[user_id].color,
            },
            exclude_user=user_id,
        )

        return True

    async def send_chat_message(
        self,
        session_id: str,
        user_id: str,
        message: str,
    ) -> Optional[Dict[str, Any]]:
        """Send a chat message in the session."""
        session = self.sessions.get(session_id)
        if not session or user_id not in session.collaborators:
            return None

        collaborator = session.collaborators[user_id]

        chat_message = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "user_name": collaborator.name,
            "color": collaborator.color,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }

        session.chat_messages.append(chat_message)

        # Keep only last 100 messages
        if len(session.chat_messages) > 100:
            session.chat_messages = session.chat_messages[-100:]

        # Broadcast message
        await self._broadcast_to_session(
            session_id,
            {
                "type": "chat_message",
                "message": chat_message,
            },
        )

        return chat_message

    def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state of a collaboration session."""
        session = self.sessions.get(session_id)
        if not session:
            return None

        return {
            "session_id": session.session_id,
            "project_id": session.project_id,
            "current_version": session.current_version,
            "collaborators": [
                self._collaborator_to_dict(c)
                for c in session.collaborators.values()
            ],
            "recent_chat": session.chat_messages[-20:],
        }

    def get_active_collaborators(self, session_id: str) -> List[Dict[str, Any]]:
        """Get list of active collaborators in a session."""
        session = self.sessions.get(session_id)
        if not session:
            return []

        # Consider active if last_active within 5 minutes
        cutoff = datetime.utcnow().timestamp() - 300

        return [
            self._collaborator_to_dict(c)
            for c in session.collaborators.values()
            if c.last_active.timestamp() > cutoff
        ]

    async def invite_collaborator(
        self,
        session_id: str,
        inviter_id: str,
        invitee_email: str,
        role: CollaboratorRole = CollaboratorRole.EDITOR,
    ) -> Dict[str, Any]:
        """Generate an invitation for a new collaborator."""
        session = self.sessions.get(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}

        inviter = session.collaborators.get(inviter_id)
        if not inviter or inviter.role not in [CollaboratorRole.OWNER, CollaboratorRole.EDITOR]:
            return {"success": False, "error": "Not authorized to invite"}

        invite_token = str(uuid.uuid4())

        return {
            "success": True,
            "invite_url": f"https://saiad.io/collaborate/{session_id}?token={invite_token}",
            "invitee_email": invitee_email,
            "role": role.value,
            "expires_at": (datetime.utcnow().timestamp() + 86400),  # 24 hours
        }

    def _can_perform_action(self, role: CollaboratorRole, action_type: ActionType) -> bool:
        """Check if a role can perform an action type."""
        if role == CollaboratorRole.OWNER:
            return True

        if role == CollaboratorRole.EDITOR:
            return action_type != ActionType.PROJECT_UPDATE

        if role == CollaboratorRole.COMMENTER:
            return action_type in [
                ActionType.SCRIPT_COMMENT,
                ActionType.CHAT_MESSAGE,
                ActionType.CURSOR_MOVE,
                ActionType.SELECTION_CHANGE,
            ]

        # Viewer can only move cursor and chat
        return action_type in [ActionType.CURSOR_MOVE, ActionType.CHAT_MESSAGE]

    def _transform_action(
        self,
        data: Dict[str, Any],
        action_type: ActionType,
        intervening_actions: List[CollaborationAction],
    ) -> Dict[str, Any]:
        """
        Transform an action based on intervening actions (Operational Transformation).
        This is a simplified version - production would need more sophisticated OT.
        """
        # For text edits, adjust positions based on intervening insertions/deletions
        if action_type == ActionType.SCRIPT_EDIT and "position" in data:
            offset = 0
            for action in intervening_actions:
                if action.action_type == ActionType.SCRIPT_EDIT:
                    if action.data.get("position", 0) <= data["position"]:
                        if action.data.get("type") == "insert":
                            offset += len(action.data.get("text", ""))
                        elif action.data.get("type") == "delete":
                            offset -= action.data.get("length", 0)

            data["position"] = data["position"] + offset

        return data

    async def _broadcast_to_session(
        self,
        session_id: str,
        message: Dict[str, Any],
        exclude_user: Optional[str] = None,
    ):
        """Broadcast a message to all connected users in a session."""
        connections = self.websocket_connections.get(session_id, {})

        for user_id, websocket in connections.items():
            if user_id != exclude_user:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send to user {user_id}: {e}")

    def _collaborator_to_dict(self, collaborator: Collaborator) -> Dict[str, Any]:
        return {
            "user_id": collaborator.user_id,
            "email": collaborator.email,
            "name": collaborator.name,
            "role": collaborator.role.value,
            "color": collaborator.color,
            "avatar_url": collaborator.avatar_url,
            "cursor_position": collaborator.cursor_position,
            "current_selection": collaborator.current_selection,
            "last_active": collaborator.last_active.isoformat(),
        }

    def _action_to_dict(self, action: CollaborationAction) -> Dict[str, Any]:
        return {
            "action_id": action.action_id,
            "action_type": action.action_type.value,
            "user_id": action.user_id,
            "timestamp": action.timestamp.isoformat(),
            "data": action.data,
            "version": action.version,
        }


# Global instance
collaboration_service = CollaborationService()
