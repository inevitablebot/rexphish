from flask import Flask, render_template, request, redirect, url_for, send_file, abort, session, Response, flash, jsonify
from functools import wraps
from config import Config
from models import db, Campaign, Target, Event, FormData, EmailTemplate, SendingProfile, Contact
from email_service import send_campaign_email
import uuid
import io
import random
import datetime
import csv
from io import StringIO
from flask import make_response

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

@app.before_request
def restrict_admin_to_localhost():
    client_ip = request.headers.get('CF-Connecting-IP') or \
                request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or \
                request.remote_addr
    is_local = client_ip in ('127.0.0.1', '::1', 'localhost')
    public_paths = ('/track/', '/account/', '/login/', '/submit/', '/static/')
    if not is_local and not any(request.path.startswith(p) for p in public_paths):
        return Response('<h1>403 Forbidden</h1><p>Access restricted.</p>', status=403)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if (request.form.get('username') == app.config['ADMIN_USERNAME'] and
                request.form.get('password') == app.config['ADMIN_PASSWORD']):
            session['admin_logged_in'] = True
            return redirect(url_for('dashboard'))
        error = 'Invalid credentials'
    return render_template('admin_login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/')
@admin_required
def dashboard():
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
    templates = EmailTemplate.query.order_by(EmailTemplate.name).all()
    profiles  = SendingProfile.query.order_by(SendingProfile.name).all()
    contacts  = Contact.query.order_by(Contact.name).all()
    return render_template('dashboard.html', campaigns=campaigns, templates=templates,
                           profiles=profiles, contacts=contacts)

