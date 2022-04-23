import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import elasticsearch
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from es.ElasticConfig import ElasticConfig

##
#@author JunHyeon.Kim 
#@date 20220412
##
class EsClusterHealthError(Exception):
    
    def __str__(self):
        return "Elastic Cluster에 문제가 있습니다."
    
class ElasticClient:

    def __init__(self):
        self.action = list()
        self.index = "women_volleyball"
        self.documentIdTemplete = "{teamName}_{playerName}_no_{playerBacknum}"
        self.client = ElasticClient.ret_es_client()
    
    def es_bulk_insert(self):
        """
		:param:
		:return:
        """
        if len(self.action):
            try:

                bulk(self.client, self.action)
            except:
                print("es insert fail") 
            else:
                print("es insert success")

    @classmethod 
    def ret_es_client(cls)-> Elasticsearch:
        esHosts = [
            "{http}://{ip}:{port}".format(http= ElasticConfig.ES_HTTP_PROTOCOL, 
                                          ip= u, 
                                          port= ElasticConfig.ES_PORT) 
            for u in ElasticConfig.ES_HOST_SERV]
        try:
            
            es = Elasticsearch(esHosts)
        except elasticsearch.exceptions.ConnectionError as err:
            print(err)
        except:
            print("err")
        else:
            response = es.cluster.health()
            if response["status"] in ["green", "yellow"]:
                print("elastic cluster health good!!!")
                return es
            else:
                raise EsClusterHealthError          

