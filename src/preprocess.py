import json
import pathlib
from shutil import copyfile


def load_data():
    processed_plots = []

    with open("../data/figureqa/train1/annotations.json", "r") as f:
        print("parsing json...")
        annotations = json.load(f)
        line_plots = list(filter(lambda plot: plot["type"] == "line", annotations))
        print("processing plots...")
        for plot in line_plots:
            plot_data = extract_plot_data(plot["models"])
            processed_plots.append({
                # if needed, can have all sorts of data from here 
                "image_name": f"{plot['image_index']}.png",
                "data": plot_data
            })
    
    return processed_plots

# models: list of models, as specified in annotations_format.txt
def extract_plot_data(models):
    return list(map(lambda model: {
        "name": model["name"],
        "values": list(zip(model["x"],model["y"])),
    }, models))


def write_metadata_json(data):
    print("writing json...")
    with open("../data/processed/data.json", "w") as f:
        json.dump(data, f)

def copy_images(data):
    print("copying images...")
    for plot in data:
        copyfile(f"../data/figureqa/train1/png/{plot['image_name']}", f"../data/processed/images/{plot['image_name']}")

data = load_data()
pathlib.Path("../data/processed/images").mkdir(parents=True, exist_ok=True)

copy_images(data)
write_metadata_json(data)