from os import listdir
from os.path import isfile, join
import csv
import pathlib
import re
from shutil import copyfile


USE_TRAIN = True

# only year based are line graphs, same definition in chart2text
def is_line_graph(data):
    return data[0][0].lower() == "year"

dataset_folder = "data/charttotext/"
data_folder = join(dataset_folder, "data")
captions_folder = join(dataset_folder, "captions")



data_files = [f for f in listdir(data_folder) if isfile(join(data_folder, f))]
caption_files = [f for f in listdir(captions_folder) if isfile(join(captions_folder, f))]


data_caption_pairing = {}

print("reading data files...")
for data_file_name in data_files:
    data_file_path = join(data_folder, data_file_name)
    data_number = data_file_name.split(".csv")[0]

    with open(data_file_path, 'r') as data_file:
        data_file_reader = csv.reader(data_file)
        data = list(data_file_reader)
        if(is_line_graph(data)):
            data_caption_pairing[data_number] = [data]


# add captions to same dict, 
for caption_file_name in caption_files:
    caption_number = caption_file_name.split(".txt")[0]
    if(caption_number in data_caption_pairing):
        caption_file_path = join(captions_folder, caption_file_name)
        with open(caption_file_path, 'r') as caption_file:
            caption = "".join(caption_file.readlines()).rstrip()
            data_caption_pairing[caption_number].append(caption)

# every data should have a caption
assert all(map(lambda pair: len(pair) == 2, data_caption_pairing.values()))



pathlib.Path("data/processed_natural/images").mkdir(parents=True, exist_ok=True)



def clean_table_data(table_data):
    new_table_data = []

    for row in table_data:
        year = int(re.sub("[^0-9]", "", row[0]))
        data = float(re.sub("[^0-9\.]", "", row[1]))
        new_table_data.append([year, data])

    return new_table_data


keys_and_captions = []

for key in list(data_caption_pairing.keys()):
    raw_data = data_caption_pairing[key][0]
    caption = data_caption_pairing[key][1]
    keys_and_captions.append([key, caption])
    copyfile(f"{dataset_folder}/matplot/{key}.png", f"data/processed_natural/images/{key}.png")


with open("data/processed_natural/captions.csv", mode="w") as captions_file:
    captions_writer = csv.writer(captions_file)

    captions_writer.writerow(['number', 'caption'])
    captions_writer.writerows(keys_and_captions)