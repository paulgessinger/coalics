from flask import Flask, render_template, request, redirect, url_for, abort
import flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from flask_session import RedisSessionInterface
from redis import StrictRedis
import uuid
from functools import wraps
import logging
from celery import Celery


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["CSRF_SECRET_KEY"] = b'0694d5d1-87b4-4afa-b6bc-03f935f41c48'


db = SQLAlchemy(app)

app.session_interface = RedisSessionInterface(StrictRedis(host="redis"), __name__)



from .models import User, Calendar, CalendarSource
from .forms import CalendarForm, CalendarSourceForm, DeleteForm, LoginForm



migrate = Migrate(app, db)

lm = LoginManager()
lm.init_app(app)

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

app.config.update(
    CELERY_BROKER_URL='redis://redis:6379',
    CELERY_RESULT_BACKEND='redis://redis:6379'
)
celery = make_celery(app)

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10*60, update.s(), name='add every 10')

    # Calls test('world') every 30 seconds
    # sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # # Executes every Monday morning at 7:30 a.m.
    # sender.add_periodic_task(
        # crontab(hour=7, minute=30, day_of_week=1),
        # test.s('Happy Mondays!'),
    # )


@celery.task()
def update():
    print("UPDATE")


@lm.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def get_or_abort(model, object_id, code=404):
    result = model.query.get(object_id)
    if result is None:
        abort(code)
    return result

def generate_csrf_token(force=False):
    if force:
        del flask.session["_csrf_token"]
    if '_csrf_token' not in flask.session:
        flask.session['_csrf_token'] = uuid.uuid4()
    return flask.session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

def csrf_protected(func):
    @wraps(func)
    def handler(*args, **kwargs):
        if request.method == "POST":
            csrf = request.form["_csrf_token"]
            sess_csrf = flask.session["_csrf_token"]
            app.logger.debug(csrf)
            app.logger.debug(sess_csrf)
            if not csrf or csrf != csrf:
                appl.logger.error("CSRF failure")
                flask.abort(403)

        return func(*args, **kwargs)
    return handler

@app.route("/")
def home():
    print("run update")
    update.delay()
    if current_user.is_authenticated:
        return flask.redirect(url_for("calendars"))
    return render_template("home.html")

@app.route("/calendar")
@login_required
def calendars():
    cals = Calendar.query.filter_by(owner=current_user)

    delete_form = DeleteForm()

    return render_template("calendars.html", 
                           calendars=cals, 
                           delete_form=delete_form)

@app.route("/calendar/add", methods=["GET", "POST"])
@login_required
def calendar_add():
    if request.method == "GET":
        form = CalendarForm()
        return render_template("calendar_add.html", form=form)

    # is post
    form = CalendarForm(request.form)
    if not form.validate():
        return render_template("calendar_add.html", form=form)
    
    cal = Calendar(name=form.name.data, owner=current_user)
    db.session.add(cal)
    db.session.commit()

    flask.flash("Calendar group {} created".format(cal.name), "success")

    return redirect(url_for("calendar_edit", cal_id=cal.id))

@app.route("/calendar/<int:cal_id>", methods=["GET", "POST"])
@login_required
def calendar_edit(cal_id):

    cal = Calendar.query.get(cal_id)
    if not cal:
        flask.flash("Calendar not found", "error")
        redirect(url_for("calendars"))

    sources = cal.sources

    if request.method == "GET":
        form = CalendarForm(obj=cal)
        return render_template("calendar_edit.html", form=form)
    
    # is post
    form = CalendarForm(request.form, obj=cal)
    if not form.validate():
        return render_template("calendar_edit.html", form=form)
    
    form.populate_obj(cal)
    db.session.commit()
    flask.flash("Calendar updated", "success")
    return redirect(url_for("calendars"))

@app.route("/calendar/<int:cal_id>/delete", methods=["post"])
@login_required
def calendar_delete(cal_id):
    delete_form = DeleteForm(request.form)
    if not delete_form.validate():
        flask.flash("Unable to delete item", "danger")
        return redirect(request.referrer)

    cal = Calendar.query.filter_by(id=cal_id, owner=current_user).first()

    if not cal:
        flask.flash("Item to delete not found", "warning")
        return redirect(request.referrer)
    
    flask.flash("Item {} deleted".format(cal.name), "success")
    db.session.delete(cal)
    db.session.commit()


    return redirect(url_for("calendars"))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        form = LoginForm()
        return render_template("login.html", form=form)

    # POST
    # return str(request.form)

    email = request.form["email"]
    psw = request.form["password"]

    form = LoginForm(request.form)

    if not form.validate():
        flask.flash("Invalid request", "danger")
        return render_template("login.html", form=form)


    user = User.query.filter_by(email=email).first()
    app.logger.debug(user)


    if user.password != psw:
        flask.flash("Invalid password")
        return render_template("login.html", form=form)
        # return render_template("login.html"), 401

    login_user(user)
    return flask.redirect(url_for("calendars"))




@app.route("/register", methods=("GET", "POST"))
def register():
    guest = User('guest', 'guest@example.com', "hallo")
    db.session.add(guest)
    db.session.commit()
    generate_csrf_token(True)
    return "Ok"

@app.route("/logout", methods=["POST"])
@login_required
@csrf_protected
def logout():
    logout_user()
    generate_csrf_token(True)
    return flask.redirect("login")
