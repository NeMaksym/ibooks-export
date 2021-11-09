import csv
from datetime import datetime


def save_to_log(msg):
    with open('log.csv', 'a', newline='', encoding='utf-8') as logfile:
        writer = csv.writer(logfile, delimiter=',')
        writer.writerow([datetime.now(), msg])
