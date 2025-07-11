import json

def print_dict(data: dict, prefix: str = ""):
    if prefix != "":
        print(prefix)
    print(json.dumps(data, indent=4, ensure_ascii=False))
