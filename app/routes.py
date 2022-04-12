from flask import flash, redirect, render_template, request, url_for, send_file
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

from app import app, db
from app.forms import (
    LoginForm,
    SessionForm,
    SkillForm,
    ProjectForm,
    ImportBackupForm,
)
from app.models import (
    Session,
    Skill,
    User,
    create_skills_from_csv_string,
    Project,
)
import pytz

import csv
import os
from zipfile import ZipFile
from datetime import datetime, timezone


@app.route("/")
@app.route("/index")
def index():
    users = reversed(User.query.all()[-3:])
    projects = reversed(Project.query.all()[-3:])
    sessions = reversed(Session.query.all()[-3:])
    skills = reversed(Skill.query.all()[-3:])
    return render_template(
        "index.html",
        users=users,
        projects=projects,
        sessions=sessions,
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


def _localize_tz(pytz_local, datetime_obj):
    localized = pytz_local.localize(datetime_obj, is_dst=None).astimezone(
        pytz.utc
    )
    return localized


@app.route("/project", methods=["GET", "POST"])
@login_required
def project():
    form = ProjectForm()

    if form.validate_on_submit():
        new_project = Project(
            name=form.name.data,
        )

        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for("project"))

    return render_template("project_form.html", title="Project", form=form)


@app.route("/project/all")
def project_all():
    projects = reversed(Project.query.all())
    return render_template(
        "project_all.html",
        title="All Project",
        short_project=True,
        projects=projects,
    )


@app.route("/project/<id>")
def project_one(id):
    projects = [Project.query.get(id)]

    if not projects[0]:
        raise ("Invalid session id")

    sessions = projects[0].sessions

    return render_template(
        "project_all.html",
        title=projects[0].name,
        projects=projects,
        sessions=sessions,
    )


@app.route("/project/<id>/update", methods=["GET", "POST"])
@login_required
def project_update(id):
    form = ProjectForm()
    pro = Project.query.get(id)

    if not pro:
        raise ("Invalid project id")

    # Successful update, replace db values with form's
    if form.validate_on_submit():
        pro.name = form.name.data
        db.session.commit()
        return redirect(url_for("project_one", id=pro.id))

    form.name.data = pro.name
    return render_template("project_form.html", title="Project", form=form)


@app.route("/project/<id>/delete")
@login_required
def project_delete(id):
    pro = Project.query.get(id)

    if pro:
        db.session.delete(pro)
        db.session.commit()
    return redirect(url_for("project_all"))


@app.route("/session", methods=["GET", "POST"])
@login_required
def session():
    form = SessionForm()

    if form.project.old_project.choices is None:
        form.project.old_project.choices = [
            (project.id, project.name) for project in Project.query.all()
        ]

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

        local = pytz.timezone(form.timezone.data)

        if form.created.data:
            new_session.created = _localize_tz(local, form.created.data)

        if form.edited.data:
            new_session.edited = _localize_tz(local, form.edited.data)

        for skill in skills:
            new_session.skills.append(skill)

        current_user.sessions.append(new_session)

        if form.project.new_project.data:
            project = Project(name=form.project.new_project.data)
            db.session.add(project)
        else:
            project = Project.query.get(form.project.old_project.data)
        project.sessions.append(new_session)

        db.session.add(new_session)
        db.session.commit()
        return redirect(url_for("session"))

    form.timezone.data = "US/Pacific"
    form.project.old_project.data = 1
    return render_template("session_form.html", title="Session", form=form)


@app.route("/session/all")
def session_all():
    sessions = reversed(Session.query.all())
    return render_template(
        "session_all.html",
        title="All Sessions",
        short_session=True,
        sessions=sessions,
    )


@app.route("/session/<id>")
def session_one(id):
    sessions = [Session.query.get(id)]

    if not sessions[0]:
        raise ("Invalid session id")

    return render_template(
        "session_all.html", title=sessions[0].name, sessions=sessions
    )


