#!/usr/bin/env python3
"""调用修复端点来修复数据库schema"""
import requests
import json

# API配置
BASE_URL = 'http://localhost:5000'
# 假设你已经登录，使用admin账号的token
# 如果没有token，需要先登录

def fix_schema():
    """调用修复端点"""
    url = f'{BASE_URL}/api/fix-schema'
    
    # 如果需要认证，添加 token
    # headers = {'Authorization': f'Bearer {token}'}
    headers = {'Content-Type': 'application/json'}
    
    print('正在调用修复端点...')
    print(f'URL: {url}')
    
    try:
        # 先尝试不带认证
        response = requests.post(url, headers=headers)
        
        print(f'\nStatus Code: {response.status_code}')
        print(f'Response:')
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            print('\n✅ 修复成功！')
        elif response.status_code == 401:
            print('\n⚠️  需要认证。请使用以下curl命令（替换TOKEN）：')
            print(f"curl -X POST {url} -H 'Authorization: Bearer YOUR_TOKEN'")
        else:
            print(f'\n❌ 修复失败：{response.status_code}')
            
    except requests.exceptions.ConnectionError:
        print('\n❌ 无法连接到服务器。请确保Flask应用正在运行。')
    except Exception as e:
        print(f'\n❌ 错误: {e}')

if __name__ == '__main__':
    fix_schema()
