import json
import asyncio
from pyppeteer import launch
from datetime import datetime, timedelta
import aiofiles
import random
import requests
import os
import re

# 从环境变量中获取 Telegram Bot Token 和 Chat ID
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def format_to_iso(date):
    return date.strftime('%Y-%m-%d %H:%M:%S')

async def delay_time(ms):
    await asyncio.sleep(ms / 1000)

# 全局浏览器实例
browser = None

# telegram消息
message = '####serv00/ct8自动化脚本运行####\n'

async def login(username, password, panel):
    global browser

    page = None  # 确保 page 在任何情况下都被定义
    serviceName = 'ct8' if 'ct8' in panel else 'serv00'
    try:
        if not browser:
            browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])

        page = await browser.newPage()
        url = f'https://{panel}/login/?next=/'
        await page.goto(url)

        username_input = await page.querySelector('#id_username')
        if username_input:
            await page.evaluate('''(input) => input.value = ""''', username_input)

        await page.type('#id_username', username)
        await page.type('#id_password', password)

        login_button = await page.querySelector('#submit')
        if login_button:
            await login_button.click()
        else:
            raise Exception('无法找到登录按钮')

        await page.waitForNavigation()

        is_logged_in = await page.evaluate('''() => {
            const logoutButton = document.querySelector('a[href="/logout/"]');
            return logoutButton !== null;
        }''')

        return is_logged_in

    except Exception as e:
        print(f'{serviceName}账号 <em>{username}</em> 登录时出现错误: {e}')
        return False

    finally:
        if page:
            await page.close()

async def main():
    global message
    message = "🌟🌟🌟serv00&ct8保号🌟🌟🌟\n"

    try:
        async with aiofiles.open('accounts.json', mode='r', encoding='utf-8') as f:
            accounts_json = await f.read()
        accounts = json.loads(accounts_json)
    except Exception as e:
        print(f'读取 accounts.json 文件时出错: {e}')
        return

    ss=0
    ff=0
    for account in accounts:
        username = account['username']
        password = account['password']
        panel = account['panel']

        #serviceName = 'ct8' if 'ct8' in panel else 'serv00'
        if 'ct8' in panel:
            serviceName = 'ct8'
        else:
            numbers = re.findall(r'\d+', panel)
            serviceName = f's{numbers[0]}'
        is_logged_in = await login(username, password, panel)

        if is_logged_in:
            ss+=1
            now_utc = format_to_iso(datetime.utcnow())
            now_beijing = format_to_iso(datetime.utcnow() + timedelta(hours=8))
            success_message = f'🟢{serviceName} 账号 <code>{username}</code> CST <small>{now_beijing}</small>（UTC <small>{now_utc}</small>）'
            message += success_message + '\n'
            print(success_message)
        else:
            ff+=1
            message += f'🔴{serviceName} 账号 <code>{username}</code> 登录失败，请检查账号&密码是否正确\n'
            print(f'{serviceName}账号 {username} 登录失败，请检查{serviceName}账号和密码是否正确。')

        delay = random.randint(1000, 8000)
        await delay_time(delay)

    patterns = ['⭐','✨','☁️','🌞','🌥️','🌤️','🌹','🌸','😄','😀','😁','😆','🌈','🌊']
    patterns = random.sample(patterns, 6)
    message += f'{patterns[0]}{patterns[1]}{patterns[2]}脚本运行结束{patterns[3]}{patterns[4]}{patterns[5]}\n'
    message += f'登录成功(<code>{ss}</code>) 登陆失败(<code>{ff}</code>) 总计(<code>{ss+ff}</code>)'
    await send_telegram_message(message)
    print(f'所有账号登录完成！')

async def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML',
        'reply_markup': {
            'inline_keyboard': [
                [
                    {
                        'text': '👉来自Github点此处直达项目👈',
                        'url': 'https://github.com/QingshiLane/serv00-login'
                    }
                ]
            ]
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"发送消息到Telegram失败: {response.text}")
    except Exception as e:
        print(f"发送消息到Telegram时出错: {e}")

if __name__ == '__main__':
    asyncio.run(main())
