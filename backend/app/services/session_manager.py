"""
Session management for farmer interactions.

Stores session state in memory (can be swapped for Redis/DB later).

Each session tracks:
- Current parameter being collected
- All answers collected so far
- Language preference
- Helper mode status
"""

import uuid
import time
from typing import Dict, Optional
from ..models import SessionState, Language, SoilTestResult


class SessionManager:
    """
    In-memory session storage.
    
    For production, replace with Redis or database.
    """
    
    def __init__(self):
        """Initialize empty session store."""
        self._sessions: Dict[str, SessionState] = {}
    
    def create_session(self, language: Language) -> SessionState:
        """
        Create a new session for a farmer.
        
        Args:
            language: Selected language ("hi" or "en")
            
        Returns:
            New SessionState with session_id and initial state
        """
        session_id = str(uuid.uuid4())
        now = time.time()
        
        session = SessionState(
            session_id=session_id,
            language=language,
            current_parameter="name",  # First parameter (NEW: name before color)
            answers=SoilTestResult(),
            helper_mode=False,
            created_at=now,
            updated_at=now,
        )
        
        self._sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionState]:
        """
        Retrieve a session by ID.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            SessionState if found, None otherwise
        """
        return self._sessions.get(session_id)
    
    def update_session(self, session: SessionState) -> None:
        """
        Update an existing session.
        
        Args:
            session: Updated SessionState to store
        """
        session.updated_at = time.time()
        self._sessions[session.session_id] = session
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session (cleanup).
        
        Args:
            session_id: Session to delete
            
        Returns:
            True if deleted, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False


# Global session manager instance
session_manager = SessionManager()

