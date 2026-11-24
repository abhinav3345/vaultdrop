from pydantic import BaseModel, Field

class DropCreate(BaseModel):
    secret: str = Field(min_length=1, max_length=10_000)
    max_views: int = Field(default=1, ge=1, le=100)
    ttl_seconds: int = Field(default=3600, ge=1, le=604_800)

class DropCreated(BaseModel):
    token: str

class DropOut(BaseModel):
    secret: str
