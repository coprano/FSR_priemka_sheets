
import csv
import logging
import os.path
logging.basicConfig(filename='logs.log', level=logging.INFO, format='%(asctime)s %(message)s')


def svodka(file_path):
    """
    Выводит на экран список столбцов
    """
    if(os.path.exists(file_path)):
        with open(file_path, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
            print(f'Processed {line_count} lines.')
        logging.info(f"SVODKA: processed {file_path}")
    else:
        logging.exception(f"SVODKA: couldn't open file:{file_path}")
        return 