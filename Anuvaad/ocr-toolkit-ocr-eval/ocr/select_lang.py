import csv
file = open('file_list.csv', 'r')
csvreader = csv.reader(file, delimiter = ';')
files_to_parse = [f for f in csvreader]
src_lng = 'en'
tgt_lng = 'hi'
csvfile_new = open('file_list_hindi.csv', 'w',encoding='utf-8')
csvwriter = csv.writer(csvfile_new, delimiter = ';')
csvwriter.writerow(["Filepath", "Source", "Target", "StartPage", "EndPage", "Domain", "Type"])

for f in files_to_parse:
    if f[1] == src_lng and f[2] == tgt_lng:
        csvwriter.writerow(f)




