import uuid
from typing import List, Dict, Optional
from datetime import datetime

class InterviewSession:
    def __init__(self, session_id: str, questions: List[str]):
        self.session_id = session_id
        self.questions = questions
        self.current_index = 0
        self.answers: List[str] = []
        self.feedbacks: Dict[int, Dict] = {}
        self.is_completed: bool = False
        self.created_at = datetime.now()
        self.pre_generated_audio: Dict[int, str] = {} # Map index -> relative_path

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, InterviewSession] = {}

    def create_session(self, questions: List[str]) -> str:
        session_id = str(uuid.uuid4())[:8]
        session = InterviewSession(session_id, questions)
        self.sessions[session_id] = session
        return session_id

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        return self.sessions.get(session_id)

    def get_current_question(self, session_id: str) -> Optional[str]:
        session = self.get_session(session_id)
        if not session:
            return None
        
        if session.current_index < len(session.questions):
            return session.questions[session.current_index]
        return None

    def submit_answer(self, session_id: str, answer: str, feedback: dict = None) -> bool:
        """
        Saves answer, optionally saves feedback, and advances to next question.
        Returns True if successful, False if session invalid or finished.
        """
        session = self.get_session(session_id)
        if not session or session.is_completed:
            return False
            
        session.answers.append(answer)
        if feedback:
            session.feedbacks[session.current_index] = feedback
            
        session.current_index += 1
        
        if session.current_index >= len(session.questions):
            session.is_completed = True
            
        return True

    def add_feedback(self, session_id: str, index: int, feedback: dict):
        """
        Asynchronously adds feedback to the session without advancing the question.
        Used for background grading.
        """
        session = self.get_session(session_id)
        if session:
            session.feedbacks[index] = feedback

    def set_cached_audio(self, session_id: str, index: int, path: str):
        session = self.get_session(session_id)
        if session:
            session.pre_generated_audio[index] = path

    def get_cached_audio(self, session_id: str, index: int) -> Optional[str]:
        session = self.get_session(session_id)
        if session:
            return session.pre_generated_audio.get(index)
        return None

    def get_all_feedback(self, session_id: str) -> Optional[List[Dict]]:
        session = self.get_session(session_id)
        if not session:
            return None
        # Return sorted by index
        return [session.feedbacks[i] for i in sorted(session.feedbacks.keys())]

    def is_finished(self, session_id: str) -> bool:
        session = self.get_session(session_id)
        if not session:
            return True # Treat invalid as finished/error
        return session.is_completed # Use the new is_completed attribute

# Global Instance
session_manager = SessionManager()
