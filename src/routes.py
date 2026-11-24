from typing import Annotated
from fastapi import APIRouter, HTTPException, Path, Response
from src import service
from src.models import DropCreate, DropCreated, DropOut

Token = Annotated[str, Path(min_length=20, max_length=100)]

router = APIRouter(prefix="/drops")

@router.post("", response_model=DropCreated, status_code=201)
def create_drop(body: DropCreate, response: Response):
    response.headers["Cache-Control"] = "no-store"
    token = service.create_drop(body.secret, body.max_views, body.ttl_seconds)
    return {"token": token}

@router.get("/{token}", response_model=DropOut)
def open_drop(token: Token, response: Response):
    response.headers["Cache-Control"] = "no-store"
    try:
        return {"secret": service.consume_drop(token)}
    except service.DropNotFound:
        raise HTTPException(status_code=404, detail="Drop not found")
    except service.DropGone:
        raise HTTPException(status_code=410, detail="Drop expired or already used")
