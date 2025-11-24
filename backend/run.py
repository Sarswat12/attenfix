import os
import sys
from dotenv import load_dotenv

# Load the backend .env file (load relative to this script so running from repo root still finds it)
base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, '.env'))

from app import create_app, db

# Allow overriding config via command-line: `python run.py testing`
cli_config = sys.argv[1] if len(sys.argv) > 1 else None
env_config = cli_config or os.getenv('FLASK_ENV', 'development')
app = create_app(env_config)

# Log masked DB URI to help debugging (mask password)
try:
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    if db_uri:
        # mask between : and @ for password
        import re
        masked = re.sub(r"://(.*?):(.*?)@", r"//\1:****@", db_uri)
        print('Using database URI:', masked)
except Exception:
    pass

@app.shell_context_processor
def make_shell_context():
    return {'db': db}

if __name__ == '__main__':
    # Ensure tables exist (helpful when migrations are not present)
    from sqlalchemy import inspect

    with app.app_context():
        try:
            inspector = inspect(db.engine)
            if not inspector.has_table('users'):
                print('Users table not found — creating all tables with SQLAlchemy db.create_all()')
                db.create_all()
        except Exception as e:
            # Don't fail hard at startup if the DB is temporarily inaccessible.
            # Log the exception and allow the app to start; runtime requests will surface DB errors.
            print('Warning: could not inspect/create DB tables at startup:', str(e))

    port = os.getenv('FLASK_PORT', '5000')
    # Force debug off in testing mode to avoid the reloader (which restarts on file changes)
    debug = False if os.getenv('FLASK_ENV', '') == 'testing' else (os.getenv('FLASK_DEBUG', 'False') == 'True')
    app.run(
        host='0.0.0.0',
        port=int(port),
        debug=debug
    )
