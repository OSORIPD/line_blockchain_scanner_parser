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

path_csv_file_name = "DB_link_blockchain_scanner_parser_v1.csv"


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



def do_job():    

    max_try_count = 10000000
    curr_try_count = 0

    while curr_try_count <  max_try_count:
        curr_try_count+= 1


        print("\n---------------------------------------------------------------")
        print("looping....", curr_try_count)
        # if curr_try_count % 360 ==0:
        #     bot.sendMessage(chat_id = chat_id, text ='observer??? ?????? ???.. ' +str(curr_try_count))


        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        
        driver = webdriver.Chrome('chromedriver',options=options ) 


 
        ### 크롬드라이버로 링크 블록체인 스캐너에서 주요거래소별 지갑 정보를 가져옴
        driver.get('https://scan.blockchain.line.me/Finschia%20Mainnet/account/link1lvpzgy352969z7mlcxjfua7jsmks6swl222agc')
        driver.implicitly_wait(20)

        # element = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[3]/div[3]/div[2]/div/div/div[2]/div/div[2]/div/div/div/div/span[3]')))

        html = driver.page_source        
        soup = BeautifulSoup(html, 'html.parser')

        balance_info =  soup.select("#app > div > div.app-content.content > div.content-wrapper > div.content-body > div > div > div.card.d-flex.flex-row > div > div.card-body.p-0 > div > div > div > div > span.text-right")
        # print("balance_info: ",balance_info)
        # print("len(balance_info): ",len(balance_info) )

        driver.close()

        
        
        
        ### 크롬드라이버로 빗썸에서 링크 가격 등의 정보를 가져옴.                  ===> 사이트에서 막아서 못씀.
    
        # driver.get('https://www.bithumb.com/trade/order/LN_BTC')
        # element = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, '//*[@id="contents"]/div[2]/div[1]/article/div[1]/div/div')))

        # html = driver.page_source        
        # soup = BeautifulSoup(html, 'html.parser')

        # price_info =  soup.select("#contents > div.order-info > div.orderArea > article > div.info_con > div > div > h3")
        # print("price_info: ",price_info)
                 
        # driver.close()
        
        
        ### 코드 저장
        # driver.implicitly_wait(10)
        # element = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CLASS_NAME, "content-body")))
        # element = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, '//*[@id="contents"]/div[2]/div[1]/article/div[1]/div/div'))) 

         
        if len(balance_info) == 0:
            print("balnace_info is empty... passing loop once")
                 
        else:
            try:
                df_info_list = pd.read_csv(path_csv_file_name, index_col =0 )

            except:
                temp_dic = { 'START_LINE' : { 'curr_time' : 0,'current_balance' : 0, 'var_balance':0 }}
                df_info_list =  pd.DataFrame.from_dict(temp_dic, orient ='index')
                #df_info_list= df_info_list.drop('START_LINE')


            df_info_list = data_listing(balance_info, df_info_list)

            temp_var_balance = df_info_list.iloc[-1,2]

            if temp_var_balance>99:

                mess1 = []
                mess1.append('빗썸 wallet balance가 ')
                mess1.append(str(temp_var_balance))
                mess1.append(" 만큼 증가했습니다. [현재 LN 수량: ")
                mess1.append(str(df_info_list.iloc[-1,1]))
                mess1.append("]")
                mess1 = ''.join(mess1)
        
                asyncio.run(do_work_bot(mess1))


            if temp_var_balance<-99:

                mess1 = []
                mess1.append('빗썸 wallet balance가 ')
                mess1.append(str(temp_var_balance))
                mess1.append(" 만큼 감소했습니다. [현재 LN 수량: ")
                mess1.append(str(df_info_list.iloc[-1,1]))
                mess1.append("]")
                mess1 = ''.join(mess1)
        
                asyncio.run(do_work_bot(mess1))


            df_info_list.to_csv(path_csv_file_name)

        time.sleep(30)




async def do_work_bot(message_to_send):
    
    my_token = "2062225545:AAGytzWEbs7_dzQK2aPV5FXjQCG5ucWq8uc" 
    my_chat_id = 2031803571    
    bot = telegram.Bot(token = my_token)
    
    await bot.send_message(chat_id=my_chat_id, text= message_to_send)
    


if __name__ == "__main__":
    
    asyncio.run(do_work_bot("link wallet tracing program has been started"))

    try:
        do_job()
        
    except Exception as e:
        trace_back = traceback.format_exc()
        message = str(e)+ " " + str(trace_back)
        print (message)
        
        asyncio.run(do_work_bot("line wallet tracing program has been terminated by error"))




