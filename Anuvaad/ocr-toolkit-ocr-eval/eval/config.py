
LOGIN='https://auth.anuvaad.org/anuvaad/user-mgmt/v1/users/login'
USER="dhiraj.daga@tarento.com"
PASS="Cv@123"





#Step 1 generate evaluation report

#language = 'Devanagari'
#language  = 'hin_v5'
language = 'hin_only_error_30k'
path = '/home/ubuntu/tess_train_data_prep/pdfs/to_process/'

#path = '/home/dhiraj/Documents/data/tess_training/GOOD_BAD_AVG/progress'

#path = '/home/ubuntu/tesseract_evaluation_hindi/tesseract_evaluation/data/'
#output_path = '/home/ubuntu/tesseract_evaluation_hindi/tesseract_evaluation/result/'
#output_path_boxes= '/home/ubuntu/tesseract_evaluation_hindi/tesseract_evaluation/test_word_boxes/'
#base_path = '/home/ubuntu/tesseract_evaluation_hindi/tesseract_evaluation/test_word_boxes/'


#output_path ='/home/dhiraj/Documents/data/tess_training/reports/'

output_path = '/home/ubuntu/tess_train_data_prep/reports/hindi/hi_test/'
output_path_boxes = output_path
base_path         = output_path


#Step 2 filter crops based on text score


score_threshold=1
tesserct_conf = 0.0
google_conf   = 0.0


# eval_csv_path='/home/ubuntu/tess_train_data_prep/reports/hi_good/good_hindi/gv.csv'
# crops_dir='/home/ubuntu/tess_train_data_prep/crops/hi_good'
# data_csv_path = '/home/ubuntu/tess_train_data_prep/text_csv/hi_good.csv'


#eval_csv_path='/home/ubuntu/tess_train_data_prep/reports/hindi/*/*.csv'
#crops_dir='/home/ubuntu/tess_train_data_prep/crops/hindi/hi_good'
#data_csv_path = '/home/ubuntu/tess_train_data_prep/text_csv/hindi/'


eval_csv_path='/home/ubuntu/tess_train_data_prep/reports/hi_good/good_hindi/*v4.csv'
crops_dir='/home/ubuntu/tess_train_data_prep/crops/hi_good/v4'
data_csv_path = '/home/ubuntu/tess_train_data_prep/text_csv/hindi/'
