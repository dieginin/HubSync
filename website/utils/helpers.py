import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from website.config import MAIL_CONFIG


def send_password_reset_email(email: str) -> None:
    from website import db_manager

    try:
        user = db_manager.get_user_by_email(email)
        if not user:
            return
        token = db_manager.generate_reset_password_token(user)
        reset_link = "https://hubsync.nextbale.com/reset_password/" + token

        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f9fafb; padding: 20px;">
                <div style="max-width: 500px; margin: auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    <h2 style="color: #333; text-align: center;">Reset Your Password</h2>
                    <p>Hello,</p>
                    <p>We received a request to reset your password. Click the button below to continue:</p>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" 
                           style="padding: 12px 25px; border-radius: 6px; font-weight: bold; display: inline-block;">
                            Reset Password
                        </a>
                    </div>

                    <p>If you didn't request a password reset, you can safely ignore this email.</p>
                    <p style="color: #888; font-size: 13px;">This link will expire in 1 hour.</p>

                    <hr style="border: none; border-top: 1px solid #eee; margin: 25px 0;">
                    <p style="text-align: center; font-size: 12px; color: #aaa;">
                        © 2025 HubSync — All rights reserved
                    </p>
                </div>
            </body>
        </html>
        """
        text = f"Click this link to reset your password: {reset_link}"
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Password Reset"
        msg["From"] = MAIL_CONFIG["AUTHOR"] + " <" + MAIL_CONFIG["SENDER"] + ">"
        msg["To"] = email
        msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL(MAIL_CONFIG["SERVER"], MAIL_CONFIG["PORT"]) as server:
            server.login(MAIL_CONFIG["USERNAME"], MAIL_CONFIG["PASSWORD"])
            server.sendmail(MAIL_CONFIG["USERNAME"], [email], msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")
