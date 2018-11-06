import os

from flask_script import Manager, Shell

from app import create_app, db
from app.models import *

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db)


@manager.command
def test():
    pass


@manager.command
def create_db():
    db.create_all()


@manager.command
def drop_db():
    db.drop_all()


@manager.command
def clear_db():
    meta = db.metadata
    session = db.session
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())
    session.commit()


manager.add_command('shell', Shell(make_context=make_shell_context))


def main():
    manager.run()


if __name__ == '__main__':
    main()
