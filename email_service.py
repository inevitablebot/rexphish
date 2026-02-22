import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_campaign_email(sender_email, sender_password, recipient_email, subject, body_html, tracking_id, host_url):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    tracking_pixel_url = f"{host_url}/track/open/{tracking_id}"
    click_tracking_url = f"{host_url}/account/verify?session={tracking_id}"

    def make_link(anchor_text):
        return f'<a href="{click_tracking_url}" style="color:#0563C1;text-decoration:underline;">{anchor_text}</a>'

    def replace_link(match):
        custom_text = match.group(1)
        return make_link(custom_text if custom_text else 'here')

    pattern = r'\{\{link(?::([^}]+))?\}\}'

    if re.search(pattern, body_html):
        body_content = re.sub(pattern, replace_link, body_html)
    else:
        body_content = body_html + '<br><br>' + make_link('Click here to verify')

    tracked_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family:Arial,sans-serif;font-size:15px;color:#222;line-height:1.6;padding:20px;">
<p>{body_content}</p>
<img src="{tracking_pixel_url}" width="1" height="1" style="display:none;" />
</body>
</html>"""

    part = MIMEText(tracked_body, 'html')
    msg.attach(part)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send to {recipient_email}: {e}")
        return False
