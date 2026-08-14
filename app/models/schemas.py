from pydantic import BaseModel
from typing import Optional
class TournamentCreate(BaseModel):
    name:str
    date:str
    location:Optional[str]=None
    mode:str="solo"
    manufacturer:Optional[str]=None
    piece_count:Optional[int]=None
    time_limit_minutes:Optional[int]=None
    notes:Optional[str]=None
