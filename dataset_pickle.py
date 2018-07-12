import pickle

file_list = ['kosarak.dat', 'formatted00.dat', 'webdocs00.dat', './zipf/000.dat',
            './zipf/003.dat', './zipf/006.dat', './zipf/009.dat', './zipf/012.dat',
            './zipf/015.dat', './zipf/018.dat', './zipf/021.dat', './zipf/024.dat',
            './zipf/027.dat', './zipf/030.dat']
byte_per_str = 4
#数据集基本信息列表为[filepath，totalnum, distinctnum, maxfreq, minfreq]
dataset_info = []

#读取数据流，element:frequency存储为字典
def file2dict(bytesNum, filePath):
    with open(filePath, "rb") as f:
        s = dict()
        st = f.read(bytesNum)
        while st:
            s[st] = s.get(st, 0) + 1
            st = f.read(bytesNum)
        return s

#统计数据流基本信息，存储为列表
def dict2list(sdict):
    ss = [sdict[key] for key in sdict]
    tot = 0
    maxFreq = 0
    minFreq = 100000
    uniq = len(ss)
    for sss in ss:
        tot += sss
        maxFreq = max(maxFreq, sss)
        minFreq = min(minFreq, sss)
    dataset_info.append([file, tot, uniq, maxFreq, minFreq])

for file in file_list:
    s = file2dict(byte_per_str, file)
    dict2list(s)

#将基本信息写入pickle文件
with open('dataset_info.pkl', 'wb') as f:
    pickle.dump(dataset_info, f)

#从pickle文件中读取基本信息
with open('dataset_info.pkl', 'rb') as rf:
    print(pickle.load(rf))
