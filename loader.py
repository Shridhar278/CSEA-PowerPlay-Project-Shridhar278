import json

def load_json(path):  
    # inst_1 & inst_2
    with open(path, "r") as f:
        return json.load(f)


def save_json(data, path):
    # schedule.json
    with open(path, "w") as f:
        json.dump(data, f, indent=4)