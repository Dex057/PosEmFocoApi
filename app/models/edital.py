from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Edital:
    titulo: str
    link: str
    data_publicacao: Optional[datetime] = None
    resumo: Optional[str] = None
    
  