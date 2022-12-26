import sys
import utils.type as type
import process_pdfs

if __name__ == "__main__":
    folder_path = sys.argv[1]  # folder path for pdfs to be processed
    file_list_path = sys.argv[2]  # The final_file.csv for your pdfs
    output_dir = sys.argv[3]  # Output folder
    source = sys.argv[4]
    type_ = int(sys.argv[5])
    if type_ == 1:
        type_info = type.PdfType(True, 1, 0, 0, False, False)
        process_pdfs.process_pdfs(
            folder_path, file_list_path, output_dir, source, type_info
        )
    elif type_ == 2:
        type_info = type.PdfType(True, 1, 1, 0, False, False)
        process_pdfs.process_pdfs(
            folder_path, file_list_path, output_dir, source, type_info
        )
    elif type_ == 3:
        type_info = type.PdfType(True, 2, 0, 0, False, False)
        process_pdfs.process_pdfs(
            folder_path, file_list_path, output_dir, source, type_info
        )

    else:
        print("eror")
