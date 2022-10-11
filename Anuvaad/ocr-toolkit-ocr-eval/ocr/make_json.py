import os
import sys
import glob
import config
import requests
import logging
import json
import multiprocessing
import re
import csv
import queue
import time
from indic_regex import regex
from multiprocessing import Queue
from pdf_to_txt import TokenizePdf
from joblib import Parallel, delayed
import string
from os.path import exists

import logging

logging.basicConfig(level=logging.INFO, filename=config.LOGS,
                    format='%(asctime)s-%(levelname)s-%(message)s')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

tokenization_queue = Queue()

def start_processes(workers=config.BATCH_SIZE):
    process = []
    for w in range(workers):
        process.append(multiprocessing.Process(target=tokenize_pdf))
        process[-1].start()

def tokenize_pdf():
    while True:
        try:
            TokenizePdf(tokenization_queue.get(block=True))
        except:
            pass

def get_auth_token():
    try:
        res = requests.post(config.LOGIN, json = {
                            "userName": config.USER, "password": config.PASS})
        auth_token = res.json()['data']['token']
        logging.info(" Authentication successful \n")
        return auth_token

    except Exception as e:
        logging.error('Error in authentication {}'.format(e), exc_info=True)
        return None

# why divide by 4?
def get_center_of_bounding_box(line):
    x = (line['boundingBox']['vertices'][0]['x'] + line['boundingBox']['vertices'][1]['x'] + line['boundingBox']['vertices'][2]['x'] + line['boundingBox']['vertices'][3]['x']) / 4
    y = (line['boundingBox']['vertices'][0]['y'] + line['boundingBox']['vertices'][1]['y'] + line['boundingBox']['vertices'][2]['y'] + line['boundingBox']['vertices'][3]['y']) / 4
    return (x,y)


def make_json_files(files_to_parse):
    """
    Input: files_to_parse -> rows of file_list.csv to get json files for the pdfs obtained from pdf_maker.py
    Output: output json in config.OUTPUT_DIR (as defined in process_multi_files.py or process_single_file.py)
    The function calls TokenizePdf from pdf_to_text.py which in turn posts an API request to Anuvaad OCR
    """
    auth_token = get_auth_token()

    if auth_token is not None:
        files = [i[0] for i in files_to_parse]
        list_pdfs = []

        for pdf in files:
            try:
                if config.OVERWRITE:
                    list_pdfs.append([pdf, auth_token])
                else:
                    json_path = config.OUTPUT_DIR + pdf[:-4] + '.json'
                    json_path = json_path.replace(" ", "_")
                    if not os.path.exists(json_path):
                        list_pdfs.append([config.OUTPUT_DIR + '/'+ pdf , auth_token])
                    else:
                        print('{} already processed'.format(pdf))
            except Exception as e:
                logging.error('Error in processing PDF  {} due to {}'.format(pdf, e), exc_info=True)
        print ("---------Tokenization Queue--------------")
        Parallel(n_jobs=4)(delayed(TokenizePdf)(i_) for i_ in list_pdfs)
        print('All pdfs processed!', flush = True)
