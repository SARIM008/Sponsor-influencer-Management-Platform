from flask import Flask,render_template,redirect,url_for,flash,request,session
from init import app,db
from models import User,Sponsor,Influencer,Campaign,Request
from functools import wraps
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import joinedload



def auth_req(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if 'username' not in session:
            flash('Please login first.',"error")
            return redirect(url_for('login'))
        return func(*args,**kwargs)
    return inner

@app.route('/')
def cover_page():
    return render_template('cover_page.html')

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/login.html', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    
    # Check if the user exists in the database
    user = User.query.filter_by(username=username).first()
    
    if role == "admin":
        # Admin login logic
        if username == "admin" and password == user.password_hash:
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Incorrect credentials for admin", "error")
            return redirect(url_for('login'))
    
    if not user:
        flash("User does not exist", "error")
        return redirect(url_for('login'))
    
    if not user.is_active:
        flash("You are flagged by admin", "error")
        return redirect(url_for('login'))
    
    
    if not user.check_password(password):
        flash('Incorrect password', "error")
        return redirect(url_for('login'))

    
    if role == "influencer":
        session['username'] = user.username
        return redirect(url_for("influencer_dashboard"))
    elif role == "sponsor":
        session['username'] = user.username
        return redirect(url_for("sponsor_dashboard"))
    else:
        flash("Invalid role selected", "error")
        return redirect(url_for('login'))

    

@app.route('/sponsor_registration.html')
def sponsor_registration():
    return render_template('sponsor_registration.html')

@app.route('/sponsor_registration.html', methods=["POST"])
def sponsor_registration_post():
    username = request.form.get('username')
    name = request.form.get('name')
    budget = request.form.get('budget')
    industry = request.form.get('industry')
    password = request.form.get('password')

    if username == '' or password == '' or name == '' or budget == '' or industry == '':
        flash('Fields cannot be left empty',"error")
        return redirect(url_for("sponsor_registration"))

    if User.query.filter_by(username=username).first():
        flash("This username is occupied, please select a unique username","error")
        return redirect(url_for("sponsor_registration"))

    user = User(username=username, role="sponsor")
    user.set_password(password)  
    spon = Sponsor(company=name, budget=budget, industry=industry,username=username)
    db.session.add(user)
    db.session.add(spon)
    db.session.commit()

    flash("User registered successfully","success")
    return redirect(url_for("login"))

@app.route('/influencer_registration.html')
def influencer_registration():
    return render_template('influencer_registration.html')
@app.route('/influencer_registration.html', methods=["POST"])
def influencer_registration_post():
    username1 = request.form.get('username')
    name = request.form.get('name')
    social_media_handle = request.form.get('social_media_handle')
    platform = request.form.get('platform')
    followers = request.form.get('followers')
    niche = request.form.get('niche')
    password1 = request.form.get('password')

    if username1 == '' or password1 == '' or name == '' or platform == '' or followers == '' or niche == ''or social_media_handle == '':
        flash('Fields cannot be left empty',"error")
        return redirect(url_for("influencer_registration"))

    if User.query.filter_by(username=username1).first():
        flash("This username is occupied, please select a unique username","error")
        return redirect(url_for("influencer_registration"))

    user1 = User(username=username1, role="influencer")
    user1.set_password(password1)  
    inf = Influencer(handle=social_media_handle, name=name, platform=platform,follower=followers,earning=0,niche=niche,username=username1)
    db.session.add(user1)
    db.session.add(inf)
    db.session.commit()

    flash("User registered successfully","success")
    return redirect(url_for("login"))

@app.route('/influencer_dashboard.html')
@auth_req
def influencer_dashboard():
    username = session.get('username')
    
    
    influencer_data = Influencer.query.filter_by(username=username).first()
    
    #  accepted requests for this influencer
    accepted_requests = Request.query.filter_by(influencer_username=username, status='Accepted').all()
    accepted_campaign_ids = [req.campaign_id for req in accepted_requests]
    accepted_campaigns = Campaign.query.filter(Campaign.id.in_(accepted_campaign_ids)).all()
    
    #  requested campaigns that are still pending
    requested_requests = Request.query.filter_by(influencer_username=username, status='Pending',request_type='Influencer').all()
    requested_campaign_ids = [req.campaign_id for req in requested_requests]
    requested_campaigns = []
    requests_dict = {}

    for req in requested_requests + accepted_requests:
        campaign = Campaign.query.filter_by(id=req.campaign_id).first()
        campaign.request_id = req.id
        campaign.message = req.message
        if req.status == 'Pending':
            requested_campaigns.append(campaign)
        requests_dict[campaign.id] = req
    
    return render_template(
        'influencer_dashboard.html',
        influencer=influencer_data,
        accepted_campaigns=accepted_campaigns,
        requested_campaigns=requested_campaigns,
        requests=requests_dict
    )

@app.route('/delete_request1/<int:request_id>', methods=['POST'])
@auth_req
def delete_request1(request_id):
    request_to_delete = Request.query.get(request_id)
    if request_to_delete:
        db.session.delete(request_to_delete)
        db.session.commit()
        flash("Request deleted successfully", "success")
    else:
        flash("Request not found", "error")
    return redirect(url_for('influencer_dashboard'))

@app.route('/edit_request1/<int:request_id>', methods=['POST'])
@auth_req
def edit_request1(request_id):
    new_message = request.form.get('message')
    request_to_edit = Request.query.get(request_id)
    if request_to_edit:
        request_to_edit.message = new_message
        db.session.commit()
        flash("Request message updated successfully", "success")
    else:
        flash("Request not found", "error")
    return redirect(url_for('influencer_dashboard'))

@app.route('/complete_campaign/<int:request_id>/<int:campaign_id>', methods=['POST'])
@auth_req
def complete_campaign(request_id, campaign_id):
    request_to_update = Request.query.get(request_id)
    campaign_to_update = Campaign.query.get(campaign_id)
    if request_to_update and campaign_to_update:
        request_to_update.status = 'Completed'
        campaign_to_update.status = 'Completed'
        db.session.commit()
        flash("Campaign marked as completed", "success")
    else:
        flash("Request or campaign not found", "error")
    return redirect(url_for('influencer_dashboard'))



@app.route('/sponsor_dashboard.html')
@auth_req
def sponsor_dashboard():
    username = session.get('username')
    sponsor_data = Sponsor.query.filter_by(username=username).first()

    # Get the requests sent by the sponsor
    requests = Request.query.filter_by(sponsor_username=username,request_type='Sponsor',status='Pending').all()
    
    # Get all influencers
    influencers = Influencer.query.all()
    
    return render_template('sponsor_dashboard.html', sponsor=sponsor_data, requests=requests, influencers=influencers)


@app.route('/edit_request/<int:request_id>', methods=['POST'])
@auth_req
def edit_request(request_id):
    request_obj = Request.query.get_or_404(request_id)
    influencer_username = request.form.get('influencer_username')
    message = request.form.get('message')

    request_obj.influencer_username = influencer_username
    request_obj.message = message
    db.session.commit()

    flash("Request updated successfully", "success")
    return redirect(url_for('sponsor_dashboard'))

@app.route('/delete_request/<int:request_id>', methods=['POST'])
@auth_req
def delete_request(request_id):
    request_obj = Request.query.get_or_404(request_id)
    db.session.delete(request_obj)
    db.session.commit()

    flash("Request deleted successfully", "success")
    return redirect(url_for('sponsor_dashboard'))


@app.route('/campaigns.html')
@auth_req
def campaigns():
    return render_template('campaigns.html')

@app.route('/campaigns.html',methods=["POST"])
@auth_req
def campaigns_post():
    name1=request.form.get("name")
    des=request.form.get("des")
    category=request.form.get("category")
    budget=request.form.get("budget")
    status=request.form.get("status")
    products=request.form.get("product")
    s_date=request.form.get("s_date")
    e_date=request.form.get("e_date")
    goal=request.form.get("goal")
    visibility = request.form.get("visibility") 
    s_date = datetime.strptime(s_date, '%Y-%m-%d').date()
    e_date = datetime.strptime(e_date, '%Y-%m-%d').date()
    if e_date <= s_date:
        flash('End date must be after the start date.',"error")
        return redirect(url_for('campaigns'))
    sponsor_username = session.get('username')
    cp=Campaign(name=name1,des=des,category=category,budget=budget,status='active',products=products,s_date=s_date,e_date=e_date,goal=goal,visibility=visibility,sponsor_username=sponsor_username)
    db.session.add(cp)
    db.session.commit()
    flash("Campaign added successfully","success")
    return redirect(url_for("campaign_details"))

@app.route('/influencer_profile.html')
@auth_req
def influencer_profile():
    return render_template('influencer_profile.html')

@app.route('/campaign_details.html')
@auth_req
def campaign_details():
    username = session.get('username')
    campaigns = Campaign.query.filter_by(sponsor_username=username, is_flagged=False).all()
    return render_template('campaign_details.html', campaigns=campaigns)

@app.route('/update_campaign/<int:campaign_id>', methods=['GET', 'POST'])
@auth_req
def update_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)

    if request.method == 'POST':
        campaign.name = request.form.get('name')
        campaign.des = request.form.get('des')
        campaign.category = request.form.get('category')
        campaign.budget = request.form.get('budget')
        campaign.status = request.form.get('status')
        campaign.products = request.form.get('products')
        campaign.visibility  = request.form.get('visibility')
        campaign.s_date = datetime.strptime(request.form.get('s_date'), '%Y-%m-%d').date()
        campaign.e_date = datetime.strptime(request.form.get('e_date'), '%Y-%m-%d').date()
        campaign.goal = request.form.get('goal')
        related_requests = Request.query.filter_by(campaign_id=campaign_id).all()
        for req in related_requests:
            req.status = campaign.status
        
        db.session.commit()
        flash('Campaign updated successfully!',"success")
        return redirect(url_for('campaign_details'))

    return render_template('update_campaign.html', campaign=campaign)



