import json

descriptions = []
fails = []
with open('./logData/canboatJSON_test.ndjson') as f:
    for i in f:
        tmp = json.loads(f.readline())
        try:
            if tmp['description'] in descriptions:
                pass
            else:
                print(tmp['description'])
                descriptions.append(tmp['description'])
        except KeyError:
            if tmp['pgn'] in fails:
                pass
            else:
                fails.append(tmp['pgn'])

