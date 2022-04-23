from abc import *
import os 


class VolleyballTemplete(metaclass=ABCMeta):
    
    def __init__(self):
        self.playerUrl = list()
        self.projectRootPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.saveFileName = "{teamName}_NO_{playerBacknum}_{playerName}.jpg"  
        self.imgDownloadTemplate = f"{self.projectRootPath}/web/static/"
        self.positionMatch  = {
                "리베로": "LIBERO",
                "라이트": "RIGHT",
                "레프트": "LEFT",
                "세터"  : "SETTER",
                "센터"  : "CENTER"}

    @abstractmethod
    def getAccessPlayerUrl(self):
        """
        """
        pass
    
    @abstractmethod
    def playerImgDownload(self):
        """
        """

    
    @abstractmethod
    def getPlayerDetailInfor(self):
        """
        """
        pass
