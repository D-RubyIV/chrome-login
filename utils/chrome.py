import json


def get_chrome_version(state_path: str = None):
    with open(state_path, encoding='utf-8') as f:
        data = json.load(f)
        print(data)
        version = data["user_experience_metrics"]["stability"]["stats_version"]
        print("Version:", version)
        return version