@app.route("/session/<id>/update", methods=["GET", "POST"])
@login_required
def session_update(id):
    form = SessionForm()
    se = Session.query.get(id)

    if not se:
        raise ("Invalid session id")

    if form.project.old_project.choices is None:
        form.project.old_project.choices = [
            (project.id, project.name) for project in Project.query.all()
        ]

    # Successful update, replace db values with form's
    if form.validate_on_submit():
        skills = create_skills_from_csv_string(form.skills.data)
        Project.query.get(se.project_id).sessions.remove(se)
        se.name = form.name.data
        se.duration = form.duration.data
        se.level = form.level.data
        se.explanation = form.explanation.data
        se.starttime = form.starttime.data
        se.endtime = form.endtime.data
        se.private = form.private.data
        se.skills = []

        local = pytz.timezone(form.timezone.data)

        if form.created.data:
            se.created = _localize_tz(local, form.created.data)

        if form.edited.data:
            se.edited = _localize_tz(local, form.edited.data)

        for skill in skills:
            se.skills.append(skill)

        if form.project.new_project.data:
            project = Project(name=form.project.new_project.data)
            db.session.add(project)
        else:
            project = Project.query.get(form.project.old_project.data)
        project.sessions.append(se)

        db.session.commit()
        return redirect(url_for("session_one", id=se.id))

    form.name.data = se.name
    form.duration.data = se.duration
    form.level.data = se.level
    form.explanation.data = se.explanation
    form.timezone.data = "UTC"
    form.created.data = se.created
    form.starttime.data = se.starttime
    form.endtime.data = se.endtime
    form.private.data = se.private
    form.skills.data = se.get_skill_list_string()
    form.project.old_project.data = se.project.id
    return render_template("session_form.html", title="Session", form=form)


@app.route("/session/<id>/delete")
@login_required
def session_delete(id):
    se = Session.query.get(id)

    if se:
        db.session.delete(se)
        db.session.commit()
    return redirect(url_for("session_all"))


@app.route("/skill", methods=["GET", "POST"])
@login_required
def skill():
    form = SkillForm()

    if form.validate_on_submit():
        new_skill = Skill(
            name=form.name.data,
            explanation=form.explanation.data,
        )

        db.session.add(new_skill)
        db.session.commit()
        return redirect(url_for("skill"))

    return render_template("skill_form.html", title="Skill", form=form)


@app.route("/skill/all")
def skill_all():
    skills = reversed(Skill.query.all())
    return render_template(
        "skill_all.html",
        title="All Skills",
        short_skill=True,
        skills=skills,
    )


@app.route("/skill/<id>")
def skill_one(id):
    skills = [Skill.query.get(id)]

    if not skills[0]:
        raise ("Invalid session id")

    return render_template(
        "skill_all.html", title=skills[0].name, skills=skills
    )


@app.route("/skill/<id>/update", methods=["GET", "POST"])
@login_required
def skill_update(id):
    form = SkillForm()
    sk = Skill.query.get(id)

    if not sk:
        raise ("Invalid session id")

    # Successful update, replace db values with form's
    if form.validate_on_submit():
        sk.name = form.name.data
        sk.explanation = form.explanation.data
        db.session.commit()
        return redirect(url_for("skill_one", id=sk.id))

    form.name.data = sk.name
    form.explanation.data = sk.explanation
    return render_template("skill_form.html", title="Skill", form=form)


@app.route("/skill/<id>/delete")
@login_required
def skill_delete(id):
    sk = Skill.query.get(id)

    if sk:
        db.session.delete(sk)
        db.session.commit()
    return redirect(url_for("skill_all"))


@app.route("/about")
def about():
    return "All about this portfolio and its creator"


@app.route("/changelog")
def changelog():
    return "Changelog goes here"


@app.route("/admin")
@login_required
def admin():
    return render_template("admin.html")


