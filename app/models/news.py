from pydantic import BaseModel,  Field, root_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class NewsRequest(BaseModel):
    status: Optional[str] = None
    totalResults: Optional[int] = None
    article_id: str
    title: str
    link: str
    source_id: str
    source_url: str
    source_icon: Optional[str] = None
    source_priority: Optional[int] = None
    keywords: Optional[List[str]] = None
    creator: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    description: Optional[str] = None
    pubDate: Optional[datetime] = None
    pubDateTZ: Optional[str] = None
    content: Optional[str] = None
    country: Optional[str] = None
    category: Optional[List[str]] = None
    language: Optional[str] = None
    ai_tag: Optional[List[str]] = None
    sentiment: Optional[str] = None
    sentiment_stats: Optional[Dict[str, Any]] = None
    ai_region: Optional[str] = None
    ai_org: Optional[List[str]] = None
    duplicate: Optional[bool] = None
    coin: Optional[str] = None
    nextPage: Optional[str] = None



    class Config:
        from_attributes = True
    
class NewsItem(BaseModel):
    id: str  # ID único da notícia
    title: str  # Título
    description: Optional[str] = None  # Descrição curta
    content: Optional[str] = None  # Conteúdo completo, quando disponível
    url: str  # Link para a notícia
    source_name: str  # Nome da fonte (ex: "G1", "CNN", etc)
    source_url: Optional[str] = None  # URL da fonte
    image_url: Optional[str] = None  # URL da imagem principal
    published_at: Optional[datetime] = None  # Data de publicação
    category: Optional[List[str]] = None  # Categorias
    source_type: str = Field(..., description="'api' para notícias da API, 'web' para buscas na web")
