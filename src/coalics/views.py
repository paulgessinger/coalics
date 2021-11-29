from flask import render_template, request, redirect, url_for, abort
import flask
from flask_login import (
    login_required,
    login_user,
    current_user,
    logout_user,
)
import sqlalchemy
import icalendar as ics
import pytz
from datetime import datetime, timedelta

from .util import (
    event_acceptor,
    TimeoutException,
    parse_from,
)
from .models import User, Calendar, CalendarSource, Event
from .forms import (
    CalendarForm,
    CalendarSourceForm,
    DeleteForm,
    LoginForm,
    LogoutForm,
    RegisterForm,
)
from .tasks import update_source_id

from coalics.models import db


def init_views(app):

    app.jinja_env.globals["logout_form"] = lambda: LogoutForm()

    @app.route("/")
    def home():
        if current_user.is_authenticated:
            return flask.redirect(url_for("calendars"))
        return render_template("home.html")

    @app.route("/robots.txt")
    def robots():
        return "User-agent: *\nDisallow: /"

    @app.route("/calendar")
    @login_required
    def calendars():
        cals = Calendar.query.filter_by(owner=current_user)

        delete_form = DeleteForm()

        return render_template(
            "calendars.html", calendars=cals, delete_form=delete_form
        )

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
            # flask.flash("Calendar not found", "error")
            # redirect(url_for("calendars"))
            abort(404)

        sources = cal.sources

        # events = Event.query.filter(Event.source in sources).all()
        events = (
            Event.query.join(CalendarSource)
            .filter_by(calendar=cal)
            .order_by(Event.start.desc())
            .paginate(max_per_page=10)
        )

        if request.method == "GET":
            form = CalendarForm(obj=cal)
            delete_form = DeleteForm()
            return render_template(
                "calendar_edit.html",
                form=form,
                sources=sources,
                cal=cal,
                delete_form=delete_form,
                events=events,
            )

        # is post
        form = CalendarForm(request.form, obj=cal)
        if not form.validate():
            return render_template(
                "calendar_edit.html", form=form, cal_id=cal_id, events=events
            )

        form.populate_obj(cal)
        db.session.commit()
        flask.flash("Calendar saved sucessfully", "success")
        return redirect(url_for("calendar_edit", cal_id=cal_id))

    @app.route("/calendar/<int:cal_id>/delete", methods=["post"])
    @login_required
    def calendar_delete(cal_id):

        delete_form = DeleteForm(request.form)
        if not delete_form.validate():
            flask.flash("Unable to delete item", "danger")
            return redirect(request.referrer)

        cal = Calendar.query.filter_by(id=cal_id, owner=current_user).first()

        if cal.owner != current_user:
            abort(404)

        if not cal:
            flask.flash("Item to delete not found", "warning")
            return redirect(request.referrer)

        flask.flash("Item {} deleted".format(cal.name), "success")
        db.session.delete(cal)
        db.session.commit()

        return redirect(url_for("calendars"))

    @app.route("/ics/<slug>/<name>.ics")
    def calendar_ics(slug, name):

        try:
            cal = Calendar.query.filter_by(slug=slug).one()
        except sqlalchemy.orm.exc.NoResultFound:
            abort(404)

        root = ics.Calendar()

        def make_zulu(dt):
            dtz = dt.astimezone(pytz.UTC)
            return dtz

        fromstr = parse_from(request.args.get("from") or "-31d")
        fromdt = datetime.now() + fromstr

        events = (
            Event.query.join(CalendarSource)
            .filter_by(calendar=cal)
            .filter(Event.start >= fromdt)
            .order_by(Event.start.desc())
        )
        for dbevent in events:
            event = ics.Event()
            event.add("summary", dbevent.summary)
            event.add("uid", dbevent.uid)
            event.add("description", dbevent.description or "")
            event.add("location", dbevent.location or "")
            event.add("url", dbevent.url or "")

            dtstart = make_zulu(dbevent.start)
            dtend = make_zulu(dbevent.end)

            if dbevent.source.all_day_override and dtstart.date() != dtend.date():
                app.logger.debug("Override start %s -> %s", dtstart, dtstart.date())
                app.logger.debug("Override end %s -> %s", dtend, dtend.date())
                event.add("dtstart", dtstart.date())
                event.add("dtend", dtend.date() + timedelta(days=1))
            else:
                event.add("dtstart", dtstart)
                event.add("dtend", dtend)

            event.add("dtstamp", make_zulu(dbevent.timestamp))

            # add alarms
            if dbevent.source.alerts != "":
                for mins in dbevent.source.alerts.split(";"):
                    # app.logger.debug(mins)
                    # td = timedelta(minutes=int(mins))
                    # alarmtime = dtstart - td
                    alarm = ics.Alarm()
                    # alarm.add("trigger", alarmtime)
                    # alarm.add("trigger", "-PT{}M".format(mins))
                    alarm["TRIGGER"] = "-PT{}M".format(mins)
                    alarm.add("action", "DISPLAY")
                    event.add_component(alarm)

            root.add_component(event)

        return root.to_ical()
        # if wants_ics:
        # return root.to_ical()
        # else:
        # return "<pre>{}</pre>".format(str(root.to_ical(), "utf-8"))

    @app.route("/calendar/<int:cal_id>/source", methods=["GET", "POST"])
    @login_required
    def add_source(cal_id):
        cal = Calendar.query.get(cal_id)
        if not cal or cal.owner != current_user:
            flask.flash("Calendar not found", "error")
            redirect(url_for("calendars"))

        if request.method == "GET":
            form = CalendarSourceForm()
            return render_template("source_edit.html", form=form, cal=cal)

        form = CalendarSourceForm(request.form)
        if not form.validate():
            return render_template("source_edit.html", form=form, cal=cal)

        source = CalendarSource()
        source.calendar = cal
        form.populate_obj(source)
        db.session.add(source)
        db.session.commit()

        # trigger update
        update_source_id(source.id)

        return redirect(url_for("calendar_edit", cal_id=cal_id))

    @app.route("/source/<int:source_id>", methods=["GET"])
    @login_required
    def view_source(source_id):
        source = CalendarSource.query.get(source_id)
        if not source or source.calendar.owner != current_user:
            abort(404)

        events = (
            Event.query.filter_by(source=source)
            .order_by(Event.start.desc())
            .paginate(max_per_page=20)
        )
        return render_template("view_source.html", events=events, source=source)

    @app.route(
        "/calendar/<int:cal_id>/source/<int:source_id>/edit", methods=["GET", "POST"]
    )
    @login_required
    def edit_source(cal_id, source_id):
        cal = Calendar.query.get(cal_id)
        source = CalendarSource.query.get(source_id)
        if not cal or cal.owner != current_user or source.calendar != cal:
            # flask.flash("Calendar not found", "error")
            # redirect(url_for("calendars"))
            abort(404)

        events = (
            Event.query.filter_by(source=source)
            .order_by(Event.start.desc())
            .paginate(max_per_page=20)
        )

        if request.method == "GET":
            form = CalendarSourceForm(obj=source)
            return render_template(
                "source_edit.html",
                edit=True,
                form=form,
                cal=cal,
                events=events,
                source=source,
            )

        form = CalendarSourceForm(request.form)
        if not form.validate():
            return render_template(
                "source_edit.html",
                edit=True,
                form=form,
                cal=cal,
                events=events,
                source=source,
            )

        form.populate_obj(source)

        # we need to reapply the filter to all existing events
        accept_event = event_acceptor(source, to=app.config["REGEX_TIMEOUT"])
        try:
            for event in source.events:
                app.logger.debug("Rechecking event {}".format(event.summary))
                if not accept_event(event):
                    db.session.delete(event)
        except TimeoutException:
            # no use in continuinging the update
            app.logger.error("Timeout exception occurred on regex execution.")

        db.session.commit()

        # check if we need old ones
        # wait max 5 secs return early if longer
        # also add timeout on task itself to make sure
        # a bad regex does not kill everything
        update_source_id(source.id)

        flask.flash("Calendar source saved sucessfully", "success")
        return redirect(url_for("edit_source", source_id=source_id, cal_id=cal_id))

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

    @app.route("/login", methods=["GET", "POST"])
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

        try:
            user = User.query.filter_by(email=email).one()
            app.logger.debug(user)
        except sqlalchemy.orm.exc.NoResultFound:
            flask.flash("Invalid login info", "danger")
            return render_template("login.html", form=form), 403

        if user.password != psw:
            flask.flash("Invalid password", "danger")
            return render_template("login.html", form=form), 403

        login_user(user)
        return flask.redirect(url_for("calendars"))

    @app.route("/register", methods=("GET", "POST"))
    def register():
        if not app.config["REGISTER_ENABLED"]:
            return "", 404

        if request.method == "GET":
            form = RegisterForm()
            return render_template("register.html", form=form)

        email = request.form["email"]
        psw1 = request.form["password"]

        form = RegisterForm(request.form)
        if not form.validate():
            flask.flash("Error creating account", "danger")
            return render_template("register.html", form=form), 400

        user = User(email=email, password=psw1)
        db.session.add(user)

        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            flask.flash("Error creating account", "danger")
            app.logger.error("Error creating account", exc_info=True)
            return render_template("register.html", form=form), 400

        login_user(user)
        flask.flash("Account created", "success")
        return flask.redirect(url_for("calendars"))

    @app.route("/logout", methods=["POST"])
    @login_required
    def logout():

        form = LogoutForm(request.form)
        if form.validate():
            logout_user()
            return flask.redirect("login")
        else:
            flask.abort(400)

    @app.route("/privacy")
    def privacy():
        return render_template("privacy.html")

    @app.route("/imprint")
    def imprint():
        return render_template("imprint.html")
