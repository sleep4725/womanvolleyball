"""
filename PinkSpiders.py
"""
import os
from select import select
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

##
# @author JunHyeon.Kim
# @date 20220416
# 흥국생명
##
class PinkSpiders(VolleyballTemplete, ElasticClient):

    def __init__(self)-> None:
        VolleyballTemplete.__init__(self)
        ElasticClient.__init__(self) 
        self.url = "https://www.pinkspiders.co.kr"
        self.cllUrl = f"{self.url}/team/player_list.php"
        self.teamName = "흥국생명"

    def getAccessPlayerUrl(self)-> None:
        """
        :param:
        :return:
        """
        chromeClient = SeleniumClient.get_selenium_client() 
        chromeClient.get(self.cllUrl)
        chromeClient.implicitly_wait(3)
        
        bsObject = BeautifulSoup(chromeClient.page_source, "html.parser")
        playerList = bsObject.select_one("div.row_group.col_3.player_list")
        playerList = playerList.select("a")
        
        for a in playerList:
            self.playerUrl.append(
                {
                    "reqUrl": "{url}/team{url_path}".format(url=self.url, url_path=str(a.attrs["href"]).lstrip(".")),
                    "srcUrl": "{url}{url_path}".format(url=self.url, url_path= a.select_one("img").attrs["src"])
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
        try:
            
            img_download_path = self.imgDownloadTemplate + saveFileNm
            urlreq.urlretrieve(url= imgUrl, filename= img_download_path)
        except KeyError as err:
            print(err)
        except:
            print("player image download fail !!")
        else:
            print("imgurl: {}".format(imgUrl))
        finally:
            return img_download_path 
        
    def getPlayerDetailInfor(self)-> None:
        """
        :param:
        :return:
        """
        for u in self.playerUrl:
            print(u["reqUrl"])
            chromeClient = SeleniumClient.get_selenium_client()
            chromeClient.get(u["reqUrl"])
            chromeClient.implicitly_wait(3)
            
            element = Player(
                    name="",        # type str (o)
                    age=0,          # type int (o)
                    year=0,         # type int (o)
                    month=0,        # type int (o)
                    day=0,          # type int (o)
                    height=0,       # type int (o)
                    weight=0,       # type int (x)
                    position="",    # type str (o)
                    back_number=0,  # type int (o)
                    team=self.teamName, # type str (o) 
                    img_file_path="", # type str (o)
                    save_file_name="" # type str (o)
            
            )
            
            playerFrameG = chromeClient.find_element(By.CLASS_NAME, "player_profile").\
                                    find_element(By.CLASS_NAME, "wrap.row_group").\
                                    find_element(By.CLASS_NAME, "col.frame_g")
            
            playerInformationList = playerFrameG.find_element(By.TAG_NAME, "ul").find_elements(By.TAG_NAME, "li") 
            '''
                생년월일 : 2001.01.25
                신장 : 180cm
                출신학교 : 중대초-일신여중-일신여고
                프로입단년도 : 2019-20
            '''
            for p in playerInformationList:
                infor = str(p.text).split(":")  
                key = str(infor[0]).strip()
                if key == "생년월일":
                    playerBirthday = str(infor[1]).strip().split(".")
                    # player birthday year
                    element.year += int(playerBirthday[0])
                    # player age
                    element.age  += int(TimeSett.currentYear) - element.year 
                    # player birthday month
                    element.month += int(str(playerBirthday[1]).strip().lstrip("0"))
                    # player birthday day
                    element.day += int(str(playerBirthday[2]).strip().lstrip("0")) 
                elif key == "신장":
                    element.height += int(str(infor[1]).strip().rstrip("cm")) 
                    
            txtG = playerFrameG.find_element(By.CLASS_NAME, "txt_g")
            # player position 
            pink = txtG.find_element(By.CLASS_NAME, "col_pink")            
            element.position += str(pink.text).strip() 
            
            # player backnumber 
            playerNo = txtG.find_element(By.CLASS_NAME, "player_no")         
            element.back_number += int(str(playerNo.text).lstrip("NO.").lstrip("0")) 
            
            # player name
            playerNm = str(txtG.find_element(By.TAG_NAME, "strong").text).strip() 
            element.name = playerNm
            
            saveFileNm = self.saveFileName.format(teamName= self.teamName, 
                                         playerBacknum=element.back_number,
                                         playerName= element.name)
            
            element.save_file_name = saveFileNm
            element.img_file_path = self.playerImgDownload(imgUrl= u["srcUrl"], saveFileNm= saveFileNm) 
            
            result = dataclasses.asdict(element)
            
            self.action.append(
                    {
                        "_index": self.index,
                        "_id": self.documentIdTemplete.format(
                                teamName= result["team"]
                                ,playerName= result["name"]
                                ,playerBacknum= str(result["back_number"])
                        ),
                        "_source": result
                    }
            )    
            chromeClient.close()

        self.es_bulk_insert() 

if __name__ == "__main__":
    o = PinkSpiders()
    o.getAccessPlayerUrl()  
    o.getPlayerDetailInfor()