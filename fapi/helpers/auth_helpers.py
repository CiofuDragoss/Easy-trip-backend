import aiosmtplib
from email.message import EmailMessage
from fapi.models import Code, User
from fastapi import HTTPException
import random
import asyncio

email_semaphore = asyncio.Semaphore(3)


async def send_email(recipient: str, code: str):
    async with email_semaphore:
        message = EmailMessage()
        message["From"] = "nume@domeniul-tau.com"
        message["To"] = recipient
        message["Subject"] = "Cod EasyTrip"
        message.set_content(f"Salut! Codul tau este: {code}.Expira in 15 minute.")

        await aiosmtplib.send(
            message,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username="dragoscoff@gmail.com",
            password="yijx wzyy lfbl gfjc",
        )


async def send_verification_code_email(email: str) -> None:
    user = await User.find_one(User.email == email)
    if not user:
        raise HTTPException(404, detail="Emailul nu este inregistrat")

    existing_code = await Code.find_one(Code.email == email)
    if existing_code:
        code = existing_code.code
    else:
        code = str(random.randint(100000, 999999))
        await Code(email=email, code=code).insert()

    await send_email(email, code)


async def validate_code(email: str, code: str) -> bool:
    existing_code = await Code.find_one(Code.email == email, Code.code == code)
    return existing_code is not None
