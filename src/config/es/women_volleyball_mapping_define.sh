#!/bin/bash 

curl -X PUT "http://localhost:9200/women_volleyball?pretty=true" -H "Content-Type: application/json" -d '
{
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "name":          {"type": "text"   },
            "age":           {"type": "integer"},
            "year":          {"type": "integer"},
            "month":         {"type": "integer"},
            "day":           {"type": "integer"},
            "height":        {"type": "integer"},
            "weight":        {"type": "integer"},
            "position":      {"type": "keyword"},
            "back_number":   {"type": "integer"},
            "team":          {"type": "keyword"},
            "img_file_path": {"type": "text"   },
            "save_file_name": {"type": "keyword"}
        }
    }
}'
