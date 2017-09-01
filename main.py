# coding: utf8
import hashlib
import logging
import os

from cos_python import qcloud_cos

base_name = u'/tmp/test'    # 本地上传的路径
app_id = 8527552  # 替换为用户的appid
secret_id = u'lo3215guhilh'  # 替换为用户的secret_id
secret_key = u'vhoipiljghjiphlkj;'  # 替换为用户的secret_key
region_info = "tj"  # 替换为用户的region，例如 sh 表示华东园区, gz 表示华南园区, tj 表示华北园区
cos_client = qcloud_cos.CosClient(app_id, secret_id, secret_key, region=region_info)
cos_bucket_name = u'ttttt'

# 日志配置
logging.basicConfig(level=logging.ERROR,
                    filename='/var/log/cos.log',
                    filemode='rw+',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


def create_dir(bucket, path_dir):
    dir_res = qcloud_cos.CreateFolderRequest(bucket, path_dir)
    create_set = cos_client.create_folder(dir_res)
    return create_set.get('code')


def cos_upload_poker(bucket, dst, source, insert_num=0):
    request = qcloud_cos.UploadFileRequest(bucket, dst, source, insert_only=insert_num)
    upload = cos_client.upload_file(request)
    if upload.get('code') != 0:
        # logging.error('%s 文件上传失败' % source)
        logging.error(upload)


# 计算本地计算机的哈希值,然后和远端对比, 如果一样则不上传
def CalcSha1(filepath):
    with open(filepath, 'rb') as f:
        sha1obj = hashlib.sha1()
        sha1obj.update(f.read())
        hash = sha1obj.hexdigest()
        return hash


# 计算远端的sha值
def get_stats(bucket, dst, source):
    get_file_stat = qcloud_cos.StatFileRequest(bucket, dst)
    res = cos_client.stat_file(get_file_stat)
    if res.get('code') == 0:
        code_stas = res.get('data').get('sha')
        if code_stas == CalcSha1(source):
            return True
    else:
        return False


def foreach(path):
    def get_file(y_path):
        for j in os.listdir(y_path):
            yield j
    for i in get_file(path):
        # dir = u'/'+os.path.relpath(os.path.join(path, i), start=u'/tmp/cos')
        dir = os.path.join(path, i)[len(base_name):]
        if os.path.isfile(os.path.join(path, i)):
            if not get_stats(cos_bucket_name, dir, base_name + dir):
                cos_upload_poker(cos_bucket_name, dir, base_name + dir)

        else:
            create_dir(cos_bucket_name, dir)
            foreach(os.path.join(path, i))

foreach(base_name)
