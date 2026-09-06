from pydantic import BaseModel

<<<<<<< Updated upstream
from schemas.analysis import AnalysisResponse
=======
from schemas.analysis import Analysis
>>>>>>> Stashed changes


class LiveResponse(BaseModel):
    session_id: int
<<<<<<< Updated upstream
    result: AnalysisResponse
=======
    timestamp: float
    analysis: Analysis
>>>>>>> Stashed changes
