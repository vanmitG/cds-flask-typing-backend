import os
from flask import Flask, jsonify, redirect, url_for, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, current_user, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_migrate import Migrate


app = Flask(__name__)

CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config['SECRET_KEY'] = os.environ['MY_SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

db = SQLAlchemy(app)
Migrate(app, db)

admin_mgr = Admin(app, template_mode='bootstrap3')
login_mgr = LoginManager(app)
login_mgr.login_view = 'login'
login_mgr.init_app(app)


class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email = db.Column(db.String(120), index=True, unique=True)
    user_name = db.Column(db.String(80), default="User")
    password_hash = db.Column(db.String(128), nullable=False)
    img_url = db.Column(
        db.String(128), default="https://randomuser.me/api/portraits/men/77.jpg")
    # events = db.relationship("Events", backref="users", lazy="dynamic")
    # comments = db.relationship("Comments", backref="users", lazy="dynamic")
    created_date = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    updated_date = db.Column(
        db.DateTime,  nullable=False, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"{self.id} user_name is {self.user_name}."


class Excerpts(db.Model):

    __tablename__ = 'exerpts'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    scores = db.relationship('Scores', backref='excerpt', lazy="dynamic")
    created_date = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"exerpts - {self.id} ."


class Scores(db.Model):

    __tablename__ = 'score'

    id = db.Column(db.Integer, primary_key=True)
    wpm = db.Column(db.Integer, nullable=False)
    time = db.Column(db.Integer, nullable=False)
    excerpt_id = db.Column(db.Integer, db.ForeignKey(
        'exerpts.id'), nullable=False)
    error_count = db.Column(db.Integer, nullable=False)
    created_date = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"{self.id} score is {self.wpm}."


admin_mgr.add_view(ModelView(Users, db.session))
admin_mgr.add_view(ModelView(Excerpts, db.session))
admin_mgr.add_view(ModelView(Scores, db.session))


@login_mgr.user_loader
def load_user(id):
    return Users.query.get(int(id))


@app.route('/', methods=['GET'])
def home():
    return jsonify(['foo', 'bar'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    return '<h1>Login</h1>'


@app.route('/score', methods=['POST'])
def score():
    json_data = request.get_json()
    print(json_data)
    time = int(json_data['time'])
    wpm = int(json_data['wpm'])
    excerpt_id = int(json_data['excerpts_id'])
    error_count = int(json_data['error_count'])
    new_score = Scores(wpm=wpm, excerpt_id=excerpt_id,
                       time=time, error_count=error_count)
    db.session.add(new_score)
    db.session.commit()
    return f'success post {json_data}'


@app.route('/excerpts', methods=['GET'])
def list_expt():
    a = Excerpts.query.all()
    resp = [{"id": i.id, "body": i.body} for i in a]
    return jsonify(resp)


@app.route('/excerpts/<int:expt_id>', methods=['GET'])
def single_expt(expt_id):
    a = Excerpts.query.get_or_404(expt_id)
    return jsonify({"id": a.id, "body": a.body})


if __name__ == '__main__':
    app.run(debug=True)
