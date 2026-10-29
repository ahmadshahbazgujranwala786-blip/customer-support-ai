from fastapi import APIRouter
from app.schemas import message
from app.services.normalizer import normalize

router = APIRouter()
CustomerRequest = message.CustomerRequest


@router.post("/process-message")
async def process_message(request: dict):

    normalized_request = normalize(request)

    return {
        "status": "success",
        "data": normalized_request
    }