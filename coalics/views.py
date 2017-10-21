from flask import Flask, render_template, request, redirect, url_for, abort
import flask
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
import time

from .util import get_or_abort, event_acceptor, wait_for, TaskTimeout
from .models import User, Calendar, CalendarSource, Event
from .forms import CalendarForm, CalendarSourceForm, DeleteForm, LoginForm, LogoutForm, EditForm
from .tasks import update_sources, update_source_id

from coalics import app, q, db

app.jinja_env.globals['logout_form'] = lambda: LogoutForm()

@app.route("/")
def home():
    # r = q.enqueue(update_sources)
    # while not r.result:
        # time.sleep(0.1)

    # return ""

    # update.delay()
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
    
    # events = Event.query.filter(Event.source in sources).all()
    events = Event.query.join(CalendarSource).filter_by(calendar=cal).order_by(Event.start.desc()).paginate(max_per_page=10)

    if request.method == "GET":
        form = CalendarForm(obj=cal)
        delete_form = DeleteForm()
        return render_template("calendar_edit.html", form=form, sources=sources, cal_id=cal_id, delete_form=delete_form, events=events)
    
    # is post
    form = CalendarForm(request.form, obj=cal)
    if not form.validate():
        return render_template("calendar_edit.html", form=form, cal_id=cal_id, events=events)
    
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

    # trigger update
    task = q.enqueue(update_source_id, source.id)
    try:
        wait_for(task, timeout=5)
    except TaskTimeout:
        # timeout
        flask.flash("Upstream source still being updated", "info")

    return redirect(url_for("calendar_edit", cal_id=cal_id))

@app.route("/source/<int:source_id>", methods=["GET"])
@login_required
def view_source(source_id):
    source = CalendarSource.query.get(source_id)
    if not source or source.calendar.owner != current_user:
        abort(400)

    # return "this is it"
    events = source.events
    # res = ""
    # for event in events:
        # res += event.summary + "<br/>"
    # return res
    return render_template("events.html", events=events)


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
        return render_template("source_edit.html", edit=True, form=form, cal_id=cal_id)

    form = CalendarSourceForm(request.form)
    if not form.validate():
        return render_template("source_edit.html", edit=True, form=form, cal_id=cal_id)

    form.populate_obj(source)

    # we need to reapply the filter to all existing events
    accept_event = event_acceptor(source)
    for event in source.events:
        app.logger.debug("Rechecking event {}".format(event.summary))
        if not accept_event(event):
            db.session.delete(event)

    db.session.commit()

    # check if we need old ones
    # wait max 5 secs return early if longer
    task = q.enqueue(update_source_id, source.id)
    try:
        wait_for(task, timeout=5)
    except TaskTimeout:
        # timeout
        flask.flash("Upstream source still being updated", "info")
        pass


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


    user = User.query.filter_by(email=email).one()
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
