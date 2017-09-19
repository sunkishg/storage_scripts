import csv
with open('arrays.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print(row['array'], row['vendor'])
