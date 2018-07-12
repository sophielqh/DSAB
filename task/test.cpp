#include "test.h"
void frequencyTest(vector<string> & v,unordered_map<string, int> & item2freq, SketchBase& sketch,const int bytesPerStr,string throughput_file_name,string frequency_file_name )
{
    string sketch_name = sketch.sketch_name;
    /*throuput test*/
    clock_t start,finish;
    start = clock();
    for(auto iter = v.begin();iter!=v.end();iter++)
        sketch.Insert(iter->c_str(), bytesPerStr);
    finish = clock();
    ofstream throughput_file;
    throughput_file.open("./result/"+throughput_file_name);
    throughput_file << "TotalNum\tTime" << endl;
    throughput_file << v.size() << "\t";
    throughput_file << double(finish-start)/CLOCKS_PER_SEC << "\t";
    throughput_file.close();

    /*accuracy test*/
    ofstream frequency_file;
    frequency_file.open("./result/"+frequency_file_name);
    for (const auto& p: item2freq) {
        frequency_file << p.second << "\t";
        frequency_file << sketch.frequencyQuery(p.first.c_str(), bytesPerStr) << "\t";
        frequency_file << endl;
    }
    frequency_file.close();
}