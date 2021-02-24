import json
import pathlib
from shutil import copyfile
import csv
import string
import sys
import random



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


def serialize_question(question):
    if (question['answer'] != 1):
        raise ValueError("Can't generate description for false question")
    
    question_type = question_id_to_type[question['question_id']]

    return {
      'description_type': question_type,
      'color1_name': question['color1_name'],
      'color2_name': question['color2_name']
    }



def load_data(data_folder, questions=["GREATER", "LESS", "INTERSECT"]):
    processed_plots = []
    image_index_to_qas = {}

    with open(f"{data_folder}/qa_pairs.json", "r") as f:
        print("parsing QA...")
        qa_pairs = json.load(f)["qa_pairs"]


        desired_question_ids = question_types_to_id(questions)
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
            
            descriptions_for_plot = list(
                map(
                    lambda qa: serialize_question(qa), 
                    qas_for_plot
                )
            )

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


# for plot with n descriptions, create n plots with 1 description each
def unroll_descriptions(data):
    print("unrolling descriptions...")
    new_data = []
    for plot in data:
        # if we want to unroll a description with multiple sentences to n plot with a single sentence description,
        # we go over all the sentences and provide a replacement description
        for description in plot['descriptions']:
            new_data.append(
                {
                    **plot,
                    'descriptions': [description]
                }
            )

    return new_data


def write_captions_csv(data, dest_folder_name):
    def get_row(plot):
        image_number = plot['image_number']
        description_type = plot['descriptions'][0]['description_type']
        color1_name = plot['descriptions'][0]['color1_name']
        color2_name = plot['descriptions'][0]['color2_name']
        all_subjects = list(map(lambda x: x['name'], plot['data']))

        return [image_number, description_type, color1_name, color2_name, all_subjects]
        
    
    csv_rows = []

    for plot in data:
        csv_rows.append(get_row(plot))

    print("writing csv...")
    with open(f"data/processed_synthetic/{dest_folder_name}/captions.csv", mode="w") as captions_file:
        captions_writer = csv.writer(captions_file)

        captions_writer.writerow(['number', 'description_type', 'color1_name', 'color2_name'])
        captions_writer.writerows(csv_rows)


def copy_images(data, src_folder, dest_folder_name):
    print("copying images...")
    for plot in data:
        copyfile(
            f"{src_folder}/png/{plot['image_name']}", 
            f"data/processed_synthetic/{dest_folder_name}/images/{plot['image_name']}"
        )



if __name__ == "__main__":
    # i want to do proper arg parsing but the only one who's going to suffer
    # from this mess is probably only going to be me so 🤷
    synthetic_config_flag_present = '--synthetic-config' in sys.argv[1:]
    synthetic_config = json.load(open(sys.argv[sys.argv.index('--synthetic-config') + 1], 'r')) if synthetic_config_flag_present else None

    replace_subjects_flag_present = '--replace-subjects' in sys.argv[1:]

    src_folder = sys.argv[-1]

    if (synthetic_config is not None):
        data = load_data(
            src_folder,
            questions=synthetic_config['questions'],
        )
    else:
        data = load_data(src_folder)

    data = unroll_descriptions(data)


    dest_folder_name = f"{pathlib.Path(src_folder).name}-types"
    pathlib.Path(f"data/processed_synthetic/{dest_folder_name}/images").mkdir(parents=True, exist_ok=True)
    copy_images(data, src_folder, dest_folder_name)
    #write_metadata_json(data)
    write_captions_csv(data, dest_folder_name)