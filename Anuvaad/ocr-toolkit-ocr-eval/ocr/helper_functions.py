import csv
from PyPDF2 import PdfFileReader, PdfFileWriter
import config
from pathlib import Path

def get_center_of_bounding_box(line):
    x = (line['boundingBox']['vertices'][0]['x'] + line['boundingBox']['vertices'][1]['x'] + line['boundingBox']['vertices'][2]['x'] + line['boundingBox']['vertices'][3]['x']) / 4
    y = (line['boundingBox']['vertices'][0]['y'] + line['boundingBox']['vertices'][1]['y'] + line['boundingBox']['vertices'][2]['y'] + line['boundingBox']['vertices'][3]['y']) / 4
    return (x,y)

def processPDF(src_lng, tgt_lng,src_dir, tgt_dir):
    ''' Set config variables, config file variables are used for Anuvaad OCR'''
    
    config.LANGUAGE = src_lng + "+" + tgt_lng
    config.INPUT_DIR = src_dir
    config.OUTPUT_DIR = tgt_dir


'''Crop a pdf to given start page and end page, then create a pdf_info.csv (same as file_list.csv before)
which is used as input to make_json_files and for creating the final xls file'''
def cropPDF (path, pdf_name, start_page, end_page, src_lng, tgt_lng, domain, col):
    csvfile = open('pdf_info.csv', 'w',encoding='utf-8')
    csvwriter = csv.writer(csvfile, delimiter = ';')
    csvwriter.writerow(["Filepath","Source","Target","StartPage","EndPage","Domain","Type"])

    input_pdf = PdfFileReader(path)
    i = int(start_page)
    j = 0
    
    while (i+25<int(end_page)):
        j+=1
        pdf_writer = PdfFileWriter()
        for n in range(i, i+25):
            page = input_pdf.getPage(n)
            pdf_writer.addPage(page)
        path = config.OUTPUT_DIR + pdf_name[:-4]+ str(j) +".pdf"
        with Path(path).open(mode="wb") as output_file:
            pdf_writer.write(output_file)
        new_path = pdf_name[:-4]+ str(j) +".pdf"
        csvwriter.writerow([new_path, src_lng, tgt_lng, i, i+25, domain, col])
        i+=26
    j+=1
    pdf_writer = PdfFileWriter()
    # for the remaining last <25 pages.
    for n in range (i, int(end_page)):
        page = input_pdf.getPage(n)
        pdf_writer.addPage(page)
    path = config.OUTPUT_DIR + pdf_name[:-4]+ str(j) +".pdf"
    with Path(path).open(mode="wb") as output_file:
        pdf_writer.write(output_file)
    new_path = pdf_name[:-4]+ str(j) +".pdf"
    csvwriter.writerow([new_path, src_lng, tgt_lng, i, end_page, domain, col]) 
    