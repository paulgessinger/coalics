from sqlalchemy_utils import types
from coalics import db
import flask_login
from coalics.util import BcryptPassword
import uuid


class User(db.Model, flask_login.mixins.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    _password = db.Column("password", db.String(255), nullable=False)
    active = db.Column(db.Boolean(), nullable=False, default=True, server_default="1")
    # password = db.Column(types.password.PasswordType(schemes=[
    # 'bcrypt',
    # ]), nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = password

    @property
    def password(self):
        return BcryptPassword(hash=self._password.encode("utf-8"))

    @password.setter
    def password(self, value):
        pw = BcryptPassword(password=value)
        self._password = pw.hash.decode("utf-8")

    @property
    def is_active(self):
        return self.active

    # def __repr__(self):
    # return '<User %r>' % self.username


class Calendar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    slug = db.Column(db.String(255), unique=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))
    owner = db.relationship(
        "User", backref=db.backref("calendars", lazy="dynamic", passive_deletes=True)
    )

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        self.slug = str(uuid.uuid4())

    @property
    def events(self):
        # query events from all sources
        return Event.query.join(CalendarSource).filter_by(calendar=self)


class CalendarSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(types.url.URLType(), nullable=True)
    positive_pattern = db.Column(db.String(255), default=".*")
    negative_pattern = db.Column(db.String(255), default="")
    all_day_override = db.Column(db.Boolean, default=0, nullable=False)
    alerts = db.Column(db.String(255), default="")
    calendar_id = db.Column(
        db.Integer, db.ForeignKey("calendar.id", ondelete="CASCADE")
    )
    calendar = db.relationship(
        "Calendar", backref=db.backref("sources", lazy="dynamic", passive_deletes=True)
    )

    def __init__(self, positive_pattern=".*", negative_pattern="", **kwargs):
        super().__init__(
            positive_pattern=positive_pattern,
            negative_pattern=negative_pattern,
            **kwargs
        )


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text())
    description = db.Column(db.Text())
    start = db.Column(db.TIMESTAMP())
    end = db.Column(db.TIMESTAMP())
    timestamp = db.Column(db.TIMESTAMP())
    url = db.Column(types.url.URLType())
    location = db.Column(db.Text())
    source_id = db.Column(
        db.Integer, db.ForeignKey("calendar_source.id", ondelete="CASCADE")
    )
    source = db.relationship(
        "CalendarSource",
        backref=db.backref("events", lazy="dynamic", passive_deletes=True),
    )
    __table_args__ = (db.UniqueConstraint("source_id", "uid", name="_source_uid_uc"),)
