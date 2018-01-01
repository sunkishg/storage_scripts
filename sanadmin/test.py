from pprint import pprint
luns = "10*512GB,20*256GB,16*4GB,4*32GB,1x1mb,50x100GB"
sg_list = ['testserver01_SG,P,13,1668,none,none,Yes,1668.0,1664.0,100', 'testserver01_g_SG,C,3,96,Gold,DSS,Yes,{32: 3}', 'testserver01_g2_SG,C,10,1572,Platinum,OLTP,Yes,{256: 6, 9: 4}', 'testserver02_SG,P,13,1668,none,none,Yes,1668.0,1662.4,100', 'testserver02_g_SG,C,3,96,Gold,DSS,Yes,{32: 3}', 'testserver02_g2_SG,C,10,1572,Platinum,OLTP,Yes,{256: 6, 9: 4}', 'testserver03_SG,P,13,1668,none,none,Yes,1668.0,1661.4,100', 'testserver03_g_SG,C,3,96,Gold,DSS,Yes,{32: 3}', 'testserver03_g2_SG,C,10,1572,Platinum,OLTP,Yes,{256: 6, 9: 4}', 'testserver04_SG,P,13,1668,none,none,Yes,1668.0,1666.4,100', 'testserver04_g_SG,C,3,96,Gold,DSS,Yes,{32: 3}', 'testserver04_g2_SG,C,10,1572,Platinum,OLTP,Yes,{256: 6, 9: 4}', 'testserver05_g_SG,S,1,26,none,none,No,26.0,0.0,0']

luns_dict = dict()
luns_list = luns.lower().split(',')
for l in luns_list:
    data = l.replace('x','*').split('*')
    lun_nos = data[0]
    size = data[1]
    if 'gb' in size:
        lun_size = size.split('gb')[0]
    elif 'g' in size:
        lun_size = size.split('g')[0]
    elif 'tb' in size:
        lun_size = int(size.split('tb')[0])//1024
    elif 't' in size:
        lun_size = int(size.split('t')[0])//1024
    elif 'mb' in size:
        lun_size = int(size.split('mb')[0]) * 1024
    elif 'm' in size:
        lun_size = int(size.split('m')[0]) * 1024
    else:
        lun_size = int(size.split('m')[0]) * 1024

    luns_dict[lun_nos] = lun_size

pprint(luns_dict)
# pprint(sg_list)
# host = 'testserver01'
host = 'Govardhan'
default_storage_group = " "
remaing_luns = luns_dict.copy()
for k,v in luns_dict.items():
    for sg_line in sg_list:
        if not host in sg_line: continue
        data = sg_line.split(',')
        if data[1] == 'S':
            storage_group = data[0]
            default_storage_group = data[0]
        elif data[1] == 'P':
            pass
        elif data[1] == 'C':
            if data[4] == 'Gold' and data[5] == 'DSS':
                default_storage_group = data[0]
            if str(v) in sg_line:
                print("Create dev count={0},size={1} GB sg={2}, emulation=FBA,  config=tdev;".format(k,v,data[0]))
                remaing_luns.pop(k)
        else:
            print("Storage group not found in the array")


if len(remaing_luns) > 0 and not default_storage_group == " ":
    print("##not found a matching SG for the following Luns, selecting default Storage group##")
    for k,v in remaing_luns.items():
        print("Create dev count={0},size={1} GB sg={2}, emulation=FBA,  config=tdev;".format(k, v, default_storage_group))
