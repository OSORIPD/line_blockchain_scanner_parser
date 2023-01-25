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

path_csv_file_name = "DB_link_blockchain_scanner_block_watcher_v1.csv"


"""가져온 데이터를 데이터프레임과 합쳐서 정렬해준다."""
def data_listing(balance_info, df_info_list):
    # print("unit_info \n",unit_info )        
    
    curr_time = get_time()
    # print("curr_time:",curr_time)

    current_balance = be_int(balance_info[0].text)
    print("current_balance: ",current_balance)

    var_balance = current_balance - df_info_list.iloc[-1,1]
    print("var_balance: ",var_balance)

    # total_supply = get_quantity_credit(unit_info[4].text)
    # print("total supply: ",total_supply)

    # var_supply = total_supply - df_info_list.iloc[-1,1]
    # print("var_supply: ",var_supply)


    # total_holder = be_int(unit_info[5].text)
    # #print("total_holder\n",total_holder)

    # var_holder = total_holder - df_info_list.iloc[-1,3]
    # #print("var_holder\n",var_holder)


    # total_transfer = get_quantity_transfer(unit_info[6].text)
    # #print("total_holder\n",total_transfer)

    # var_transfer = total_transfer - df_info_list.iloc[-1,5]
    # #print("var_transfer\n",var_transfer)


    df_info_list.loc[curr_time] = { 'curr_time' : curr_time, 'current_balance' : current_balance, 'var_balance':var_balance }  
    return df_info_list





def get_time():
    timeList = time.localtime()
    timeStr = timeList[0]*10000000000+timeList[1]*100000000+timeList[2]*1000000+timeList[3]*10000+timeList[4]*100+timeList[5]
    return timeStr


def trim_space(str_input):
    """str의 공백을 제거하여 반환"""

    return str_input.replace(' ', '')
    

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



def get_txhash_from_block_if_exist(block_height_input): 
    """
    block_number의 핀시아 블록을 서칭하여, 트랜잭션이 있을 경우, 해당 해쉬값을 string 형태로 반환함. 없을경우 빈 str을 반환함. 
    """


    tx_hash = ""

    block_height = str(block_height_input)
    print("\n----------------------------------------------------")
    print("block seraching started.....", block_height)

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
        
    driver = webdriver.Chrome('chromedriver',options=options ) 

    target_url = 'https://scan.blockchain.line.me/Finschia%20Mainnet/blocks/' + block_height
    print('target_url is.. ',target_url)

    driver.get(target_url)
    driver.implicitly_wait(10)

    # element = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[3]/div[3]/div[2]/div/div/div[2]/div/div[2]/div/div/div/div/span[3]')))

    html = driver.page_source        
    soup = BeautifulSoup(html, 'html.parser')


    # null_str = '<tbody role="rowgroup"></tbody>' #비어있는 tbody의 경우, [0]이 왼쪽과 같은 str을 반환함. 

    tx_info =  soup.select("#app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div:nth-child(3) > div > div > table > tbody")
    # print("tx_info: ",tx_info)
    # print("tx_info[0]: ", tx_info[0])
    # print(type(tx_info[0]))


    if tx_info == None or len(tx_info) == 0:
        print("Failed to loading page information..")
        return (block_height_input, "FAILED")


    if tx_info[0].text != "":
        tx_info_detail = soup.select("#app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div:nth-child(3) > div > div > table > tbody > tr > td > a")
        
        # print("tx_info_detail[0].text: ",tx_info_detail[0].text)
        
        tx_hash = trim_space(tx_info_detail[0].text)
        

    else:
        tx_hash = "NA"
        print("this block has no TX")

    driver.close()

    return (block_height_input, tx_hash)




"""BOT에게 메시지 보내는 비동기 함수"""
async def do_work_bot(message_to_send):
    
    my_token = "2062225545:AAGytzWEbs7_dzQK2aPV5FXjQCG5ucWq8uc" 
    my_chat_id = 2031803571    
    bot = telegram.Bot(token = my_token)
    
    await bot.send_message(chat_id=my_chat_id, text= message_to_send)
    





if __name__ == "__main__":
    
    # asyncio.run(do_work_bot("link wallet tracing program has been started"))

    #finschia 시작: "51775519" 2022/12/22
    
    #52660132 - 트랜잭션 1개 있는 블록
    #52660175 - 트랜잭션 없는 블록


    try:
        df_info_list = pd.read_csv(path_csv_file_name, index_col =0 )


    except:
        curr_time = get_time()            

        temp_dic = { "START_LINE" : { 'block_hash' : 0, 'tx_hash': "" }}
        df_info_list =  pd.DataFrame.from_dict(temp_dic, orient ='index')



    try:
        for i in range(52660131,52660155):    
            
            if (df_info_list['block_hash'] == i).any() == False  :
                
                temp_tx_pair = get_txhash_from_block_if_exist(i)
                print(temp_tx_pair) 
                curr_time = get_time()        
                df_info_list.loc[curr_time] = {  'block_hash' : temp_tx_pair[0], 'tx_hash':temp_tx_pair[1] }  
                df_info_list.to_csv(path_csv_file_name)

            else:
                print ("the block was already recorded")


        
        df_info_list.drop(labels=['START_LINE'],errors='ignore', inplace=True)        
        df_info_list.to_csv(path_csv_file_name)


    except Exception as e:
        trace_back = traceback.format_exc()
        message = str(e)+ " " + str(trace_back)
        print (message)
        
        # asyncio.run(do_work_bot("line wallet tracing program has been terminated by error"))







