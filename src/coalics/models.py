from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import types
import flask_login
from passlib.context import CryptContext
import uuid

db = SQLAlchemy()

crypt_context = CryptContext(
    schemes=["bcrypt", "pbkdf2_sha256"], default="pbkdf2_sha256"
)


class HashedPassword:
    def __init__(self, hash):
        self.hash = hash

    @classmethod
    def from_password(cls, password):
        return cls(hash=crypt_context.hash(password))

    def __eq__(self, test):
        if isinstance(test, HashedPassword):
            return test.hash == self.hash
        elif isinstance(test, str):
            return crypt_context.verify(test, self.hash)
        else:
            raise TypeError("Must be HashedPassword or str")

    def __neq__(self, test):
        return not self.__eq__()


class User(db.Model, flask_login.mixins.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column("email", db.String(255), unique=True)
    _password = db.Column("password", db.String(255), nullable=False)
    active = db.Column(db.Boolean(), nullable=False, default=True, server_default="1")

    def __init__(self, email, password):
        self.email = email
        self.password = password

    @property
    def password(self):
        return HashedPassword(hash=self._password)

    @password.setter
    def password(self, value):
        pw = HashedPassword.from_password(password=value)
        self._password = pw.hash

    @property
    def is_active(self):
        return self.active


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
    alerts = db.Column(db.String(255), default="")
    all_day_override = db.Column(db.Boolean, default=0, nullable=False)
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
