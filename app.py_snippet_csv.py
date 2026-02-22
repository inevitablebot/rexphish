import csv
from io import StringIO
from flask import make_response

@app.route('/export/<int:campaign_id>')
def export_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Create CSV data
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Email', 'Status', 'Tracking ID', 'Opened', 'Clicked', 'Data Submitted', 'Captured Data'])
    
    for target in campaign.targets:
        opens = [e for e in target.events if e.type == 'open']
        clicks = [e for e in target.events if e.type == 'click']
        submits = [e for e in target.events if e.type == 'submit']
        
        opened = 'Yes' if opens else 'No'
        clicked = 'Yes' if clicks else 'No'
        submitted = 'Yes' if submits else 'No'
        
        data_str = ''
        if target.form_data:
            # Flatten the first submission for CSV
            data_str = str(target.form_data[0].data)
            
        cw.writerow([target.email, target.status, target.tracking_id, opened, clicked, submitted, data_str])
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=campaign_{campaign_id}_export.csv"
    output.headers["Content-type"] = "text/csv"
    return output