@app.route('/delete_campaign/<int:campaign_id>', methods=['POST'])
@auth_req
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully!',"success")
    return redirect(url_for('campaign_details'))



@app.route('/inf_update_profile.html', methods=['GET'])
@auth_req
def inf_update_profile():
    username = session.get('username')
    influencer = Influencer.query.filter_by(username=username).first()
    return render_template('inf_update_profile.html', influencer=influencer)

@app.route('/inf_update_profile.html', methods=['POST'])
@auth_req
def inf_update_profile_post():
    username = session.get('username')
    influencer = Influencer.query.filter_by(username=username).first()

    influencer.name = request.form.get('name')
    influencer.platform = request.form.get('platform')
    influencer.handle = request.form.get('handle')
    influencer.follower = request.form.get('follower')
    influencer.niche = request.form.get('niche')

    db.session.commit()
    flash('Profile updated successfully!',"success")
    return redirect(url_for('influencer_dashboard'))

@app.route('/inf_campaign.html', methods=['GET'])
@auth_req
def inf_campaign():
   
    username = session.get('username')

    # Check if the "Show All" button was clicked
    show_all = request.args.get('show_all')

    # Query for campaigns that are active and public
    query = Campaign.query.filter(Campaign.status == 'active', Campaign.visibility == 'public')

    # If the "Show All" button was not clicked, apply filters
    if not show_all:
        category = request.args.get('category')
        products = request.args.get('products')
        
        # Apply filters based on search parameters
        if category:
            query = query.filter(Campaign.category.ilike(f'%{category}%'))
        if products:
            query = query.filter(Campaign.products.ilike(f'%{products}%'))

    campaigns = query.all()

    # Get the campaigns that have requests from the influencer
    existing_requests = Request.query.filter_by(influencer_username=username).all()
    requested_campaign_ids = [req.campaign_id for req in existing_requests]

    # Filter out the campaigns that have been requested by the influencer
    filtered_campaigns = [campaign for campaign in campaigns if campaign.id not in requested_campaign_ids]

    return render_template('inf_campaign.html', campaigns=filtered_campaigns)


