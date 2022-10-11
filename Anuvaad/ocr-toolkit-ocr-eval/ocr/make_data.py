import json
import helper_functions
import re
from indic_regex import regex
import config
import csv
import logging

logging.basicConfig(level=logging.INFO, filename=config.LOGS,
                    format='%(asctime)s-%(levelname)s-%(message)s')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def parse_type_1_new(f, filename, src_lng, tgt_lng, domain, source):
    result = []
    try:
        word_dict = json.load(open(f, encoding="utf8"))
    except:
        logging.error("Following json file not available: " + word_dict)
        return result
    
    for dictionary in word_dict["outputs"]:
        for page in dictionary['pages']:
            l = [] # list of words extracted from json
            new_l = []
            height = page["boundingBox"]["vertices"][3]["y"]
            upper_limit = height / 10
            lower_limit = height - upper_limit
            
            # Extract all words from json
            for region in page['regions']:
                if region['class'] == 'PARA':
                    for r_region in region["regions"]:
                        coords = helper_functions.get_center_of_bounding_box(r_region)
                        l.append((r_region['text'], coords)) 


            # Create pairs of src-tgt words
            for i in range(len(l)):
                # If i == 0 => first word, first word should belong to src_lang, else continue
                if i == 0 or len(new_l) == 0:
                    if (re.search(regex(src_lng), l[i][0])!=None):
                        new_l.append([(l[i][0], l[i][1]), ()])
                    else:
                        continue
                else:
                    
                    # check if word belongs to src lang
                    # structure of new_l: 
                    # [[(src_word1, (src_width1, src_height1)), (tgt_word1, (src_width1, tgt_width1))], ..., [(src_wordn, (src_widthn, src_heightn)), (tgt_wordn, (src_widthn, tgt_widthn))]]
                    if (re.search(regex(src_lng), l[i][0])!=None):
                        prev_word = new_l[-1][0][0]
                        prev_height = new_l[-1][0][1][1] # the height of the last entry of new_l
                        if (abs(prev_height - l[i][1][1]))<85:
                            new_height = (prev_height + l[i][1][1])//2
                            width = new_l[-1][0][1][0]
                            new_l[-1][0] = tuple((prev_word + " "+ l[i][0], [width, new_height]))
                        
                        else:
                            new_l.append([(l[i][0], l[i][1]), ()])
                            
                    elif (re.search(regex(tgt_lng), l[i][0])!=None):
                        # the prev's tgt array could be empty. In that case, compare the height of the src word and current word, if diff <85: add the tgt word
                        if (new_l[-1][1] == ()):
                            prev_src_word = new_l[-1][0][0]
                            prev_src_height = new_l[-1][0][1][1]
                            if (abs(prev_src_height - l[i][1][1]))<85:
                                new_l[-1][1] = tuple((l[i][0], [l[i][1][0], l[i][1][1]]))
                        else:
                            # divide into two cases, along the same line, along different line.
                            # to check if on same line or diff line, compare height, can 
                            prev_word = new_l[-1][1][0]
                            prev_height = new_l[-1][1][1][1]
                            
                            if (abs(prev_height - l[i][1][1]))<80:
                                new_height = (prev_height + l[i][1][1])//2
                                width = new_l[-1][0][1][0]
                                new_l[-1][1] = tuple((prev_word + " " + l[i][0], [width, new_height]))
                                
                            else:
                               logging.info("Couldn't process word " + l[i][0])
                               continue
            # remove noise from new_l
            l = []
            for i in new_l:
                if i[0] == () or i[1] == () or len(i[0][0]) < 2 or i[0][0].isnumeric() or len(i[1][0])< 2 or i[1][0].isnumeric():
                    pass
                else:
                    l.append(i)
            # create the output for csv file
            final_list = []
            for i in range (len(l)):
                src_word = l[i][0][0]
                trgt_word = l[i][1][0]
                if len(l[i][0]) == 1:
                    final_list.append([src_word, trgt_word,src_lng, tgt_lng, domain, source, "p",filename[:-5]+ ".pdf"])
                else:
                    final_list.append([src_word, trgt_word, src_lng, tgt_lng, domain , source, "w", filename[:-5]+ ".pdf"])
            result.extend(final_list)
    
    tsv_path = config.OUTPUT_DIR + filename[:-5] +'.xlsx'
    csvfile2 = open(tsv_path, 'w', encoding='utf-8')
    csvwriter = csv.writer(csvfile2, delimiter = '\t')
    csvwriter.writerow(["Source" , "Target",	"Src Language",	"Tgt Language",	"Domain", "Collection Source", "Glossary Level", "PDF"])
    for i in range (len(result)):
        csvwriter.writerow(result[i])
        
    return result


