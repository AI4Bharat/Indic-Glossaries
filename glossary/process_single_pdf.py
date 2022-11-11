import os
import sys
import logging
import csv

# from glossary.ocr.indic_regex import regex
# from PyPDF2 import PdfFileReader, PdfFileWriter
import utils.config as config
from data_maker.parse_type_1 import parse_type_1
from data_maker.parse_type_2 import parse_type_2
import utils.helper_functions as helper_functions
import ocr.make_json as make_json

if __name__ == "__main__":
    """
    Takes input parameters for a single PDF from user to output a digitized glossary.
    """
    # TODO add name arg
    src_lng = sys.argv[1]
    tgt_lng = sys.argv[2]
    path = sys.argv[3]  # path of the pdf / json
    col = sys.argv[4]
    start_page = sys.argv[5]  # not needed for json processing
    end_page = sys.argv[6]  # not needed for json processing
    domain = sys.argv[7]
    source = sys.argv[8]

    pdf_name = os.path.basename(os.path.normpath(path))
    tgt_dir = config.OUTPUT_DIR
    src_dir = os.path.dirname(path)

    if path.endswith(".pdf") and os.path.exists(path):
        helper_functions.cropPDF(
            path, pdf_name, start_page, end_page, src_lng, tgt_lng, domain, col
        )
        helper_functions.processPDF(src_lng, tgt_lng, src_dir, tgt_dir)

        if os.path.exists("pdf_info.csv"):
            file = open("pdf_info.csv", "r")
            csvreader = csv.reader(file, delimiter=";")
            files_to_parse = [f for f in csvreader]

            # create a list of filename.json
            json_list = [f[0][:-4] + ".json" for f in files_to_parse[1:]]

            try:
                make_json.make_json_files(files_to_parse[1:])
            except:
                logging.error("Unable to create json for the pdf: " + pdf_name)
            for file_ in json_list:
                file_ = file_.replace(" ", "_")
                if file_ in os.listdir(config.OUTPUT_DIR):
                    json_file_path = config.OUTPUT_DIR + file_
                    file_name = file_

                    if os.path.exists(json_file_path):
                        if int(col) == 1:
                            json_file_path = config.OUTPUT_DIR + file_name
                            parse_type_1(
                                json_file_path,
                                file_name,
                                src_lng,
                                tgt_lng,
                                domain,
                                source,
                            )
                        elif int(col) == 2:
                            parse_type_2(
                                json_file_path,
                                file_name,
                                src_lng,
                                tgt_lng,
                                domain,
                                source,
                            )

                        else:
                            logging.error(
                                "Currently only 1 column and 2 column documents are supported"
                            )
    elif path.endswith(".json") and os.path.exists(path):
        if int(col) == 1:
            parse_type_1(path, pdf_name, src_lng, tgt_lng, domain, source)
        elif int(col) == 2:
            parse_type_2(path, pdf_name, src_lng, tgt_lng, domain, source)
        else:
            logging.error(
                "Currently only 1 column and 2 column documents are supported"
            )

    else:
        logging.error("Please check the path and filename")
