import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    if "RDS_HOSTNAME" in os.environ:
        user = os.environ["RDS_USERNAME"]
        passw = os.environ["RDS_PASSWORD"]
        host = os.environ["RDS_HOSTNAME"]
        port = os.environ["RDS_PORT"]
        db_name = os.environ["RDS_DB_NAME"]
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{user}:{passw}@{host}:{port}/{db_name}"
        )
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
            basedir, "app.db"
        )

    SECRET_KEY = os.environ.get("SECRET_KEY") or "test_secret_key"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
