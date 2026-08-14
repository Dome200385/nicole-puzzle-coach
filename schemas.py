from typing import Optional
from pydantic import BaseModel,Field
class TournamentCreate(BaseModel):
    name:str; date:str; location:Optional[str]=None; mode:str="solo"; manufacturer:Optional[str]=None
    piece_count:Optional[int]=None; time_limit_minutes:Optional[int]=None; priority:str="normal"
    international:bool=False; notes:Optional[str]=None
class TrainingSessionCreate(BaseModel):
    date:str; puzzle_name:str; puzzle_id:Optional[str]=None; manufacturer:Optional[str]=None
    piece_count:Optional[int]=None; mode:str="solo"; duration_seconds:Optional[int]=None
    target_seconds:Optional[int]=None; tournament_id:Optional[int]=None
    perceived_difficulty:Optional[float]=Field(default=None,ge=1,le=10); focus:Optional[str]=None; notes:Optional[str]=None
