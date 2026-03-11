from config.settings import Settings
from starlette.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from typing import List
from fastapi import UploadFile, File, HTTPException

# pip install fastapi-mail pydantic-settings

class EmailContent(BaseModel):
    subject: str
    recipients: List[EmailStr]
    body: str
    template: str = None  # Ruta al template HTML (opcional)
    context: dict = None  # Contexto para renderizar el template (opcional)


class BaseNotification:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.mail_config = ConnectionConfig(
            MAIL_USERNAME=self.settings.EMAIL_HOST_USER,
            MAIL_PASSWORD=self.settings.EMAIL_HOST_PASSWORD,
            MAIL_FROM=self.settings.EMAIL_FROM,
            MAIL_PORT=self.settings.EMAIL_PORT,
            MAIL_SERVER=self.settings.EMAIL_HOST,
            MAIL_SSL_TLS=self.settings.EMAIL_USE_TLS,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        self.mailer = FastMail(self.mail_config)
        self.path_template = self.settings.EMAIL_PATH_TEMPLATE

    async def send_email(self, email_content: EmailContent) -> JSONResponse:
        message = MessageSchema(
            subject=email_content.subject,
            recipients=email_content.recipients,
            body=email_content.body,
            subtype=MessageType.html if email_content.template else MessageType.plain
        )

        try:
            await self.mailer.send_message(message)
            return JSONResponse(content={"message": "Email sent successfully"}, status_code=200)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)
        
    async def send_template_email(self, email_content: EmailContent) -> JSONResponse:
        if not email_content.template:
            return JSONResponse(content={"error": "Template path is required for template emails"}, status_code=400)
        
        path_template = f"{self.path_template}/{email_content.template}"

        message = MessageSchema(
            subject=email_content.subject,
            recipients=email_content.recipients,
            body=email_content.body,
            subtype=MessageType.html
        )

        try:
            await self.mailer.send_message(message, template=path_template, context=email_content.context)
            return JSONResponse(content={"message": "Template email sent successfully"}, status_code=200)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)
        
    async def send_file_email(self, email_content: EmailContent, file: UploadFile = File(...)) -> JSONResponse:
        message = MessageSchema(
            subject=email_content.subject,
            recipients=email_content.recipients,
            body=email_content.body,
            subtype=MessageType.html if email_content.template else MessageType.plain,
            attachments=[file]
        )

        try:
            await self.mailer.send_message(message)
            return JSONResponse(content={"message": "Email with attachment sent successfully"}, status_code=200)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)