import os
import sys
import logging
import json
import re
import csv
from indic_regex import regex
from os.path import exists

import config
import make_data
import helper_functions
import make_json

if __name__ == '__main__':
    folder_path = sys.argv[1]
    file_list_path = sys.argv[2]
    src_dir = os.path.dirname(folder_path)
    source = sys.argv[3]
    file = open(file_list_path, 'r')
    csvreader = csv.reader(file, delimiter = ';')
    files_list= [f for f in csvreader]
    orig_output_path = config.OUTPUT_DIR
    if os.path.exists(folder_path):
        pdf_list = files_list[1:]
        for i in pdf_list:
            if i[0] in os.listdir(folder_path):
                pdf = i[0]
                src_lng = i[1]
                tgt_lng = i[2]
                start_page = i[3]
                end_page = i[4]
                domain = i[5]
                col = i[6]
                
                # Define the output directory according to the source and target language
                directory = src_lng + "-" + tgt_lng
                path = os.path.join(orig_output_path, directory)
                if (os.path.exists(path) == False):
                    os.mkdir(path)
                config.OUTPUT_DIR = path + '/'
                # print (config.OUTPUT_DIR)
                tgt_dir = config.OUTPUT_DIR
                
                pdf_path = folder_path + '/' + pdf
                helper_functions.cropPDF(pdf_path, pdf,start_page, end_page, src_lng, tgt_lng, domain, col)
                
                if (os.path.exists('pdf_info.csv')):
                    files = open('pdf_info.csv', 'r')
                    csvreader = csv.reader(files, delimiter = ';')
                    files_to_parse = [f for f in csvreader]
                    helper_functions.processPDF(src_lng, tgt_lng,src_dir, tgt_dir)
                    json_list = [f[0][:-4]+".json" for f in files_to_parse[1:]]
                    try:
                        make_json.make_json_files(files_to_parse[1:]) 
                    except: 
                        logging.error("Unable to create json for the pdf")
                    
                    for file_name in json_list:
                        file_name = file_name.replace(" ", "_")
                        if file_name in os.listdir(config.OUTPUT_DIR):                           
                            json_file_path = config.OUTPUT_DIR + file_name
                            if int(col) == 1:
                                make_data.parse_type_1_new(json_file_path, file_name, src_lng, tgt_lng, domain, source)
                            elif int(col) ==2 :
                                make_data.parse_type_2_new(json_file_path, file_name, src_lng, tgt_lng, domain, source)
                                        
                            else:
                                logging.error("Currently only 1 column and 2 column documents are supported")
                        else: 
                            print ("json not found: " + file_name)
                    
        