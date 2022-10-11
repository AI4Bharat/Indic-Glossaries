import cv2,glob
import pandas as pd
from io import StringIO
import json
import numpy as np
import requests
#import matplotlib.pyplot as plt
import uuid
import config
import os


def read_json(json_path):
    with open(json_path,'r') as j_file:
        j_data = json.load(j_file)
    return j_data


def download_file(outputfile,f_type='json'):
    download_url ='https://auth.anuvaad.org/download/'+str(outputfile)
    res = requests.get(download_url)
    if f_type == 'json':
        return res.json()
    else :
        return res.content


def get_page(page_path):
    page_path = page_path.split('upload')[1]
    print(page_path)
    nparr = np.fromstring( download_file(page_path,f_type='image'), np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def write_to_file(file_path,text):
    with open(file_path, "w",encoding='utf8') as txtfile:
        txtfile.write("{}\n".format(text))

def to_df(data_csv,folder,folder_name,prefix):     
    data_df = pd.DataFrame(data_csv,columns=['path','boundingBox','key','score','g_conf','tess_text','ground_text'])    
    data_df.to_csv(folder+"/" + prefix + '_' + folder_name + '.csv',index=False)

   
        
def remove_trailing_space(a):
    m_text = ''
    for text in a.split(' '):
        if len(text) > 0:
            if m_text == '' :
                m_text += text
            else :
                m_text = m_text + ' ' + text
    return m_text


def crop_image_with_df(image,page_path, df ,folder_name,job_id,page_index,prefix):
    
    folder = config.crops_dir+str(folder_name)
    crops_folder = folder + '/' + prefix
    if not os.path.exists(folder):
            os.mkdir(folder)
    if not os.path.exists(crops_folder):
            os.mkdir(crops_folder)        
    data_csv = []
    
    for line_index in range(len(df)):
        try:
            bbox = df['boundingBox'].iloc[line_index]
            score = df['score'].iloc[line_index]
            g_conf = df['g_conf'].iloc[line_index]
            t_text = df['tess_text'].iloc[line_index]
            ground_text= df['text'].iloc[line_index]
            key = '{}_{}_{}'.format(job_id,page_index,line_index)
            vertices =  json.loads(bbox.replace("'",'"'))['vertices']
            crop = image[int(vertices[0]['y']):int( vertices[2]['y']),\
                int(vertices[0]['x']):int(vertices[1]['x']) ]
            if ground_text is not None and len(ground_text) > 0 :
                ground_text = remove_trailing_space(ground_text)
            data_csv.append([page_path, bbox, key,score,g_conf ,t_text, ground_text])
            cv2.imwrite('{}/{}.tif'.format(crops_folder,key),crop)
            write_to_file(crops_folder + '/' + key + '.gt.txt',ground_text)
        except Exception as e:
            print("erro in processing {} , box {} due to {} ".format(key,bbox,e))
    return data_csv


def get_error_crops(eval_csv_path):
    file_name = eval_csv_path.split("/")[-1]
    folder_name = eval_csv_path.split("/")[-2]
    folder = os.path.join(config.crops_dir,str(folder_name))
    eval_df = pd.read_csv(eval_csv_path)
    correct_data = []
    error_data = []
    job_id = str(uuid.uuid4())

    for page_index in range(len(eval_df)):

        page_path = eval_df['page_path'][page_index]
        df_string = StringIO(eval_df['page_data'][page_index])
        page_df = pd.read_csv(df_string, sep=",")
        
        image = get_page(page_path)
        
        errors_df = page_df[ (page_df['score'] < config.score_threshold) \
                            & (page_df['g_conf'] > config.g_conf_threshold)]
        correct_df =  page_df[ page_df['score'] >= config.score_threshold]
        
        error_data += crop_image_with_df(image,page_path ,errors_df ,folder_name,job_id,page_index , prefix='error')
        correct_data += crop_image_with_df(image, page_path,correct_df ,folder_name,job_id,page_index, prefix='correct')
        
        print('% error in page {} is {} '.format(page_index,(len(errors_df) * 100) / len(page_df)))
    
    to_df(correct_data,folder,folder_name,prefix='correct')    
    to_df(error_data,folder,folder_name,prefix='error')  

        
         

if __name__ == '__main__':

    for eval_csv_path in glob.glob(config.eval_csv_path):
        get_error_crops(eval_csv_path)