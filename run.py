from app import app, db
from app.models import Session, Skill, User, Project


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
    app.run()
