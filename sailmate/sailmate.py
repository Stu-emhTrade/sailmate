from datetime import datetime
import os
import json
from logger.app import app
from db.setup import con


def main():
    ## initialise an sqllite file

    ## run flask app

    app.run(host="0.0.0.0")


if __name__ == "__main__":
    main()

# ## setup file dump
