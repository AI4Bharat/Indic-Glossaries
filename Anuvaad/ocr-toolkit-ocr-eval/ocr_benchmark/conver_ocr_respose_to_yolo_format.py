import cv2
import os
import uuid
import glob
import config
import numpy as np
import pandas as pd
from utils.utils import read_json, download_file


class Page:
    def __init__(self, page):
        self.page = page
        self.im_h = None
        self.im_w = None
        self.lines = []
        self.line_coords = []

    def get_page_coords(self):
        return {'boundingBox': page['boundingBox']}

    def get_image(self):
        page_path = self.page['path']
        page_path = page_path.split('upload')[1]
        nparr = np.frombuffer(download_file(
            page_path, f_type='image'), np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        self.im_h, self.im_w = image.shape[0], image.shape[1]
        return image

    def get_lines(self):

        if len(self.lines) > 0:
            return self.lines
        regions = page['regions']
        if len(regions) < 2:
            return []
        for para in regions:
            if 'regions' in para.keys() and len(para['regions']) > 0:
                self.lines.extend(para['regions'])

    def bbox2yolo(self, box, c_lass=0):
        vertices = box['boundingBox']['vertices']
        xmin = vertices[0]['x']
        xmax = vertices[1]['x']
        ymin = vertices[0]['y']
        ymax = vertices[2]['y']

        xcen = float((xmin + xmax)) / 2 / self.im_w
        ycen = float((ymin + ymax)) / 2 / self.im_h

        w = float((xmax - xmin)) / self.im_w
        h = float((ymax - ymin)) / self.im_h

        return [str(c_lass), str(xcen), str(ycen), str(w), str(h)]

    def get_annotations(self):
        if len(self.line_coords) == 0:
            self.get_lines()
            for line in self.lines:
                self.line_coords.append(self.bbox2yolo(line))
        return self.line_coords


def write_to_file(annotations, txt_path):
    for c_index, coords in enumerate(annotations):
        with open(txt_path, "a") as file_object:
            if c_index > 0:
                file_object.write('\n')
            file_object.write(' '.join(coords))


if __name__ == '__main__':

    os.system('mkdir -p ' + config.OUTPUT_TXT_DIR)
    os.system('mkdir -p ' + config.OUTPUT_IMG_DIR)

    gv_paths = glob.glob(config.GV_OUTPUT_DIR)

    for gv_path in gv_paths:
        file_identifier = str(uuid.uuid4())
        file_name = gv_path.split('/')[-1][:-5]
        print('Processing file ', file_name)
        try:
            pdf_data = read_json(gv_path)
            pages = pdf_data['outputs'][0]['pages']
            #print('Processing file ', file_name)
            for page_index, page in enumerate(pages):
                txt_path = os.path.join(config.OUTPUT_TXT_DIR, '{}_{}_{}.txt'.format(
                    file_name, page_index, file_identifier))
                image_path = os.path.join(config.OUTPUT_IMG_DIR, '{}_{}_{}.png'.format(
                    file_name, page_index, file_identifier))
                if not os.path.exists(txt_path):

                    page_properties = Page(page)
                    image = page_properties.get_image()
                    annotations = page_properties.get_annotations()

                    txt_path = os.path.join(config.OUTPUT_TXT_DIR, '{}_{}_{}.txt'.format(
                        file_name, page_index, file_identifier))
                    image_path = os.path.join(config.OUTPUT_IMG_DIR, '{}_{}_{}.png'.format(
                        file_name, page_index, file_identifier))

                    write_to_file(annotations, txt_path)
                    cv2.imwrite(image_path, image)
        except Exception as e:
            print('Failed for file {} due to '.format(file_name, e))
