import json

RESULT_FILE = "results.json"

def already_computed(commit):
    with open(RESULT_FILE, "r+") as f:
        results = json.load(f)
        return commit in results

def add_result(commit, value):
    with open(RESULT_FILE, "r+") as f:
        print("Adding results...")
        results = json.load(f)
        f.seek(0)
        f.truncate()
        if commit not in results: results[commit]= {}
        results[commit].update(value)
        json.dump(results, f, sort_keys=True, indent=2)

