"""
filename PinkSpiders.py
"""
from lib2to3.pgen2.token import AT
import os
from select import select
import string
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
import ssl 
ssl._create_default_https_context = ssl._create_unverified_context 

import urllib.request as urlreq

from selenium.webdriver.common.by import By
import dataclasses
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re

from common.ReqUrl import ReqUrlConstants
from common.TimeSett import TimeSett
from model.Templete import VolleyballTemplete
from model.Player import Player
from util.StringHandler import StringHandler
from es.ElasticClient import ElasticClient 
from seleniumClient.SeleniumClient import SeleniumClient

'''
    @author JunHyeon.Kim
    @date 20220417
    IBK 기업 은행
'''
class IBK(VolleyballTemplete, ElasticClient):

    def __init__(self)-> None:
        VolleyballTemplete.__init__(self)
        ElasticClient.__init__(self) 
        self.url = "http://sports.ibk.co.kr"
        self.urlPath = "/volleyball/team"
        self.cllUrl = f"{self.url}{self.urlPath}/player_list.php"
        self.teamName = "IBK기업은행"
    
    def getAccessPlayerUrl(self)-> None:
        """
        :param:
        :return:
        """
        chromeClient = SeleniumClient.get_selenium_client() 
        chromeClient.get(self.cllUrl)
        chromeClient.implicitly_wait(3)
        
        bsObject = BeautifulSoup(chromeClient.page_source, "html.parser")
        playerList = bsObject.select("div.plist")

         
        for a in playerList:
            for l in a.select_one("ul").select("li"):
                aTag = l.select_one("a")
                # ./player_detail.php?p_code=0000476
                href = str(aTag.attrs['href']).lstrip(".")
                
                imgTag = aTag.select_one("img") 
                # ../../images/volleyball/player/player_list_0000476.png?ver=1.1
                srcUrl = str(imgTag.attrs['src']).lstrip("../")
                
                self.playerUrl.append(
                    {
                        "reqUrl": f"{self.url}{self.urlPath}{href}"
                        ,"srcUrl": f"{self.url}/{srcUrl}"
                    }
                )
        
        chromeClient.close()

    def playerImgDownload(self, imgUrl: str, saveFileNm: str)-> str:
        """
        :imgUrl:
        :element: img_file_path 경로를 셋팅하기 위해 사용
        :playername:
        :playerbacknum:
        """

    def getPlayerDetailInfor(self)-> None:
        """
        :param:
        :return:
        """
        """
        :param:
        :return:
        """
        for u in self.playerUrl:
            response = requests.get(u["reqUrl"], headers= ReqUrlConstants.HEADER)

            if response.status_code == 200:
                element = Player(
                        name="",        # type str ()
                        age=0,          # type int ()
                        year=0,         # type int ()
                        month=0,        # type int ()
                        day=0,          # type int ()
                        height=0,       # type int ()
                        weight=0,       # type int ()
                        position="",    # type str (o)
                        back_number=0,  # type int (o)
                        team=self.teamName, # type str () 
                        img_file_path="", # type str ()
                        save_file_name="" # type str ()
                        ) 

                bsObject = BeautifulSoup(response.text, "html.parser")              
                # player-position
                playerPosition = str(bsObject.select_one("div.pic > span.position").string).strip()
                element.position = playerPosition
                
                playerProfile =  bsObject.select_one("div.profile")
                # player-backnumber
                playerBacknumber = playerProfile.select_one("div.pname")
                
                # player-name
                playerNm = playerProfile.select_one("div.pname > strong")
                playerNm = str(playerNm.text).strip()
                element.name = playerNm 
                 
                playerBacknumber = int(str(playerBacknumber.text).strip().rstrip(playerNm).lstrip("0"))
                element.back_number = playerBacknumber
                
                proList = playerProfile.select_one("div.pro_list > ul")
                proList = proList.select("li")
                for p in proList:
                    key = p.select_one("strong")
                    key = str(key.string).replace(":", "").rstrip(" ")
                    if (key == "생년월일"):
                        playerBirthdayList = str(p.text).\
                        lstrip("\n"+key).\
                        strip(" ").\
                        lstrip(":").\
                        replace(" ", "").\
                        replace("년", " ").\
                        replace("월", " ").\
                        replace("일", " ").\
                        split(" ")
                       
                        element.year = playerBirthdayList[0] # 년 
                        element.month = int(str(playerBirthdayList[1]).lstrip("0")) # 월
                        element.day = int(str(playerBirthdayList[2]).lstrip("0")) # 일
                    elif (key == "신장"):
                        playerHeight = 
                    
                    
                print(playerNm, playerBacknumber)
                
                
                ''' 
                # player-name
                playerNm = playerProfile.select_one("div.pname > strong")
                playerNm = str(playerNm.string).strip()
                
                checkPrint = """
                position: {plyPosition} 
                backnumber: {plyBacknm} 
                name: {plyNm}""".format(
                    plyPosition= playerPosition, 
                    plyBacknm= playerBacknumber,
                    plyNm= playerNm)
                
                print(checkPrint)
                '''   
if __name__ == "__main__":
    o = IBK()
    o.getAccessPlayerUrl()
    o.getPlayerDetailInfor()    