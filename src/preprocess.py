import json
import pathlib
from shutil import copyfile


USE_TRAIN = False

if (USE_TRAIN):
    data_folder = "../data/figureqa/train1/" 
else:
    data_folder = "../data/figureqa/sample_train1/"



# https://github.com/Maluuba/FigureQA/blob/master/docs/question_id_map.txt
line_question_id_map = {
    "MIN_AUC": 6,
    "MAX_AUC": 7,
    "SMOOTHEST": 8,
    "ROUGHEST": 9,
    "GLOBAL_MIN": 10, 
    "GLOBAL_MAX": 11,
    "LESS": 12,
    "GREATER": 13,
    "INTERSECT": 14 
}

def question_types_to_id(questions):
    return list(map(lambda question_type: line_question_id_map[question_type], questions))

def load_data():
    processed_plots = []

    with open(f"{data_folder}/annotations.json", "r") as f:
        print("parsing annotations...")
        annotations = json.load(f)
        line_plots = list(filter(lambda plot: plot["type"] == "line", annotations))
        print("processing plots...")
        for plot in line_plots:
            plot_data = extract_plot_data(plot["models"])
            processed_plots.append({
                # if needed, can have all sorts of data from here 
                "image_name": f"{plot["image_index"]}.png",
                "data": plot_data
            })
    
    with open(f"{data_folder}/qa_pairs.json", "r") as f:
        print("parsing QA...")
        qa_pairs = json.load(f)["qa_pairs"]
        line_plot_indexes = list(map(lambda plot: plot["image_index"], line_plots))


        # it"s faster to do this
        desired_question_ids = question_types_to_id(["GREATER", "LESS", "INTERSECT"])

        line_qa_questions = list(filter(lambda qa: qa["question_id"] in desired_question_ids, qa_pairs))
        print(list(map(lambda x: x["question_string"], line_qa_questions)))
        
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
        copyfile(f"{data_folder}/png/{plot["image_name"]}", f"../data/processed/images/{plot["image_name"]}")

data = load_data()
#pathlib.Path("../data/processed/images").mkdir(parents=True, exist_ok=True)

#copy_images(data)
#write_metadata_json(data)