#IO
#INPUT_DIR='/home/srihari/Desktop/anuvaad-toolkit/t3'
#OUTPUT_DIR='/home/srihari/Desktop/anuvaad-toolkit/outputs'

INPUT_DIR='/home/dhiraj/Documents/Anuwad/AIB/ta_set_1'
OUTPUT_DIR='/home/dhiraj/Documents/Anuwad/AIB/ta_set_1'

#INPUT_DIR='/home/dhiraj/Documents/Anuwad/AIB/tn_budget_parallel_docs/tn_budget_parallel_docs'
#OUTPUT_DIR='/home/dhiraj/Documents/Anuwad/AIB/tn_budget_parallel_docs/tn_budget_parallel_docs'


#INPUT_DIR='/home/dhiraj/Documents/Anuwad/AIB/test_large'
#OUTPUT_DIR='/home/dhiraj/Documents/Anuwad/AIB/test_large'
BATCH_SIZE=9

#LOGS='ocr_tok_stage_p3.log'
LOGS='ocr_tok_budget_docs.log'

SAVE_JSON=True
OVERWRITE=False

#LOGIN DEV
# LOGIN='https://auth.anuvaad.org/anuvaad/user-mgmt/v1/users/login'
# USER="dhiraj.daga@tarento.com"
# PASS="Cv@123"

#LOGIN STAGE
LOGIN='https://stage-auth.anuvaad.org/anuvaad/user-mgmt/v1/users/login'
USER="stageuser@tarento.com"
PASS="Welcome@123"


#WF CONFIG DEV
# WF_INIT= "https://auth.anuvaad.org/anuvaad-etl/wf-manager/v1/workflow/async/initiate"
# WF_CODE  = "WF_A_FCWDLDBSOD15GVOTK"
# SEARCH='https://auth.anuvaad.org/anuvaad-etl/wf-manager/v1/workflow/jobs/search/bulk'
# DOWNLOAD="https://auth.anuvaad.org/download/"
# UPLOAD='https://auth.anuvaad.org/anuvaad-api/file-uploader/v0/upload-file'

#WF CONFIG STAGE
WF_INIT= "https://stage-auth.anuvaad.org/anuvaad-etl/wf-manager/v1/workflow/async/initiate"
WF_CODE  = "WF_A_FCWDLDBSOD15GVOTK"
SEARCH='https://stage-auth.anuvaad.org/anuvaad-etl/wf-manager/v1/workflow/jobs/search/bulk'
DOWNLOAD="https://stage-auth.anuvaad.org/download/"
UPLOAD='https://stage-auth.anuvaad.org/anuvaad-api/file-uploader/v0/upload-file'
