# -*- coding: utf-8 -*-
"""
Created on Fri Apr  4 09:31:17 2025

@author: u0156396
"""

import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# ========= CONFIG =========
visa_url = "https://infovisa.ibz.be/ResultFr.aspx?place=TPE&visumnr=15966"
last_known_status = "En traitement"

sender_email = "sdfgh5343@gmail.com"
receiver_email = "howard.chihhao.hsu@gmail.com"
app_password = "axvy lldi amgf bgdx"
# ===========================

def get_current_status():
    response = requests.get(visa_url)
    if response.status_code != 200:
        raise Exception(f"請求失敗: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    decision_cell = soup.find('td', string='Décision: ')
    if decision_cell:
        return decision_cell.find_next('td').get_text(strip=True)
    else:
        raise Exception("無法找到簽證狀態")

def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

def main():
    try:
        current_status = get_current_status()

        if current_status != last_known_status:
            print(f"狀態改變！從「{last_known_status}」變為「{current_status}」")
            send_email("簽證狀態更新", f"老婆，簽證狀態已變更：\n\n舊狀態：{last_known_status}\n新狀態：{current_status}，辣福U")
            write_current_status(current_status)
        else:
            send_email("Test", f"test")
            print("狀態無變化，不寄信。")
    except Exception as e:
        print("錯誤發生：", e)
        send_email("簽證查詢錯誤", f"發生錯誤：{str(e)}")

if __name__ == "__main__":
    main()
