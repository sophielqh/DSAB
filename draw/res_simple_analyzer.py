import sys
import os
import pickle
import numpy as np
import math
import json
import re
from res_simple_grapher import draw_free

#read file ####
def load_json(filename):
    f = open(filename)
    input_str = "\n".join(f.readlines())
    input_str = re.sub(r'\\\n', '', input_str)
    input_str = re.sub(r'//.*\n', '\n', input_str)
    lt = json.loads(input_str)
    f.close()
    return lt

def read_file(name):
    with open(name) as f:
        res = []
        for line in f:
            res.append(line.split())
        names = res[0][1:]
        data = []
        for line in res[1:]:
            data.append([eval(n) for n in line])
        return names, data
    return []
#read file ####

#analyze ####
def cdf(arr, thres):
    res = [0 for thr in thres]
    for n in arr:
        for i in range(len(thres)):
            if n <= thres[i]:
                res[i] += 1
    return [r / len(arr) for r in res]

def analyze_freq_mre(r, e):
    order = np.argsort(r)
    r = np.array(r)[order] #ascending order
    e = np.array(e)[order] #ascending order
    
    r_distinct = []
    e_distinct = []
    tmp = r[0]
    stt = 0
    for i in range(len(r)):
        if i == len(r) - 1:
            r_distinct.append(r[i])
            e_distinct.append(sum(e[stt : i + 1]) / (i + 1 - stt))
            break
        if r[i + 1] != tmp:
            r_distinct.append(r[i])
            e_distinct.append(sum(e[stt : i + 1]) / (i + 1 - stt))
            tmp = r[i + 1]
            stt = i + 1
    sre = [(e_distinct[i] - r_distinct[i]) / r_distinct[i] for i in range(len(r_distinct))] #re with sigh
    re  = [abs(sre[i]) for i in range(len(r_distinct))]
    return {
        'r'   : r_distinct,
        're'  : re,
        'sre' : sre,
    }
    
def analyze_freq_cdf(r, e):
    ae = [abs(r[i] - e[i]) for i in range(len(r))]
    re = [ae[i] / r[i] for i in range(len(r))]
    ae_cdf = cdf(ae, list(range(10)))
    re_cdf = cdf(re, [n / 10 for n in range(10)])
    return {
        'ae-cdf': ae_cdf,
        're-cdf': re_cdf,
    }

def analyze_freq(r, e):    
    ae = [abs(r[i] - e[i]) for i in range(len(r))]
    re = [ae[i] / r[i] for i in range(len(r))]
    aae = (sum(ae) / len(ae))
    are = (sum(re) / len(re))
    acc = (len([aei for aei in ae if aei == 0]) / len(ae))

    return {
        'aae': aae,
        'are': are,
        'acc': acc,
    }

def analyze_topk(rid, rf, eid, ef):
    rid = rid[ : len(eid)]
    recall = len([p for p in rid if p in eid])/ len(eid)
    return {
        'recall': recall,
    }

def analyze_throughput(n, t):
    throughput = n[0] / t[0];
    return {
        'throughput': throughput,
    }
#analyze ####
  
def read_topk(lines, exact):
    names, data = read_file(exact)
    rid, rf = [dat[0] for dat in data], [dat[1] for dat in data]

    reses = []
    for line in lines:
        res = []
        for fn in line:
            names, data = read_file(fn)
            d0, d1 = [dat[0] for dat in data], [dat[1] for dat in data]
            res.append(analyze_topk(rid, rf, d0, d1))
        reses.append(res);
    return reses
    
def read_freq(lines):
    reses = []
    for line in lines:
        res = []
        for fn in line:
            names, data = read_file(fn)
            d0, d1 = [dat[0] for dat in data], [dat[1] for dat in data]
            res.append(analyze_freq(d0, d1))
        reses.append(res);
    return reses


arg = load_json(sys.argv[1])
if arg['type'] == 'topk':
    reses = read_topk(arg['lines'], arg['exact'])
    draw_free(arg['xs'], reses, arg['output'])
elif arg['type'] == 'freq':
    reses = read_freq(arg['lines'])
    draw_free (arg['xs'], reses, arg['output'])