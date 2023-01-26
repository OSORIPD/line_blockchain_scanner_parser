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

path_csv_file_name_input = "DB_link_blockchain_scanner_block_watcher_v1_52600000.csv"
path_csv_file_name_account_list = "DB_account_list_v1_52600000.csv" 


def get_time():
    timeList = time.localtime()
    timeStr = timeList[0]*10000000000+timeList[1]*100000000+timeList[2]*1000000+timeList[3]*10000+timeList[4]*100+timeList[5]
    return timeStr


def trim_space(str_input):
    """str의 공백을 제거하여 반환"""

    return str_input.replace(' ', '')
    


# def get_txhash_from_block_if_exist(block_height_input): 
#     """
#     block_number의 핀시아 블록을 서칭하여, 트랜잭션이 있을 경우, 해당 해쉬값을 string 형태로 반환함. 없을경우 빈 str을 반환함. 
#     """

#     block_height = str(block_height_input)
#     print("\n----------------------------------------------------")
#     print("block seraching started.....", block_height)

#     options = webdriver.ChromeOptions()
#     options.add_argument('headless')
#     options.add_argument('window-size=1920x1200')
#     options.add_argument("disable-gpu")
        
#     driver = webdriver.Chrome('chromedriver',options=options ) 

#     target_url = 'https://scan.blockchain.line.me/Finschia%20Mainnet/blocks/' + block_height
#     print('target_url is.. ',target_url)

#     driver.get(target_url)
#     time.sleep(1)
#     # driver.implicitly_wait(5)

#     # element = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[3]/div[3]/div[2]/div/div/div[2]/div/div[2]/div/div/div/div/span[3]')))

#     html = driver.page_source        
#     soup = BeautifulSoup(html, 'html.parser')


#     # null_str = '<tbody role="rowgroup"></tbody>' #비어있는 tbody의 경우, [0]이 왼쪽과 같은 str을 반환함. 

#     tx_info =  soup.select("#app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div:nth-child(3) > div > div > table > tbody")
#     # print("tx_info: ",tx_info)
#     # print("tx_info[0]: ", tx_info[0])
#     # print(type(tx_info[0]))


#     if tx_info == None or len(tx_info) == 0:
#         print("Failed to loading page information..")
#         return (block_height_input, "FAILED")


#     if tx_info[0].text != "":
#         tx_info_detail = soup.select("#app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div:nth-child(3) > div > div > table > tbody > tr > td > a")
        
#         # print("tx_info_detail[0].text: ",tx_info_detail[0].text)
        
#         tx_hash_return = trim_space(tx_info_detail[0].text)
        

#     else:        
#         tx_hash_return = "NA"
#         print("this block has no TX")

#     driver.close()
#     return (block_height_input, tx_hash_return)


def get_accounts_from_tx_hash(tx_hash):
    """트랜잭션 해쉬로부터, from, to address를 뽑는다."""
    
    # tx_hash = str(tx_hash)
    
    
    print("\n----------------------------------------------------")
    print("tx_hash seraching started.....", tx_hash)

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1200')
    options.add_argument("disable-gpu")
        
    driver = webdriver.Chrome('chromedriver',options=options ) 
    target_url = 'https://scan.blockchain.line.me/Finschia%20Mainnet/tx/' + tx_hash
    print('target_url is.. ',target_url)

    driver.get(target_url)
    time.sleep(1)

    html = driver.page_source        
    soup = BeautifulSoup(html, 'html.parser')

    # __BVID__127 : #app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div:nth-child(2) > div > table
    # __BVID__135 : #__BVID__127 > tbody > tr:nth-child(2) > td.overflow-hidden > div > table
                    #app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div:nth-child(2) > div > table > tbody > tr:nth-child(2) > td.overflow-hidden > div > table
    # from_address: #__BVID__135 > tbody > tr:nth-child(1) > td:nth-child(2) > div > span
    # to_address: #__BVID__135 > tbody > tr:nth-child(2) > td:nth-child(2) > div > span

    
    tx_type = soup.select("#app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div:nth-child(2) > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > div")
    str_type = trim_space(tx_type[0].text)
    
    print( str_type)

    TYPE_MSG_SEND = 'cosmos-sdk/MsgSend'
    TYPE_MSG_CONTRACT = 'wasm/MsgExecuteContract'

    if str_type == TYPE_MSG_SEND:  #ex) 7C271E8B8C9A59C37719DF4DC1025DF6D656660A800C220223450E824E57B093
        from_address_obj = soup.select("#app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div:nth-child(2) > div > table > tbody > tr:nth-child(2) > td.overflow-hidden > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > div")
        to_address_obj = soup.select("#app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div:nth-child(2) > div > table > tbody > tr:nth-child(2) > td.overflow-hidden > div > table > tbody > tr:nth-child(2) > td:nth-child(2) > div")
        # print( from_address_obj[0].text)
        # print( to_address_obj[0].text)

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
     
     
     
    
    return_account_list = []
    
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
    
    # asyncio.run(do_work_bot("link wallet tracing program has been started"))

    #finschia 시작: "51775519" 2022/12/22
    
    #block~tx list를 가져온다.
    try:
        df_info_list = pd.read_csv(path_csv_file_name_input, index_col =0 )

    except:
        print("wrong input filed...")
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
                print("not valid block-TX type (row)")
                df_info_list.iloc[row, 2] += 1
                continue
                        
            #트랜잭션을 돌면서, 셀레니움으로 어카운트를 추출하여 리스트에 넣어서 파일로 떨군다.(저장까지)
            #단, 중복되는 어카운트의 경우는 어카운트 리스트에 넣지 않아야 하겠다.
            
            if df_info_list['search_count'].iloc[row] > 0:                
                print('this is searched Block and TX, passing...')            
            
            else:
                df_info_list.iloc[row, 2] += 1  
                temp_account_list = get_accounts_from_tx_hash(df_info_list['tx_hash'].iloc[row])
                                
                for i in range(0, len(temp_account_list)):                    
                    
                    print(temp_account_list[i])
                    
                    if (df_account_list['account'] == temp_account_list[i]).any() == False:# df_account_list에 서칭된 해당 account를포함하고 있찌 않으면. 
                        df_account_list.loc[get_time()] = {'account': temp_account_list[i],'search_count':0,  'balance' : 0 }
                         
                    else:
                        print ('that account was already inserted to the list :', temp_account_list[i])        
                
            
            df_account_list.to_csv(path_csv_file_name_account_list)
            df_info_list.to_csv(path_csv_file_name_input)
        
        
       
        df_account_list.drop(labels=['START_LINE'],errors='ignore', inplace=True)
        df_account_list.to_csv(path_csv_file_name_account_list)
        df_info_list.to_csv(path_csv_file_name_input)   


    except Exception as e:
        trace_back = traceback.format_exc()
        message = str(e)+ " " + str(trace_back)
        print (message)
        
        # asyncio.run(do_work_bot("line wallet tracing program has been terminated by error"))







