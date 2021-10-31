from datetime import datetime
import os
import json
from flask import Flask

app = Flask(__name__)

print('this ran')


@app.route("/")
def index():
    return "Hello World!"

if __name__ == "__main__":
    app.run(host="0.0.0.0")

# ## setup file dump
# today = datetime.now().strftime('%Y%m%d')
# files = os.listdir('./logData/')
# matching_files = [ i for i, f in enumerate(files) if f.split('_')[0] == today ]
# if len(matching_files) > 0:
#     new_incr = 1 + max([int(files[i].split('_')[1].split('.')[0]) for i in matching_files])
#     filename = today + '_' + str(new_incr) + '.ndjson'
# else:
#     filename = today + '_0.ndjson'
