#include "../dataset/StreamData.h"
#include "../sketch/sketchList.h"
#include <fstream>
#include <sstream>
#include <string>
#include <iostream>
#include <set>
#include "test.h"
using namespace std;

int main(int argc, char *argv[]) {
    
    ifstream config("./config/config.txt");
    string s;
    set<string> datasrc;
    set<string> sketch;
    while (config>>s)
    {
        int l = s.length();
        if(l>0)
        {
            int a = s.find("dataset=");
            if(a!=-1)
            {
                string tmp(s,a+8,l-a-8);
                datasrc.insert(tmp);
                continue;

            }
            a =s.find("sketch=");
            if(a!=-1)
            {
                string tmp(s,a+7,l-a-7);
                sketch.insert(tmp);
            }
        }
    }
    auto i = datasrc.begin();
    for(;i!=datasrc.end();++i)
    {
        const int bytesPerStr = 4;
        string datasetName = *i;
        StreamData dat(datasetName.c_str(), bytesPerStr);

        unordered_map<string, int> item2freq;
        unordered_map<string, int> item2idx;

        int idx =0;
        char str[bytesPerStr];
        vector<string> v;
        while (dat.GetNext(str))
        {
            v.push_back(string(str, bytesPerStr));
            ++item2freq[string(str, bytesPerStr)];
            item2idx[string(str, bytesPerStr)]= idx++;
        }
        auto j = sketch.begin();
        for (; j!=sketch.end(); ++j)
        {
            SketchBase* player = (SketchBase*)ClassFactory::getInstance().getClassByName(*j);
            set<string> task;
            ifstream para("./config/"+*j+".txt");
            string s;
            getline(para,s);
            while (getline(para,s))
            {
                int a=s.find("task=");
                if(a!=-1)
                {
                    //read task lines
                    string tmp(s,a+5,s.length()-a-5);
                    task.insert(tmp);
                    continue;
                }
                
                string throughputFile = "throughput_"+*j;
                string accFile = "accurate_"+*j;
                while (true)
                {
                    int indent = s.find(' ');
                    string oneSeg;
                    if(indent!=-1)
                        oneSeg.assign(s,0,indent);
                    else
                        oneSeg = s;
                    int equPos =oneSeg.find('=');
                    string name(s,0,equPos);
                    string valueStr(s,equPos+1,oneSeg.length()-equPos-1);
                    throughputFile +="+"+name+"="+valueStr;
                    accFile +="+"+name+"="+valueStr;
                    double value = stod(valueStr);
                    player->parameterSet(name,value);
                    if(indent!=-1)
                        s.assign((const string &)s,indent+1,s.length()-indent-1);
                    else
                        break;
                }
                cout<<"ok"<<endl;
                player->init();
                frequencyTest(v,item2freq,*player,bytesPerStr,throughputFile+".txt",accFile+".txt");
            }
            
        }
    }
    return 0;
}
