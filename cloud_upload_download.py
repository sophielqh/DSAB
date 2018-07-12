from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging
import time

#设置用户配置
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

secret_id = 'AKIDTzTsGYhBOYceduNNXbfeXL3No494wOwR'
secret_key = 'Xv8qNl5JSeqw2660rdEiCYk4LSOEwT5d'
region = 'ap-beijing'
token = ''
config = CosConfig(Secret_id=secret_id, Secret_key=secret_key, Region=region, Token=token)
#获取客户端对象
client = CosS3Client(config)

#文件上传，速度大约100M/min
#待上传文件的本地路径
input_path = './zipf/030.dat'
#文件上传后在云盘存储桶中的路径
upload_path = './zipf/030.dat'
#start_time = time.time()
with open(input_path, 'rb') as fp:
    response = client.put_object(
        Bucket = 'test01-1257045059',
        Body = fp,
        Key = upload_path,
    )
print(response['ETag'])
#end_time = time.time()
#print(end_time - start_time)

#文件下载
#文件下载后的本地路径
output_path = './cloudTest/formatted00.dat'
#待下载文件在云盘存储桶中的路径
download_path = 'formatted00.dat'
#start_time = time.time()
response = client.get_object(
    Bucket = 'test01-1257045059',
    Key = download_path,
)
response['Body'].get_stream_to_file(output_path)
#end_time = time.time()
#print(end_time - start_time)




