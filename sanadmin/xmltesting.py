import xml.etree.ElementTree as ET

source_file = open(r'C:\Users\sunkishg\Desktop\tdev_total.xml')
sgtree = ET.fromstring(source_file.read())

recods = sgtree.findall('Symmetrix/ThinDevs/Totals')
for item in recods:
    total_tracks_gb = item.find('total_tracks_gb').text
    total_alloc_tracks_gb = item.find('total_alloc_tracks_gb').text
    total_alloc_percent = item.find('total_alloc_percent').text
    print(total_tracks_gb,total_alloc_tracks_gb,total_alloc_percent)
