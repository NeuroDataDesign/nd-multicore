import csv
import glob

centroids = []

for csv_file in glob.glob('process_folder/*.csv'):
    csv_content = open(csv_file).read()
    csv_lines = csv_content.strip().split('\n')
    for pt in csv_lines:
        pts = pt.split(',')
        centroids.append([int(pts[0]), int(pts[1]), int(pts[2])])

print(len(centroids))
