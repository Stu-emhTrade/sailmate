import os
from datetime import datetime
import sqlite3


def get_db_filename():
    today = datetime.now().strftime('%Y%m%d')
    files = os.listdir('./data/logData/')
    matching_files = [i for i, f in enumerate(files) if f.split('_')[0] == today]
    if len(matching_files) > 0:
        new_incr = 1 + max([int(files[i].split('_')[1].split('.')[0]) for i in matching_files])
        filename = today + '_' + str(new_incr) + '.db'
    else:
        filename = today + '_0.db'

    return filename


con = sqlite3.connect(get_db_filename())