@app.route('/campaign/<int:campaign_id>')
@admin_required
def campaign_details(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    return render_template('campaign_details.html', campaign=campaign)


@app.route('/analytics')
@admin_required
def analytics():
    from models import Event, FormData
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
    all_targets = Target.query.all()
    all_events  = Event.query.all()

    total_sent    = sum(1 for t in all_targets if t.status and t.status.lower() == 'sent')
    total_opens   = sum(1 for e in all_events if e.type == 'open')
    total_clicks  = sum(1 for e in all_events if e.type == 'click')
    total_submits = sum(1 for e in all_events if e.type == 'submit')

    stats = {
        'total_campaigns': len(campaigns),
        'total_targets':   len(all_targets),
        'total_sent':      total_sent,
        'total_opens':     total_opens,
        'total_clicks':    total_clicks,
        'total_submits':   total_submits,
    }

    campaign_rows = []
    for c in campaigns:
        total = len(c.targets)
        if total == 0:
            campaign_rows.append({'id': c.id, 'name': c.name,
                'date': c.created_at.strftime('%Y-%m-%d'),
                'total': 0, 'open_pct': 0, 'click_pct': 0, 'submit_pct': 0})
            continue
        opens   = sum(1 for t in c.targets for e in t.events if e.type == 'open')
        clicks  = sum(1 for t in c.targets for e in t.events if e.type == 'click')
        submits = sum(1 for t in c.targets if t.form_data)
        campaign_rows.append({
            'id':  c.id,
            'name': c.name,
            'date': c.created_at.strftime('%Y-%m-%d'),
            'total': total,
            'open_pct':   round(min(opens   / total * 100, 100)),
            'click_pct':  round(min(clicks  / total * 100, 100)),
            'submit_pct': round(min(submits / total * 100, 100)),
        })

    recent_events = []
    for ev in sorted(all_events, key=lambda e: e.timestamp, reverse=True)[:50]:
        t = Target.query.get(ev.target_id)
        recent_events.append({
            'type':      ev.type,
            'email':     t.email if t else '?',
            'timestamp': ev.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'ip':        ev.ip_address or '',
        })

    return render_template('analytics.html',
        stats=stats, campaign_rows=campaign_rows, recent_events=recent_events)


@app.route('/settings', methods=['GET'])
@admin_required
def settings():
    from models import Event, FormData
    sys_info = {
        'campaigns': Campaign.query.count(),
        'targets':   Target.query.count(),
        'events':    Event.query.count(),
        'captures':  FormData.query.count(),
    }
    return render_template('settings.html',
        current_username=app.config['ADMIN_USERNAME'],
        sys_info=sys_info,
        cred_error=None, cred_ok=None)


@app.route('/settings/credentials', methods=['POST'])
@admin_required
def settings_credentials():
    from models import Event, FormData
    current_pw   = request.form.get('current_password', '')
    new_username = request.form.get('new_username', '').strip()
    new_password = request.form.get('new_password', '')
    confirm_pw   = request.form.get('confirm_password', '')

    sys_info = {
        'campaigns': Campaign.query.count(),
        'targets':   Target.query.count(),
        'events':    Event.query.count(),
        'captures':  FormData.query.count(),
    }

    if current_pw != app.config['ADMIN_PASSWORD']:
        return render_template('settings.html',
            current_username=app.config['ADMIN_USERNAME'],
            sys_info=sys_info,
            cred_error='Incorrect current password', cred_ok=None)

    if new_password and new_password != confirm_pw:
        return render_template('settings.html',
            current_username=app.config['ADMIN_USERNAME'],
            sys_info=sys_info,
            cred_error='New passwords do not match', cred_ok=None)

    if new_username:
        app.config['ADMIN_USERNAME'] = new_username
    if new_password:
        app.config['ADMIN_PASSWORD'] = new_password

    return render_template('settings.html',
        current_username=app.config['ADMIN_USERNAME'],
        sys_info=sys_info,
        cred_error=None, cred_ok='Credentials updated for this session')


@app.route('/settings/clear_data', methods=['POST'])
@admin_required
def settings_clear_data():
    from models import Event, FormData
    FormData.query.delete()
    Event.query.delete()
    Target.query.delete()
    Campaign.query.delete()
    db.session.commit()
    return redirect(url_for('settings'))

@app.route('/send', methods=['POST'])
def send_emails():
    sender_email    = request.form.get('sender_email', '').strip()
    sender_password = request.form.get('sender_password', '').strip()
    subject         = request.form.get('subject', '').strip() or None
    body            = request.form.get('body', '').strip() or None
    template_ids    = request.form.getlist('template_ids')
    profile_ids     = request.form.getlist('profile_ids')
    contact_ids     = request.form.getlist('contact_ids')   # selected from contact book

    # Build recipient map: email -> name
    recipient_map = {}  # {email: name}

    # From manual textarea
    manual_raw = request.form.get('recipients', '').splitlines()
    for line in manual_raw:
        line = line.strip()
        if not line:
            continue
        # Support "Name <email>" syntax
        m = re.match(r'^(.+?)\s*<([^>]+)>$', line)
        if m:
            recipient_map[m.group(2).strip()] = m.group(1).strip()
        elif '@' in line:
            recipient_map[line] = ''

    # From selected contacts
    if contact_ids:
        ids = [int(i) for i in contact_ids if str(i).isdigit()]
        for c in Contact.query.filter(Contact.id.in_(ids)).all():
            recipient_map[c.email] = c.name

    if not recipient_map:
        flash('No recipients provided.', 'error')
        return redirect(url_for('dashboard'))

    if not sender_email or not sender_password:
        # Allow no defaults when profile rotation is used
        if not profile_ids:
            flash('Missing sender credentials.', 'error')
            return redirect(url_for('dashboard'))
        sender_email = sender_email or ''
        sender_password = sender_password or ''

    if not template_ids and (not subject or not body):
        flash('Provide a Subject + Body or select at least one template.', 'error')
        return redirect(url_for('dashboard'))

    public_url = (request.form.get('public_url') or '').strip().rstrip('/')
    host_url   = public_url if public_url else request.url_root.rstrip('/')

    new_campaign = Campaign(
        sender_email=sender_email,
        sender_password=sender_password,
        subject=subject,
        body=body,
        host_url=host_url,
        redirect_url=request.form.get('redirect_url', '').strip() or None
    )

    if template_ids:
        linked_tpls = EmailTemplate.query.filter(EmailTemplate.id.in_(
            [int(i) for i in template_ids if str(i).isdigit()]
        )).all()
        new_campaign.templates = linked_tpls

    if profile_ids:
        linked_profs = SendingProfile.query.filter(SendingProfile.id.in_(
            [int(i) for i in profile_ids if str(i).isdigit()]
        )).all()
        new_campaign.profiles = linked_profs

    db.session.add(new_campaign)
    db.session.commit()

    for email, name in recipient_map.items():
        tracking_id = str(uuid.uuid4())
        target = Target(email=email, name=name or None,
                        tracking_id=tracking_id,
                        campaign_id=new_campaign.id, status='Pending')
        db.session.add(target)
    db.session.commit()

    return redirect(url_for('campaign_details', campaign_id=new_campaign.id))

@app.route('/api/campaign/<int:campaign_id>/status')
def campaign_status(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    targets = []
    for t in campaign.targets:
        open_events  = [e for e in t.events if e.type == 'open']
        click_events = [e for e in t.events if e.type == 'click']
        submits      = sum(1 for e in t.events if e.type == 'submit')

        # real = not bot-suspected
        real_opens  = [e for e in open_events  if not e.is_bot]
        real_clicks = [e for e in click_events if not e.is_bot]
        bot_opens   = [e for e in open_events  if e.is_bot]
        bot_clicks  = [e for e in click_events if e.is_bot]

        # All captured payloads (Fix 4)
        all_captured = [
            {'data': fd.data, 'ts': fd.timestamp.strftime('%H:%M:%S'), 'ip': fd.ip_address or ''}
            for fd in t.form_data
        ]

        tpl_name  = t.template.name if t.template else 'Default'
        prof_name = t.sending_profile.name if t.sending_profile else 'Default'

        targets.append({
            'id':         t.id,
            'email':      t.email,
            'name':       t.name or '',
            'status':     t.status or 'Pending',
            'opens':      len(real_opens),
            'clicks':     len(real_clicks),
            'bot_opens':  len(bot_opens),
            'bot_clicks': len(bot_clicks),
            'submits':    submits,
            'captured':   all_captured,
            'template':   tpl_name,
            'sender':     prof_name,
        })
    return jsonify({'targets': targets})

@app.route('/api/send_target/<int:target_id>', methods=['POST'])
def send_single_target(target_id):
    target   = Target.query.get_or_404(target_id)
    campaign = target.campaign

    # Pick a random sending profile
    used_profile = None
    if campaign.profiles:
        used_profile = random.choice(campaign.profiles)
        target.sending_profile_id = used_profile.id

    send_email = used_profile.email    if used_profile else campaign.sender_email
    send_pass  = used_profile.password if used_profile else campaign.sender_password

    if not send_email or not send_pass:
        return {'success': False, 'message': 'Missing sender credentials'}, 400

    # Pick a random template
    used_tpl = None
    if campaign.templates:
        used_tpl = random.choice(campaign.templates)
    elif not campaign.subject or not campaign.body:
        all_templates = EmailTemplate.query.all()
        if all_templates:
            used_tpl = random.choice(all_templates)

    if used_tpl:
        subject = used_tpl.subject
        body    = used_tpl.body
        target.template_id = used_tpl.id
    else:
        subject = campaign.subject
        body    = campaign.body

    if not subject or not body:
        return {'success': False, 'message': 'No subject/body and no templates configured'}, 400

    # Determine display names for placeholder substitution
    target_name = target.name or target.email.split('@')[0]
    sender_name = used_profile.name if used_profile else (send_email.split('@')[0])

    try:
        success = send_campaign_email(
            send_email, send_pass,
            target.email, subject, body,
            target.tracking_id, campaign.host_url,
            target_name=target_name,
            sender_name=sender_name
        )
        target.status = 'Sent' if success else 'Failed'
        if success:
            target.sent_at = datetime.datetime.utcnow()
        db.session.commit()
        return {
            'success': success,
            'status':   target.status,
            'template': used_tpl.name if used_tpl else 'Default',
            'sender':   sender_name,
        }
    except Exception as e:
        target.status = 'Error'
        db.session.commit()
        return {'success': False, 'message': str(e), 'status': 'Error'}

def _is_bot(target):
    """Heuristic: if event fires within 30s of send, likely a scanner."""
    if not target or not target.sent_at:
        return False
    delta = (datetime.datetime.utcnow() - target.sent_at).total_seconds()
    return delta < 5

@app.route('/track/open/<tracking_id>')
def track_open(tracking_id):
    target = Target.query.filter_by(tracking_id=tracking_id).first()
    if target:
        event = Event(
            type='open',
            target_id=target.id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            is_bot=_is_bot(target)
        )
        db.session.add(event)
        db.session.commit()
    pixel = io.BytesIO(b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b')
    return send_file(pixel, mimetype='image/gif')

@app.route('/account/verify')
def masked_click():
    t = request.args.get('session')
    if not t:
        return redirect('https://microsoft.com')
    target = Target.query.filter_by(tracking_id=t).first()
    if not target:
        return redirect('https://microsoft.com')

    bot = _is_bot(target)

    # Infer "open" from click if pixel was blocked
    already_opened = Event.query.filter_by(target_id=target.id, type='open').first()
    if not already_opened:
        db.session.add(Event(
            type='open', target_id=target.id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            is_bot=bot
        ))

    db.session.add(Event(
        type='click', target_id=target.id,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        is_bot=bot
    ))
    db.session.commit()
    host = target.campaign.host_url or request.url_root.rstrip('/')
    return redirect(f"{host}/login/{t}")

@app.route('/login/<path:tracking_id>')
def landing_page(tracking_id):
    target = Target.query.filter_by(tracking_id=tracking_id).first_or_404()
    return render_template('landing.html', tracking_id=tracking_id)

@app.route('/submit/<tracking_id>', methods=['POST'])
def submit_data(tracking_id):
    target = Target.query.filter_by(tracking_id=tracking_id).first_or_404()
    data = request.form.to_dict()
    # Always append — capture ALL submissions (Fix 4)
    form_data = FormData(data=data, target_id=target.id, ip_address=request.remote_addr)
    db.session.add(form_data)

    # Infer open if pixel was blocked
    already_opened = Event.query.filter_by(target_id=target.id, type='open').first()
    if not already_opened:
        db.session.add(Event(type='open', target_id=target.id,
                             ip_address=request.remote_addr,
                             user_agent=request.user_agent.string,
                             is_bot=False))

    # Infer click if link was not followed (direct form post)
    already_clicked = Event.query.filter_by(target_id=target.id, type='click').first()
    if not already_clicked:
        db.session.add(Event(type='click', target_id=target.id,
                             ip_address=request.remote_addr,
                             user_agent=request.user_agent.string,
                             is_bot=False))

    db.session.add(Event(type='submit', target_id=target.id,
                         ip_address=request.remote_addr,
                         user_agent=request.user_agent.string,
                         is_bot=False))
    db.session.commit()
    campaign = target.campaign
    if campaign and campaign.redirect_url:
        return redirect(campaign.redirect_url)
    return redirect('https://microsoft.com')

@app.route('/delete/<int:campaign_id>', methods=['POST'])
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    for target in campaign.targets:
        Event.query.filter_by(target_id=target.id).delete()
        FormData.query.filter_by(target_id=target.id).delete()
        db.session.delete(target)
    db.session.delete(campaign)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/export/<int:campaign_id>')
def export_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Email', 'Status', 'Template Used', 'Tracking ID', 'Opened', 'Clicked', 'Data Submitted', 'Captured Data'])
    for target in campaign.targets:
        opens   = [e for e in target.events if e.type == 'open']
        clicks  = [e for e in target.events if e.type == 'click']
        submits = [e for e in target.events if e.type == 'submit']
        tpl_name = EmailTemplate.query.get(target.template_id).name if target.template_id else 'default'
        data_str = str(target.form_data[0].data) if target.form_data else ''
        cw.writerow([target.email, target.status, tpl_name, target.tracking_id,
                     'Yes' if opens else 'No',
                     'Yes' if clicks else 'No',
                     'Yes' if submits else 'No',
                     data_str])
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=campaign_{campaign_id}_export.csv"
    output.headers["Content-type"] = "text/csv"
    return output

# ─── Contact Book CRUD ───────────────────────────────────────────────────────

@app.route('/contacts')
@admin_required
def contacts_list():
    contacts = Contact.query.order_by(Contact.name, Contact.email).all()
    return render_template('contacts.html', contacts=contacts)

@app.route('/contacts/new', methods=['POST'])
@admin_required
def contact_new():
    name  = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    if not email:
        return redirect(url_for('contacts_list'))
    # Avoid duplicate emails
    existing = Contact.query.filter_by(email=email).first()
    if not existing:
        db.session.add(Contact(name=name, email=email))
        db.session.commit()
    return redirect(url_for('contacts_list'))

@app.route('/contacts/<int:contact_id>/delete', methods=['POST'])
@admin_required
def contact_delete(contact_id):
    c = Contact.query.get_or_404(contact_id)
    db.session.delete(c)
    db.session.commit()
    return redirect(url_for('contacts_list'))

@app.route('/contacts/delete_all', methods=['POST'])
@admin_required
def contact_delete_all():
    Contact.query.delete()
    db.session.commit()
    return redirect(url_for('contacts_list'))

@app.route('/contacts/import_csv', methods=['POST'])
@admin_required
def contact_import_csv():
    f = request.files.get('csv_file')
    if not f:
        return redirect(url_for('contacts_list'))
    stream = io.StringIO(f.stream.read().decode('utf-8-sig'), newline=None)
    reader = csv.reader(stream)
    added = 0
    for row in reader:
        if not row:
            continue
        # Accept "name,email" or just "email"
        if len(row) >= 2:
            name, email = row[0].strip(), row[1].strip()
        else:
            name, email = '', row[0].strip()
        # Skip header rows
        if not email or '@' not in email:
            continue
        if not Contact.query.filter_by(email=email).first():
            db.session.add(Contact(name=name, email=email))
            added += 1
    db.session.commit()
    flash(f'Imported {added} contacts.', 'ok')
    return redirect(url_for('contacts_list'))

# ─── Template Library CRUD ────────────────────────────────────────────────────

@app.route('/templates')
@admin_required
def templates_list():
    templates = EmailTemplate.query.order_by(EmailTemplate.created_at.desc()).all()
    return render_template('templates.html', templates=templates)

@app.route('/templates/new', methods=['POST'])
@admin_required
def template_new():
    name    = request.form.get('name', '').strip()
    subject = request.form.get('subject', '').strip()
    body    = request.form.get('body', '').strip()
    if not name or not subject or not body:
        return redirect(url_for('templates_list'))
    tpl = EmailTemplate(name=name, subject=subject, body=body)
    db.session.add(tpl)
    db.session.commit()
    return redirect(url_for('templates_list'))

@app.route('/templates/<int:tpl_id>/edit', methods=['POST'])
@admin_required
def template_edit(tpl_id):
    tpl = EmailTemplate.query.get_or_404(tpl_id)
    tpl.name    = request.form.get('name', tpl.name).strip()
    tpl.subject = request.form.get('subject', tpl.subject).strip()
    tpl.body    = request.form.get('body', tpl.body).strip()
    db.session.commit()
    return redirect(url_for('templates_list'))

@app.route('/templates/<int:tpl_id>/delete', methods=['POST'])
@admin_required
def template_delete(tpl_id):
    tpl = EmailTemplate.query.get_or_404(tpl_id)
    db.session.delete(tpl)
    db.session.commit()
    return redirect(url_for('templates_list'))

# ─── Sending Profile Library CRUD ───────────────────────────────────────────

@app.route('/profiles')
@admin_required
def profiles_list():
    profiles = SendingProfile.query.order_by(SendingProfile.created_at.desc()).all()
    return render_template('sending_profiles.html', profiles=profiles)

@app.route('/profiles/new', methods=['POST'])
@admin_required
def profile_new():
    name     = request.form.get('name', '').strip()
    email    = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    if not name or not email or not password:
        return redirect(url_for('profiles_list'))
    prof = SendingProfile(name=name, email=email, password=password)
    db.session.add(prof)
    db.session.commit()
    return redirect(url_for('profiles_list'))

@app.route('/profiles/<int:prof_id>/edit', methods=['POST'])
@admin_required
def profile_edit(prof_id):
    prof = SendingProfile.query.get_or_404(prof_id)
    prof.name     = request.form.get('name', prof.name).strip()
    prof.email    = request.form.get('email', prof.email).strip()
    prof.password = request.form.get('password', prof.password).strip()
    db.session.commit()
    return redirect(url_for('profiles_list'))

@app.route('/profiles/<int:prof_id>/delete', methods=['POST'])
@admin_required
def profile_delete(prof_id):
    prof = SendingProfile.query.get_or_404(prof_id)
    db.session.delete(prof)
    db.session.commit()
    return redirect(url_for('profiles_list'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