@app.route('/search_influencer.html', methods=['GET', 'POST'])
@auth_req
def search_influencer():
    if request.method == 'POST':
        influencers = []
        search_name = request.form.get('search_name')
        search_niche = request.form.get('search_niche')
        
        if search_name or search_niche:
            influencers = Influencer.query.filter(
                Influencer.name.contains(search_name),
                Influencer.niche.contains(search_niche),
                User.is_active == True  # Filter out flagged influencers
            ).all()
            if not influencers:
                flash("No influencers found matching your criteria.", "info")
        else:
            flash("Please enter a search term.", "error")
    
    else:
        if request.args.get('show_all'):
            influencers = Influencer.query.filter_by(is_flagged=False).all()  
        else:
            influencers = []

    sponsor_username = session.get('username')
    campaigns = Campaign.query.filter_by(sponsor_username=sponsor_username, is_flagged=False,visibility="public",status='active').all()

    return render_template('search_influencer.html', influencers=influencers, campaigns=campaigns)

@app.route('/send_request', methods=['POST'])
@auth_req
def send_request():
    influencer_username = request.form.get('influencer_username')
    campaign_id = request.form.get('campaign_id')
    message = request.form.get('message')
    sponsor_username = session.get('username')

    new_request = Request(
        sponsor_username=sponsor_username,
        influencer_username=influencer_username,
        campaign_id=campaign_id,
        message=message,
        request_type='Sponsor'
    )

    db.session.add(new_request)
    db.session.commit()

    flash("Request sent successfully!","success")
    return redirect(url_for('search_influencer'))

