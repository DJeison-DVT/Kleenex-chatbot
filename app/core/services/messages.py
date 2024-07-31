from bson import ObjectId
from datetime import datetime

from app.schemas.user import User
from app.db.db import _MongoClientSingleton, MessagesCollection
from app.core.services.datetime_mexico import *
from app.core.config import settings


async def save_message(message_sid: str, user: User, from_user: bool = False):
    async with await _MongoClientSingleton().mongo_client.start_session() as session:
        async with session.start_transaction():
            try:
                document = {
                    "client_id": ObjectId(user.id),
                    "from": user.phone if from_user else settings.BUSINESS_NUMBER,
                    "to": settings.BUSINESS_NUMBER if from_user else user.phone,
                    "message_sid": message_sid,
                    "datetime": get_current_datetime(),
                }

                await MessagesCollection().insert_one(document, session=session)

            except Exception as e:
                print(e)
                await session.abort_transaction()
                raise e
