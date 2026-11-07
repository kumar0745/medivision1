import httpx
from .config import settings

class EmailDeliveryUnavailable(RuntimeError):
    pass

def send_password_reset_email(recipient: str, reset_url: str) -> None:
    if not settings.email_configured:
        raise EmailDeliveryUnavailable("Password-reset email delivery is not configured.")
    response = httpx.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {settings.resend_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "from": settings.email_from,
            "to": [recipient],
            "subject": "Reset your MediVision password",
            "html": (
                "<p>We received a request to reset your MediVision password.</p>"
                f'<p><a href="{reset_url}">Choose a new password</a></p>'
                "<p>This link expires in 30 minutes and can only be used once. "
                "If you did not request this, you can ignore this message.</p>"
            ),
        },
        timeout=10.0,
    )
    response.raise_for_status()
