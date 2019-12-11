import os
from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch_wrapper import connectES
import config

def _get_es_client():
    # es
    esdomain = os.environ['elasticsearch_domain_name']
    region = os.environ['AWS_REGION']
    print(region)
    auth = AWSRequestsAuth(aws_access_key=os.environ['AWS_ACCESS_KEY_ID'],
                           aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                           aws_token=os.environ['AWS_SESSION_TOKEN'],
                           aws_host=esdomain,
                           aws_region=region,
                           aws_service='es')
    esClient = connectES(esdomain, auth)
    return esClient

def get_index(dataset_id):
    indexName = config.DataSet[dataset_id][config.INDEXNAME]
    return indexName

def search_popular_movies(event, context):
    dataset_id = event["params"]["querystring"]["dataset_id"]
    esClient = _get_es_client()
    indexName = get_index(dataset_id)
    size = 3
    sort = {"mo"}
    res = esClient.search(index=indexName, body={"query": query, "size": size, "sort":sort})
    return res
