import os
from app import app, db
from app.models import Session, Skill, User, Project

application = app

with app.app_context():
    from flask_migrate import upgrade as upgrd

    upgrd()
    if not User.query.all():
        default_user = User(
            username="admin",
            email="cabrera.student@gmail.com",
            password_hash=os.environ["DEFAULT_PASS_HASH"],
            admin=True,
        )
        db.session.add(default_user)
        db.session.commit()


@app.shell_context_processor
def make_shell_processor():
    return {
        "db": db,
        "User": User,
        "Session": Session,
        "Skill": Skill,
        "Project": Project,
    }


if __name__ == "__main__":
    application.run()
