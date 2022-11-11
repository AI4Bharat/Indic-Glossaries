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
# This is the main file to be run for results. Run it as with command line arguments src_language and tgt_language.



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


def parse_files(parent_dir):
    return glob.glob(os.path.join(parent_dir))


def get_json_path(pdf_path):
    folder_name = pdf_path.split('/')[-2]
    pdf_name = pdf_path.split('/')[-1].split('.')[0]
    return os.path.join(config.OUTPUT_DIR, folder_name, '{}.json'.format(pdf_name))


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
    Output: json files for each pdf in test_outputs/updated_glossaries folder
    The function calls TokenizePdf from pdf_to_text.py which in turn posts an API request to Anuvaad OCR, 
    """
    auth_token = get_auth_token()

    if auth_token is not None:
        # start_processes()
        files = [i[0] for i in files_to_parse]
        list_pdfs = []

        for pdf in files:
            # print(pdf, flush = True)
            try:
                # 
                if config.OVERWRITE:
                    list_pdfs.append([pdf, auth_token])
                else:
                    # -> Can try removing the indexing
                    json_path = 'test_outputs/dividedPDF_hindi/' + pdf[:-4] + '.json'
                    json_path = json_path.replace(" ", "_")
                    # print(json_path, flush=True)
                    if not os.path.exists(json_path):
                        list_pdfs.append([config.INPUT_DIR + "/" + pdf, auth_token])
                    else:
                        print('{} already processed'.format(pdf))
            except Exception as e:
                print("error", flush = True)
                logging.error('Error in processing PDF  {} due to {} {}'.format(
                    pdf, e), exc_info=True)
        print ("---------Tokenization Queue--------------")
        Parallel(n_jobs=4)(delayed(TokenizePdf)(i_) for i_ in list_pdfs)
        print('All pdfs processed!', flush = True)



def parse_type_1_helper2(n1,files_to_parse, src_lng, tgt_lng ):
    result = []
    f = 'test_outputs/dividedPDF_hindi/' + files_to_parse[n1][0][:-4] + '.json'
    print (f)
    f = f.replace(" ", "_")
    word_dict = json.load(open(f, encoding="utf8"))

    for dictionary in word_dict["outputs"]:
        pp = 0
        for page in dictionary['pages']:
            pp+=1

            l = []
            new_l = []
            new_l_idx = -1
            height = page["boundingBox"]["vertices"][3]["y"]
            # what is upper and lower limit -> 
            upper_limit = height / 10
            lower_limit = height - upper_limit
            for region in page['regions']:
                if region['class'] == 'PARA':
                    for r_region in region["regions"]:
                        
                        # At this point we are getting all words on one page, so we should process here itself. Comapre their centers basically
                        # however we are adding below, we should do that here itself, because we can be sure that they are corresponding
                        # will contain words for each page
                        for line in r_region["regions"]:
                            coords = get_center_of_bounding_box(line)
                            # l.append((line['text'], coords))   # add the word and its center. Do this for all words
                            l.append((line['text'], coords)) 

                
                
                
                
            # print ("len_l",len(l))
            # print (l)
            i = 0
            # print ("l_Len", len(l))
            while i < len(l):
                if new_l_idx == -1:
                    new_l.append(l[i])
                    new_l_idx += 1
                else:
                    # height diff <15 pix
                    if abs(new_l[new_l_idx][1][1] - l[i][1][1]) < 20:
                        new_l[new_l_idx] = tuple((new_l[new_l_idx][0] + " " + l[i][0], new_l[new_l_idx][1]))
                            
                    else:
                        new_l.append(l[i])
                        new_l_idx += 1
                i += 1
            l = []
            # print ("len of new _L" ,len(new_l))
            # print (new_l)
                        
            for i in new_l:
                if len(i[0]) < 2 or i[0].isnumeric():
                    pass
                else:
                    l.append(i)
            final_list = []
            for i in  l:
                # print (i[0])
                words = i[0].split(" ")
                # print (words[0])
                src_list = []
                trgt_list = []
                flag = -1
                for j in words:
                    # print ("entered")
                    if (j not in string.punctuation):
                        if (re.search(regex(src_lng), j))!=None:
                            src_list.append(j)
                            flag = 1

                        elif re.search(regex(src_lng),j) == None:
                            trgt_list.append(j)
                            flag = 0

                    else:
                        if (flag == 1):
                            src_list.append(j)
                        elif (flag == 0):
                            trgt_list.append(j)

                print (src_list)
                print(trgt_list)
                src_word = " ".join(src_list)
                trgt_word = " ".join(trgt_list)
                if (src_list == []):
                    # print ("final_list", final_list[-1][1])
                    # print (trgt_word)
                    # print ("srcSrja", src_list)
                    final_list[-1][1] = final_list[-1][1] + trgt_word
                    # print ("final_list__", final_list[-1][1])
                    continue

                if (len(src_list)>1):
                    final_list.append([src_word, trgt_word,src_lng, tgt_lng, files_to_parse[n1][5], "cstt", "p", files_to_parse[n1][0][:-4]])
                elif (len(src_list)==1):
                    final_list.append([src_word, trgt_word, src_lng, tgt_lng, files_to_parse[n1][5], "cstt", "w", files_to_parse[n1][0][:-4]])
            result.extend(final_list)

                    
    print (len(result))
    return result
  
def parse_type_1_helper(n1, files_to_parse, src_lng, tgt_lng):
    print ("parse_type_1_helper")
    result = []
    print ("n1", n1)
    
    f = 'test_outputs/dividedPDF_hindi/' + files_to_parse[n1][0][:-4] + '.json'
    print (f)
    f = f.replace(" ", "_")
    word_dict = json.load(open(f, encoding="utf8"))

    for dictionary in word_dict["outputs"]:
        for page in dictionary['pages']:
            l = []
            new_l = []
            new_l_idx = -1
            height = page["boundingBox"]["vertices"][3]["y"] # height of page ?
            # what is upper and lower limit -> 
            upper_limit = height / 10
            lower_limit = height - upper_limit
            for region in page['regions']:
                if region['class'] == 'PARA':
                    for r_region in region["regions"]:
                        
                        for line in r_region["regions"]:
                            coords = get_center_of_bounding_box(line)
                            l.append((line['text'], coords))
            # What kind of data does l have?
            i = 0
            # print ("l_Len", len(l))
            while i < len(l):
                if new_l_idx == -1:
                    new_l.append(l[i])
                    new_l_idx += 1
                else:
                    # height diff <15 pix
                    if abs(new_l[new_l_idx][1][1] - l[i][1][1]) < 15:
                        new_l[new_l_idx] = tuple((new_l[new_l_idx][0] + " " + l[i][0], new_l[new_l_idx][1]))
                        
                    else:
                        new_l.append(l[i])
                        new_l_idx += 1
                i += 1
            l = []
            print (new_l)

            # for remaining i which were not processed, if their len is < 2 or it's values are less than upper limit and more than lower limit
            for i in new_l:
                if len(i[0]) < 2 or i[1][1] < upper_limit or i[1][1] > lower_limit:  #???
                    pass
                else:
                    l.append(i)
            # print ("l_changed",   l)
            
            final_list = []
            for word in l:
                # print (word)
                col1_eng = [] # src col
                col1_hin = [] # trgt col
                if len(word[0]) <= 50 and len(word[1]) <= 50 and len(word[0])>2:
                    split_word = word[0].split(" ")
                    flag = -1
                    for i in split_word:
                        if (i not in string.punctuation):
                            if (re.search(src_lng, i))!=None:
                                col1_eng.append(i)
                                flag = 0
                            elif re.search(regex(src_lng),i) == None:
                                col1_hin.append(i)
                                flag = 1
                        else:
                            if (flag == 1):
                                col1_hin.append(i)
                            elif (flag ==0):
                                col1_eng.append(i)
                src_words = " ".join(col1_eng)
                trgt_words = " ".join(col1_hin)
                # print (src_words, trgt_words)
                if (len(col1_eng)>1):
                    final_list.append([src_words, trgt_words,src_lng, tgt_lng, files_to_parse[n1][5], "cstt", "p", files_to_parse[n1][0][:-4]])
                elif (len(col1_eng)==1):
                    final_list.append([src_words, trgt_words, src_lng, tgt_lng, files_to_parse[n1][5], "cstt", "w", files_to_parse[n1][0][:-4]])
            # print (final_list)
            # print (len(final_list))

    return result

    #             col1eng_new = []
    #             col1hin_new = []                
    #             k = 0
    #             while k < len(col1_eng):
    #                 j = k + 1
    #                 w = col1_eng[k][0]
    #                 while j < len(col1_eng):
    #                     if abs(col1_eng[k][1][1] - col1_eng[j][1][1]) < 20:
    #                         w += " " + col1_eng[j][0]
    #                         j += 1
    #                     else:
    #                         break
    #                 col1eng_new.append((w, col1_eng[k][1]))
    #                 k = j
    #             k = 0
    #             while k < len(col1_hin):
    #                 j = k + 1
    #                 w = col1_hin[k][0]
    #                 while j < len(col1_hin):
    #                     if abs(col1_hin[k][1][1] - col1_hin[j][1][1]) < 20:
    #                         w += " " + col1_hin[j][0]
    #                         j += 1
    #                     else:
    #                         break
    #                 col1hin_new.append((w, col1_hin[k][1]))
    #                 k = j
                    
    #             col1_hin = col1hin_new
    #             col1_eng = col1eng_new

    #             final_list = []
    #             eng_index = 0
    #             hin_index = 0
    #             ovr_index = 0
    #             while True:
    #                 try: 
    #                     if eng_index < len(col1_eng) and hin_index < len(col1_hin):
    #                         if abs(col1_eng[eng_index][1][1] - col1_hin[hin_index][1][1]) < 20: # checking height diff
    #                             final_list.append((col1_eng[eng_index][0], col1_hin[hin_index][0], col1_eng[eng_index][1]))
    #                             ovr_index += 1
    #                             eng_index += 1
    #                             hin_index += 1
    #                         elif abs(col1_eng[eng_index][1][1] - col1_hin[hin_index][1][1]) > 100 or ovr_index == 0:
    #                             eng_index += 1
    #                         elif col1_eng[eng_index][1][1] < col1_hin[hin_index][1][1]:
    #                             old = final_list[ovr_index - 1]
    #                                 # print(old)
    #                             final_list[ovr_index - 1] = (old[0] + " " + col1_eng[eng_index][0], old[1], col1_eng[eng_index][1])
    #                             eng_index += 1
    #                                 # print(final_list)
    #                         elif col1_eng[eng_index][1][1] > col1_hin[hin_index][1][1]:
    #                             old = final_list[ovr_index - 1]
    #                             final_list[ovr_index - 1] = ( old[0], old[1] + " " + col1_hin[hin_index][0], col1_hin[hin_index][1])
    #                             hin_index += 1
    #                     elif eng_index < len(col1_eng) and ovr_index != 0 and abs(col1_eng[eng_index][1][1] - final_list[ovr_index - 1][2][1]) < 100:
    #                         old = final_list[ovr_index - 1]
    #                         final_list[ovr_index - 1] = (old[0] + " " + col1_eng[eng_index][0], old[1], col1_eng[eng_index][1])
    #                         eng_index += 1
    #                     elif hin_index < len(col1_hin):
    #                         old = final_list[ovr_index - 1]
    #                         final_list[ovr_index - 1] = ( old[0], old[1] + " " + col1_hin[hin_index][0], col1_hin[hin_index][1])
    #                         hin_index += 1
    #                     else:
    #                         break
    #                 except:
    #                     break

    #             # print (final_list)
    #             for tup in final_list:    
    #                 if len(tup[0]) <= 50 and len(tup[1]) <= 50:
    #                     # Added utf encode when reading the file
    #                     if (len(tup[0].split(" ")) > 1):
    #                         result.append([tup[0], tup[1], src_lng, tgt_lng, files_to_parse[n1][5], "cstt", "p", files_to_parse[n1][0][:-4]]) 
    #                     else:
    #                         result.append([tup[0], tup[1], src_lng, tgt_lng, files_to_parse[n1][5], "cstt", "w", files_to_parse[n1][0][:-4]]) 
    # except:
    #     logging.info("Unable to process" +  f)

    # print (len(result))

    
def parse_type_1_helper_orig(n1, files_to_parse, src_lng, tgt_lng):
    print ("parse_type_1_helper")
    result = []
    print ("n1", n1)
    
    f = 'test_outputs/dividedPDF_hindi/' + files_to_parse[n1][0][:-4] + '.json'
    print (f)
    f = f.replace(" ", "_")
    word_dict = json.load(open(f, encoding="utf8"))

    try:
        for dictionary in word_dict["outputs"]:
            for page in dictionary['pages']:
                l = []
                new_l = []
                new_l_idx = -1
                height = page["boundingBox"]["vertices"][3]["y"]
                # what is upper and lower limit -> 
                upper_limit = height / 10
                lower_limit = height - upper_limit
                for region in page['regions']:
                    if region['class'] == 'PARA':
                        for r_region in region["regions"]:
                            
                            for line in r_region["regions"]:
                                coords = get_center_of_bounding_box(line)
                                l.append((line['text'], coords))
                i = 0
                while i < len(l):
                    if new_l_idx == -1:
                        new_l.append(l[i])
                        new_l_idx += 1
                    else:
                        if abs(new_l[new_l_idx][1][1] - l[i][1][1]) < 15:
                            
                            new_l[new_l_idx] = tuple((new_l[new_l_idx][0] + " " + l[i][0], new_l[new_l_idx][1]))
                        else:
                            new_l.append(l[i])
                            new_l_idx += 1
                    i += 1
                l = []
                for i in new_l:
                    if len(i[0]) < 2 or i[1][1] < upper_limit or i[1][1] > lower_limit:
                        pass
                    else:
                        l.append(i)
                    
                col1_eng = []
                col1_hin = []
                
                for word in l:
                    if len(word[0]) <= 50 and len(word[1]) <= 50:

                        if re.search(regex(src_lng), word[0]) != None and re.search(regex(tgt_lng), word[0]) == None:
                                col1_eng.append(word)
                        elif re.search(regex(tgt_lng), word[0]) != None and re.search(regex(src_lng), word[0]) == None:
                            col1_hin.append(word)

                col1eng_new = []
                col1hin_new = []                
                k = 0
                while k < len(col1_eng):
                    j = k + 1
                    w = col1_eng[k][0]
                    while j < len(col1_eng):
                        if abs(col1_eng[k][1][1] - col1_eng[j][1][1]) < 20:
                            w += " " + col1_eng[j][0]
                            j += 1
                        else:
                            break
                    col1eng_new.append((w, col1_eng[k][1]))
                    k = j
                k = 0
                while k < len(col1_hin):
                    j = k + 1
                    w = col1_hin[k][0]
                    while j < len(col1_hin):
                        if abs(col1_hin[k][1][1] - col1_hin[j][1][1]) < 20:
                            w += " " + col1_hin[j][0]
                            j += 1
                        else:
                            break
                    col1hin_new.append((w, col1_hin[k][1]))
                    k = j
                    
                col1_hin = col1hin_new
                col1_eng = col1eng_new

                final_list = []
                eng_index = 0
                hin_index = 0
                ovr_index = 0
                while True:
                    try:
                        if eng_index < len(col1_eng) and hin_index < len(col1_hin):
                            if abs(col1_eng[eng_index][1][1] - col1_hin[hin_index][1][1]) < 20:
                                final_list.append((col1_eng[eng_index][0], col1_hin[hin_index][0], col1_eng[eng_index][1]))
                                ovr_index += 1
                                eng_index += 1
                                hin_index += 1
                            elif abs(col1_eng[eng_index][1][1] - col1_hin[hin_index][1][1]) > 100 or ovr_index == 0:
                                eng_index += 1
                            elif col1_eng[eng_index][1][1] < col1_hin[hin_index][1][1]:
                                old = final_list[ovr_index - 1]
                                    # print(old)
                                final_list[ovr_index - 1] = (old[0] + " " + col1_eng[eng_index][0], old[1], col1_eng[eng_index][1])
                                eng_index += 1
                                    # print(final_list)
                            elif col1_eng[eng_index][1][1] > col1_hin[hin_index][1][1]:
                                old = final_list[ovr_index - 1]
                                final_list[ovr_index - 1] = ( old[0], old[1] + " " + col1_hin[hin_index][0], col1_hin[hin_index][1])
                                hin_index += 1
                        elif eng_index < len(col1_eng) and ovr_index != 0 and abs(col1_eng[eng_index][1][1] - final_list[ovr_index - 1][2][1]) < 100:
                            old = final_list[ovr_index - 1]
                            final_list[ovr_index - 1] = (old[0] + " " + col1_eng[eng_index][0], old[1], col1_eng[eng_index][1])
                            eng_index += 1
                        elif hin_index < len(col1_hin):
                            old = final_list[ovr_index - 1]
                            final_list[ovr_index - 1] = ( old[0], old[1] + " " + col1_hin[hin_index][0], col1_hin[hin_index][1])
                            hin_index += 1
                        else:
                            break
                    except:
                        break
                for tup in final_list:    
                    if len(tup[0]) <= 50 and len(tup[1]) <= 50:
                        # Added utf encode when reading the file
                        if (len(tup[0].split(" ")) > 1):
                            result.append([tup[0], tup[1], src_lng, tgt_lng, files_to_parse[n1][5], "cstt", "p", files_to_parse[n1][0][:-4]]) 
                        else:
                            result.append([tup[0], tup[1], src_lng, tgt_lng, files_to_parse[n1][5], "cstt", "w", files_to_parse[n1][0][:-4]]) 
    except:
        logging.info("Unable to process" +  f)

    print (len(result))
    return result
    
    
def parse_type_1(files_to_parse, src_lng, tgt_lng, csvwriter):
    '''
    Input
        files_to_parse: The list of json files to parse
        src_lng       : Source language
        tgt_lng       : Target Language

    Output: src_lng-tgt_lng.tsv : Source, Target, Src Language, Tgt Language, Domain, Collection Source, Glossary Level
    Used for 1 column glossaries.
    Initialize the tsv file, calls parse_type_1_helper to create glossary
    '''
    print ("entered parse_type_1")
    arr = []
    for n1 in range (len(files_to_parse)):
        arr.append(parse_type_1_helper2(n1, files_to_parse, src_lng, tgt_lng))

    # arr = Parallel(n_jobs=1)(delayed(parse_type_1_helper_orig)(n1, files_to_parse, src_lng, tgt_lng) for n1 in range (len(files_to_parse)))

    for i in range (len(arr)):
        for j in range (len(arr[i])):
            csvwriter.writerow(arr[i][j])

    return arr


def parse_type_2_helper(n1, files_to_parse, src_lng, tgt_lng):
    print ("parse_type_2_helper")
    result = []
    print (n1)
    for n1 in range(len(files_to_parse)):
        f = 'test_outputs/dividedPDF_hindi/' + files_to_parse[n1][0][:-4] + '.json'
        f = f.replace(" ", "_")
        word_dict = json.load(open(f, encoding="utf8"))
        # print("ok", flush = True)
        for dic in word_dict["outputs"]:
            # if dic['class'] == 'WORD':
            step = 0
            for page in dic['pages']:
                step+=1
                
                l = []
                
                height = page["boundingBox"]["vertices"][3]["y"]
                width = page["boundingBox"]["vertices"][2]["x"]
                upper_limit = height / 8
                lower_limit = height - upper_limit
                columns = [width/2, width]

                for region in page['regions']:
                    if region['class'] == 'PARA':
                        for r_region in region["regions"]:
                            
                            for line in r_region["regions"]:
                                coords = get_center_of_bounding_box(line)
                                l.append((line['text'], coords))

                l_2cols = [[], []]
                for x in l:
                    if x[1][0] <= width/2:
                        l_2cols[0].append(x)
                    else:
                        l_2cols[1].append(x)

                for l in l_2cols:
                    
                    new_l = []
                    new_l_idx = -1
                    i = 0
                    while i < len(l):
                        if new_l_idx == -1:
                            new_l.append(l[i])
                            new_l_idx += 1
                        else:
                            if abs(new_l[new_l_idx][1][1] - l[i][1][1]) < 30:
                                new_l[new_l_idx] = tuple((new_l[new_l_idx][0] + " " + l[i][0], new_l[new_l_idx][1]))
                            else:
                                new_l.append(l[i])
                                new_l_idx += 1
                        i += 1
                    l = []
                    
                    for i in new_l:
                        if len(i[0]) < 2 or i[0].isnumeric() or i[1][1] < upper_limit or i[1][1] > lower_limit:
                            pass
                        else:
                            l.append(i)

                    final_list = []

                    for i in  l:
                        words = i[0].split(" ")
                        src_list = []
                        trgt_list = []
                        flag = -1
                        for j in words:
                            # print ("entered")
                            if (j not in string.punctuation):
                                if (re.search(regex(src_lng), j))!=None:
                                    src_list.append(j)
                                    flag = 1

                                elif re.search(regex(src_lng),j) == None:
                                    trgt_list.append(j)
                                    flag = 0

                            else:
                                if (flag == 1):
                                    src_list.append(j)
                                elif (flag == 0):
                                    trgt_list.append(j)
                        
                        src_word = " ".join(src_list)
                        trgt_word = " ".join(trgt_list)

                        if (final_list != []):

                                if (src_list == []):
                                    final_list[-1][1] = final_list[-1][1] + " "+ trgt_word
                                    continue

                                if (trgt_list == []):
                                    final_list[-1][0] = final_list[-1][0] + " "+ src_word
                                    continue

                        if (len(src_list)>1):
                            final_list.append([src_word, trgt_word,src_lng, tgt_lng, files_to_parse[n1][5], "cstt", "p", files_to_parse[n1][0][:-4]])
                        elif (len(src_list)==1):
                            final_list.append([src_word, trgt_word, src_lng, tgt_lng, files_to_parse[n1][5], "cstt", "w", files_to_parse[n1][0][:-4]])
                    result.extend(final_list)

                    

                #     # print(l, flush = True)
                #     col1_eng = []
                #     col1_hin = []
                #     for word in l:
                        
                #         if re.search(regex(src_lng), word[0]) != None and re.search(regex(tgt_lng), word[0]) == None:
                #             col1_eng.append(word)
                #         if re.search(regex(tgt_lng), word[0]) != None and re.search(regex(src_lng), word[0]) == None:
                #             col1_hin.append(word)
                #     col1eng_new = []
                #     col1hin_new = []                
                #     k = 0
                #     while k < len(col1_eng):
                #         j = k + 1
                #         w = col1_eng[k][0]
                #         while j < len(col1_eng):
                #             if abs(col1_eng[k][1][1] - col1_eng[j][1][1]) < 20:
                #                 w += " " + col1_eng[j][0]
                #                 j += 1
                #             else:
                #                 break
                #         col1eng_new.append((w, col1_eng[k][1]))
                #         k = j
                #     k = 0
                #     while k < len(col1_hin):
                #         j = k + 1
                #         w = col1_hin[k][0]
                #         while j < len(col1_hin):
                #             if abs(col1_hin[k][1][1] - col1_hin[j][1][1]) < 20:
                #                 w += " " + col1_hin[j][0]
                #                 j += 1
                #             else:
                #                 break
                #         col1hin_new.append((w, col1_hin[k][1]))
                #         k = j
                        
                #     col1_hin = col1hin_new
                #     col1_eng = col1eng_new
                #     final_list = []
                #     eng_index = 0
                #     hin_index = 0
                #     ovr_index = 0
                #     while True:
                #         try:
                #             if eng_index < len(col1_eng) and hin_index < len(col1_hin):
                #                 if abs(col1_eng[eng_index][1][1] - col1_hin[hin_index][1][1]) < 20:
                #                     final_list.append((col1_eng[eng_index][0], col1_hin[hin_index][0], col1_eng[eng_index][1]))
                #                     ovr_index += 1
                #                     eng_index += 1
                #                     hin_index += 1
                #                 elif abs(col1_eng[eng_index][1][1] - col1_hin[hin_index][1][1]) > 100 or ovr_index == 0:
                #                     eng_index += 1
                #                 elif col1_eng[eng_index][1][1] < col1_hin[hin_index][1][1]:
                #                     old = final_list[ovr_index - 1]
                #                         # print(old)
                #                     final_list[ovr_index - 1] = (old[0] + " " + col1_eng[eng_index][0], old[1], col1_eng[eng_index][1])
                #                     eng_index += 1
                #                         # print(final_list)
                #                 elif col1_eng[eng_index][1][1] > col1_hin[hin_index][1][1]:
                #                     old = final_list[ovr_index - 1]
                #                     final_list[ovr_index - 1] = ( old[0], old[1] + " " + col1_hin[hin_index][0], col1_hin[hin_index][1])
                #                     hin_index += 1
                #             elif eng_index < len(col1_eng) and ovr_index != 0 and abs(col1_eng[eng_index][1][1] - final_list[ovr_index - 1][2][1]) < 20:
                #                 old = final_list[ovr_index - 1]
                #                 final_list[ovr_index - 1] = (old[0] + " " + col1_eng[eng_index][0], old[1], col1_eng[eng_index][1])
                #                 eng_index += 1
                #             elif hin_index < len(col1_hin) and ovr_index != 0 and abs(col1_hin[hin_index][1][1] - final_list[ovr_index - 1][2][1]) < 20:
                #                 old = final_list[ovr_index - 1]
                #                 final_list[ovr_index - 1] = ( old[0], old[1] + " " + col1_hin[hin_index][0], col1_hin[hin_index][1])
                #                 hin_index += 1
                #             else:
                #                 break
                #         except:
                #             break
                # for tup in final_list:    
                #     if len(tup[0]) <= 50 and len(tup[1]) <= 50:
                #         # print ([tup[0], tup[1], src_lng, tgt_lng, files_to_parse[n1][5])
                #         if (len(tup[0].split(" ")) > 1):
                #             result.append([tup[0], tup[1], src_lng, tgt_lng, files_to_parse[n1][5], "cstt", "p", files_to_parse[n1][0][:-4]]) 
                #         else:
                #             result.append([tup[0], tup[1], src_lng, tgt_lng, files_to_parse[n1][5], "cstt", "w", files_to_parse[n1][0][:-4]]) 
    print (len(result))
    return result
                            

def parse_type_2(files_to_parse, src_lng, tgt_lng, csvwriter):
    '''
    Input
        files_to_parse: The list of json files to parse
        src_lng       : Source language
        tgt_lng       : Target Language

    Output: src_lng-tgt_lng.tsv : Source, Target, Src Language, Tgt Language, Domain, Collection Source, Glossary Level
    Used for 2 column glossaries.
    Initialize the tsv file, calls parse_type_2_helper to create glossary
    '''

    # tsv_path = 'test_outputs/language_pairs/' +src_lng + '-' + tgt_lng +'.xlsx'
    # file_exists = exists(tsv_path)
    
    # csvfile2 = open('test_outputs/language_pairs/' +src_lng + '-' + tgt_lng +'.xlsx', 'a', encoding='utf-8')
    # csvwriter = csv.writer(csvfile2, delimiter = '\t')
    # if (file_exists == False):
        # csvwriter.writerow(["Source"	,"Target",	"Src Language",	"Tgt Language",	"Domain"	,"Collection Source"	,"Glossary Level", "PDF"])
 
    arr = Parallel(n_jobs=4)(delayed(parse_type_2_helper)(n1, files_to_parse, src_lng, tgt_lng) for n1 in range (len(files_to_parse)))
    print ("received_arr")
    for i in range (len(arr)):
        for j in range (len(arr[i])):
            csvwriter.writerow(arr[i][j])
    return arr
                                
      

if __name__ == '__main__':
    src_lng = sys.argv[1]
    tgt_lng = sys.argv[2]
    
    file = open('file_hindi_new.csv', 'r')
    csvreader = csv.reader(file, delimiter = ';')
    files_to_parse = [f for f in csvreader]
    # print (files_to_parse)
    f1 = []
    f2 = []
    for f in files_to_parse:
        # print (f)
        if f[6] == '1' and f[1] == src_lng and f[2] == tgt_lng:
            f1.append(f)
        elif f[6] == '2' and f[1] == src_lng and f[2] == tgt_lng:
            f2.append(f)
    #tsv_path = 'test_outputs/language_pairs/new/' +src_lng + '-' + tgt_lng +'.xlsx'
    tsv_path = 'test_outputs/new/' +src_lng + '-' + tgt_lng +'.xlsx'
    file_exists = exists(tsv_path)
    csvfile2 = open(tsv_path, 'w', encoding='utf-8')
    csvwriter = csv.writer(csvfile2, delimiter = '\t')
    if (file_exists == False):
        csvwriter.writerow(["Source" , "Target",	"Src Language",	"Tgt Language",	"Domain", "Collection Source", "Glossary Level", "PDF"])
    # print (f2)
    # make_json_files(files_to_parse[1:])
    parse_type_1(f1, src_lng, tgt_lng, csvwriter)
    parse_type_2(f2, src_lng, tgt_lng, csvwriter)
