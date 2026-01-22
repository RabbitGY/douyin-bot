import os
import requests
import time
import hmac
import hashlib
import base64
import urllib.parse

# 从 GitHub Secrets 中读取配置
SEC_USER_ID = os.environ.get('SEC_USER_ID')
DINGTALK_WEBHOOK = os.environ.get('DING_WEBHOOK')
DINGTALK_SECRET = os.environ.get('DING_SECRET')

def get_douyin_fans():
    # 使用移动端通用信息接口
    url = f"https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid={SEC_USER_ID}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        nickname = data['user_info']['nickname']
        fans_count = data['user_info']['mplatform_followers_count']
        return nickname, fans_count
    except Exception as e:
        print(f"获取抖音数据失败: {e}")
        return None, None

def send_to_dingtalk(nickname, fans):
    # 钉钉加签逻辑
    timestamp = str(round(time.time() * 1000))
    secret_enc = DINGTALK_SECRET.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, DINGTALK_SECRET)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    
    webhook_url = f"{DINGTALK_WEBHOOK}&timestamp={timestamp}&sign={sign}"
    
    msg = {
        "msgtype": "markdown",
        "markdown": {
            "title": "抖音粉丝数据报送",
            "text": f"### 📊 抖音粉丝数据报送\n\n"
                    f"**账号昵称**：{nickname}\n\n"
                    f"**当前粉丝数**：`{fans}`\n\n"
                    f"统计时间：{time.strftime('%Y-%m-%d %H:%M:%S')}"
        }
    }
    requests.post(webhook_url, json=msg)
    response = requests.post(webhook_url, json=msg)
    print(f"钉钉返回结果: {response.text}") # 添加这一行

if __name__ == "__main__":
    name, count = get_douyin_fans()
    if name:
        send_to_dingtalk(name, count)
        print(f"发送成功：{name} 有 {count} 粉丝")
