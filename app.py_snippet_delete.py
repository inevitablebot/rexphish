@app.route('/delete/<int:campaign_id>', methods=['POST'])
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Simple cascade delete (if not handled by DB constraints)
    # Since we didn't set cascade in models, we do it manually or rely on SQLAlchemy cascade if configured.
    # Let's do manual to be safe for this simple app.
    for target in campaign.targets:
        Event.query.filter_by(target_id=target.id).delete()
        FormData.query.filter_by(target_id=target.id).delete()
        db.session.delete(target)
        
    db.session.delete(campaign)
    db.session.commit()
    return redirect(url_for('dashboard'))
