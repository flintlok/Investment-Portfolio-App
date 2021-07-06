from __future__ import print_function
from datetime import datetime, date, time, timedelta
import time
import PySimpleGUI as sg
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from helper import *
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import sys

driver_path = 'driver/chromedriver.exe'

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

#makes sure that the browser runs in the background instead of popping up
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')  
driver = webdriver.Chrome(resource_path(driver_path), chrome_options=options)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

#current stock information
name = ''
stock_type = ''
nav = 0
url = ''

#input this list to webscraper script
portfolio = [{},{},{}]
table_values = [['','','']]
dropdown_values = []

toggle_sheets_section = False
toggle_instructions = False

#create token.json file that is unique to every device
def build_service():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)
    print('success')
    return service
    
# get portfolio values for the day, used for 
def get_portfolio(portfolio):
    driver_path = 'C:/Users/User/Desktop/portfolio app/chromedriver/chromedriver.exe'
    driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)

    values = [0,0,0]

    for d in portfolio:
        for url in d.keys():
            info = d[url]
            stock_type = info[2]
            units = float(info[-1])

            if stock_type == 'Pasar Uang':
                index = 0
            elif stock_type == 'Obligasi':
                index = 1
            elif stock_type == 'Saham':
                index = 2

            driver.get(url)
            time.sleep(2.5)
            price = driver.find_element_by_xpath('/html/body/div/ui-view/ui-view/ui-view/main/div[1]/section[2]/table/tbody/tr/td[1]').text
            nav = price.split()[1]
            
            if '.' in nav:
                nav = nav.replace(',','.').replace('.','',1)
            else:
                nav = nav.replace(',','.')

            value = float(nav)*units

            values[index] += value
    
    return values

