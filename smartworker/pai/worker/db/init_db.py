from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import pathlib
import yaml

from models import Base

BASE_DIR = pathlib.Path(__file__).parent
config_path = BASE_DIR /  'config.yaml'


def get_config(path):
    with open(str(path), 'rb') as f:
        config = yaml.load(f.read())
    return config

config = get_config(config_path)

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

engine = create_engine(DSN.format(
    **config['postgres_user']
))


def setup_db(**kwargs):
    db_user = kwargs.get('user')
    db_pass = kwargs.get('password')
    db_name = kwargs.get('database')

    conn = create_engine(
        DSN.format(**config['postgres_admin']),
        isolation_level='AUTOCOMMIT'
    ).connect()

    conn.execute("DROP DATABASE IF EXISTS {}".format(db_name))
    conn.execute("DROP ROLE IF EXISTS {}".format(db_user))
    conn.execute("CREATE USER {} WITH PASSWORD '{}'".format(db_user, db_pass))
    conn.execute("CREATE DATABASE {} ENCODING 'UTF8'".format(db_name))
    conn.execute("GRANT ALL PRIVILEGES ON DATABASE {} TO {}".format(db_name, db_user) )
    conn.close()


if __name__ == '__main__':
    setup_db(**config['postgres_user'])
    Base.metadata.create_all(bind=engine)