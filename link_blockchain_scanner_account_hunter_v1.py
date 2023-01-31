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
import os

path_csv_file_name_account_list = "DB_account_list_v1_20230128.csv"   #어카운트 리스트는 하나로 통일하되 버전관리를 위해 날짜를 새긴다.


def get_time():
    timeList = time.localtime()
    timeStr = timeList[0]*10000000000+timeList[1]*100000000+timeList[2]*1000000+timeList[3]*10000+timeList[4]*100+timeList[5]
    return timeStr


def trim_space(str_input):
    """str의 공백을 제거하여 반환"""

    return str_input.replace(' ', '')
    


def get_accounts_from_tx_hash(tx_hash):
    """트랜잭션 해쉬로부터, from, to address를 뽑는다."""
        
    return_account_list = []

    # print("\n----------------------------------------------------")
    print("tx_hash seraching started.....", tx_hash)

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1200')
    options.add_argument("disable-gpu")
        
    driver = webdriver.Chrome('chromedriver',options=options ) 
    target_url = 'https://scan.blockchain.line.me/Finschia%20Mainnet/tx/' + tx_hash
    print('target_url is.. ',target_url)

    driver.get(target_url)
    time.sleep(2)

    html = driver.page_source        
    soup = BeautifulSoup(html, 'html.parser')

    # __BVID__127 : #app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div:nth-child(2) > div > table
    # __BVID__135 : #__BVID__127 > tbody > tr:nth-child(2) > td.overflow-hidden > div > table
                    #app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div:nth-child(2) > div > table > tbody > tr:nth-child(2) > td.overflow-hidden > div > table
    # from_address: #__BVID__135 > tbody > tr:nth-child(1) > td:nth-child(2) > div > span
    # to_address: #__BVID__135 > tbody > tr:nth-child(2) > td:nth-child(2) > div > span

    
    tx_type = soup.select("#app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div:nth-child(2) > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > div")
    if len(tx_type) ==0:
        return return_account_list
    
    str_type = trim_space(tx_type[0].text)
    
    print( str_type)

    TYPE_MSG_SEND = 'cosmos-sdk/MsgSend'
    TYPE_MSG_CONTRACT = 'wasm/MsgExecuteContract'

    if str_type == TYPE_MSG_SEND:  #ex) 7C271E8B8C9A59C37719DF4DC1025DF6D656660A800C220223450E824E57B093
        from_address_obj = soup.select("#app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div:nth-child(2) > div > table > tbody > tr:nth-child(2) > td.overflow-hidden > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > div")
        to_address_obj = soup.select("#app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div:nth-child(2) > div > table > tbody > tr:nth-child(2) > td.overflow-hidden > div > table > tbody > tr:nth-child(2) > td:nth-child(2) > div")

        from_address = str(from_address_obj[0].text)
        to_address = str(to_address_obj[0].text)
        
    elif str_type == TYPE_MSG_CONTRACT: #ex) 1E493FCC7B67E0A7DB2BF73220C130070B7F7477D341E6AB3CFEB2F34D46DADF
        
        from_address_obj = soup.select("#app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div:nth-child(2) > div > table > tbody > tr:nth-child(2) > td.overflow-hidden > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > div")
        to_address_obj = soup.select("#app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div:nth-child(2) > div > table > tbody > tr:nth-child(2) > td.overflow-hidden > div > table > tbody > tr:nth-child(2) > td:nth-child(2) > div")

        from_address = str(from_address_obj[0].text)
        to_address = str(to_address_obj[0].text)
         
        
    else:
        print("Failed to loading page information..")
        from_address =""
        to_address =""
        

    driver.close()
     
     
     
    
    
    if(from_address != ""):        
        return_account_list.append(from_address)        
        
    if(to_address != ""):
        return_account_list.append(to_address)

    return return_account_list




async def do_work_bot(message_to_send):
    """BOT에게 메시지 보내는 비동기 함수"""

    my_token = "2062225545:AAGytzWEbs7_dzQK2aPV5FXjQCG5ucWq8uc" 
    my_chat_id = 2031803571    
    bot = telegram.Bot(token = my_token)
    
    await bot.send_message(chat_id=my_chat_id, text= message_to_send)
    





if __name__ == "__main__":
    
    #finschia 시작: "51775519" 2022/12/22
    asyncio.run(do_work_bot("account hunter_program has been started"))

    #block~tx 파일 list를 가져온다.
    block_file_name_list = []  #이건 DB 폴더위의 파일명 리스트 전체.

    path = "./DB_52500000_52599999/"
    block_file_name_list = os.listdir(path)

    # print ("block_file_name_list: {}".format(block_file_name_list))
    
    
    
    for file_name in block_file_name_list:        
    
        adjusted_file_name = 'DB_52500000_52599999/'+file_name 
        print('processing... ',adjusted_file_name)

        try:
            df_info_list = pd.read_csv(adjusted_file_name, index_col =0 )

        except:
            print("wrong input filed...")
            #continue
            sys.exit()


        #tx_hash를 str로 형변환해준다.
        df_info_list = df_info_list.astype({'tx_hash' : 'str'})



        #account list를 생성하거나 로딩한다.
        try:
            df_account_list = pd.read_csv(path_csv_file_name_account_list, index_col =0 )
            df_account_list.drop(labels=['START_LINE'],errors='ignore', inplace=True)        

        except:
            temp_dic = { "START_LINE" : { 'account' : '' ,'search_count':0,  'balance' : 0 }}  #잔액 조회는 다른 스크립트로 짠다.
            df_account_list =  pd.DataFrame.from_dict(temp_dic, orient ='index')




        try:
            for row in range(0, len(df_info_list)):
                                                    
                if df_info_list['tx_hash'].iloc[row] == 'nan'  or df_info_list['tx_hash'].iloc[row] == 'FAILED' :
                    #print("not valid block-TX type (row)")
                    df_info_list.iloc[row, 2] += 1
                    continue
                            
                #트랜잭션을 돌면서, 셀레니움으로 어카운트를 추출하여 리스트에 넣어서 파일로 떨군다.(저장까지)
                #단, 중복되는 어카운트의 경우는 어카운트 리스트에 넣지 않아야 하겠다.
                
                if df_info_list['search_count'].iloc[row] > 0:                
                    #print('this is searched Block and TX, passing...')            
                    pass
                
                else:
                    df_info_list.iloc[row, 2] += 1
                    print('--------------------------------------------------------') 
                    print('the file name: ',adjusted_file_name)
                    temp_account_list = get_accounts_from_tx_hash(df_info_list['tx_hash'].iloc[row])
                                    
                    for i in range(0, len(temp_account_list)):                    
                        
                        print(temp_account_list[i])
                        
                        if (df_account_list['account'] == temp_account_list[i]).any() == False:# df_account_list에 서칭된 해당 account를포함하고 있찌 않으면. 
                            df_account_list.loc[get_time()] = {'account': temp_account_list[i],'search_count':0,  'balance' : 0 }
                            
                        else:
                            print ('that account was already inserted to the list :', temp_account_list[i])        
                    
                
                df_account_list.to_csv(path_csv_file_name_account_list)
                df_info_list.to_csv(adjusted_file_name)
            
            
        
            df_account_list.drop(labels=['START_LINE'],errors='ignore', inplace=True)
            df_account_list.to_csv(path_csv_file_name_account_list)
            df_info_list.to_csv(adjusted_file_name)   


        except Exception as e:
            trace_back = traceback.format_exc()
            message = str(e)+ " " + str(trace_back)
            print (message)


    asyncio.run(do_work_bot("account_hunter program has been completed"))







