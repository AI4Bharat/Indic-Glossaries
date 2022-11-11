import sys
import os
import csv

import utils.config as config
from data_maker.parse_type_1 import parse_type_1
from data_maker.parse_type_2 import parse_type_2

folder_path = sys.argv[1]
config.OUTPUT_DIR = folder_path
languages = folder_path.split("\\")[-1]
src, tgt = languages.split("-")
file_list = open("file_list.csv", "r")
csvreader = csv.reader(file_list, delimiter=";")
data_list = [f for f in csvreader]
file_names = [d[0] for d in data_list]

for file in os.listdir(folder_path):
    if file.endswith(".json"):
        json_path = os.path.join(folder_path, file)
        pdf_name = file[:-6] + ".pdf"
        pdf_list_name = pdf_name.replace("_", " ")
        if pdf_list_name in file_names:
            index = file_names.index(pdf_list_name)
            if data_list[index][6] == 1:
                parse_type_1(
                    json_path,
                    file,
                    data_list[index][1],
                    data_list[index][2],
                    data_list[index][5],
                    "cstt",
                )
            else:
                parse_type_2(
                    json_path,
                    file,
                    data_list[index][1],
                    data_list[index][2],
                    data_list[index][5],
                    "cstt",
                )
