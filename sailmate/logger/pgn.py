from dataclasses import dataclass
from datetime import datetime
import json
from dateutil import parser


@dataclass
class DataPoint:
    variable_name: str
    value: [int, float, str]

@dataclass
class TelemetryRecord:
    timestamp: datetime
    pgn: int
    variable_name: str
    value: [int, float, str]

@dataclass
class PgnRecord:
    pgn: int
    timestamp: datetime
    record: [DataPoint]

    def unpack(self) -> []:
        output_list = []
        for i in self.record:
            output_list.append(TelemetryRecord(self.timestamp, self.pgn, i.variable_name, i.value))
        return output_list


pgn_model = {
    13036: {
        "paths": [
            "environment.wind.speedApparent",
            "environment.wind.angleApparent"
        ]
    },
    128259: {
        "paths": [
            "navigation.speedThroughWater"  # "navigation.speedThroughWaterReferenceType"
        ]
    },
    127250: {
        "paths": [
            "navigation.headingMagnetic"
        ]
    },
    127245: {
        "paths": [
            "steering.rudderAngle"
        ]
    }
}


# todo add others that are in config.json, also work out whether any of the stuff coming down the pipe is useful
# eg
# 65341
# 127237


def pgn_handler(sig_k_row, pgn_model) -> [PgnRecord, None]:
    obj_to_load = json.loads(sig_k_row)
    pgn_records = []
    for u in obj_to_load['updates']:  # usually just one i think
        pgn = u['source']['pgn']
        if pgn not in pgn_model.keys():
            continue

        ts = parser.parse(u['timestamp'])
        path_x_value = dict([(x['path'], x['value']) for x in u['values']])

        paths_to_store = pgn_model[pgn]['paths']

        data_records = []
        for p in paths_to_store:
            path_name = p.split(".")[-1]
            data_records.append(DataPoint(variable_name=path_name,
                                          value=path_x_value[p]))

        pgn_records.append(PgnRecord(pgn, ts, data_records))

    return pgn_records