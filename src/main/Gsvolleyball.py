"""
filename Gsvolleyball.py
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
import ssl 
ssl._create_default_https_context = ssl._create_unverified_context

import urllib.request as urlreq

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

##
# @author JunHyeon.Kim
# @date 20220416
# gs 칼텍스
##
class Gsvolleyball(VolleyballTemplete, ElasticClient):

    def __init__(self)-> None:
        VolleyballTemplete.__init__(self)
        ElasticClient.__init__(self)
        self.cllUrl = "https://www.gsvolleyball.com/team/player"
        self.teamName = "gs칼텍스"

    def getAccessPlayerUrl(self)-> None:
        """
        :param:
        :return:
        """
        response = requests.get(self.cllUrl, headers=ReqUrlConstants.HEADER)
        if response.status_code == 200:
            bsObject = BeautifulSoup(response.text, "html.parser")
            teamList = bsObject.select_one("ul.teamListUl")
            liList = teamList.select("li")

            for a in liList:
                href = a.select_one("a").attrs["href"]
                srcUrl = a.select_one("a > div.pPhotoWrap > img").attrs["src"]
                urlParseOpt = urlparse(self.cllUrl)
                reqUrl = f"{urlParseOpt.scheme}://{urlParseOpt.netloc}{href}"

                self.playerUrl.append({
                        "reqUrl": reqUrl,
                        "srcUrl": srcUrl
                    })

            response.close()
        else:
            """ except code """

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
            
    def getPlayerDetailInfor(self):
        """
        :param:
        :return:
        """
        for u in self.playerUrl:
            response = requests.get(u["reqUrl"], headers= ReqUrlConstants.HEADER)

            if response.status_code == 200:
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

                bsObject = BeautifulSoup(response.text, "html.parser")
                playerDetailTable = bsObject.select_one("div.tDetailInfo")
                tdi_1 = playerDetailTable.select_one("div > div.tdi_1")
                tdi_2 = playerDetailTable.select_one("div > div.tdi_2")
                tdi_3 = playerDetailTable.select_one("div > div.tdi_3")

                div_list =  tdi_1.select("div")

                for d in div_list:
                    dl = d.select_one("dl")
                    dt = str(dl.select_one("dt").text).strip()

                    if dt == "number":
                        # 선수 백넘버
                        element.back_number = int(str(dl.select_one("dd.tDetailNumber").text).strip().lstrip("0"))

                    elif dt == "position":
                        # 선수 포지션
                        element.position = str(dl.select_one("dd.tDetailPosition").text).strip()

                # 선수 이름
                element.name = str(tdi_2.select_one("strong").text).strip()

                dlList = tdi_3.select("dl")
                for dl in dlList:
                    dtValue = str(dl.select_one("dt").text)
                    # 선수 생년월일
                    if dtValue == "생년월일":
                        plyBrthDay = str(dl.select_one("dd").text).replace(" ", "").replace("년", " ").replace("월", " ").replace("일", " ").split(" ")
                        element.age = int(TimeSett.currentYear) - int(plyBrthDay[0])
                        element.year = int(plyBrthDay[0])
                        element.month = int(plyBrthDay[1])
                        element.day = int(plyBrthDay[2])

                    # 선수 키
                    elif dtValue == "신장":
                        element.height = int(str(dl.select_one("dd").text).strip().rstrip("cm"))

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
        
        self.es_bulk_insert()            
                
if __name__ == "__main__":
    o = Gsvolleyball()
    o.getAccessPlayerUrl()
    o.getPlayerDetailInfor()
