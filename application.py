from flask import Flask,render_template,request,jsonify,redirect,url_for
from werkzeug.utils import secure_filename
from subprocess import run,Popen
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
        upload_path = os.path.join(basepath, 'static/uploads',secure_filename(f.filename))  #注意：没有的文件夹一定要先创建，不然会提示没有该路径
        f.save(upload_path)
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
    for i in sketchList :
        filepath = './config/'+i+'.txt'
        with open(filepath,'w') as f:
            f.write('sketch='+i+'\n')
            writeConfig('sketch='+i+'\n')
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
        Popen('python3 ./result/res_simple_analyzer.py ./result/json_freq.txt',shell=True)
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

if __name__ == '__main__':
    app.run(host= '0.0.0.0',port =8086, debug=True)             #启动app的调试模式
