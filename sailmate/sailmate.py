import argparse
from .db.setup import setup_log_db, setup_app_db
from sailmate.app import create_app
import logging
from logging.handlers import RotatingFileHandler

LOG_DATA_PATH = './sailmate/data/logData/'
APP_DB_FILE = './sailmate/data/app_data.db'

APPLICATION_LOG_FILE = './sailmate/app_logs.log'

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

# log_handler = RotatingFileHandler(APPLICATION_LOG_FILE,
#                                   mode='a',
#                                   maxBytes=10 * 1024 * 1024,
#                                   backupCount=2,
#                                   encoding=None)

log_handler = logging.StreamHandler()

log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)

app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)
app_log.addHandler(log_handler)


def main(test_can_file=None):
    # setup app db
    if not setup_app_db(APP_DB_FILE):
        raise ValueError("app db not setup")
    app_log.info('app db setup')
    
    # run flask app
    app = create_app(APP_DB_FILE, LOG_DATA_PATH, test_can_file)
    app_log.info('running flask')
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', action='store', default=None)
    args = parser.parse_args()
    main(test_can_file=args.filename)
