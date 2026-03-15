"""
OMNIMIND AI — tools/email_sender.py
Sends the intelligence report to any email address via Gmail SMTP.
Requires in .env:
    EMAIL_SENDER=nishanth.artwork@gmail.com
    EMAIL_APP_PASSWORD=bvqx taik gsfs qwih
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text       import MIMEText
from email.mime.base       import MIMEBase
from email                 import encoders
from datetime              import datetime
from dotenv                import load_dotenv

load_dotenv()


def send_report_email(
    to_email: str,
    company:  str,
    research: str,
    stock:    str,
    news:     str,
    report:   str,
    pdf_path: str = None,
) -> dict:
    """
    Send OMNIMIND intelligence report by Gmail SMTP.
    Returns: {"success": bool, "message": str}
    """
    sender   = os.getenv("EMAIL_SENDER", "")
    password = os.getenv("EMAIL_APP_PASSWORD", "") or os.getenv("EMAIL_PASSWORD", "")

    if not sender or not password:
        return {
            "success": False,
            "message": (
                "EMAIL_SENDER or EMAIL_APP_PASSWORD not set in .env file.\n\n"
                "To fix this:\n"
                "1. Go to https://myaccount.google.com/apppasswords\n"
                "2. Sign in to your Google account\n"
                "3. Select 'Mail' as the app and 'Windows Computer' as the device\n"
                "4. Click 'Generate' and copy the 16-character password\n"
                "5. Add to your .env file:\n"
                "   EMAIL_SENDER=your_email@gmail.com\n"
                "   EMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx"
            ),
        }

    def _section(icon, title, content):
        rows = "".join(
            f"<tr><td style='padding:6px 0;color:#222;font-size:13px;"
            f"border-bottom:1px solid #f0f0f0;'>{line}</td></tr>"
            for line in content.split("\n") if line.strip()
        )
        return f"""
        <div style="margin:18px 0;background:#fff;border-radius:10px;
                    border-left:4px solid #cc5500;padding:18px 22px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);">
          <h3 style="margin:0 0 12px;color:#cc5500;font-size:14px;
                     text-transform:uppercase;letter-spacing:1px;">
            {icon} {title}
          </h3>
          <table style="width:100%;border-collapse:collapse;">{rows}</table>
        </div>
        """

    now_str  = datetime.now().strftime("%d %B %Y, %I:%M %p")
    html_body = f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"></head>
    <body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;">
      <div style="max-width:680px;margin:30px auto;background:#fafafa;
                  border-radius:14px;overflow:hidden;
                  box-shadow:0 4px 24px rgba(0,0,0,0.1);">

        <!-- Header -->
        <div style="background:linear-gradient(135deg,#1a1a1a,#2d1500);
                    padding:32px 30px;text-align:center;">
          <h1 style="margin:0;color:#ff8c00;font-size:28px;letter-spacing:3px;">
            ⚡ OMNIMIND AI
          </h1>
          <p style="margin:6px 0 0;color:#ffcc00;font-size:11px;
                    text-transform:uppercase;letter-spacing:2px;">
            Autonomous Business Intelligence Report
          </p>
        </div>

        <!-- Company Banner -->
        <div style="background:#cc5500;padding:16px 30px;text-align:center;">
          <h2 style="margin:0;color:#fff;font-size:22px;letter-spacing:2px;">
            🎯 {company.upper()}
          </h2>
          <p style="margin:4px 0 0;color:rgba(255,255,255,0.8);font-size:11px;">
            Scan Date: {now_str}
          </p>
        </div>

        <!-- Content -->
        <div style="padding:24px 28px;">
          {_section("📊", "Executive Intelligence Report", report)}
          {_section("🔬", "Research Intelligence",         research)}
          {_section("📈", "Stock Market Analysis",         stock)}
          {_section("📰", "News Intelligence",             news)}
        </div>

        <!-- Footer -->
        <div style="background:#1a1a1a;padding:18px 30px;text-align:center;">
          <p style="margin:0;color:#666;font-size:11px;">
            OMNIMIND AI · Autonomous Business Intelligence · Built by Nishanth R
          </p>
          {"<p style='margin:6px 0 0;color:#ff8c00;font-size:11px;'>📎 PDF Report attached</p>" if pdf_path else ""}
        </div>

      </div>
    </body></html>
    """

    try:
        msg = MIMEMultipart("mixed")
        msg["From"]    = sender
        msg["To"]      = to_email
        msg["Subject"] = f"⚡ OMNIMIND AI — {company} Intelligence Report | {now_str}"
        msg.attach(MIMEText(html_body, "html"))

        # Attach PDF if provided and valid
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            fname = os.path.basename(pdf_path)
            part.add_header("Content-Disposition", f'attachment; filename="{fname}"')
            msg.attach(part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())

        return {"success": True,
                "message": f"Report sent to {to_email}!"}

    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "message": (
                "Gmail authentication failed. You need a Gmail App Password, NOT your regular password.\n\n"
                "Steps to fix:\n"
                "1. Go to https://myaccount.google.com/apppasswords\n"
                "2. Generate a new App Password for 'Mail'\n"
                "3. Update EMAIL_APP_PASSWORD in your .env file with the 16-character password\n"
                "4. Make sure 2-Step Verification is enabled on your Google account"
            ),
        }
    except Exception as e:
        return {"success": False, "message": f"Email error: {str(e)}"}
