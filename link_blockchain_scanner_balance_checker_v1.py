from os import times
from numpy import concatenate
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import time
import telegram
import asyncio

import pandas as pd 
import traceback
import sys

path_csv_file_name_account_list = "DB_account_list_v1_20230128.csv"  #이거 하나로 읽고 쓰고 하면 됨. 


def get_time():
    timeList = time.localtime()
    timeStr = timeList[0]*10000000000+timeList[1]*100000000+timeList[2]*1000000+timeList[3]*10000+timeList[4]*100+timeList[5]
    return timeStr


def be_int(value_input):
    
    value = value_input.replace(',', '')
    value = value.replace('L', '')
    value = value.replace('I', '')
    value = value.replace('N', '')
    value = value.replace('K', '')
    value = value.replace('(', '')
    value = value.replace(')', '')

    new_str = ''
    for char in value:
        if char != '.':
            new_str+=char
        else:
            break
    
    return int(new_str)


def trim_space(str_input):
    """str의 공백을 제거하여 반환"""

    return str_input.replace(' ', '')
    


def get_account_balance(account_adress):
    """해당 어카운트의 링크 밸런스를 찾아서 반환한다."""

    balance = 0

    print("\n----------------------------------------------------")
    print("account balance seraching started.....", account_adress)


    options = webdriver.ChromeOptions()
    options.add_argument('headless')   
    options.add_argument('window-size=1920x1200')
    options.add_argument("disable-gpu")
    options.add_argument('--incognito')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

        
    driver = webdriver.Chrome('chromedriver',options=options ) 

    target_url = 'https://scan.blockchain.line.me/Finschia%20Mainnet/account/' + account_adress
    print('target_url is.. ',target_url)

    driver.get(target_url)
    time.sleep(2)

    html = driver.page_source        
    soup = BeautifulSoup(html, 'html.parser')

    
    balance_obj = soup.select("#app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div > div.card.d-flex.flex-row > div > div.card-body.p-0 > div > div > div > div > span.text-right")
    # print(balance_obj)

    if(len(balance_obj)==0):
        balance = 0
    
    else:
        balance = be_int(balance_obj[0].text)


    driver.close()

     
    return balance





async def do_work_bot(message_to_send):
    """BOT에게 메시지 보내는 비동기 함수"""

    my_token = "2062225545:AAGytzWEbs7_dzQK2aPV5FXjQCG5ucWq8uc" 
    my_chat_id = 2031803571    
    bot = telegram.Bot(token = my_token)
    
    await bot.send_message(chat_id=my_chat_id, text= message_to_send)
    





if __name__ == "__main__":
    
    #finschia 시작: "51775519" 2022/12/22
    
    asyncio.run(do_work_bot("account balance checker program has been started"))

    #account list를 생성하거나 로딩한다. 없을 경우, 오류로 처리하고 프로그램 종료.
    try:
        df_account_list = pd.read_csv(path_csv_file_name_account_list, index_col =0 )

    except:
        print("account list file was missed . program will be ended")
        sys.exit()




    try:
        for row in range(0, len(df_account_list)):

            #search_count:  df_account_list.iloc[row, 1]
            #balance:  df_account_list.iloc[row, 2]

            if df_account_list['search_count'].iloc[row] > 0:                
                print('this is already searched account, passing...')            
            
            else:
                df_account_list.iloc[row, 1] += 1  

                temp_balance = get_account_balance(df_account_list['account'].iloc[row])
                print('row ',row , ': ',temp_balance)
                df_account_list.iloc[row, 2] = temp_balance 
                      
            if row % 10 == 0:
                df_account_list.to_csv(path_csv_file_name_account_list)
       
        df_account_list.to_csv(path_csv_file_name_account_list)

        asyncio.run(do_work_bot("account balance checker program has been completed"))


    except Exception as e:
        trace_back = traceback.format_exc()
        message = str(e)+ " " + str(trace_back)
        print (message) 
        asyncio.run(do_work_bot("account balance checker program has been terminated"))


