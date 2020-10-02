# encoding:utf-8

import requests
import base64
import os
import json
import sys
import random
import ssl
#防止https证书校验不正确
ssl._create_default_https_context = ssl._create_unverified_context

'''
# 保证兼容python2以及python3
IS_PY3 = sys.version_info.major == 3
if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.parse import quote_plus
else:
    import urllib2
    from urllib import quote_plus
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib import urlencode
'''
##############使用python3
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.parse import quote_plus
IS_PY3 = sys.version_info.major == 3
os.environ['NO_PROXY'] = 'aip.baidubce.com'#设置

'''
地标识别
'''
API_KEY = ''#通过新建任务获取

SECRET_KEY = ''#不是直接在帐户下申请密钥，是通过新建的地标识别任务获取

IMAGE_RECOGNIZE_URL = "https://aip.baidubce.com/rest/2.0/image-classify/v1/landmark"

train_path = ''#训练数据

"""  TOKEN start """
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'


"""
    获取token
"""
def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print(err)
    if (IS_PY3):
        result_str = result_str.decode()

    result = json.loads(result_str)

    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'brain_all_scope' in result['scope'].split(' '):
            print ('please ensure has check the  ability')
            exit()
        return result['access_token']
    else:
        print ('please overwrite the correct API_KEY and SECRET_KEY')
        exit()
"""
    读取文件
"""
def read_file(image_path):
    f = None
    try:
        f = open(image_path, 'rb')
        return f.read()
    except:
        print('read image file fail')
        return None
    finally:
        if f:
            f.close()

"""
    调用远程服务
"""
def request(url, data):
    req = Request(url, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()
        if (IS_PY3):
            result_str = result_str.decode()
        return result_str
    except  URLError as err:
        print(err)

processed_id = []
txt_path2 = './batch_API_result_full1.txt'#写入识别结果的记录
txt_f2 = open(txt_path2, 'r')
txt_path3 = './processed_id.txt'#识别成功的结果id记录文件
txt_f3 = open(txt_path3, 'w')

for lines in txt_f2:
    if lines.split(',')[0] not in processed_id:
        processed_id.append(lines.split(',')[0])

for element in processed_id:
    txt_f3.write('{}\n'.format(element))

txt_path = './batch_API_result_full.txt'#后面统计识别的结果的时候用到的
txt_f = open(txt_path, 'w')
full_list = os.listdir(train_path)
print(len(full_list))
print(len(processed_id))
landmark_id_list = list(set(full_list) - set(processed_id))
print(len(landmark_id_list))



"""
    识别代码的核心
"""
'''
for landmark_id in landmark_id_list:
    landmark_num = len(os.listdir(os.path.join(train_path, landmark_id)))
    landmark_img_list = os.listdir(os.path.join(train_path, landmark_id))
    if landmark_num > 5:
        sample_list = random.sample(landmark_img_list, 5)
    else:
        sample_list = landmark_img_list
    print(len(sample_list))

    for sample_img in sample_list:
        f = open(os.path.join(os.path.join(train_path, landmark_id),sample_img), 'rb')
        file_content = f.read()

        token = fetch_token()
        request_url = IMAGE_RECOGNIZE_URL + "?access_token=" + token

        response = request(request_url, urlencode(
            {
                'image': base64.b64encode(file_content),
                'top_num': 1
            }))
        result_json = json.loads(response)#字典格式
        landmark_dic = {key: value for key, value in result_json.items() if key == 'result'}
        landmark_msg = landmark_dic.values()
        txt_f.write('{},{},{}'.format(landmark_id, sample_img, landmark_msg))
        txt_f.write('\n')
        print('{},{},{}'.format(landmark_id, sample_img, landmark_msg))
    print('finish No.{} landmark'.format(landmark_id))
'''

"""
    一些处理说明
"""
"""
地标样本数量分布极不均匀,gldv1每类地标从1~5000+张图片变化
样本数量5个以上的随机出五张图进行识别，5个以下的全部识别
识别结果包括中文外文、识别失败或识别为空
如何构造一个严密的判别逻辑（！）
识别结果：11,114个识别成功，3837个未识别或识别失败
"""


"""
    严密的判别逻辑
"""
"""
是否全空/失败
↓
按(values, counts)，判counts345成功
↓
Values出现两个2次，判失败；一个2次，判成功
这里要注意先2后3，先2后1的区分
↓
Values出现一个1次，判成功；出现一次的个数等于无重复结果的个数，判失败
"""