#for influencer send request
@app.route('/send_influencer_request/<int:campaign_id>', methods=['POST'])
@auth_req
def send_influencer_request(campaign_id):
    influencer_username = session.get('username')
    
   
    if not influencer_username:
        flash("You must be logged in to send a request.","error")
        return redirect(url_for('login'))
    
    new_request = Request(
        sponsor_username=request.form.get('sponsor_username'),
        influencer_username=influencer_username,
        campaign_id=campaign_id,
        message=request.form.get('message'),
        request_type='Influencer'
    )

    db.session.add(new_request)
    db.session.commit()

    flash("Request sent successfully!","success")
    return redirect(url_for('inf_campaign'))

@app.route('/update_request_status/<int:request_id>', methods=['POST'])
@auth_req
def update_request_status(request_id):
    request = Request.query.get_or_404(request_id)
    status = request.form.get('status')
    
    if status not in ['Accepted', 'Rejected']:
        flash('Invalid status.',"error")
        return redirect(url_for('manage_requests'))

    if status == 'Accepted':
        if request.request_type == 'Sponsor':
            influencer = Influencer.query.get_or_404(request.influencer_id)
            campaign = Campaign.query.get_or_404(request.campaign_id)
            influencer.earning += campaign.budget  # Update influencer's earnings
            
            
            campaign.status = 'Completed' 

        
        
    request.status = status
    db.session.commit()
    
    flash(f'Request {status} successfully!',"success")
    return redirect(url_for('manage_requests'))