def parse_type_2_new(f, filename, src_lng, tgt_lng, domain, source):
    result = []
    print (f)
    
    word_dict = json.load(open(f, encoding="utf8"))
   
    
    for dictionary in word_dict["outputs"]:
        for page in dictionary['pages']:
            l = [] # list of words extracted from json
            height = page["boundingBox"]["vertices"][3]["y"]
            width = page["boundingBox"]["vertices"][2]["x"]
            upper_limit = height / 10
            lower_limit = height - upper_limit
            columns = [width/2, width]
            
            # Extract all words from json
            for region in page['regions']:
                if region['class'] == 'PARA':
                    for r_region in region["regions"]:       
                        for line in r_region["regions"]:
                            coords = helper_functions.get_center_of_bounding_box(line)
                            l.append((line['text'], coords))
                        
            # divide the two cols
            l_2cols = [[], []]
            for x in l:
                if x[1][0] <= width/2:
                    l_2cols[0].append(x)
                else:
                    l_2cols[1].append(x)
            
            for l in l_2cols:
                new_l = []
                for i in range(len(l)):
                
                # If i == 0 => first word, first word should belong to src_lang, else continue
                    if i == 0 or (len(new_l) == 0):
                        if (re.search(regex(src_lng), l[i][0])!=None):
                            new_l.append([(l[i][0], l[i][1]), ()])
                        else:
                            continue
                    else:  
                        # check if word belongs to src lang
                        # structure of new_l: 
                        # [[(src_word1, (src_width1, src_height1)), (tgt_word1, (src_width1, tgt_width1))], ..., [(src_wordn, (src_widthn, src_heightn)), (tgt_wordn, (src_widthn, tgt_widthn))]]
                        if (re.search(regex(src_lng), l[i][0])!=None):
                            prev_word = new_l[-1][0][0]
                            prev_height = new_l[-1][0][1][1] # the height of the last entry of the new_l
                            if (abs(prev_height - l[i][1][1]))<85:
                                new_height = (prev_height + l[i][1][1])//2
                                width = new_l[-1][0][1][0]
                                new_l[-1][0] = tuple((prev_word + " "+ l[i][0], [width, new_height]))
                            
                            else:
                                new_l.append([(l[i][0], l[i][1]), ()])
                                
                        elif (re.search(regex(tgt_lng), l[i][0])!=None):
                            # the prev's tgt array could be empty. In that case, compare the height of the src word and current word, if diff <85: add the tgt word
                            if (new_l[-1][1] == ()):
                                prev_src_word = new_l[-1][0][0]
                                prev_src_height = new_l[-1][0][1][1]
                                if (abs(prev_src_height - l[i][1][1]))<85:
                                    new_l[-1][1] = tuple((l[i][0], [l[i][1][0], l[i][1][1]]))
                            else:
                                # divide into two cases, along the same line, along different line.
                                # to check if on same line or diff line, compare height, can 
                                prev_word = new_l[-1][1][0]
                                prev_height = new_l[-1][1][1][1]
                                
                                if (abs(prev_height - l[i][1][1]))<80:
                                    new_height = (prev_height + l[i][1][1])//2
                                    width = new_l[-1][0][1][0]
                                    new_l[-1][1] = tuple((prev_word + " " + l[i][0], [width, new_height]))
                                    
                                else:
                                    logging.info("Couldn't process word " + l[i][0])
                                    continue

                clean_l = []

                for i in new_l:
                    if i[0] == () or i[1] == () or len(i[0][0]) < 2 or i[0][0].isnumeric() or len(i[1][0])< 2 or i[1][0].isnumeric():
                        pass
                    else:
                        clean_l.append(i)
                final_list = []
                for i in range (len(clean_l)):
                    src_word = clean_l[i][0][0]
                    trgt_word = clean_l[i][1][0]
                    if len(clean_l[i][0]) == 1:
                        final_list.append([src_word, trgt_word,src_lng, tgt_lng, domain, source, "p",filename[:-5]+ ".pdf"])
                    else:
                        final_list.append([src_word, trgt_word, src_lng, tgt_lng, domain , source, "w", filename[:-5]+ ".pdf"])
                result.extend(final_list)
                
    tsv_path = config.OUTPUT_DIR + filename[:-5] +'.xlsx'
    csvfile2 = open(tsv_path, 'w', encoding='utf-8')
    csvwriter = csv.writer(csvfile2, delimiter = '\t')
    csvwriter.writerow(["Source" , "Target",	"Src Language",	"Tgt Language",	"Domain", "Collection Source", "Glossary Level", "PDF"])
    
    for i in range (len(result)):
        csvwriter.writerow(result[i])
    
    return result
        