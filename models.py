from init import db
from init import app
from werkzeug.security import check_password_hash,generate_password_hash

class User(db.Model):
    __tablename__='User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)  

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
class Influencer(db.Model):
    __tablename__='Influencer'
    id=db.Column(db.Integer,primary_key=True)
    handle=db.Column(db.String(32),unique=True,nullable=False)
    name=db.Column(db.String(32),nullable=False)
    platform=db.Column(db.String(32),nullable=False)
    follower=db.Column(db.Integer,nullable=False)
    earning=db.Column(db.Integer,nullable=False)
    niche=db.Column(db.String(32),nullable=False)
    username=db.Column(db.String(32),nullable=False)
    is_flagged = db.Column(db.Boolean, default=False)
    received_requests = db.relationship('Request', back_populates='influencer', foreign_keys='Request.influencer_username', cascade='all, delete-orphan')

class Sponsor(db.Model):
    __tablename__='Sponsor'
    id=db.Column(db.Integer,primary_key=True)
    company=db.Column(db.String(32),unique=True,nullable=False)
    industry=db.Column(db.String(32),nullable=False)
    budget=db.Column(db.Integer,nullable=False)
    username=db.Column(db.String(32),nullable=False)
    is_flagged = db.Column(db.Boolean, default=False)
    sent_requests = db.relationship('Request', back_populates='sponsor', foreign_keys='Request.sponsor_username', cascade='all, delete-orphan')


class Campaign(db.Model):
    __tablename__='Campaign'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(32),unique=True,nullable=False)
    des=db.Column(db.String(32),nullable=True)
    category=db.Column(db.String(32),nullable=True)
    budget=db.Column(db.Integer,nullable=False)
    status=db.Column(db.String(32),nullable=False)
    products=db.Column(db.String(32),nullable=False)
    s_date=db.Column(db.Date, nullable=False)
    e_date=db.Column(db.Date, nullable=False)
    goal=db.Column(db.String(32),nullable=False)
    visibility = db.Column(db.String(50), nullable=False) 
    is_flagged = db.Column(db.Boolean, default=False)
    sponsor_username = db.Column(db.String(32), nullable=False) 
    #relationships
    requests = db.relationship('Request', back_populates='campaign', cascade='all, delete-orphan')

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('Campaign.id'), nullable=False)
    influencer_username = db.Column(db.Integer, db.ForeignKey('Influencer.username'), nullable=True)
    sponsor_username = db.Column(db.String(32), db.ForeignKey('Sponsor.username'), nullable=True)
    message = db.Column(db.String(256), nullable=True)
    status = db.Column(db.String(32), default='Pending')  # 'Pending', 'Accepted', 'Rejected'
    request_type = db.Column(db.String(32), nullable=False)  # 'Sponsor' or 'Influencer'

    campaign = db.relationship('Campaign', back_populates='requests')
    influencer = db.relationship('Influencer', back_populates='received_requests')
    sponsor = db.relationship('Sponsor', back_populates='sent_requests')


with app.app_context():
    db.create_all()
    admin=User.query.filter_by(role='admin').first()
    if not admin:
        admin=User(username='admin',password_hash='admin123',role='admin',is_active=True)
        db.session.add(admin)
        db.session.commit()