@app.route('/manage_requests.html')
def manage_requests():
    username = session.get('username')
    user = User.query.filter_by(username=username).first()
    role = user.role

    if role == 'influencer':
        influencer = Influencer.query.filter_by(username=username).first()
        requests = Request.query.filter_by(influencer_username=influencer.username, status='Pending',request_type="Sponsor").all()
    elif role == 'sponsor':
        requests = Request.query.filter_by(sponsor_username=username, status='Pending',request_type="Influencer").all()

    return render_template('manage_requests.html', requests=requests, user=user, role=role)
@app.route('/accept_request/<int:request_id>', methods=['POST'])
@auth_req
def accept_request(request_id):
    req = Request.query.get_or_404(request_id)
    user = User.query.filter_by(username=session.get('username')).first()
    campaign = Campaign.query.get(req.campaign_id)
    influencer = Influencer.query.filter_by(username=req.influencer_username).first()
    if user.role == 'influencer' and req.influencer_username == user.username:
        req.status = 'Accepted'
        influencer = Influencer.query.filter_by(username=req.influencer_username).first()
        campaign.status="alloted"
        influencer.earning += campaign.budget  # Update influencer's earnings
        db.session.commit()
        flash('Request accepted successfully.',"success")
    elif user.role == 'sponsor' and req.sponsor_username == user.username:
        req.status = 'Accepted'
        campaign.status="alloted"
        influencer.earning += campaign.budget  # Update influencer's earnings
        db.session.commit()
        flash('Request accepted successfully.',"success")
    else:
        flash('Unauthorized action.',"error")

    return redirect(url_for('manage_requests'))

@app.route('/reject_request/<int:request_id>', methods=['POST'])
@auth_req
def reject_request(request_id):
    req = Request.query.get_or_404(request_id)
    user = User.query.filter_by(username=session.get('username')).first()

    if (user.role == 'influencer' and req.influencer_username == user.username) or (user.role == 'sponsor' and req.sponsor_username == user.username):
        req.status = 'Rejected'
        db.session.delete(req)  # Remove the request only if rejected
        db.session.commit()
        flash('Request rejected successfully.',"success")
    else:
        flash('Unauthorized action.',"error")

    return redirect(url_for('manage_requests'))

@app.route('/admin_dashboard')
def admin_dashboard():
   
    campaign_statuses = db.session.query(Campaign.status, func.count(Campaign.id)).group_by(Campaign.status).all()
    flagged_campaigns = Campaign.query.filter_by(is_flagged=1).count()
    unflagged_campaigns = Campaign.query.filter_by(is_flagged=0).count()

    campaign_labels = [status[0] for status in campaign_statuses] + ['Flagged', 'Unflagged']
    campaign_counts = [status[1] for status in campaign_statuses] + [flagged_campaigns, unflagged_campaigns]

    influencer_count = Influencer.query.count()
    sponsor_count = Sponsor.query.count()
    flagged_users = User.query.filter(User.role!="admin",User.is_active==0).count()
    unflagged_users = User.query.filter(User.role!="admin",User.is_active==1).count()

    user_labels = ['Influencers', 'Sponsors', 'Flagged Users', 'Unflagged Users']
    user_counts = [influencer_count, sponsor_count, flagged_users, unflagged_users]

    return render_template('admin_dashboard.html', 
                           campaign_labels=campaign_labels, 
                           campaign_counts=campaign_counts, 
                           user_labels=user_labels, 
                           user_counts=user_counts)

