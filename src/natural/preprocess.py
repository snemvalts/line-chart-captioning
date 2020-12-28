from os import listdir
from os.path import isfile, join
import csv
import pathlib
import re
from shutil import copyfile


broken_images = ["50", "71", "85", "95", "115", "159",
"237", "298", "345", "354", "455", "475", "510", "517",
"554", "609", "700", "748", "750", "815", "845", "868",
"875", "911", "928", "1016", "1054", "1058", "1213", "1281",
"1317", "1326", "1406", "1527", "1553", "1563", "1683", "1690",
"1736", "1801", "1884", "1885", "1929", "1939", "2041", "2046",
"2077", "2098", "2159", "2191", "2246", "2295", "2312", "2318",
"2331", "2562", "2572", "2639", "2648", "2657", "2707", "2780",
"2788", "2824", "2859", "2920", "3026", "3178", "3282", "3342", 
"3354", "3357", "3366", "3493", "3520", "3582", "3583", "3598",
"3636", "3975", "4048", "4078", "4154", "4165", "4169", "4182", 
"4340", "4365", "4434", "4447", "4469", "4478", "4499", "4511",
"4544", "4549", "4585", "4619", "4828", "4912", "4913", "4938",
"5013", "5052", "5055", "5070", "5097", "5098", "5106", "5111",
"5324", "5360", "5406", "5408", "5411", "5548", "5608", "5706",
"5732", "5761", "5790", "5872", "5897", "5951", "5979", "6013",
"6062", "6069", "6097", "6100", "6203", "6272", "6274", "6324",
"6343", "6430", "6541", "6564", "6568", "6617", "6623", "6668", 
"6683", "6756"]

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
        if(is_line_graph(data) and data_number not in broken_images):
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