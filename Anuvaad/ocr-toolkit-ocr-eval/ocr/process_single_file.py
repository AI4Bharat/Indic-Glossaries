import os
import sys
import logging
import json
import re
import csv
from indic_regex import regex
from os.path import exists
from PyPDF2 import PdfFileReader, PdfFileWriter

import config
import make_data
import helper_functions
import make_json

''' Update config.py variables according to user input, used for OCR'''

if __name__ == '__main__':
    src_lng = sys.argv[1]
    tgt_lng = sys.argv[2]
    path = sys.argv[3] # path of the pdf / json
    pdf_name = os.path.basename(os.path.normpath(path))
    col = sys.argv[4]
    # scanned_pdf = sys.argv[5]
    start_page = sys.argv[5] # not needed for json processing
    end_page = sys.argv[6] # not needed for json processing
    domain = sys.argv[7]
    source = sys.argv[8]
    tgt_dir = config.OUTPUT_DIR
    src_dir = os.path.dirname(path)

    if (path.endswith('.pdf') and os.path.exists(path)):
            cropPDF(path, pdf_name,start_page, end_page, src_lng, tgt_lng, domain, col)
            if (os.path.exists('pdf_info.csv')):
                file = open('pdf_info.csv', 'r')
                csvreader = csv.reader(file, delimiter = ';')
                files_to_parse = [f for f in csvreader]
                
                processPDF(src_lng, tgt_lng,src_dir, tgt_dir)
                
                json_list = [f[0][:-4]+".json" for f in files_to_parse[1:]]

                try:
                    make_json.make_json_files(files_to_parse[1:]) 
                except: 
                    logging.error("Unable to create json for the pdf: " + pdf_name)
                for file_ in json_list:
                    if file_ in os.listdir(config.OUTPUT_DIR):                           
                        json_file_path = config.OUTPUT_DIR + file_
                        file_name = file_
                        if (os.path.exists(json_file_path)):
                            if int(col) == 1:
                                json_file_path = config.OUTPUT_DIR + file_name
                                make_data.parse_type_1_new(json_file_path, file_name, src_lng, tgt_lng, domain, source)
                            elif int(col) ==2 :
                                make_data.parse_type_2_new(json_file_path, src_lng, tgt_lng, domain, source)
                                        
                            else:
                                logging.error("Currently only 1 column and 2 column documents are supported")
    elif (path.endswith('.json') and os.path.exists(path)):
        if int(col) == 1:
            make_data.parse_type_1_new(path, pdf_name, src_lng, tgt_lng, domain, source)
        elif int(col) == 2:
            make_data.parse_type_2_new(path, pdf_name, src_lng, tgt_lng, domain, source)
        else:
            logging.error("Currently only 1 column and 2 column documents are supported")
            
    else:
        logging.error("Please check the path and filename")
            
    
    
    
    
    
    