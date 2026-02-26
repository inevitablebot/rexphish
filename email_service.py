import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def _text_to_html(text):
    """
    Convert plain-text body to proper HTML paragraphs.
    - Blank lines separate <p> tags
    - Single newlines become <br> within a paragraph
    - Existing HTML tags are left untouched
    """
    # Normalise line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Split on blank lines to get paragraphs
    paragraphs = re.split(r'\n{2,}', text.strip())
    html_parts = []
    for para in paragraphs:
        if not para.strip():
            continue
        # Convert single newlines inside paragraph to <br>
        inner = para.replace('\n', '<br>\n')
        html_parts.append(f'<p>{inner}</p>')
    return '\n'.join(html_parts)


def send_campaign_email(sender_email, sender_password, recipient_email, subject,
                        body_html, tracking_id, host_url,
                        target_name=None, sender_name=None):
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To']   = recipient_email
    # NOTE: Subject is set AFTER placeholder substitution below (only once)

    tracking_pixel_url = f"{host_url}/track/open/{tracking_id}"
    click_tracking_url = f"{host_url}/account/verify?session={tracking_id}"

    def make_link(anchor_text):
        return (f'<a href="{click_tracking_url}" '
                f'style="color:#0563C1;text-decoration:underline;">'
                f'{anchor_text}</a>')

    def replace_link(match):
        custom_text = match.group(1)
        return make_link(custom_text if custom_text else 'here')

    link_pattern = r'\{\{link(?::([^}]+))?\}\}'

    # ── Placeholder substitution ─────────────────────────────────
    t_name = target_name or recipient_email.split('@')[0]
    s_name = sender_name  or sender_email.split('@')[0]

    body_html = body_html.replace('{{target}}', t_name)
    body_html = body_html.replace('{{sender}}', s_name)

    # ── Subject placeholder substitution ────────────────────────
    subject = subject.replace('{{target}}', t_name)
    subject = subject.replace('{{sender}}', s_name)
    msg['Subject'] = subject  # update after substitution

    # ── Link replacement ──────────────────────────────────────────
    if re.search(link_pattern, body_html):
        body_content = re.sub(link_pattern, replace_link, body_html)
    else:
        body_content = body_html + '<br><br>' + make_link('Click here to verify')

    # ── Convert plain-text paragraphs → HTML if no block tags found ──
    has_block_tags = bool(re.search(r'<(p|div|table|ul|ol|h[1-6])\b', body_content, re.I))
    if not has_block_tags:
        body_content = _text_to_html(body_content)

    tracked_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family:Arial,sans-serif;font-size:15px;color:#222;line-height:1.6;padding:20px;max-width:680px;margin:0 auto;">
{body_content}
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
