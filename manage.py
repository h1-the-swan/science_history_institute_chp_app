#!/usr/bin/env python
import os
import subprocess

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from redis import Redis
from rq import Connection, Queue, Worker

from app import create_app, db
from app.models import Role, User, OralHistory
from config import Config

URL_PREFIX = "/chp"
app = create_app(os.getenv('FLASK_CONFIG') or 'default', url_prefix=URL_PREFIX)
app.config['APPLICATION_ROOT'] = URL_PREFIX
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def recreate_db():
    """
    Recreates a local database. You probably should not use this on
    production.
    """
    db.drop_all()
    db.create_all()
    db.session.commit()

@manager.command
def recreate_db_if_not_exists():
    """
    Recreates a local database. You probably should not use this on
    production.
    """
    try:
        User.query.filter_by(username='admin').one()
        # if the above succeeds, do not recreate the database
        RECREATE_DB = False
    except:
        # if the above failed, then recreate the database
        RECREATE_DB = True

    if RECREATE_DB is True:
        db.drop_all()
        db.create_all()
        db.session.commit()


@manager.option(
    '-n',
    '--number-users',
    default=10,
    type=int,
    help='Number of each model type to create',
    dest='number_users')
def add_fake_data(number_users):
    """
    Adds fake data to the database.
    """
    User.generate_fake(count=number_users)


@manager.command
def setup_dev():
    """Runs the set-up needed for local development."""
    setup_general()


@manager.command
def setup_prod():
    """Runs the set-up needed for production."""
    setup_general()


def setup_general():
    """Runs the set-up needed for both local development and production.
       Also sets up first admin user."""
    Role.insert_roles()
    admin_query = Role.query.filter_by(name='Administrator')
    if admin_query.first() is not None:
        if User.query.filter_by(email=Config.ADMIN_EMAIL).first() is None:
            user = User(
                # first_name='Admin',
                # last_name='Account',
                username='admin',
                full_name='Admin Account',
                password=Config.ADMIN_PASSWORD,
                confirmed=True,
                email=Config.ADMIN_EMAIL)
            db.session.add(user)
            db.session.commit()
            print('Added administrator {}'.format(user.full_name))

    try:
        OralHistory.insert_oral_histories()
        print("loaded oral histories")
    except FileNotFoundError as e:
        print("ERROR could not load oral histories -- {}".format(e))


@manager.command
def run_worker(host=None, port=None):
    """Initializes a slim rq task queue."""
    listen = ['default']
    conn = Redis(
        host = host if host is not None else app.config['RQ_DEFAULT_HOST'],
        port = port if port is not None else app.config['RQ_DEFAULT_PORT'],
        db=0,
        password=app.config['RQ_DEFAULT_PASSWORD'])

    conn.flushall()

    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()


@manager.command
def format():
    """Runs the yapf and isort formatters over the project."""
    isort = 'isort -rc *.py app/'
    yapf = 'yapf -r -i *.py app/'

    print('Running {}'.format(isort))
    subprocess.call(isort, shell=True)

    print('Running {}'.format(yapf))
    subprocess.call(yapf, shell=True)


if __name__ == '__main__':
    manager.run()
