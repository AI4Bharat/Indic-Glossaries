import glob
from statistics import mode
import config
import pandas as pd
import os
import cv2
from utils.dynamic_adjustment import coord_adjustment
from utils.post_process import post_process_ocr_text
from utils.utils import scale_coords, get_page_resolution, get_file_name, crop_region, get_tess_text, frequent_height, seq_matcher, append_to_file


def init_file():
    if not os.path.exists(config.OUTPUT_FILE):
        columns = ['gt_text', 'tess_text', 'score', 'gt_lenght',
                   'mismatch_count', 'exp', 'coord', 'image_name', 'crop_name', 'ocr_conf']
        text = ','.join(columns) + '\n'
        with open(config.OUTPUT_FILE, "a") as txtfile:
            txtfile.write(text)


def append_line(line_stats):
    append_to_file(config.OUTPUT_FILE, line_stats)


def tess_eval(input):
    lang, image_crop, gt_text, coord, mode_height, image_name, crop_name = input
    ocr_text, ocr_conf = get_tess_text(image_crop, lang, mode_height)
    ocr_text, ocr_conf = post_process_ocr_text(
        image_crop, ocr_text, ocr_conf, mode_height)

    score, gt_len, mismatch_count = seq_matcher(str(ocr_text), str(gt_text))

    return [gt_text, ocr_text, score, gt_len, mismatch_count, str(config.EXP_NAME) + '_' + lang, coord, image_name, crop_name, ocr_conf]


def add_lines_to_tess_queue(gt_source, queue, lang):

    csv_paths = glob.glob(gt_source)

    for csv_path in csv_paths:
        config.logging.info('process started for file  {} '.format(csv_path))
        image_name = get_file_name(csv_path)
        image_path = os.path.join(config.IMAGE_DIR, '{}.{}'.format(
            image_name, config.IMAGE_FORMAT))
        # print(image_path)
        page_data = pd.read_csv(csv_path)
        image = cv2.imread(image_path, 0)

        if len(page_data) > 0:
            page_resolution = get_page_resolution(page_data)
            coords = scale_coords(page_data, image.shape, page_resolution)
            if config.DYNAMIC_MARGINS:
                coords = coord_adjustment(image, coords)
            mode_height = frequent_height(coords)

            for index, coord in enumerate(coords):
                crop_name = page_data['images'].iloc[index]
                image_crop = crop_region(coord, image, crop_name)

                if image_crop is not None and image_crop.shape[1] > 3 and image_crop.shape[0] > 3:
                    line_meta_data = [
                        lang, image_crop, page_data['groundTruth'].iloc[index], coord, mode_height, image_name, crop_name]
                    queue.put(line_meta_data)
