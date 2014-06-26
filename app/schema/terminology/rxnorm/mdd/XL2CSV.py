__author__ = 'dave'
import sys, os
lib_path = os.path.abspath('../nadac/xlrd-0.9.3')
sys.path.append(lib_path)
import xlrd
import csv

mdd=''

#find the MDD file
for file in os.listdir(os.path.abspath('.')):
    if file.__contains__(".xls"):
        mdd=os.path.abspath('.')+'/'+file

#convert the file to csv
wb = xlrd.open_workbook(mdd)
sh = wb.sheet_by_name('Sheet1')
your_csv_file = open('MDD.csv', 'wt')
wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)
for rownum in range (2,sh.nrows):
    wr.writerow(sh.row_values(rownum))

your_csv_file.close()
