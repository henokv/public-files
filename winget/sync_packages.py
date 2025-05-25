import json
import os
import glob
from datetime import datetime, timezone

# Delete all JSON files in ../docs/winget before generating new ones
def clean_docs_winget():
    docs_dir = os.path.join(os.path.dirname(__file__), "../docs/winget")
    for f in glob.glob(os.path.join(docs_dir, "*.json")):
        try:
            os.remove(f)
        except Exception:
            pass

def load_package_list():
    with open(os.path.join(os.path.dirname(__file__), "packages.json"), "r", encoding="utf-8") as f:
        return json.load(f)

file_map = {
    "full": "../docs/winget/full.json",
    "private": "../docs/winget/private.json",
    "work": "../docs/winget/work.json",
    "az": "../docs/winget/az.json"
}

def load_json(filename):
    if not os.path.exists(filename):
        # Create a minimal initial structure if file does not exist
        data = {
            "$schema": "https://aka.ms/winget-packages.schema.2.0.json",
            "CreationDate": "",
            "Sources": [
                {
                    "Packages": [],
                    "SourceDetails": {
                        "Argument" : "https://cdn.winget.microsoft.com/cache",
                        "Identifier" : "Microsoft.Winget.Source_8wekyb3d8bbwe",
                        "Name" : "winget",
                        "Type" : "Microsoft.PreIndexed.Package"
                    }
                }
            ],
            "WinGetVersion" : "1.10.390"
        }
        save_json(filename, data)
        return data
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        f.write("\n")

def build_package_sets(package_list):
    sets = {k: set() for k in file_map}
    for entry in package_list:
        sets["full"].add(entry["package"])
        for target in entry["inList"]:
            if target in sets:
                sets[target].add(entry["package"])
    return sets

def update_packages_json(filename, packages):
    data = load_json(filename)
    # Set CreationDate in the required format
    data["CreationDate"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "-00:00"
    data["Sources"][0]["Packages"] = [
        {"PackageIdentifier": pkg} for pkg in sorted(packages)
    ]
    save_json(filename, data)

def main():
    clean_docs_winget()
    package_list = load_package_list()
    sets = build_package_sets(package_list)
    for key, filename in file_map.items():
        update_packages_json(filename, sets[key])

if __name__ == "__main__":
    main()
