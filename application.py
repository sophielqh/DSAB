# -*- coding:UTF-8 -*-
from flask import Flask,render_template,request,jsonify,redirect,url_for
from werkzeug.utils import secure_filename
from subprocess import Popen
import  os
import json

app = Flask(__name__)     #创建一个wsgi应用
#to store sketches choosen by users
sketchList = []
writeList = []
task="frequency"
metrics = ""
numOfXinterval =0
numOfLines=0
fileList = []

@app.route('/')           #添加路由：根
def index():
    return render_template('homepage.html')

@app.route('/dataset')           #add route dataset
def dataset():
    with open('existingDataset.json', 'r') as f:
        json_info = json.load(f)
        for i in json_info['datasetArray']:
            if os.path.exists('./dataset_temp/' + i["name"]):
                i["location"] = "local"
            else:
                i["location"] = "cloud"
    with open('existingDataset.json', 'w') as f:
        json.dump(json_info, f)

    return render_template('dataset.html')

@app.route('/existing',methods=['POST','GET'])
def datasetDisplay():

    filepath = 'existingDataset.json'
    with open(filepath, 'r') as f:
        json_info = json.load(f)
    return jsonify(json_info)

@app.route('/uploadNewSketch',methods=['POST','GET'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        upload_path = os.path.join(basepath, 'sketch',secure_filename(f.filename))  #注意：没有的文件夹一定要先创建，不然会提示没有该路径
        f.save(upload_path)

        '''
        Here Need To Process New Sketch
        1) modify sketchlist
        2) compiling
        '''

        return redirect(url_for('upload'))
    return render_template('uploadNewSketch.html')

@app.route('/choosenSketch',methods=['POST','GET'])
def choosenSketch():
    '''
    user has finished choosing sketches to be tested
    '''
    clearConfig('sketch')
    global  sketchList
    sketchList=request.form.getlist('sketch')
    tasks = ['freq', 'topk']

    '''
    Here need to get task type from web


    '''


    for sketch in sketchList:
        filepath = './config/' + sketch +'.txt'
        with open(filepath,'w') as f: #clear old content
            f.write('sketch='+ sketch +'\n')
            writeConfig('sketch='+ sketch +'\n')
    for task in tasks: #add supported task
        for sketch in request.form.getlist(task):
            filepath = './config/' + sketch +'.txt'
            with open(filepath,'a+') as f:
                f.write('task=' + task + '\n')
    return render_template('choosenSketch.html')

@app.route('/choosenDataset',methods=['POST','GET'])
def choosenDataset():
    '''
    user has finished choosing dataset to be tested
    '''
    clearConfig('dataset')
    if request.method  == 'POST':
        datasetList = request.form.getlist('dataset')
        for i in datasetList:
            writeConfig('dataset='+i)

        dataset_path = './dataset_temp'
        if not os.path.exists(dataset_path):
            os.makedirs(dataset_path)
        if not os.path.exists(dataset_path + '/zipf'):
            os.makedirs(dataset_path + '/zipf')
        for d in datasetList:
            dataset_file = dataset_path + '/' + d
            if not os.path.exists(dataset_file):
                cloud_download(dataset_file, d)
                with open('existingDataset.json', 'r') as f:
                    json_info = json.load(f)
                    for i in json_info['datasetArray']:
                        if i["name"] == d:
                            i["location"] = "local"
                with open('existingDataset.json', 'w') as f:
                    json.dump(json_info, f)

        return redirect('/')


@app.route('/distribution', methods=['POST', 'GET'])
def distributionDisplay():
    if request.method == 'POST':
        filepath = 'existingDistribution.json'
        with open(filepath, 'r') as f:
            json_info = json.load(f)
        return jsonify(json_info)
    else:
        return render_template('distribution.html')

@app.route('/choosenDistribution',methods=['POST','GET'])
def choosenDistribution():
    '''
    user has finished choosing distribution to be generated
    '''
    global  distributionList
    distributionList=request.form.getlist('distribution')
    return render_template('choosenDistribution.html')

@app.route('/distributionParaShow',methods=['POST','GET'])
def distributionParaShow():
    '''
    user has finished choosing distributions to be generated
    now they need to set parameters
    '''
    if request.method == 'POST':
        filepath = 'existingDistribution.json'
        with open(filepath, 'r') as f:
            json_info = json.load(f)
        upload_json_info = {}
        upload_json_info['distributionArray'] = []
        for i  in range(len(json_info['distributionArray'])):
            if json_info['distributionArray'][i]['name'] in distributionList:
               upload_json_info['distributionArray'].append(json_info['distributionArray'][i])
        return jsonify(upload_json_info)

@app.route('/setDistributionPara',methods=['POST','GET'])
def setDistributionPara():
    '''
    distribution parameters settings are returned
    datasets are generated
    '''
    import json
    global  distributionList
    if request.method == 'POST':
        filepath = 'existingDistribution.json'
        with open(filepath, 'r') as f:
            json_info = json.load(f)

        for i in range(len(distributionList)):
            for j in range(len(json_info['distributionArray'])):
                distributionName = json_info['distributionArray'][j]['name']
                if distributionList[i] == distributionName:
                    writeConfig('dataset='+ distributionName)
                    break

            para  = request.form.get("parameter")
            total = request.form.get("total")
            dist = request.form.get("distinct")
            writeConfig('_' + str(float(para)))
            writeConfig('_' + total)
            writeConfig('_' + dist)

            #生成对应的数据集
            minFreq, maxFreq = generate_dataset(distributionName, float(para), int(total), int(dist))

            datasetName = distributionName + '_' + str(float(para)) + '_' + total + '_' + dist + '.dat'
            with open('existingDataset.json', 'r') as f:
                json_info = json.load(f)
                json_info['datasetArray'].append({"name": datasetName, "totalNum": total,
                                                "distinctNum": dist, "minFrequency": str(minFreq),
                                                "maxFrequency": str(maxFreq), "bytePerItem": '4',
                                                "location": "local"})
            with open('existingDataset.json', 'w') as f:
                json.dump(json_info, f)
        return redirect('/')

@app.route('/sketchParaShow',methods=['POST','GET'])
def sketchParaShow():
    '''
    user has finished choosing sketches to be tested
    now they need to set parameters
    '''
    if request.method == 'POST':
        filepath = 'existingSketch.json'
        with open(filepath, 'r') as f:
            json_info = json.load(f)
        upload_json_info = {}
        upload_json_info['sketchArray'] = []
        for i  in range(len(json_info['sketchArray'])):
            if json_info['sketchArray'][i]['name'] in sketchList:
               upload_json_info['sketchArray'].append(json_info['sketchArray'][i])
        return jsonify(upload_json_info)

@app.route('/setSketchPara',methods=['POST','GET'])

def setSketchPara():
    '''
    sketch parameters settings are returned
    :return:
    '''
    paraDict = {}
    global  sketchList
    global  writeList
    global  fileList
    if request.method == 'POST':
        filepath = 'existingSketch.json'
        with open(filepath, 'r') as f:
            json_info = json.load(f)
        for i in range(len(sketchList)):
            sketchName = json_info['sketchArray'][i]['name']
            paraList =[]
            for p in json_info['sketchArray'][i]['parameterList']:
                low = sketchName+'_'+p+'_lowerbound'
                high =  sketchName+'_'+p+'_upperbound'
                interval =  sketchName+'_'+p+'_interval'
                tmpList = []
                lowValue  = float(request.form.get(low))
                highValue = float(request.form.get(high))
                intervalValue = float(request.form.get(interval))
                while(lowValue<=highValue):
                    tmpList.append(p+'='+str(lowValue))
                    lowValue += intervalValue
                paraList.append(tmpList)
            writeList = []
            writeSketchConfig(paraList,0,'')
            with open('./config/'+sketchName+'.txt','a+') as f:
                for i in writeList:
                    f.write(i+'\n')

                    filename ="accurate_"+sketchName
                    tmp = i.split()
                    for j in tmp:
                        filename += "+"+j
                    filename += '.txt'
                    fileList.append(filename)
        #os.system('./AAA.out')
        Popen('./AAA.out > ./result/process.txt',shell =True)
        return redirect('/wait')

@app.route('/wait',methods=['POST','GET'])
def wait():
    global  writeList
    if request.method == 'POST':
        filepath = './result/process.txt'
        with open(filepath,'r') as  f:
            lines = f.readlines()
            json_info ={}
            json_info['process']  = int(float(len(lines))/len(writeList) * 100)
            return jsonify(json_info)
    else:
        return render_template('wait.html')

@app.route('/sketch',methods=['POST','GET'])
def sketchDisplay():
    if request.method == 'POST':
        filepath = 'existingSketch.json'
        with open(filepath, 'r') as f:
            json_info = json.load(f)
        return jsonify(json_info)
    else:
        return render_template('sketch.html')

@app.route('/graph')           #add route dataset
def drawingGraph():
    return render_template('graph.html')


@app.route('/graphSetting',methods=['POST','GET'])           #add route dataset
def graphSetting():
    if request.method == 'POST':
        json_result = {}
        filepath = 'existingMetrics.json'
        with open(filepath, 'r') as f:
            json_info = json.load(f)
            json_result['metrics'] = json_info[task]
            print(json_result['metrics'])
        return jsonify(json_result)


@app.route('/selectPoint',methods=['POST','GET'])
def selectPoint():
    global  metrics,numOfXinterval,numOfLines
    if request.method == 'POST':
        metrics = request.form.get('metrics')
        numOfXinterval = int(request.form.get('xscale'))
        numOfLines = int(request.form.get('lines'))
    return render_template('choosenPoint.html')

@app.route('/choosingDrawPoint',methods=['POST','GET'])
def offerDrawPoint():
    global  numOfXinterval,numOfLines,fileList
    if request.method == 'POST':
        json_info ={}
        json_info['numOfXinterval'] =numOfXinterval
        json_info['numOfLines'] = numOfLines
        json_info['fileList'] = fileList
        return jsonify(json_info)

@app.route('/draw',methods=['POST','GET'])
def draw():
    '''
    {
    "type": "freq",
    "xs": [1, 2, 3],
    "lines": [ ["frequency_asketch_test1.dat_hashnum4_bitPerCounter16_counterPerArray65344.txt", "frequency_asketch_test2.dat_hashnum4_bitPerCounter16_counterPerArray65344.txt", "frequency_asketch_test3.dat_hashnum4_bitPerCounter16_counterPerArray65344.txt"],
               ["frequency_cmmsketch_test1.dat_hashnum4_bitPerCounter16_counterPerArray65536.txt", "frequency_cmmsketch_test2.dat_hashnum4_bitPerCounter16_counterPerArray65536.txt", "frequency_cmmsketch_test3.dat_hashnum4_bitPerCounter16_counterPerArray65536.txt"]
             ],
    "output": "test.pdf"
}
    :return:
    '''
    '''
    :return:
    '''
    global  numOfXinterval,numOfLines
    if request.method == 'POST':
        json_info = {}
        json_info['type'] = 'freq'

        '''
        Here you need to  get graph metrics type



        '''

        json_info['xs'] =[ i+1 for i in range(numOfXinterval)]
        tmpList = []
        json_info['lines'] = [] #init lines
        j = 0
        for i in range(numOfXinterval*numOfLines):
            tmpList.append('./result/'+request.form.get(str(i)))
            j += 1
            if j == numOfXinterval:
                json_info['lines'].append(tmpList)
                tmpList = []
                j = 0
        json_info['output'] = 'zcxy.pdf'
        print(json_info)
        json_point_path = './result/json_freq.txt'
        with open(json_point_path,'w') as f:
            json.dump(json_info,f)
        p = Popen('python3 ./result/res_simple_analyzer.py ./result/json_freq.txt',shell=True)
        p.wait() #wait for drawing to finish
        return redirect('/graphShow')

@app.route('/graphShow',methods=['POST','GET'])
def graphShow():
    return  render_template('graphShow.html')



def writeSketchConfig(paraList,idx,paraStr):
    global writeList
    if(idx==len(paraList)-1):
        for i in paraList[idx]:
            writeList.append(paraStr+i)
    else:
        for i in paraList[idx]:
            writeSketchConfig(paraList,idx+1,paraStr+i+' ')

def writeConfig(s):
    configFilePath = './config/config.txt'
    with open(configFilePath,'a+') as f:
        f.write(s+'\n')
def clearConfig(s): #filter out configs starting with s
    configFilePath = './config/config.txt'
    with open(configFilePath, 'r') as f:
        lines = [line.strip() for line in f if not line.startswith(s)]
    lines = [line + '\n' for line in lines if len(line) > 1] #remove empty lines
    with open(configFilePath, 'w') as f:
        f.writelines(lines)

def cloud_download(local_path, cloud_path):
    from qcloud_cos import CosConfig
    from qcloud_cos import CosS3Client
    import sys
    import logging

    #设置用户配置
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    secret_id = 'AKIDTzTsGYhBOYceduNNXbfeXL3No494wOwR'
    secret_key = 'Xv8qNl5JSeqw2660rdEiCYk4LSOEwT5d'
    region = 'ap-beijing'
    token = ''
    config = CosConfig(Secret_id=secret_id, Secret_key=secret_key, Region=region, Token=token)
    #获取客户端对象
    client = CosS3Client(config)

    #文件下载
    response = client.get_object(
        Bucket = 'test01-1257045059',
        Key = cloud_path,
    )
    response['Body'].get_stream_to_file(local_path)

def generate_dataset(distriName, para, tot, dis):
    import sys
    import random
    from scipy.stats import powerlaw
    import numpy as np
    import math

    bytePerStr = 4
    filepath = "./dataset_temp/" + distriName + '_'+str(para) + '_'+str(tot) + '_'+str(dis) + ".dat"
    filenum = 1000
    filesize = tot // filenum
    if (os.path.exists("./dataset_temp") == False):
        os.mkdir("./dataset_temp")
    if (os.path.exists("./dataset_temp/temp") == False):
        os.mkdir("./dataset_temp/temp")

    def powerlaw(N, s):
        res = []
        base = 0.0
        for n in range(1, N + 1):
            t = 1 / (n ** s)
            base += t
            res.append(t)
        return [r / base for r in res]

    def weibull(N, p, k):
        res = []
        for n in range(0, N, 1):
            power1 = n ** k
            p1 = (1 - p) ** power1
            power2 = (n + 1) ** k
            p2 = (1 - p) ** power2
            res.append(p1 - p2)
        return res

    def random_bytes(byts):
        import random
        import string

        st = ''
        for j in range(byts):
            st += random.choice(string.printable[:-5])
        b = bytes(st, encoding = 'utf-8')
        return b

    def gen_random_strings(len, byts):
        strs = set()
        res = []
        for i in range(len):
            s = random_bytes(byts)
            while s in strs:
                s = random_bytes(byts)
            res.append(s)
            strs.add(s)
            print(s)
        return res

    def gen(freqs, byts):
        strs = gen_random_strings(len(freqs), byts)
        chs = [i for i in range(len(freqs))]
        for fileno in range(0, filenum - 1):
            temp_filepath = "./dataset_temp/temp/" + str(fileno) + ".dat"
            with open(temp_filepath, "ab") as f:
                for j in range(0, filesize):
                    p = random.randint(0, len(chs) - 1)
                    pos = chs[p]
                    f.write(strs[pos])
                    if(freqs[pos] > 0):
                        freqs[pos] -= 1
                    if freqs[pos] == 0:
                        del chs[p]
                f.close()

        last_filesize = 0
        fileno = filenum - 1
        temp_filepath = "./dataset_temp/temp/" + str(fileno) + ".dat"
        with open(temp_filepath, "ab") as f:
            while len(chs) != 0:
                p = random.randint(0, len(chs) - 1)
                pos = chs[p]
                f.write(strs[pos])
                last_filesize += 1
                if(freqs[pos] > 0):
                    freqs[pos] -= 1
                if freqs[pos] == 0:
                    del chs[p]

    def read_str(fp, sl, bytesNum):
        st = fp.read(bytesNum)
        while st:
            sl.append(st)
            st = fp.read(bytesNum)

    def read_shuffle_write(sl, fp1, fp2, bytesNum):
        with open(fp1, "rb") as f1:
            read_str(f1, sl, bytesNum)
            f1.close()
        with open(fp2, "rb") as f2:
            read_str(f2, sl, bytesNum)
            f2.close()
        random.shuffle(sl)
        with open(fp1, "wb") as f1:
            for j in range(filesize):
                f1.write(sl[j])
            f1.close()
        with open(fp2, "wb") as f2:
            for j in range(filesize, len(sl)):
                f2.write(sl[j])
            f2.close()

    def front_tail_shuffle(bytesNum):
        frontfile = [i for i in range(100, 200)]
        tailfile = [i for i in range(900, 1000)]
        random.shuffle(frontfile)
        random.shuffle(tailfile)
        for i in range(0, 100):
            str_list = []
            frontfilepath = "./dataset_temp/temp/" + str(frontfile[i]) + ".dat"
            tailfilepath = "./dataset_temp/temp/" + str(tailfile[i]) + ".dat"
            read_shuffle_write(str_list, frontfilepath, tailfilepath, bytesNum)

    def whole_shuffle(bytesNum):
        file1 = random.randint(0, filenum - 1)
        file2 = random.randint(0, filenum - 1)
        while file2 == file1:
            file2 = random.randint(0, filenum - 1)
        str_list = []
        filepath1 = "./dataset_temp/temp/" + str(file1) + ".dat"
        filepath2 = "./dataset_temp/temp/" + str(file2) + ".dat"
        read_shuffle_write(str_list, filepath1, filepath2, bytesNum)

    if distriName == 'zipf' or distriName == 'powerlaw':
        props = powerlaw(dis, para)
    elif distriName == 'weibull':
        pa = 0.3
        props = weibull(dis, pa, para)

    freq = [math.ceil(prop * tot) for prop in props]
    minFreq = min(freq)
    maxFreq = max(freq)
    gen(freq, bytePerStr)
    front_tail_shuffle(bytePerStr)
    for i in range(100):
        whole_shuffle(bytePerStr)
    file_list = [i for i in range(filenum)]
    random.shuffle(file_list)
    with open(filepath, "wb") as f:
        for i in range(filenum):
            readfilepath = "./dataset_temp/temp/" + str(file_list[i]) + ".dat"
            with open(readfilepath, "rb") as rf:
                st = rf.read(bytePerStr)
                while st:
                    f.write(st)
                    st = rf.read(bytePerStr)
                rf.close()
        f.close()
    for fileno in range(0, filenum):
        temp_filepath = "./dataset_temp/temp/" + str(fileno) + ".dat"
        os.remove(temp_filepath)
    os.rmdir("./dataset_temp/temp")

    return(minFreq, maxFreq)

if __name__ == '__main__':
    app.run(host= '0.0.0.0',port =8086, debug=True)             #启动app的调试模式
