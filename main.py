from threading import local
import PySimpleGUI as sg
from helper import *
from helper import table_values
from helper import portfolio as pf
from helper import dropdown_values
import os

#the main application
def main():

    info = []
    tv = table_values
    dv = dropdown_values
    
    toggle_sheets_section = False
    toggle_instructions = False

    ###### GUI ######

    #CREATE LAYOUT COMPONENTS

    local_portfolio = [{},{},{}]

    sg.theme('DefaultNoMoreNagging')

    #first page
    stock_input = [
        [sg.Text('Investment Portfolio App', font = 'Helvetica', justification = 'center')],
        [sg.Text()],
        [sg.Text('Enter PasarDana Link (include https://)')],
        [
            sg.Input('https://pasardana.id/fund/', key = 'link'),
            sg.Button('Check', enable_events = True, key = 'check', bind_return_key = True),
            sg.Image('', data = loading_gif, key = 'loading_gif', visible = False)
        ],
        [sg.Multiline('', key = 'check_result', size = (43,1))],
        [sg.Text('Enter number of units owned: ', key = 'units_text', justification='left')],
        [
            sg.Input('', disabled = True, key = 'units'),
            sg.Button('Add to List', enable_events = True, key ='add', disabled = True, bind_return_key = True),
        ],
        [sg.Text(size = (20,1), key = 'error')],
        [sg.Button('Refresh Table', key = 'refresh', disabled = True, enable_events= True), sg.Text('Last refreshed: ', size = (50,1), key = 'last_refreshed_date')],
        [sg.Table(
            values = tv, 
            auto_size_columns= False, 
            headings = ['Pasar Uang', 'Obligasi', 'Saham'], 
            key = 'table',
            justification = 'left',
            def_col_width = 30,
            enable_events = True,
            alternating_row_color = 'lightblue',
            num_rows= 3,
            row_height = 49
            )
        ],
        [sg.Text('Update table entry:')],
        [
            sg.DropDown([], key = 'cur_entry', enable_events= True, size = (50,6)),
            sg.Button('Update', key = 'update_entry', disabled = True),
            sg.Button('Remove', key = 'remove_entry', disabled = True),
        ],
        [sg.Text('Units'), sg.In(key = 'update_units')],
        [sg.Text(size = (20,1),key = 'error_update_entry')],
        [
            sg.In(key = 'load', visible = False, enable_events= True),
            sg.FileBrowse('Load', key = 'load_button', initial_folder= 'savefiles'),
            sg.In(key = 'save', visible = False, enable_events = True),
            sg.FileSaveAs(target = 'save', key= 'savepath', file_types = (('Text Files','*.txt'),), initial_folder = 'savefiles', enable_events= True)
        ],
        [sg.Text()],
        [sg.Button('Next', key = 'next', enable_events = True, disabled = True)]
    ]

    #second page
    sheets_section = [
        [sg.Text('Investment Portfolio App', font = 'Helvetica', justification = 'center')],
        [sg.Text()],
        [sg.Button('Instructions', key = 'instructions_button', enable_events= True)],
        [sg.Multiline("""INSTRUCTIONS
        0. Open the sheets template URL : 
            bit.ly/InvestmentPortfolioTemplate
        1. Go to File > Make a Copy 
        2. Save the new file in your preferred location
        3. Share the file in the top right corner (editor mode) to the script's service account, to allow automation: 
            financialportfolio@financial-portfolio-webscraper.iam.gserviceaccount.com 
        4. Input the new file's url to the program
        5. Click execute to automate""", visible = toggle_instructions, k = 'instructions', enable_events= True, disabled = True, size = (100,10))],
        [sg.Text('Enter your Google Sheets Link!')],
        [sg.In(key = 'sheet_url', size = (100,1), enable_events= True), sg.Button('Execute', enable_events = True, key = 'execute')],
        [sg.Text('')],
        [sg.Button('Back', key = 'back', enable_events = True)],
        [sg.Text(size = (20,1),k = 'message')]
    ]

    #CREATE THE LAYOUT
    layout = [
        [collapse(stock_input, 'stock_input', True),
        collapse(sheets_section, 'sheets', False)]
    ]

    #CREATE THE WINDOW
    window = sg.Window('investment app', layout, finalize = True, resizable= True)

    #READ THE WINDOW
    while True:
        #checks if there are no previous saved files
        if len(os.listdir('savefiles')) == 0:
            window['load_button'].Update(disabled = True)
        else:
            window['load_button'].Update(disabled = False)      

        #reads the window
        button, values = window.read(timeout = 3)

        #exits the program
        if button in ['Exit', sg.WIN_CLOSED]:
            print(button, values)
            break
        
        #checks if dropdown menu is empty or not
        if len(values['cur_entry']) != 0:
            window['update_entry'].Update(disabled = False)
            window['remove_entry'].Update(disabled = False)

        #runs the loading gif for 'check'
        window['loading_gif'].UpdateAnimation(loading_gif, time_between_frames = 3)

        #finds the stock prices from pasardana.id
        if button == 'check':
            
            window['loading_gif'].Update(visible = True)

            gif(window)

            window.write_event_value('start','')

            print(button, values)

        elif button == 'start':
            try:
                url, name, stock_type, nav = query(values['link'])

                info = [url, name, stock_type, nav]

                message = f'Check Complete! Item is {name} of type {stock_type} \nNet Asset Value: Rp.{float(nav):,.2f}'

                #output result of check
                window['check_result'].Update(message, text_color = 'green')

                #enable add to list button if link is valid
                window['add'].Update(disabled = False)

                #make units owned button visible
                window['units'].Update(disabled = False)

            except Exception as e:
                print(e)
                message = 'Link invalid! Please try again!'

                #output invalid result
                window['check_result'].Update(message, text_color = 'red')
                
                #add to list remains disabled
                window['add'].Update(disabled = True)
                window['units'].Update(disabled = True)

            window['loading_gif'].Update(visible = False)

            print(button, values)

        #adds the query to the table
        if button == 'add':

            updated_portfolio = update_table(window, local_portfolio, stock_type, values, tv, dv)

            local_portfolio = updated_portfolio

            #empty input 
            window['units'].Update('')

            if updated_portfolio:
                #disable add button
                window['add'].Update(disabled = True)

                #reset the link input
                window['link'].Update('https://pasardana.id/fund/')

                #disable units
                window['units'].Update(disabled = True)

                #reset check
                window['check_result'].Update('')

                window['error'].Update('')


            print(button, values)

            print(local_portfolio)

        #loads previously saved tables
        if button == 'load':
            path = values['load']

            if path == '':
                continue
            
            with open(path) as file:
                portfolio = eval(file.read())

            tv, dv = load_table(window, portfolio)

            local_portfolio = portfolio

            print(portfolio)
            print(button, values)
            
            window['next'].Update(disabled = False)
            window['refresh'].Update(disabled = False)

        #saves current table
        if button == 'save':
            path = values['savepath']

            if path == '':
                continue
            
            with open(path, 'w+') as file:
                file.write(str(local_portfolio))
            
            print(button, values)
            window['next'].Update(disabled = False)
            window['refresh'].Update(disabled = False)

        #alerts user to double check table before updating the sheets file
        if button in ('next', 'back'):
            toggle_sheets_section = not toggle_sheets_section
            window['stock_input'].Update(visible = not toggle_sheets_section)
            window['sheets'].Update(visible = toggle_sheets_section)
            if button == 'next':
                sg.Popup('Check the table before finalizing. The execution process cannot be reversed!')

        #shows instructions for updating to sheets file
        if button == 'instructions_button':
            toggle_instructions = not toggle_instructions
            window['instructions'].Update(visible = toggle_instructions)

        #executes automatic sheet update
        if button == 'execute':
            sheet_url = values['sheet_url']
            try:
                spreadsheetId = sheet_url.split('/')[5]
                template_gid = sheet_url.split('/')[-1].split('=')[1]
                portfolio_path = path
            except Exception:
                window['message'].Update('Pleas input valid url')
                continue
            create_spreadsheet(spreadsheetId, template_gid, portfolio_path)
            print('yes')
            window['message'].Update('Spreadsheet update complete!', text_color = 'green')

        #updates number of units owned for entry in table
        if button == 'update_entry':

            try:
                cur_name, cur_stock_type = values['cur_entry']

            except Exception:
                continue

            try:
                cur_units = float(values['update_units'])
            except Exception:
                window['error_update_entry'].Update('Please input a valid number!', text_color = 'red')
                continue

            res = update_entry(window, cur_stock_type, local_portfolio, cur_name, cur_units)

            window['update_units'].Update('')

            print(local_portfolio)

        #deletes entry from table
        if button == 'remove_entry':
            try:
                cur_name, cur_stock_type = values['cur_entry']
            except Exception:
                continue
            if cur_stock_type == 'Pasar Uang':
                index = 0
            if cur_stock_type == 'Obligasi':
                index = 1
            if cur_stock_type == 'Saham':
                index = 2

            for key in local_portfolio[index]:
                if cur_name == local_portfolio[index][key][1]:
                    local_portfolio[index].pop(key)
                    break

            load_table(window, local_portfolio)

            print(local_portfolio)

        #refreshes table daily to accomodate changing prices     
        if button == 'refresh':
            last_refreshed_date = refresh_table(window, portfolio)
            print(last_refreshed_date)
            window['last_refreshed_date'].Update(f'Last refreshed: {last_refreshed_date}')
            print(portfolio, values)

if __name__ == '__main__':
    main()

            

            


        
            

            

            
            



            






