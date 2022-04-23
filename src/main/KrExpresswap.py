"""
filename KrExpressway.py
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
# @email sleep4725@naver.com
# @date 20220412
# 한국 도로공사
##

"""
VolleyballTemplete 
ElasticClient 
"""
class KrExpressway(VolleyballTemplete, ElasticClient):

    def __init__(self)-> None:
        VolleyballTemplete.__init__(self)
        ElasticClient.__init__(self)
        self.cllUrl = "https://www.exsportsclub.com/player/player/"
        self.teamName = "한국도로공사"

    def getAccessPlayerUrl(self)-> None:
        """
        :param:
        :return:
        """
        response = requests.get(self.cllUrl, headers=ReqUrlConstants.HEADER)
        if response.status_code == 200:
            bsObject = BeautifulSoup(response.text, "html.parser")

            tags = bsObject.select(
                    "{} > {}".format(
                        "div.wpb_text_column.wpb_content_element.web-player-bt",
                        "div.wpb_wrapper"))

            for t in tags:
                href = t.select_one("p > a").attrs["href"]
                urlParseOpt = urlparse(self.cllUrl)
                reqUrl = f"{urlParseOpt.scheme}://{urlParseOpt.netloc}{href}"
                self.playerUrl.append(reqUrl)
            
            response.close()
        else:
            """ except code """
    
    def playerImgDownload(self, bsObject: BeautifulSoup, saveFileNm: str)-> str:
        """
        :param: bsObject 
        :param: playername 선수 이름 
        :param: playerbacknum 선수 백넘버
        :return: 저장된 파일의 경로를 리턴한다.
        """
        try:
            
            divTag = bsObject.select_one("div.vc_single_image-wrapper.vc_box_border_grey")
            img = divTag.select_one("img") 
            img = img.attrs["src"]
            
            img_download_path = self.imgDownloadTemplate + saveFileNm
            urlreq.urlretrieve(url= img, filename= img_download_path)
        except KeyError as err:
            print(err)
        except:
            print("player image download fail !!")
        else:
            print("imgurl: {}".format(img))
        finally:
            return img_download_path
        
    def getPlayerDetailInfor(self)-> None:
        """
        :param:
        :return:
        """
        for u in self.playerUrl:
            response = requests.get(u, headers= ReqUrlConstants.HEADER)
            
            if response.status_code == 200:
                bsObject = BeautifulSoup(response.text, "html.parser")
                
                playerDetailTable = bsObject.select_one("table.web-main-player-detail-table")
                playerTbody = playerDetailTable.select_one("tbody")
                playerTrTags = playerTbody.select("tr")
                
                element = Player(
                        name="",       # type str (o)
                        age=0,         # type int (o)
                        year=0,        # type int (o) 
                        month=0,       # type int (o)
                        day=0,         # type int (o)
                        height=0,      # type int (o)
                        weight=0,      # type int (o)
                        position="",   # type str (o)
                        back_number=0, # type int (o)
                        team="",       # type str (o)  
                        img_file_path="",  # type str (o)
                        save_file_name=""  # type str (o)
                ) 

                for tr in playerTrTags:
                    tdList = [td.text for td in tr.select("td")]
                    if tdList[0] == "이름":
                        plyName = tdList[1]
                        plyNumb = re.findall(StringHandler.bracketExtraction, plyName)[0]
                        plyNumb = int(str(plyNumb).lstrip("NO.").lstrip("0"))
                        plyName = str(re.sub(StringHandler.bracketRemove, "", plyName)).strip()
                        #print("선수이름: {} / 선수 등번호: {}".format(plyName, plyNumb))
                        
                        plyBrthDay = str(tdList[3]).replace(" ", "").replace("년", " ").replace("월", " ").replace("일", " ").split(" ")
                        plyAge = int(TimeSett.currentYear) - int(plyBrthDay[0])
                        plyYear = int(plyBrthDay[0])
                        plyMonth = int(plyBrthDay[1])
                        plyDay = int(plyBrthDay[2])

                        #result = "선수 나이: {}/ 선수 년도: {}/ 선수 월: {}/ 선수 일: {}".format(plyAge, plyYear, plyMonth, plyDay)
                        #print(result)    
                        
                        element.name = plyName 
                        element.age = plyAge 
                        element.year = plyYear 
                        element.month = plyMonth
                        element.day = plyDay 
                        element.back_number = plyNumb
                        element.team = self.teamName

                    elif tdList[0] == "신장 / 체중":
                        plyH, plyW = str(tdList[1]).split("/")
                        plyH = int(str(plyH).strip().rstrip("cm"))
                        plyW = int(str(plyW).strip().rstrip("kg"))
                        #print("선수 키: {} / 선수 몸무게 : {}".format(plyH, plyW))
                        
                        element.height = plyH
                        element.weight = plyW 

                    elif tdList[0] == "포지션":
                        plyPosition = self.positionMatch[str(tdList[1]).strip()]
                        #print("선수 포지션: {}".format(plyPosition))
                        
                        element.position = plyPosition
                
                saveFileNm = self.saveFileName.format(teamName= self.teamName, 
                                         playerBacknum=element.back_number,
                                         playerName= element.name)
                
                element.save_file_name = saveFileNm
                element.img_file_path= self.playerImgDownload(bsObject= bsObject, saveFileNm= saveFileNm)
                
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
    o = KrExpressway()
    o.getAccessPlayerUrl()
    o.getPlayerDetailInfor()
    
