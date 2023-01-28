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
from functools import partial
# from pathos.multiprocessing import ProcessingPool as Pool #pip install pathos
import multiprocessing

path_csv_file_name_frame = "DB\DB_link_blockchain_scanner_block_parser_v1"

#finschia 시작: "51775519" 2022/12/22

#sample
#52660132 - 트랜잭션 1개 있는 블록
#52660175 - 트랜잭션 없는 블록
start_block = 52500000


def get_time():
    timeList = time.localtime()
    timeStr = timeList[0]*10000000000+timeList[1]*100000000+timeList[2]*1000000+timeList[3]*10000+timeList[4]*100+timeList[5]
    return timeStr


def trim_space(str_input):
    """str의 공백을 제거하여 반환"""

    return str_input.replace(' ', '')
    

async def do_work_bot(message_to_send):
    """BOT에게 메시지 보내는 비동기 함수"""

    my_token = "2062225545:AAGytzWEbs7_dzQK2aPV5FXjQCG5ucWq8uc" 
    my_chat_id = 2031803571    
    bot = telegram.Bot(token = my_token)
    
    await bot.send_message(chat_id=my_chat_id, text= message_to_send)
    
    
    

def get_txhash_from_block_if_exist(block_height_input): 
    """
    block_number의 핀시아 블록을 서칭하여, 트랜잭션이 있을 경우, 해당 해쉬값을 string 형태로 반환함. 없을경우 빈 str을 반환함. 
    """

    block_height = str(block_height_input)
    # print("\n----------------------------------------------------")
    # print("block seraching started.....", block_height)

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1200')
    options.add_argument("disable-gpu")
        
    driver = webdriver.Chrome('chromedriver',options=options ) 

    target_url = 'https://scan.blockchain.line.me/Finschia%20Mainnet/blocks/' + block_height
    # print('target_url is.. ',target_url)

    driver.get(target_url)
    time.sleep(1)

    html = driver.page_source        
    soup = BeautifulSoup(html, 'html.parser')


    tx_info =  soup.select("#app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div:nth-child(3) > div > div > table > tbody")


    if tx_info == None or len(tx_info) == 0:
        # print("Failed to loading page information..")
        return (block_height_input, "FAILED")


    if tx_info[0].text != "":
        tx_info_detail = soup.select("#app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div:nth-child(3) > div > div > table > tbody > tr > td > a")        
        tx_hash_return = trim_space(tx_info_detail[0].text)
        

    else:        
        tx_hash_return = "NA"
        # print("this block has no TX")

    driver.close()
    
    return (block_height_input, tx_hash_return)
    
  
    
    

def do_multi( code):
    """멀티스레드 실행."""    
    
    print("do_multi.. ", code)
    #50000개 / 5프로세스 = 10000.   무조건 10000개씩 끊어서 파일 간격 맞춰서 프로세싱 돌리기.     
    message_temp = "node "+str(code)+" :block_parser_program has been started"
    asyncio.run(do_work_bot(message_temp ))

    temp_start_block = start_block + code*10000
    temp_end_block = temp_start_block + 9999
    temp_path_csv_file_name = path_csv_file_name_frame + "_"+str(temp_start_block) +"_"+str(temp_end_block) + ".csv"
    
    try:
        df_info_list = pd.read_csv(temp_path_csv_file_name, index_col =0 )
        df_info_list.drop(labels=['START_LINE'],errors='ignore', inplace=True)        

    except:
        temp_dic = { "START_LINE" : { 'block_hash' : 0, 'tx_hash': "DUMMY" , 'search_count':0 }}
        df_info_list =  pd.DataFrame.from_dict(temp_dic, orient ='index')


    # print(df_info_list)

    
    
    for i in range(temp_start_block,temp_end_block):
             
        # print("multithreade.. node .. ", code, ': ',i)

        if (df_info_list['block_hash'] == i).any() == False  :
            
            temp_tx_pair = get_txhash_from_block_if_exist(i)

            # print(code, temp_tx_pair) 
        
            df_info_list.loc[get_time()] = {'block_hash' : temp_tx_pair[0], 'tx_hash':temp_tx_pair[1] ,'search_count':0 }  
            df_info_list.to_csv(temp_path_csv_file_name)

        else:
            pass
            # print ("the block was already recorded")


    df_info_list.drop(labels=['START_LINE'],errors='ignore', inplace=True) 
    df_info_list.to_csv(temp_path_csv_file_name)

    message_temp = "node "+str(code)+": block_parser_program has been completed"
    asyncio.run(do_work_bot(message_temp ))


    return df_info_list




if __name__ == "__main__":

    asyncio.run(do_work_bot("block_parser_program has been started"))

    code_list = [0,1,2,3,4,5,6,7,8,9]
    print ('--- start _multiprocessing')


    # cpu 갯수 확인
    cpu_count = multiprocessing.cpu_count()
    print ('--- cpu_count ', cpu_count)

    # cpu 수 결정
    pool = multiprocessing.Pool(processes= 10)
    
     # 실행 함수, 넘겨줄 파라미터
    
    pool.map(do_multi, code_list)

    # 모든 프로세스 종료까지 기다림
    pool.close()
    pool.join()
    
    print ('--- end _multiprocessing')

    asyncio.run(do_work_bot("block_parser_program has been completed"))




