from fastapi import APIRouter,HTTPException, status, Depends

from schemas.chat_schemas import ChatRequest , ChatResponse ,ChatID
from dependencies import SessionDep
from jwt_auth import JWTBearer , decode_jwt

from celery.result import AsyncResult
from tasks.chat_tasks import process_chat_task
from celery_app import celery_app

router = APIRouter()

@router.post("/chat/{user_id}", response_model=ChatID ,status_code=status.HTTP_200_OK)
async def ask_from_gpt(user_id: int, data: ChatRequest, session: SessionDep, token=Depends(JWTBearer())):

    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(status_code=403, detail="Invalid or expired token.")

    user_identifier = str(decode_jwt(token)["user_id"])
    if str(user_id) != str(user_identifier):
        raise HTTPException(status_code=403, detail="not owner")

    task = process_chat_task.delay(user_id, data.prompt)

    return {"task_id": task.id}



@router.get("/chat/{user_id}/result/{task_id}", response_model=ChatResponse)
async def get_task_result(user_id: int,task_id: str,session: SessionDep, token=Depends(JWTBearer())):

    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(status_code=403, detail="Invalid or expired token.")

    user_identifier = str(decode_jwt(token)["user_id"])
    if str(user_id) != str(user_identifier):
        raise HTTPException(status_code=403, detail="not owner")

    task_result = AsyncResult(task_id, app=celery_app)
    result = task_result.get()
    if result.get("error"):  # بررسی خطا
        raise HTTPException(
            status_code=result["status_code"],
            detail=result["detail"]
        )

    if not task_result.ready():
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="Task is still processing")


    result = task_result.get()
    return result