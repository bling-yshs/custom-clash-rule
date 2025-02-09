import requests
import os
import sys
import json


def get_token(username, password):
    url = "https://pan.ystech.top/api/auth/login"

    payload = json.dumps({
        "username": username,
        "password": password
    })

    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Host': 'pan.ystech.top',
        'Connection': 'keep-alive'
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        response_data = response.json()
        if response_data.get('code') == 200 and 'data' in response_data and 'token' in response_data['data']:
            return response_data['data']['token']
        else:
            print("获取token失败:", response.text)
            sys.exit(1)
    except Exception as e:
        print("获取token时发生错误:", str(e))
        sys.exit(1)


def upload_file(file_path, remote_path, token):
    url = "https://pan.ystech.top/api/fs/put"

    # 读取文件内容作为payload
    with open(file_path, 'rb') as file:
        payload = file.read()

    headers = {
        'Authorization': token,
        'File-Path': remote_path,
        'As-Task': 'true',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/octet-stream',
        'Accept': '*/*',
        'Host': 'pan.ystech.top',
        'Connection': 'keep-alive'
    }

    try:
        response = requests.put(url, headers=headers, data=payload)
        print(f"上传文件 {file_path} 到 {remote_path}")
        print(f"响应: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"上传文件 {file_path} 失败: {str(e)}")
        return False


def main():
    # 检查命令行参数
    if len(sys.argv) < 5:
        print("使用方法: python up.py <用户名> <密码> <本地文件夹路径> <远程目录路径>")
        print("示例: python up.py admin password /files /share")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    local_folder = sys.argv[3]
    remote_base_dir = sys.argv[4]

    # 检查文件夹是否存在
    if not os.path.exists(local_folder):
        print(f"错误: 文件夹 '{local_folder}' 不存在!")
        sys.exit(1)

    # 获取token
    print("正在获取token...")
    token = get_token(username, password)
    print("token获取成功!")

    # 处理远程路径格式
    if not remote_base_dir.startswith('/'):
        remote_base_dir = '/' + remote_base_dir
    if not remote_base_dir.endswith('/'):
        remote_base_dir += '/'
    
    # 获取本地文件夹名称并添加到远程路径
    folder_name = os.path.basename(os.path.normpath(local_folder))
    remote_base_dir = remote_base_dir + folder_name + '/'

    # 遍历文件夹
    success_count = 0
    fail_count = 0

    for root, dirs, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)

            # 计算相对路径，用于构建远程路径
            rel_path = os.path.relpath(local_path, local_folder)
            remote_path = remote_base_dir + rel_path.replace('\\', '/')

            if upload_file(local_path, remote_path, token):
                success_count += 1
            else:
                fail_count += 1

    print(f"\n上传完成!")
    print(f"成功: {success_count} 个文件")
    print(f"失败: {fail_count} 个文件")


if __name__ == "__main__":
    main()
