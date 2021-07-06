# Investment Portfolio App
#### Video Demo:  <URL HERE>
#### Description:

This is a Python-based application for creating personalized mutual funds 
portfolios based on the <br>Indonesian stock exchange. The app has **two** main functionalities:

1. Storing personal portfolio information (a.k.a. stocks owned, how many units, 
total value)
2. Linking the portfolio information to a Google Sheets file, where the total 
values can be updated daily <br>(and automated, which is optional 
and requires extra steps)

#### How it Works:

- The app uses [PySimpleGUI](https://pysimplegui.readthedocs.io/en/latest/) as the framework for the front-end UI that users interact with. <br> 
- To get the daily stock prices, the app uses [Selenium](https://selenium-python.readthedocs.io/) and [Chromedriver](https://chromedriver.chromium.org/) to scrape 
stock prices off <br> of [Pasardana](https://pasardana.id/), a popular website to get information about stocks, bonds, and other commodities <br>in the Indonesian market. A simple query takes information about its current NAV (Net Asset Value),<br> which will determine the final price based on how many units the owner has.
- All inputted stocks will be stored in a table, separated by specific categories (Pasar Uang, Obligasi <br> and Saham). Entries can be removed and updated accordingly. There is also an option to load <br> previously saved portfolios (in .txt format) and save newly made ones.
- After finalizing and saving the table, the user will be prompted to make a copy of a Google Sheets <br> file to store the portfolio information and track daily prices. The [template](https://bit.ly/InvestmentPortfolioTemplate) groups all prices based on <br>their categories, and sums them all up in the end. Then, the program uses the Google Sheets API <BR> to automate the sheets updating process (which requires manual authorization in its first use)
- **[OPTIONAL]**: Automating the process of updating the information daily is also possible using <br> the Windows Task Scheduler. Saving webscraper.py as a .bat file will make this possible. More <br> information [here](https://towardsdatascience.com/automate-your-python-scripts-with-task-scheduler-661d0a40b279), on a blog post made by Vincent Tatan.

#### Files:

- *chromedriver* (folder): Stores the chromedriver.exe file used for webscraping purposes
- *savefiles* (folder): Stores the previously saved portfolios in the form of a text file (.txt)
- *main.py* (file): The python version of the application (Note: to change this to .exe, install pyinstaller, <br> via: `python -m pip install pyinstaller`, then execute this command in the working directory of <br> the program: `pyinstaller --onefile main.py`
- *helper.py* (file): Stores all the functions that run the application, such as loading previously saved <br> tables, saving new tables, removing table entries, making queries to the Pasardana website, etc.
- *credentials.json* (file): Stores the API credentials necessary to run the Google Sheets API, which will  <br> automatically update the spreadsheet daily by refreshing the table first then running the program. <br>***DO NOT delete this!***

#### Design Choices:
- I was struggling to find an easy way to save previously made portfolios. I initially thought about <br> storing a long list of tuples, which stored the Pasardana URL and the number of units owned. <br>However, this approach was heavilytime consuming, as every time the user loaded the saved file,  <br> they would have to make queries for every single entry again. So, I ended up making a list of  <br> dictionaries (one for each category) and stored the URL and other basic information (name,  <br> category, units owned, and its current NAV).
- I initially had one large file, where all the functions and GUI code were housed. However, the code <br> wasn't really concise and keeping track of everything was really difficult. So, I resorted to separating <br> the functions and GUI elements into two different files, which ultimately made the code much more <br> legible.





