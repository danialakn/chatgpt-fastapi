from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession
from services.chat_service import ChatService
import asyncio
from fastapi import HTTPException


@shared_task
def process_chat_task(user_id: int, prompt: str):
    async def _process():
        async with AsyncSession() as db:
            service = ChatService(db)
            response = await service.send_to_gpt(prompt)
            if "429" in str(response) or "quota" in str(response).lower():
                return {"error": True, "status_code": 429, "detail": "rate limit exceeded"}

            chat_msg = await service.save_message(user_id, prompt, response)
            return {
                "id": chat_msg.id,
                "prompt": chat_msg.prompt,
                "response": chat_msg.response
            }

    return asyncio.run(_process())
