from app import app, db
from app.models import User, Session, Skill

@app.shell_context_processor
def make_shell_processor():
    return {'db':db, 'User': User, 'Session': Session, 'Skill': Skill}

if __name__ == "__main__":
    app.run()
