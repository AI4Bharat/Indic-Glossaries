# IO

# INPUT_DIR = '/home/glossary/AI4Bharat_GlossaryMaker/Anuvaad/ocr-toolkit-ocr-eval/ocr/updated_glossaries/PDF_kannada'
# OUTPUT_DIR = '/home/glossary/AI4Bharat_GlossaryMaker/Anuvaad/ocr-toolkit-ocr-eval/ocr/test_outputs/'

INPUT_DIR = '/home/glossary/AI4Bharat_GlossaryMaker/Anuvaad/ocr-toolkit-ocr-eval/ocr/updated_glossaries/'
OUTPUT_DIR = '/home/glossary/AI4Bharat_GlossaryMaker/Anuvaad/ocr-toolkit-ocr-eval/ocr/new_output/'
LANGUAGE = 'en+hi'

craft_word="False"
craft_line="False"
line_layout = "False"

BATCH_SIZE = 1


LOGS = '/home/glossary/AI4Bharat_GlossaryMaker/Anuvaad/ocr-toolkit-ocr-eval/ocr/test_outputs/ocr.log'
SAVE_JSON = True
OVERWRITE = False

#LOGIN DEV
LOGIN = 'https://auth.anuvaad.org/anuvaad/user-mgmt/v1/users/login'
USER = "dhiraj.daga@tarento.com"  # dev env
PASS = "Cv@123"

# LOGIN = 'https://users-auth.anuvaad.org/anuvaad/user-mgmt/v1/users/login'
# USER = "srih854@gmail.com"
# PASS = "Welcome@123"

# LOGIN STAGE
# LOGIN='https://stage-auth.anuvaad.org/anuvaad/user-mgmt/v1/users/login'
# USER="stageuser@tarento.com"
# PASS="Welcome@123"


# WF CONFIG DEV

#WF_CODE = "WF_A_FCWDLDBSOD15GVOTK"
# WF_CODE = 'WF_A_OD10GV'

WF_CODE = "WF_A_WDOD15GV"
SEARCH = 'https://auth.anuvaad.org/anuvaad-etl/wf-manager/v1/workflow/jobs/search/bulk'
DOWNLOAD = "https://auth.anuvaad.org/download/"
UPLOAD = 'https://auth.anuvaad.org/anuvaad-api/file-uploader/v0/upload-file'
WF_INIT = "https://auth.anuvaad.org/anuvaad-etl/wf-manager/v1/workflow/async/initiate"

# SEARCH = 'https://users-auth.anuvaad.org/anuvaad-etl/wf-manager/v1/workflow/jobs/search/bulk'
# DOWNLOAD = "https://users-auth.anuvaad.org/download/"
# UPLOAD = 'https://users-auth.anuvaad.org/anuvaad-api/file-uploader/v0/upload-file'
# WF_INIT = "https://users-auth.anuvaad.org/anuvaad-etl/wf-manager/v1/workflow/async/initiate"

# WF CONFIG STAGE
# WF_INIT= "https://stage-auth.anuvaad.org/anuvaad-etl/wf-manager/v1/workflow/async/initiate"
# WF_CODE  = "WF_A_FCWDLDBSOD15GVOTK"

# SEARCH='https://stage-auth.anuvaad.org/anuvaad-etl/wf-manager/v1/workflow/jobs/search/bulk'
# DOWNLOAD="https://stage-auth.anuvaad.org/download/"
# UPLOAD='https://stage-auth.anuvaad.org/anuvaad-api/file-uploader/v0/upload-file'
