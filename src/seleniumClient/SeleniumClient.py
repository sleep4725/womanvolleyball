from selenium import webdriver
import os
import sys 
rootPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(rootPath)

##
#@author JunHyeon.Kim
#@date 20220417
##
class SeleniumClient:
    
    @classmethod
    def get_selenium_client(cls)-> webdriver.Chrome:
        global rootPath
        options = webdriver.ChromeOptions()
        options.add_argument('window-size=1920x1080')
        options.add_argument('headless')
        options.add_argument("disable-gpu")
        # 혹은 options.add_argument("--disable-gpu")
        
        driver = webdriver.Chrome(f'{rootPath}/config/chromeDriver/chromedriver', options=options)
        return driver
        