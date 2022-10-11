import config
from utils.utils import get_tess_text


def post_process_ocr_text(image_crop, ocr_text, ocr_conf, mode_height):

    if config.POST_PROCESSING_MODE == None:
        return ocr_text, ocr_conf

    if config.POST_PROCESSING_MODE == 'FixInts':
        return process_ints(ocr_text), ocr_conf

    if config.POST_PROCESSING_MODE == 'DoubleOcr':
        return double_ocr(image_crop, ocr_text, ocr_conf, mode_height)


def double_ocr(image_crop, ocr_text, ocr_conf, mode_height):
    d_ocr = False
    if 'conf' in ocr_conf.keys():
        for conf in ocr_conf['conf']:
            if conf < config.DOUBLE_OCR_THRESHLOD:
                d_ocr = True
                break
    if d_ocr:
        return get_tess_text(image_crop, config.DOUBLE_OCR_LANG, mode_height)

    return ocr_text, ocr_conf


def process_ints(text):
    try:
        if type(text) in [int, float]:
            if int(text) == text:
                return str(int(text))
            else:
                return str(text)
        else:
            return str(text)
    except Exception as e:
        print(e)
        return str(text)
