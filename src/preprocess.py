import json


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
    
    print(processed_plots[0])


# models: list of models, as specified in annotations_format.txt
def extract_plot_data(models):
    return list(map(lambda model: {
        "name": model["name"],
        "values": list(zip(model["x"],model["y"])),
    }, models))

load_data()