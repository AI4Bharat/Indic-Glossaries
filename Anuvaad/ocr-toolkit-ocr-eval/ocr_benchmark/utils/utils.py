import cv2
import config
import json
import statistics
import numpy as np
import requests
import csv
from os import path
import pytesseract
from pytesseract import Output
from leven import levenshtein
from utils.dynamic_adjustment import validate_region


def get_file_name(csv_path):
    # return csv_path.split('/')[-3]
    return csv_path.split('/')[-1][:-4]


def get_page_resolution(page_data):
    page_info = json.loads(page_data['page_coords'].iloc[0].replace("'", '"'))
    height = page_info['boundingBox']['vertices'][2]['y']
    width = page_info['boundingBox']['vertices'][1]['x']
    return height, width


def scale_coords(page_data, image_shape, page_resolution):
    page_data['coords'] = page_data['coords'].str.replace("'", '"')
    page_data['coords'] = page_data['coords'].apply(json.loads)
    coords = page_data['coords'].values
    scaled_coords = []
    x_ratio = image_shape[1]/page_resolution[1]
    y_ratio = image_shape[0]/page_resolution[0]
    #print('ratios  ',x_ratio,y_ratio, page_resolution,image_shape)
    for coord in coords:
        region = {'boundingBox': {'vertices': []}}
        for point in coord['boundingBox']['vertices']:
            region['boundingBox']['vertices'].append(
                {'x': int(point['x'] * x_ratio), 'y': int(point['y'] * y_ratio)})
        scaled_coords.append(region)
    return scaled_coords


def frequent_height(coords):
    text_height = []
    if len(coords) > 0:
        for box in coords:
            text_height.append(abs(
                box['boundingBox']['vertices'][0]['y'] - box['boundingBox']['vertices'][3]['y']))
        return statistics.median(text_height)
    else:
        return 0


def crop_region(coord, image, crop_name):
    try:
        if validate_region(coord):
            vertices = coord['boundingBox']['vertices']
            if config.PERSPECTIVE_TRANSFORM:
                box = get_box(coord)
                crop_image = get_crop_with_pers_transform(
                    image, box, height=abs(box[0, 1]-box[2, 1]))
            else:
                crop_image = image[vertices[0]['y']: vertices[2]
                                   ['y'], vertices[0]['x']: vertices[2]['x']]

            if config.CHECK:
                crop_path = path.join(config.OUTPUT_DIR + '/crops', crop_name)
                cv2.imwrite(crop_path, crop_image)
            return crop_image
        else:
            config.logging.error(
                'Error in region region {}  due to invalid coordinates'.format(coord))
            return None
    except Exception as e:
        config.logging.error(
            'Error in region region {}  due to invalid coordinates'.format(coord))
        return None


def get_tess_text(image_crop, lang, median_height):

    crop_height = image_crop.shape[0]
    if crop_height > median_height * 1.5:

        # experiment with FALL_BACK_LANGUAGE as orignal and trained
        if config.FALL_BACK_LANGUAGE is not None:
            fall_back_lang = config.FALL_BACK_LANGUAGE
        else:
            fall_back_lang = lang
        dfs = pytesseract.image_to_data(
            image_crop, config='--psm 6', lang=fall_back_lang, output_type=Output.DATAFRAME)
        text, conf_dict = process_dfs(dfs)
        return text, conf_dict
    else:
        dfs = pytesseract.image_to_data(
            image_crop, config='--psm '+str(config.PSM), lang=lang, output_type=Output.DATAFRAME)
        text, conf_dict = process_dfs(dfs)
    return text, conf_dict


def seq_matcher(tgt_text, gt_text):
    if tgt_text is not None and gt_text is not None:
        tgt_text = remove_space(tgt_text)
        gt_text = remove_space(gt_text)
        mismatch_count = levenshtein(tgt_text, gt_text)
        gt_len = len(gt_text)
        if gt_len > 0:
            score = 1 - mismatch_count/gt_len
            if score < 0:
                score = 0
            return score, gt_len, mismatch_count
    return 0, 0, 0


def append_to_file(file_path, line_stats):
    with open(file_path, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(line_stats)


def get_box(bbox):
    temp_box = []
    temp_box.append([bbox["boundingBox"]['vertices'][0]['x'],
                    bbox["boundingBox"]['vertices'][0]['y']])
    temp_box.append([bbox["boundingBox"]['vertices'][1]['x'],
                    bbox["boundingBox"]['vertices'][1]['y']])
    temp_box.append([bbox["boundingBox"]['vertices'][2]['x'],
                    bbox["boundingBox"]['vertices'][2]['y']])
    temp_box.append([bbox["boundingBox"]['vertices'][3]['x'],
                    bbox["boundingBox"]['vertices'][3]['y']])

    temp_box = np.array(temp_box)
    return temp_box


def get_crop_with_pers_transform(image, box, height=140):

    w = max(abs(box[0, 0] - box[1, 0]), abs(box[2, 0] - box[3, 0]))
    height = max(abs(box[0, 1] - box[3, 1]), abs(box[1, 1] - box[2, 1]))
    pts1 = np.float32(box)
    pts2 = np.float32(
        [[0, 0], [int(w), 0], [int(w), int(height)], [0, int(height)]])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    result_img = cv2.warpPerspective(
        image, M, (int(w), int(height)))  # flags=cv2.INTER_NEAREST
    return result_img


def process_dfs(temp_df):
    temp_df = temp_df[temp_df.text.notnull()]
    text = ""
    conf = 0
    temp_dict1 = {"text": [], "conf": []}
    for index, row in temp_df.iterrows():
        #temp_dict2 = {}
        conf = conf + row["conf"]
        temp_dict1["text"].append(row['text'])
        temp_dict1["conf"].append(row['conf'])
        text = text + " " + str(row['text'])
        # temp_dict1.append(temp_dict2)
    return text, temp_dict1


def remove_space(a):
    return a.replace(" ", "")


def read_json(json_path):
    with open(json_path, 'r') as j_file:
        j_data = json.load(j_file)
    return j_data


def download_file(outputfile, f_type='json'):
    download_url = config.DOWLOAD_URL + outputfile
    res = requests.get(download_url)
    if f_type == 'json':
        return res.json()
    else:
        return res.content
