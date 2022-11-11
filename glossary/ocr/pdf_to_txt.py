import os
import json
import logging
import requests
from time import sleep

import utils.config as config

logging.basicConfig(
    level=logging.INFO,
    filename=config.LOGS,
    format="%(asctime)s-%(levelname)s-%(message)s",
)


class TokenizePdf:
    def __init__(self, input):
        self.path = input[0]
        self.header = {"auth-token": input[1]}
        print("ok0", flush=True)
        self.upload()
        self.lang = config.LANGUAGE
        print("ok1", flush=True)
        self.ocr_and_tokenize()
        print("ok2", flush=True)
        self.download_file()
        print("ok3", flush=True)
        self.write_to_txt()
        print("ok4", flush=True)

    def upload(self):
        logging.info("Processing file {}".format(self.path))
        self.file_name = self.path.split("/")[-1].split(".")[0]
        self.file_name = self.file_name.replace(" ", "_")
        files = [("file", (open(self.path, "rb")))]
        try:
            response = requests.post(config.UPLOAD, headers=self.header, files=files)
            self.file_id = response.json()["data"]
            logging.info(
                "{} upload response : {}".format(self.file_name, response.json())
            )
        except Exception as e:
            logging.error(
                "Error in processing {} due to {}  \n {}".format(
                    self.file_name, e, response.json()
                ),
                exc_info=True,
            )
            self.file_id = None

    def ocr_and_tokenize(self):
        if self.lang is not None:
            self.init_request()
            self.tok_json = self.bulk_serach()
        else:
            self.tok_json = None

    def init_request(self):
        try:
            file = {
                "workflowCode": config.WF_CODE,
                "files": [
                    {
                        "path": str(self.file_id),
                        "type": "pdf",
                        "locale": self.lang,
                        "config": {
                            "OCR": {
                                "option": "HIGH_ACCURACY",
                                "language": self.lang,
                                "top_correction": "False",
                                "craft_word": config.craft_word,
                                "craft_line": config.craft_line,
                                "line_layout": config.line_layout,
                                "mask_image": "False",
                            }
                        },
                    }
                ],
            }

            logging.info("OCR and Toeknization statred  for {}".format(self.file_name))
            res = requests.post(config.WF_INIT, json=file, headers=self.header)
            self.job_id = res.json()["jobID"]
        except Exception as e:
            logging.error(
                "Error in initiating WF requeest for {} due to {} ".format(
                    self.file_name, e
                ),
                exc_info=True,
            )
            self.job_id = None

    def bulk_serach(self):
        if self.job_id is not None:
            bs_request = {"jobIDs": [self.job_id], "taskDetails": "false"}
        logging.info(
            "process started for file  {} with job id {}".format(
                self.file_name, self.job_id
            )
        )
        res = requests.post(
            config.SEARCH, json=bs_request, headers=self.header, timeout=10000
        )
        retry = 0
        while 1:
            retry += 1
            try:
                r_j = res.json()
                progress = r_j["jobs"][0]["status"]
                if retry % 100 == 0:
                    logging.info("retrying bulk search: {} \n".format(retry))
            except Exception as e:
                logging.error(
                    "Error in bulk search for {} due to {} ".format(self.file_name, e),
                    exc_info=True,
                )
                progress = "p"

            if progress in ["COMPLETED", "FAILED", "SUCCESS"]:
                if progress == "FAILED":
                    logging.error(
                        "Process failed for file  {} with job id {} ".format(
                            self.file_name, self.job_id
                        )
                    )
                    return None
                else:
                    outputfile = r_j["jobs"][0]["output"][0]["outputFile"]
                    return outputfile
            res = requests.post(
                config.SEARCH, json=bs_request, headers=self.header, timeout=10000
            )
            sleep(2)

    def download_file(self):
        if self.tok_json is not None:
            try:
                download_url = config.DOWNLOAD + str(self.tok_json)
                res = requests.get(download_url, headers=self.header)
                self.o_tk_json = res.json()
                # save_folder_name = self.path.split('/')[-2]
                save_folder_name = os.path.dirname(self.path)
                self.save_dir = os.path.join(config.OUTPUT_DIR, save_folder_name)
                # self.save_dir = config.OUTPUT_DIR
                os.system("mkdir -p {}".format(self.save_dir))
                if config.SAVE_JSON:
                    json_path = os.path.join(
                        self.save_dir, "{}.json".format(self.file_name)
                    )
                    with open(json_path, "w", encoding="utf8") as write_file:
                        json.dump(self.o_tk_json, write_file, ensure_ascii=False)
            except Exception as e:
                logging.error(
                    "Error in downloading file  {} \n {}  ".format(self.tok_json, e),
                    exc_info=True,
                )
                self.o_tk_json = None
        else:
            self.o_tk_json = None

    def write_to_txt(self):
        if self.o_tk_json is not None:
            try:

                file_path = os.path.join(self.save_dir, "{}.txt".format(self.file_name))
                # os.system('rm {}'.format(file_path))
                for page in self.o_tk_json["outputs"][0]["pages"]:
                    for region in page["regions"]:
                        if "tokenized_sentences" in region.keys():
                            for sentence in region["tokenized_sentences"]:
                                with open(file_path, "a") as txtfile:
                                    txtfile.write("{}\n".format(sentence["src"]))
                logging.info("file {} successfully processed ".format(self.file_name))
            except Exception as e:
                logging.error(
                    "Error occured during writing to txt for file {} \n {} ".format(
                        self.file_name, e
                    ),
                    exc_info=True,
                )
        else:
            logging.error("Error occured druing processig {} ".format(self.file_name))
