import json
import os


def get_description(instance):
    return ". ".join(instance["descriptions"])

def load_processed_data():
    with open("../data/processed/data.json", "r") as f:
        print("parsing json...")
        annotations = json.load(f)
        return annotations



plots = load_processed_data()
to_template = plots[4]
print(len(plots))
print(get_description(to_template))
os.system(f"open ../data/processed/images/{to_template['image_name']}")