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


# generates a description for the plot, based on the question
def question_to_description(question, question_selection=None):
    if (question['answer'] != 1):
        raise ValueError("Can't generate description for false question")
    
    question_type = question_id_to_type[question['question_id']]

    if (question_selection is not None):
        question_selections = question_selection[question_type]
        question_template = random.choice(question_selections)
        color1_var_present = '<Color1>' in question_template
        color2_var_present = '<Color2>' in question_template

        final_question = question_template

        if (color1_var_present):
            final_question = final_question.replace('<Color1>', question['color1_name'])

        if (color2_var_present):
            final_question = final_question.replace('<Color2>', question['color2_name'])

        return final_question


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


def load_data(data_folder, questions=["GREATER", "LESS", "INTERSECT"], question_selection=None):
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
                    lambda qa: question_to_description(qa, question_selection=question_selection), 
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


# replace subjects with <A>, <B>, <C>...
def replace_subjects(data, replace_locally=False):
    print('replacing subjects...')
    for plot in data:
        subject_names = list(map(lambda x: x['name'], plot['data']))
        # here, we will only replace those subjects that are present in the single unrolled description
        # so we won't have a, b, c, d, rather only a, b
        if (replace_locally):
            assert len(plot['descriptions']) == 1, f"Descriptions for plot {plot['name']} not unrolled"
            # only include subjects that are present in the only unrolled description
            subject_names = list(filter(lambda subject: subject in plot['descriptions'][0], subject_names))
            # filter out any cases where "gold" ends up in subjects, even though it's only because "dark gold" really is
            subject_names = [subject for subject in subject_names if len(list(filter(lambda other_subject: subject in other_subject, subject_names))) == 1]

        #['A', 'B', 'C']
        replacement_subject_names = string.ascii_uppercase[:len(subject_names)]
        #['<A>', '<B>', '<C>']
        replacement_subject_names = list(map(lambda x: f'<{x}>', replacement_subject_names))
        # {'Red Violet': '<A>', 'Green Lime': '<B>'}
        subject_replacement_map = dict(zip(subject_names, replacement_subject_names))

        for idx, description in enumerate(plot['descriptions']):
            # largest elements first: prevents cases where substring is replaced first
            for subject in sorted(subject_replacement_map.keys(), reverse=True, key=len):
                plot['descriptions'][idx] = plot['descriptions'][idx].replace(subject, subject_replacement_map[subject])

        plot['subject_map'] = {replacement: subject for subject, replacement in subject_replacement_map.items()}


# models: list of models, as specified in annotations_format.txt
def extract_plot_data(models):
    return list(map(lambda model: {
        "name": model["name"],
        "values": list(zip(model["x"],model["y"])),
    }, models))

# dump the whole metadata as json
def write_metadata_json(data):
    print("writing json...")
    with open("data/processed_synthetic/data.json", "w") as f:
        json.dump(data, f)

# for plot with n descriptions, create n plots with 1 description each
def unroll_descriptions(data):
    print("unrolling descriptions...")
    new_data = []
    for plot in data:
        # if we want to unroll a description with multiple sentences to n plot with a single sentence description,
        # we go over all the sentences and provide a replacement description
        for description_sentence in plot['descriptions']:
            new_data.append(
                {
                    **plot,
                    'descriptions': [description_sentence]
                }
            )

    return new_data

def write_captions_csv(data, dest_folder_name, description_limit, include_subjects=None, unroll_descriptions=False):
    def get_row(plot):
        image_number = plot['image_number']
        description = None

        if (description_limit is None):
            description = ". ".join(plot['descriptions'])
        else:
            description = ". ".join(plot['descriptions'][:description_limit])
        
        if (include_subjects):
            return [image_number, description, plot['subject_map']]
        else:
            return [image_number, description]
        
    
    csv_rows = []

    for plot in data:
        csv_rows.append(get_row(plot))

    print("writing csv...")
    with open(f"data/processed_synthetic/{dest_folder_name}/captions.csv", mode="w") as captions_file:
        captions_writer = csv.writer(captions_file)

        if (include_subjects):
            captions_writer.writerow(['number', 'caption', 'subject_map'])
        else:
            captions_writer.writerow(['number', 'caption'])
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

    unroll_descriptions_flag_present = '--unroll-descriptions' in sys.argv[1:]
    replace_subjects_flag_present = '--replace-subjects' in sys.argv[1:]
    replace_subjects_locally_flag_present = '--replace-subjects-locally' in sys.argv[1:]

    description_limit_flag_present = '--description-limit' in sys.argv[1:]
    description_limit = int(sys.argv[sys.argv.index('--description-limit') + 1]) if description_limit_flag_present else None

    src_folder = sys.argv[-1]

    assert not(unroll_descriptions_flag_present and description_limit_flag_present), 'Cannot pass unroll and description limit flag concurrently'

    # replace subjects locally only if unroll is present
    # p -> q
    assert not(replace_subjects_locally_flag_present) or unroll_descriptions_flag_present, 'For local subject replacement, descriptions must be unrolled as well'

    if (synthetic_config is not None):
        data = load_data(
            src_folder,
            questions=synthetic_config['questions'],
            question_selection=synthetic_config['question_selection']
        )
    else:
        data = load_data(src_folder)

    if (unroll_descriptions_flag_present):
        data = unroll_descriptions(data)

    if (replace_subjects_flag_present or replace_subjects_locally_flag_present):
        replace_subjects(data, replace_locally = replace_subjects_locally_flag_present)

    dest_folder_name = pathlib.Path(src_folder).name
    pathlib.Path(f"data/processed_synthetic/{dest_folder_name}/images").mkdir(parents=True, exist_ok=True)
    copy_images(data, src_folder, dest_folder_name)
    #write_metadata_json(data)
    write_captions_csv(data, dest_folder_name, description_limit, 
                       include_subjects=replace_subjects_flag_present or replace_subjects_locally_flag_present,
                       unroll_descriptions=unroll_descriptions_flag_present)