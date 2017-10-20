from sqlalchemy_utils import types
from coalics import db
import flask_login


class User(db.Model, flask_login.mixins.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(types.password.PasswordType(schemes=[
            'bcrypt',
    ]), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

class Calendar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    owner = db.relationship("User", backref=db.backref("calendars", lazy="dynamic"))

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner


class CalendarSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(types.url.URLType(), nullable=True)
    positive_pattern = db.Column(db.String(255), default=".*")
    negative_pattern = db.Column(db.String(255), default="")
    alerts = db.Column(db.String(255), default="")
    calendar_id = db.Column(db.Integer, db.ForeignKey("calendar.id"))
    calendar = db.relationship("Calendar", backref=db.backref("sources", lazy="dynamic"))


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(255), nullable=False, unique=True)
    summary = db.Column(db.Text())
    description = db.Column(db.Text())
    start = db.Column(db.TIMESTAMP())
    end = db.Column(db.TIMESTAMP())
    timestamp = db.Column(db.TIMESTAMP())
    url = db.Column(types.url.URLType())
    location = db.Column(db.Text())
    source_id = db.Column(db.Integer, db.ForeignKey("calendar_source.id"))
    source = db.relationship("CalendarSource", backref=db.backref("events", lazy="dynamic"))

