
class FrameBuffer:
    def __init__(self, max_len):
        self.max_len=max_len
        self.sessions = {}

    def add(self, session_id, frame):
        self.sessions[session_id] = frame


    
