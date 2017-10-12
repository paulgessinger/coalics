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
from .forms import CalendarForm, CalendarSourceForm, DeleteForm, LoginForm, LogoutForm, EditForm



migrate = Migrate(app, db)

lm = LoginManager()
lm.login_view = "login"
lm.init_app(app)

app.jinja_env.globals['logout_form'] = lambda: LogoutForm()


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
    sender.add_periodic_task(10*60, update.s(), name='add every 10')

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
    if not cal or cal.owner != current_user:
        flask.flash("Calendar not found", "error")
        redirect(url_for("calendars"))

    sources = cal.sources

    if request.method == "GET":
        form = CalendarForm(obj=cal)
        delete_form = DeleteForm()
        return render_template("calendar_edit.html", form=form, sources=sources, cal_id=cal_id, delete_form=delete_form)
    
    # is post
    form = CalendarForm(request.form, obj=cal)
    if not form.validate():
        return render_template("calendar_edit.html", form=form, cal_id=cal_id)
    
    form.populate_obj(cal)
    db.session.commit()
    flask.flash("Calendar updated", "success")
    return redirect(url_for("calendars"))


@app.route("/calendar/<int:cal_id>/source", methods=["GET", "POST"])
@login_required
def add_source(cal_id):
    cal = Calendar.query.get(cal_id)
    if not cal or cal.owner != current_user:
        flask.flash("Calendar not found", "error")
        redirect(url_for("calendars"))
    
    if request.method == "GET":
        form = CalendarSourceForm()
        return render_template("source_edit.html", form=form, cal_id=cal_id)

    form = CalendarSourceForm(request.form)
    if not form.validate():
        return render_template("source_edit.html", form=form, cal_id=cal_id)

    source = CalendarSource()
    source.calendar=cal
    form.populate_obj(source)
    db.session.add(source)
    db.session.commit()

    return redirect(url_for("calendar_edit", cal_id=cal_id))

@app.route("/source/<int:source_id>", methods=["GET"])
@login_required
def view_source(source_id):
    source = CalendarSource.query.get(source_id)
    if not source or source.calendar.owner != current_user:
        abort(400)

    return "this is it"

@app.route("/calendar/<int:cal_id>/source/<int:source_id>/edit", methods=["GET", "POST"])
@login_required
def edit_source(cal_id, source_id):
    cal = Calendar.query.get(cal_id)
    source = CalendarSource.query.get(source_id)
    if not cal or cal.owner != current_user or source.calendar != cal:
        flask.flash("Calendar not found", "error")
        redirect(url_for("calendars"))

    
    if request.method == "GET":
        form = CalendarSourceForm(obj=source)
        return render_template("source_edit.html", form=form, cal_id=cal_id)

    form = CalendarSourceForm(request.form)
    if not form.validate():
        return render_template("source_edit.html", form=form, cal_id=cal_id)

    # source = CalendarSource()
    # source.calendar=cal
    # form.populate_obj(source)
    # db.session.add(source)
    form.populate_obj(source)
    db.session.commit()

    return redirect(url_for("calendar_edit", cal_id=cal_id))

@app.route("/calendar/<int:cal_id>/source/<int:source_id>/delete", methods=["POST"])
@login_required
def delete_source(cal_id, source_id):
    cal = Calendar.query.get(cal_id)
    source = CalendarSource.query.get(source_id)
    if not cal or cal.owner != current_user or source.calendar != cal:
        abort()
    
    delete_form = DeleteForm(request.form)
    if not delete_form.validate():
        flask.flash("Unable to delete item", "danger")
        return redirect(request.referrer)

    db.session.delete(source)
    db.session.commit()
    return redirect(url_for("calendar_edit", cal_id=cal_id))

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
    return "Ok"

@app.route("/logout", methods=["POST"])
@login_required
def logout():

    form = LogoutForm(request.form)
    if form.validate():
        logout_user()
        return flask.redirect("login")
    else:
        flask.abort(400)
