from __future__ import print_function

import csv
import config
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch import helpers


def connectES(esEndPoint, auth):
    print('Connecting to the ES Endpoint {0}'.format(esEndPoint))
    try:
        esClient = Elasticsearch(
            hosts=[{'host': esEndPoint, 'port': 443}],
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            http_auth=auth)
        return esClient
    except Exception as E:
        print("Unable to connect to {0}".format(esEndPoint))
        print(E)
        exit(3)


def createIndex(esClient, indexName):
    try:
        res = esClient.indices.exists(indexName)
        print("Index Exists ... {}".format(res))
        if res is False:
            indexDoc = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                }
            }
            esClient.indices.create(indexName, body=indexDoc)
            return 1
    except Exception as E:
        print("Unable to Create Index {0}".format(indexName))
        print(E)
        exit(4)


def indexBulkCsv(esClient, indexName, doc_type, filepath, fieldnames, delimiter='|', encoding='utf-8'):
    with open(filepath, encoding=encoding) as f:
        reader = csv.DictReader(f,  fieldnames=fieldnames, delimiter=delimiter)
        helpers.bulk(esClient, reader,  index=indexName, doc_type=doc_type, request_timeout=30)

def search(esClient, indexName, query, sort, size):
    res = esClient.search(index=indexName, body={"query": query, "size": size, "sort":sort})
    return res

def search_movies_by_ids(esClient, indexName, movie_ids):
    movie_query = {
        "ids": {
            "type": config.DOCTYPE_MOVIES,
            "values": movie_ids
        }

    }
    search_movies_result = search(esClient, indexName, movie_query, {}, 100000)["hits"]["hits"]
    return search_movies_result