@app.route('/admin_users', methods=['GET', 'POST'])
def admin_users():
    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')

        user = User.query.filter_by(username=username).first_or_404()

        if action == 'edit':
            if user.role == "influencer":
                influencer = Influencer.query.filter_by(username=username).first_or_404()
                influencer.name = request.form.get('name')
                influencer.platform = request.form.get('platform')
                influencer.follower = request.form.get('follower')
                influencer.niche = request.form.get('niche')
                influencer.earning = request.form.get('earning')
            elif user.role == "sponsor":
                sponsor = Sponsor.query.filter_by(username=username).first_or_404()
                sponsor.company = request.form.get('company')
                sponsor.industry = request.form.get('industry')
                sponsor.budget = request.form.get('budget')

            db.session.commit()
            flash('User details updated successfully!', 'success')

        elif action == 'toggle_flag':
            if user.role == "influencer":
                influencer = Influencer.query.filter_by(username=username).first_or_404()
                influencer.is_flagged = not influencer.is_flagged
                user.is_active = not user.is_active


            elif user.role == "sponsor":
                sponsor = Sponsor.query.filter_by(username=username).first_or_404()
                sponsor.is_flagged = not sponsor.is_flagged
                user.is_active = not user.is_active

            db.session.commit()
            flash('User flag status updated successfully!', 'success')

        elif action == 'delete':
            if user.role == "influencer":
                influencer = Influencer.query.filter_by(username=username).first_or_404()
                db.session.delete(user)
                db.session.delete(influencer)
            elif user.role == "sponsor":
                sponsor = Sponsor.query.filter_by(username=username).first_or_404()
                db.session.delete(user)
                db.session.delete(sponsor)
                
            db.session.commit()
            flash('User deleted successfully!', 'success')

        return redirect(url_for('admin_users'))

    influencers = Influencer.query.all()
    sponsors = Sponsor.query.all()
    total_users = len(influencers) + len(sponsors)
    total_influencers = len(influencers)
    total_sponsors = len(sponsors)

    return render_template('admin_users.html',
                           influencers=influencers,
                           sponsors=sponsors,
                           total_users=total_users,
                           total_influencers=total_influencers,
                           total_sponsors=total_sponsors)


@app.route('/admin_campaigns', methods=['GET', 'POST'])
def admin_campaigns():
    if request.method == 'POST':
        action = request.form.get('action')
        campaign_id = request.form.get('campaign_id')

        campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()

        if action == 'toggle_flag':
            campaign.is_flagged = not campaign.is_flagged
            db.session.commit()
            flash(f'Campaign {"unflagged" if not campaign.is_flagged else "flagged"} successfully!', 'success')

        elif action == 'delete':
            db.session.delete(campaign)
            db.session.commit()
            flash('Campaign deleted successfully!', 'success')

        return redirect(url_for('admin_campaigns'))

    campaigns = Campaign.query.all()

    return render_template('admin_campaigns.html', campaigns=campaigns)

@app.route('/admin_request')
def admin_request():
    # Fetch all requests along with their associated campaigns
    requests = db.session.query(Request).options(joinedload(Request.campaign)).all()
    return render_template('admin_request.html', requests=requests)

@app.route('/delete_request2/<int:request_id>', methods=['POST'])
def delete_request2(request_id):
    request_to_delete = Request.query.get_or_404(request_id)
    try:
        db.session.delete(request_to_delete)
        db.session.commit()
        flash('Request deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting request: {str(e)}', 'danger')
    return redirect(url_for('admin_request'))

@app.route('/update_sponsor_profile', methods=["GET", "POST"])
@auth_req
def update_sponsor_profile():
    sponsor_username = session.get('username')
    sponsor = Sponsor.query.filter_by(username=sponsor_username).first()

    if request.method == "POST":
        
        name = request.form.get('name')
        budget = request.form.get('budget')
        industry = request.form.get('industry')

    
        if not name or not budget or not industry:
            flash('Fields cannot be left empty', "error")
            return redirect(url_for('update_sponsor_profile'))

        
        sponsor.company = name
        sponsor.budget = budget
        sponsor.industry = industry

        
        db.session.commit()

        
        flash('Profile updated successfully', "success")
        return redirect(url_for('sponsor_dashboard'))

    return render_template('update_sponsor_profile.html', sponsor=sponsor)


@app.route('/logout')
def logout():
    # Pop the session to log the user out
    session.pop('username', None)
    flash('You have successfully logged out.',"success") 
    return redirect(url_for('login'))

