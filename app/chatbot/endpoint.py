from fastapi import APIRouter, Request, HTTPException, Response

from app.chatbot.messages import *
from app.chatbot.user_flow import handle_flow


router = APIRouter()


@router.post("/")
async def webhook(request: Request, response: Response):
    try:
        body_bytes = await request.body()
        message = Message(body_bytes)
        if not (message.body_content or message.num_media) or not message.from_number:
            raise AttributeError

        await handle_flow(message)

        return {"message": "Received", "from": message.from_number}

    except AttributeError:
        error_message = "Invalid message format. Please ensure the message is correctly formatted."
        response.status_code = 400
        return {"error": error_message}

    except HTTPException as http_exc:
        response.status_code = http_exc.status_code
        return {"error": http_exc.detail}

    except Exception as exc:
        response.status_code = 500
        print(f'Exception: {exc}')
        return {"error": "An unexpected error occurred. Please try again later."}
