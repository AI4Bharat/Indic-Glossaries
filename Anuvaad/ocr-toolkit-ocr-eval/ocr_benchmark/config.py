import logging
import sys
logging.basicConfig(level=logging.INFO, filename='tesseract.logs',
                    format='%(asctime)s-%(levelname)s-%(message)s')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


# The output csv will cotatin a column  'exp' which will have the vlaue  : EXP_NAME_LANG_WEIGHT
EXP_NAME = 'tess_baseline'


# Will save the intermediate image crops in the output dir
CHECK = True


# Number of parallel tesseract processes to fork
BATCH_SIZE = 2
MAX_QUEUE_SIZE = 100


# i/o dirs
#GT_SOURCE  = '/home/dhiraj/Documents/data/tess_training/iise_gt/iit_line_mapped/101/*/*.csv'
#IMAGE_DIR= '/home/dhiraj/Documents/data/tess_training/iise_gt/IIIT_Hindi_100-20210531T041306Z-001/IIIT_Hindi_100/Images'
# IMAGE_FORMAT='jpg'
#OUTPUT_DIR = '/home/dhiraj/Documents/data/tess_training/scrits/output'
#OUTPUT_FILE = '/home/dhiraj/Documents/data/tess_training/iise_gt/benchmark/test.csv'

# GT_SOURCE = '/home/dhiraj/Documents/data/tess_training/batch_2/output/csv/*'
# IMAGE_DIR  = '/home/dhiraj/Documents/data/tess_training/batch_2/output/images'
# IMAGE_FORMAT ='png'
# OUTPUT_DIR = '/home/dhiraj/Documents/data/tess_training/scrits/output'
# OUTPUT_FILE = '/home/dhiraj/Documents/data/tess_training/iise_gt/benchmark/test_1.csv'

GT_SOURCE = '/home/ubuntu/tess_train_data_prep/reports/hindi/batch_2/csv/*'
IMAGE_DIR = '/home/ubuntu/tess_train_data_prep/reports/hindi/batch_2/images'
IMAGE_FORMAT = 'png'
OUTPUT_DIR = '/home/ubuntu/tess_train_data_prep/reports/hindi/batch_2'

#OUTPUT_FILE = '/home/ubuntu/tess_train_data_prep/reports/hindi/batch_2/report_with_dynamic_margins.csv'
OUTPUT_FILE = '/home/ubuntu/tess_train_data_prep/reports/hindi/batch_2/report_without_dynamic_margins.csv'


# OCR  config
LANGUAGES = ['Devanagari']
PSM = 7
DYNAMIC_MARGINS = False
PERSPECTIVE_TRANSFORM = False


# if set to None the lang provide in OCR config will be used for psm 6 ocr (when text block contains more than one line)
FALL_BACK_LANGUAGE = None


# For more info about postprocssing flags rfer the module post_process.py
POST_PROCESSING_MODE = None
DOUBLE_OCR_THRESHLOD = 80
DOUBLE_OCR_LANG = 'exp1'


# Preporcessing config
DOWLOAD_URL = "https://auth.anuvaad.org/download/"
# GV_OUTPUT_DIR ='/home/dhiraj/Documents/data/tess_training/batch_2/gv_json/*'
# OUTPUT_CSV_DIR = '/home/dhiraj/Documents/data/tess_training/batch_2/output/csv'
# OUTPUT_IMG_DIR  = '/home/dhiraj/Documents/data/tess_training/batch_2/output/images'

# GV_OUTPUT_DIR ='/home/dhiraj/Documents/data/tess_training/batch_2/gv_json/*'
# OUTPUT_CSV_DIR = '/home/dhiraj/Documents/data/tess_training/batch_2/output/csv'
# OUTPUT_IMG_DIR  = '/home/dhiraj/Documents/data/tess_training/batch_2/output/images'

GV_OUTPUT_DIR = '/home/ubuntu/data/text_detect/v1/pdfs/annotations/*/*.json'
OUTPUT_TXT_DIR = '/home/ubuntu/data/text_detect/v1/txt'
OUTPUT_IMG_DIR = '/home/ubuntu/data/text_detect/v1/images'
