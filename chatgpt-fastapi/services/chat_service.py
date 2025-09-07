from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI
from models.chat_models import ChatMessage
from time import time
from fastapi import HTTPException
import os



OPENAI_API_KEY =  os.getenv("OPENAI_API_KEY")

class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    async def send_to_gpt(self, prompt: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

        except Exception as e:
            msg = str(e)
            if "429" in msg or "quota" in msg.lower():
                return msg
            return f"  API problem: {msg}"

    async def save_message(self, user_id: int, prompt: str, response: str) -> ChatMessage:
        chat_msg = ChatMessage(
            user_id=user_id,
            prompt=prompt,
            response=response,
            created_at=int(time())
        )
        self.db.add(chat_msg)
        await self.db.commit()
        await self.db.refresh(chat_msg)
        return chat_msg

    async def get_message(self, chat_id: int, user_id: int) -> ChatMessage:
        chat_msg = await self.db.get(ChatMessage, chat_id)

        if not chat_msg or chat_msg.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not owner")

        return chat_msg