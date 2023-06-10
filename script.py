import os
import smtplib
import requests
import schedule
import time
import winreg
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

variables = {}

def env_variables(mode = 1):
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    with open(env_path) as f:
        for line in f:
            key, value = line.strip().split('=', 1)
            os.environ[key] = value
    v = {}
    v['smtp_server'] = os.getenv('SMTP_SERVER')
    v['smtp_port'] = os.getenv('SMTP_PORT')
    v['sender_email'] = os.getenv('SENDER_EMAIL')
    v['app_password'] = os.getenv('APP_PASSWORD')
    v['recipient_email'] = os.getenv('RECIPIENT_EMAIL')
    v['key_path'] = os.getenv('KEY_PATH')
    v['value_name'] = os.getenv('VALUE_NAME')
    v['log_file'] = os.getenv('LOG_FILE')
    return v

def send_email():    
    message = MIMEMultipart('alternative')
    message['From'] = variables['sender_email']
    message['To'] = variables['recipient_email']
    message['Subject'] = 'Daily Quote'

    quote = get_quote()
    
    html = f'''
    <html>
    <body>
      <img src="cid:image1">
      <blockquote>
        {quote[0]}
        <cite>{quote[1]}</cite>
       </blockquote>      
    </body>
    </html>
    '''
    
    with open('smiley.jpg', 'rb') as img_file:
        image = MIMEImage(img_file.read())
        image.add_header('Content-ID', '<image1>')
        message.attach(image)

    html_part = MIMEText(html, 'html')
    message.attach(html_part)
    
    try:
        with smtplib.SMTP(variables['smtp_server'], variables['smtp_port']) as server:
            server.starttls()
            server.login(variables['sender_email'], variables['app_password'])
            server.sendmail(variables['sender_email'], variables['recipient_email'], message.as_string())
        print('Email successfully sent!')
    except:
        raise Exception('Email sending failed!')
    
def get_quote():
    response = requests.get('https://zenquotes.io/api/random')

    if response.status_code == 200:
        data = response.json()

        quote = data[0]['q']
        author = data[0]['a']

        return [quote, author]
    else:
        raise Exception("Failed to retrieve quote. Error:", response.status_code)

def configure_autorun():
    key_path = variables["key_path"]
    value_name = variables["value_name"]
    script_path = os.path.abspath(__file__)
    python_path = os.path.join(sys.exec_prefix, "python.exe")
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, f'"{python_path}" "{script_path}"')
        winreg.CloseKey(key)
        print("Autorun configured successfully")
    except FileNotFoundError:
        print("Registry key not found")

def execution_log():
    current_time = time.time()
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time))
    with open(variables["log_file"], "a") as file:
    	file.write(f"[{formatted_time}] Running...\n")
variables = env_variables()

configure_autorun()
schedule.every().day.at("14:25").do(send_email)
print("Successfully scheduled!")
execution_log()
while True:
    schedule.run_pending()
    time.sleep(1)
