import cv2,glob
import pandas as pd
import json
import numpy as np
#import matplotlib.pyplot as plt
import config
import os
#import swifter
from utils.utils import crop_region


# def write_to_file(file_path,text):
#     with open(file_path, "w",encoding='utf8') as txtfile:
#         txtfile.write("{}".format(text))

# def to_df(data_csv,folder,folder_name,prefix):     
#     data_df = pd.DataFrame(data_csv,columns=['path','boundingBox','key','score','g_conf','tess_text','ground_text'])    
#     data_df.to_csv(folder+"/" + prefix + '_' + folder_name + '.csv',index=False)

   
        
# def remove_trailing_space(a):
#     m_text = ''
#     for text in a.split(' '):
#         if len(text) > 0:
#             if m_text == '' :
#                 m_text += text
#             else :
#                 m_text = m_text + ' ' + text
#     return m_text


def cut_crops(row,image):
    #gt_text = row['gt_text']
    coords  = json.loads(row['coord'].replace("'",'"'))
    crop_name = row['crop_name']
    crop_region(coords,image,crop_name)
    

def cut_crops_form_df(df):

    pages  = df.groupby('image_name')
    for page in pages:
        image_name  = page[0]
        page_df     = page[1]
        print('Processing image ',image_name)
        image_path = os.path.join(config.IMAGE_DIR,"{}.png".format(image_name))
        image   = cv2.imread(image_path)          
        if len(page_df) > 0:
            page_df.apply(lambda x:cut_crops(x,image),axis=1)


def get_error_crops(eval_csv_path):

    eval_csv = pd.read_csv(eval_csv_path)
    correct_df = eval_csv[eval_csv['score']==1]
    error_df   = eval_csv[eval_csv['score'] < 1]

    #cut_crops_form_df(correct_df)
    cut_crops_form_df(error_df)

    error_df.to_csv(config.OUTPUT_DIR + '/error_lines.csv')
    #correct_df.to_csv(config.OUTPUT_DIR + '/correct_lines.csv')


         

if __name__ == '__main__':

    for eval_csv_path in glob.glob(config.OUTPUT_FILE):
        get_error_crops(eval_csv_path)