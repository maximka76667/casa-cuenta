from datetime import datetime
import json


def serialize_dates(v):
    return v.isoformat() if isinstance(v, datetime) else v


def datetime_parser(dct):
    for k, v in dct.items():
        if isinstance(v, str):
            if v.endswith(("+00:00", "+00", "Z")) or "+00:" in v:
                try:
                    dct[k] = datetime.fromisoformat(v)
                except:
                    pass
    return dct


def dump_json(data):
    return json.dumps(data, default=serialize_dates)


def load_json(data):
    return json.loads(data, object_hook=datetime_parser)