@app.route("/admin/download_data_backup")
@login_required
def download_data_backup():
    us = User.query.all()
    sk = Skill.query.all()
    po = Project.query.all()
    se = Session.query.all()

    basedir = os.path.abspath(os.path.dirname(__file__) + "/static/backup/")
    if not os.path.exists(basedir):
        os.makedirs(basedir)

    with open(basedir + r"/user.csv", "w", newline="") as user_file:
        header = ["username", "email", "password_hash", "admin"]
        writer = csv.writer(user_file)
        writer.writerow(header)
        for u in us:
            writer.writerow([u.username, u.email, u.password_hash, u.admin])

    with open(basedir + r"/skill.csv", "w", newline="") as skill_file:
        header = ["name", "explanation"]
        writer = csv.writer(skill_file)
        writer.writerow(header)
        for s in sk:
            writer.writerow([s.name, s.explanation])

    with open(basedir + r"/project.csv", "w", newline="") as project_file:
        header = ["name"]
        writer = csv.writer(project_file)
        writer.writerow(header)
        for p in po:
            writer.writerow([p.name])

    with open(basedir + r"/session.csv", "w", newline="") as session_file:
        header = [
            "name",
            "duration",
            "level",
            "explanation",
            "created",
            "edited",
            "starttime",
            "endtime",
            "private",
            "user_id",
            "project_id",
            "skills,",
        ]
        writer = csv.writer(session_file)
        writer.writerow(header)
        for s in se:
            writer.writerow(
                [
                    s.name,
                    s.duration,
                    s.level,
                    s.explanation,
                    s.created,
                    s.edited,
                    s.starttime,
                    s.endtime,
                    s.private,
                    s.user_id,
                    s.project_id,
                    s.get_skill_list_string().replace(",", "|"),
                ]
            )

    with ZipFile(basedir + r"/backup.zip", "w") as backup:
        backup.write(basedir + r"/user.csv", arcname=r"/user.csv")
        backup.write(basedir + r"/skill.csv", arcname=r"/skill.csv")
        backup.write(basedir + r"/project.csv", arcname=r"/project.csv")
        backup.write(basedir + r"/session.csv", arcname=r"/session.csv")

    return send_file(basedir + r"/backup.zip", as_attachment=True)


def _remove_dot_leftover(string_date):
    if "." in string_date:
        return string_date.split(".")[0]
    return string_date


@app.route("/admin/import_data_backup", methods=["GET", "POST"])
def import_data_backup():
    form = ImportBackupForm()

    if form.validate_on_submit():
        file = request.files["file"]
        archive = ZipFile(file, "r")

        users = csv.reader(archive.read("user.csv").decode().splitlines())
        next(users)
        skills = csv.reader(archive.read("skill.csv").decode().splitlines())
        next(skills)
        projects = csv.reader(
            archive.read("project.csv").decode().splitlines()
        )
        next(projects)
        sessions = csv.reader(
            archive.read("session.csv").decode().splitlines()
        )
        next(sessions)

        if not User.query.filter_by(username="admin").first():
            for u in users:
                if u:
                    new_u = User(
                        username=u[0],
                        email=[1],
                        password_hash=u[2],
                        admin=True if u[3] == "True" else False,
                    )
                    db.session.add(new_u)
            db.session.commit()

        for s in skills:
            if s:
                new_s = Skill(
                    name=s[0],
                    explanation=s[1],
                )
                db.session.add(new_s)
        db.session.commit()

        for p in projects:
            if p:
                new_p = Project(
                    name=p[0],
                )
                db.session.add(new_p)
        db.session.commit()

        for se in sessions:
            if se:
                new_se = Session(
                    name=se[0],
                    duration=se[1],
                    level=se[2],
                    explanation=se[3],
                    created=datetime.strptime(
                        _remove_dot_leftover(se[4]), "%Y-%m-%d %H:%M:%S"
                    ).replace(tzinfo=timezone.utc),
                    edited=datetime.strptime(
                        _remove_dot_leftover(se[5]), "%Y-%m-%d %H:%M:%S"
                    ).replace(tzinfo=timezone.utc),
                    starttime=datetime.strptime(
                        _remove_dot_leftover(se[6]), "%Y-%m-%d %H:%M:%S"
                    ).replace(tzinfo=timezone.utc),
                    endtime=datetime.strptime(
                        _remove_dot_leftover(se[7]), "%Y-%m-%d %H:%M:%S"
                    ).replace(tzinfo=timezone.utc),
                    private=True if se[8] == "True" else False,
                )
                user = User.query.get(se[9])
                user.sessions.append(new_se)

                project = Project.query.get(se[10])
                project.sessions.append(new_se)

                new_se.skills = []
                skill_objects = create_skills_from_csv_string(
                    se[11].replace("|", ",")
                )
                for skill in skill_objects:
                    new_se.skills.append(skill)
                db.session.add(new_se)

        db.session.commit()

        return redirect(url_for("admin"))

    return render_template("import_backup_form.html", form=form)
