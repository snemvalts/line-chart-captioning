import json
import os

# very crude templating system at the moment. 

# TODO: calculate deltas given previous value. if delta goes over threshold, not flat
def is_flat(data):
    delta = abs((data[0][1] / data[len(data) - 1][1]) - 1)
    return True if delta < 0.001 else False

# TODO: calculate deltas again. see if there are any bigger changes inbetween
def has_increased(data):
    if (is_flat(data)): return False
    # if first y is smaller than last y 
    return True if data[0][1] < data[len(data) - 1][1] else False

#TODO: same as increased
def has_decreased(data):
    if (is_flat(data)): return False
    # if first y is smaller than last y 
    return True if data[0][1] > data[len(data) - 1][1] else False


#TODO: qualifier function that finds the most appropriate template given values
def increase_decrease_template(lines):
    increased = list(filter(lambda line: has_increased(line['values']), lines))
    decreased = list(filter(lambda line: has_decreased(line['values']), lines))
    increased_names =  list(map(lambda x: x['name'], increased))
    decreased_names = list(map(lambda x: x['name'], decreased))

    if (len(increased_names) > 0 and len(decreased_names) > 0):
        return f"{', '.join(increased_names)} increased while {', '.join(decreased_names)} decreased"
    elif(len(increased_names) == 0 and len(decreased_names) > 0):
        return f"{', '.join(decreased_names)} decreased"
    elif(len(increased_names) > 0 and len(decreased_names) == 0):
        return f"{', '.join(increased_names)} increased"


def load_processed_data():
    with open("../data/processed/data.json", "r") as f:
        print("parsing json...")
        annotations = json.load(f)
        return annotations



plots = load_processed_data()
to_template = plots[0]
print(increase_decrease_template(to_template['data']))
os.system(f"open ../data/processed/images/{to_template['image_name']}")