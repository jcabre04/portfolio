from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, SessionForm
from app.models import Session, Skill, User, create_skills_from_csv_string


@app.route("/")
@app.route("/index")
def index():
    users = User.query.all()[-5:]
    sessions = Session.query.all()[-5:]
    skills = Skill.query.all()[-5:]
    return render_template(
        "index.html",
        users=users,
        sessions=sessions,
        short_session=True,
        skills=skills,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")

        return redirect(next_page)

    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/session", methods=["GET", "POST"])
@login_required
def session():
    form = SessionForm()

    if form.validate_on_submit():
        skills = create_skills_from_csv_string(form.skills.data)
        new_session = Session(
            name=form.name.data,
            duration=form.duration.data,
            level=form.level.data,
            explanation=form.explanation.data,
            starttime=form.starttime.data,
            endtime=form.endtime.data,
            private=form.private.data,
        )

        if form.created.data:
            new_session.created = form.created.data

        if form.edited.data:
            new_session.edited = form.edited.data

        for skill in skills:
            new_session.skills.append(skill)

        current_user.sessions.append(new_session)

        db.session.add(new_session)
        db.session.commit()
        return redirect(url_for("session"))

    return render_template("session_form.html", title="Session", form=form)


@app.route("/session/all")
@login_required
def session_all():
    sessions = Session.query.all()
    return render_template(
        "session_all.html",
        title="All Sessions",
        short_session=True,
        sessions=sessions,
    )


@app.route("/session/<id>")
@login_required
def session_one(id):
    sessions = [Session.query.get(id)]

    if not sessions[0]:
        raise ("Invalid session id")

    return render_template(
        "session_all.html", title="All Sessions", sessions=sessions
    )


@app.route("/session/<id>/update", methods=["GET", "POST"])
@login_required
def session_update(id):
    form = SessionForm()
    se = Session.query.get(id)

    if not se:
        raise ("Invalid session id")

    # Successful update, replace db values with form's
    if form.validate_on_submit():
        skills = create_skills_from_csv_string(form.skills.data)
        se.name = form.name.data
        se.duration = form.duration.data
        se.level = form.level.data
        se.explanation = form.explanation.data
        se.starttime = form.starttime.data
        se.endtime = form.endtime.data
        se.private = form.private.data
        se.skills = []

        if form.created.data:
            se.created = form.created.data

        if form.edited.data:
            se.edited = form.edited.data

        for skill in skills:
            se.skills.append(skill)

        db.session.commit()
        return redirect(url_for("session_one", id=se.id))

    form.name.data = se.name
    form.duration.data = se.duration
    form.level.data = se.level
    form.explanation.data = se.explanation
    form.created.data = se.created
    form.starttime.data = se.starttime
    form.endtime.data = se.endtime
    form.private.data = se.private
    form.skills.data = se.get_skill_list_string()
    return render_template("session_form.html", title="Session", form=form)


@app.route("/session/<id>/delete")
@login_required
def session_delete(id):
    se = Session.query.get(id)

    if se:
        db.session.delete(se)
        db.session.commit()
    return redirect(url_for("session_all"))


@app.route("/about")
def about():
    return "All about Flask"


@app.route("/changelog")
def changelog():
    return "Changelog goes here"


@app.route("/admin")
@login_required
def admin():
    return "Admin dashboard"
