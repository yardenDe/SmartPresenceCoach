from sqlalchemy.orm import Session as DBSession
from models.session import Session 
from datetime import datetime

class SessionRepository:
    def __init__(self, db: DBSession):
        self.db = db

    def create_session(self, user_id: int) -> Session:
        session = Session(user_id=user_id)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def start_session(self, session_id: int) -> Session | None:
        session = self.db.get(Session, session_id)
        if session:
            session.start_time = datetime.now()
            self.db.commit()
            self.db.refresh(session)
        return session

    def end_session(self, session_id: int) -> Session | None:
        session = self.db.get(Session, session_id)
        if session:
            session.end_time = datetime.now()
            self.db.commit()
            self.db.refresh(session)
        return session
    
    def get_by_id(self, session_id: int) -> Session | None:
        return self.db.get(Session, session_id)
        