#create spreadsheet if not yet previously created
def create_spreadsheet(spreadsheetId, template_gid, portfolio_path):
    sheet_id = spreadsheetId
    template_gid = template_gid
    sheet_range = 'A1:L40'

    service = build_service()

    #call the sheet

    sheet = service.spreadsheets()
    sheetInfo = sheet.get(spreadsheetId = sheet_id).execute()
    num_sheets = len(sheetInfo['sheets'])
    sheet_name = f"{datetime.now().strftime('%h')} '{datetime.now().strftime('%y')}"

    #make request
    request = sheet.values().get(spreadsheetId = sheet_id, range = sheet_range).execute()

    #get pasar uang, obligasi, and saham values
    with open(portfolio_path) as f:
        portfolio = eval(f.read())

    pasar_uang, obligasi, saham  = get_portfolio(portfolio)

    today = date.today()
    latest_date = today - timedelta(days = 1)

    #if new month, make new sheet
    if today.day == 2 or num_sheets == 1:
        if today.month == 1:
            sheet_name = f"{datetime.now().strftime('%h')} '{latest_date.strftime('%y')}"

        request_body = {
            'requests': [
                {

                    'duplicateSheet': {
                        'sourceSheetId': template_gid,
                        'newSheetName' : sheet_name
                    }    
                }
            ]
        }
        
        service.spreadsheets().batchUpdate(spreadsheetId = sheet_id, body= request_body).execute()

    #determine current day to update in sheet
    days_of_the_week = ['Monday', 'Tuesday', "Wednesday", 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day = days_of_the_week[datetime.today().weekday() - 1]
    values = [[day, str(latest_date), pasar_uang, obligasi, saham]]

    body = {'values': values}


    #to account for the late update schedule of pasardana website, update is done in a later day
    if today.day == 1:
        if today.month != 1:
            sheet_name = f"{latest_date.strftime('%h')} '{datetime.now().strftime('%y')}"
        cur_row = int(latest_date.day) + 4
    else:
        cur_row = today.day + 3


    request = sheet.values().update(spreadsheetId = sheet_id, range = f"{sheet_name}!B{cur_row}:H{cur_row}", valueInputOption = 'USER_ENTERED', body = body).execute()
    #execute
    

    return 0

#collapses page 1 to reveal page 2, vice versa
def collapse(layout, key, visible):
    return sg.pin(sg.Column(layout, key = key, visible = visible))

#search for stock prices from pasardana.id
def query(url):
    driver.get(url)
    time.sleep(2.5)
    
    text1 = driver.find_element_by_xpath('/html/body/div/ui-view/ui-view/ui-view/main/div[1]/section[2]/table/tbody/tr/td[4]').text
    text2 = driver.find_element_by_xpath('/html/body/div/ui-view/ui-view/ui-view/main/div[1]/section[1]/h1').text
    stock_type = text1.split('-')[0].strip()
    stock_name = text2.strip()

    if stock_type == 'Pendapatan Tetap':
        stock_type = 'Obligasi'
    
    price = driver.find_element_by_xpath('/html/body/div/ui-view/ui-view/ui-view/main/div[1]/section[2]/table/tbody/tr/td[1]').text
    
    nav = price.split()[1]

    if '.' in nav:
        nav = nav.replace(',','.').replace('.','',1)
    else:
        nav = nav.replace(',','.')

    global info 
    info = [url, stock_name, stock_type, nav]

    return info

#animates the loading GIF
def gif(window):
    
    for i in range(33):
        button, values = window.read(timeout = 3)
        window['loading_gif'].UpdateAnimation(loading_gif, time_between_frames = 3)

#load previously saved table
def load_table(window, portfolio):
    dropdown_values = []
    table_values = [['','','']]
    for d in portfolio:
        for url in d.keys():

            inserted = False

            info = d[url]

            stock_type = info[2]

            if stock_type == 'Pasar Uang':
                index = 0
            elif stock_type == 'Obligasi':
                index = 1
            elif stock_type == 'Saham':
                index = 2

            name = info[1]
            nav = info[-2]
            cur_units = info[-1]

            value = float(cur_units) * float(nav)

            entry = f'''{name} \nUnits: {cur_units} \nValue: Rp.{value:,.2f}'''

            for i in range(len(table_values)):
                #if found empty row 
                if table_values[i][index] == '':
                    table_values[i][index] = entry
                    inserted = True
                    break
                
                #if already in list
                if name in table_values[i][index]:
                    table_values[i][index] = entry
                    inserted = True
                    break

            #if all created rows have no space, create new row
            if not inserted:
                new_lst = ['','','']
                new_lst[index] = entry
                table_values.append(new_lst)

            window['table'].Update(values = table_values)

            dropdown_values.append([str(name), str(stock_type)])

            window['cur_entry'].Update(values = dropdown_values)

    window['table'].Update(values = table_values)

    return table_values, dropdown_values

#refreshes table with updated prices
def refresh_table(window, portfolio):
    for d in portfolio:
        for url in d.keys():
            driver.get(url)
            time.sleep(3)
            price = driver.find_element_by_xpath('/html/body/div/ui-view/ui-view/ui-view/main/div[1]/section[2]/table/tbody/tr/td[1]').text
            nav = price.split()[1]

            if '.' in nav:
                nav = nav.replace(',','.').replace('.','',1)
            else:
                nav = nav.replace(',','.')

            d[url][-2] = nav

    load_table(window, portfolio)

    last_refreshed_date = str(datetime.today())

    return last_refreshed_date

#updates table when stock added to list
def update_table(window, portfolio, stock_type, values, table_values, dropdown_values):

    if stock_type == 'Pasar Uang':
        index = 0
    elif stock_type == 'Obligasi':
        index = 1
    elif stock_type == 'Saham':
        index = 2
    
    inserted = False

    try:
        units = float(values['units'])
        if units <= 0:
            window['error'].Update('Please enter a valid amount!', text_color = 'red')
            return 1

    except ValueError as e:
        window['error'].Update('Please enter a valid amount!', text_color = 'red')
        return 1

    cur_units = units
    url = values['link']

    if url in portfolio[index]:
        portfolio[index][url][-1] = cur_units
    else:
        portfolio[index][url] = info
        portfolio[index][url].append(cur_units)

    cur_units = portfolio[index][url][-1]
    name = portfolio[index][url][1]
    nav = portfolio[index][url][-2]

    value = float(cur_units) * float(nav)
    print(value)
    entry = f'''{name} \nUnits: {cur_units} \nValue: Rp.{value:,.2f}'''

    for i in range(len(table_values)):
        #if found empty row 
        if table_values[i][index] == '' or name in table_values[i][index]:
            table_values[i][index] = entry
            inserted = True
            break

    #if all created rows have no space, create new row
    if not inserted:
        new_lst = ['','','']
        new_lst[index] = entry
        table_values.append(new_lst)

    window['table'].Update(values = table_values)

    dropdown_values.append([str(name), str(stock_type)])
    
    window['cur_entry'].Update(values = dropdown_values)

    updated_portfolio = portfolio

    return updated_portfolio

#updates entry in the table
def update_entry(window, stock_type, portfolio, name, cur_units):
    if stock_type == 'Pasar Uang':
        index = 0
    elif stock_type == 'Obligasi':
        index = 1
    elif stock_type == 'Saham':
        index = 2

    for key in portfolio[index]:
        if portfolio[index][key][1] == name:
            #update units amount
            if type(cur_units) not in (float, int):
                return 1
            portfolio[index][key][-1] = cur_units
    
    return load_table(window, portfolio)


#base 64 representation of the loading GIF
loading_gif = b'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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA='

