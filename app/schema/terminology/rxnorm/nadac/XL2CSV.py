__author__ = 'dave'
import sys, os
lib_path = os.path.abspath('./xlrd-0.9.3')
sys.path.append(lib_path)
import xlrd
import csv

nadac=''

#find the nadac file
for file in os.listdir(os.path.abspath('.')):
    if file.__contains__(".xls"):
        nadac=os.path.abspath('.')+'/'+file

#convert the file to csv
wb = xlrd.open_workbook(nadac)
sh = wb.sheet_by_name('NADAC')
your_csv_file = open('NADAC.csv', 'wt')
wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)
for rownum in range (5,sh.nrows):
    wr.writerow(sh.row_values(rownum))

your_csv_file.close()