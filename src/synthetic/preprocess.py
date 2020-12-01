import json
import pathlib
from shutil import copyfile
import csv

USE_TRAIN = True

if (USE_TRAIN):
    data_folder = "data/figureqa/train1/" 
else:
    data_folder = "data/figureqa/sample_train1/"



# https://github.com/Maluuba/FigureQA/blob/master/docs/question_id_map.txt
question_type_to_id = {
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

question_id_to_type = {v: k for k, v in question_type_to_id.items()}


# can be used to check whether the original question is in expected form
question_ab_form = {
    "MIN_AUC": "Does A have the minimum area under the curve?",
    "MAX_AUC": "Does A have the maximum area under the curve?",
    "SMOOTHEST": "Is A the smoothest?",
    "ROUGHEST": "Is A the roughest?",
    "GLOBAL_MIN": "Does A have the lowest value?", 
    "GLOBAL_MAX": "Does A have the highest value?",
    "LESS": "Is A smaller than B?",
    "GREATER": "Is A greater than B?",
    "INTERSECT": "Does A intersect B?",
}



def question_types_to_id(questions):
    return list(map(lambda question_type: question_type_to_id[question_type], questions))


# generates a description for the plot, based on the question
def question_to_description(question):
    if (question['answer'] != 1):
        raise ValueError("Can't generate description for false question")
    
    question_type = question_id_to_type[question['question_id']]

    if (question_type == 'LESS'):
        return f"{question['color1_name']} is less than {question['color2_name']}"
    elif (question_type == 'GREATER'):
        return f"{question['color1_name']} is greater than {question['color2_name']}"
    elif (question_type == 'INTERSECT'):
        return f"{question['color1_name']} intersects {question['color2_name']}"
    elif (question_type == 'GLOBAL_MAX'):
        return f"{question['color1_name']} has the highest value"
    elif (question_type == 'GLOBAL_MIN'):
        return f"{question['color1_name']} has the lowest value"
    elif (question_type == 'SMOOTHEST'):
        return f"{question['color1_name']} is the smoothest"
    elif (question_type == 'ROUGHEST'):
        return f"{question['color1_name']} is the roughest"
    elif (question_type == 'MIN_AUC'):
        return f"{question['color1_name']} has the minimum area under the curve"
    elif (question_type == 'MAX_AUC'):
        return f"{question['color1_name']} has the maximum area under the curve"  


def load_data():
    processed_plots = []
    image_index_to_qas = {}

    with open(f"{data_folder}/qa_pairs.json", "r") as f:
        print("parsing QA...")
        qa_pairs = json.load(f)["qa_pairs"]


        desired_question_ids = question_types_to_id(["GREATER", "LESS", "INTERSECT"])
        desired_qa = list(
            filter(
                lambda qa: qa["question_id"] in desired_question_ids, 
                filter(
                    lambda qa: qa['answer'] == 1,
                    qa_pairs
                )
            )
        )

        for qa in desired_qa:
            image_index = qa['image_index']
            if(image_index in image_index_to_qas):
                image_index_to_qas[image_index].append(qa)
            else:
                image_index_to_qas[image_index] = [qa]


    with open(f"{data_folder}/annotations.json", "r") as f:
        print("parsing annotations...")
        annotations = json.load(f)
        line_plots = list(filter(lambda plot: plot["type"] == "line", annotations))
        print("processing plots...")
        for plot in line_plots:
            plot_data = extract_plot_data(plot["models"])

            qas_for_plot = image_index_to_qas[plot["image_index"]] if plot["image_index"] in image_index_to_qas else []
            
            descriptions_for_plot = list(map(lambda qa: question_to_description(qa), qas_for_plot))

            if (len(descriptions_for_plot) > 0):
                processed_plots.append({
                    # if needed, can have all sorts of data from here 
                    "image_name": f"{plot['image_index']}.png",
                    "image_number": plot['image_index'],
                    "data": plot_data,
                    "descriptions": descriptions_for_plot
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
    with open("data/processed_synthetic/data.json", "w") as f:
        json.dump(data, f)


def write_captions_csv(data):
    csv_rows = []

    for plot in data:
        image_number = plot['image_number']
        description = ". ".join(plot['descriptions'])
        csv_rows.append([image_number, description])

    print("writing csv...")
    with open("data/processed_synthetic/captions.csv", mode="w") as captions_file:
        captions_writer = csv.writer(captions_file)

        captions_writer.writerow(['number', 'caption'])
        captions_writer.writerows(csv_rows)


def copy_images(data):
    print("copying images...")
    for plot in data:
        copyfile(f"{data_folder}/png/{plot['image_name']}", f"data/processed_synthetic/images/{plot['image_name']}")

data = load_data()
pathlib.Path("data/processed_synthetic/images").mkdir(parents=True, exist_ok=True)

copy_images(data)
#write_metadata_json(data)
write_captions_csv(data)