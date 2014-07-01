#!/usr/bin/env python
import httplib
import json
import sys

ELASTIC_SEARCH_HOST = '127.0.0.1'
ELASTIC_SEARCH_PORT = 9200

def responseToTweetFormat(response):
    outputJSONFields = ['username', 'lang', 'screen_name',
            'in_reply_to_id', 'text', 'description', 'userid', 'tweetid']
    return map(
            lambda x : {key: x['_source'][key] for key in x['_source'] if key in outputJSONFields}, response['hits']['hits'])


if len(sys.argv) != 2:
    print("usage: match_tweets.py string_to_match")
    sys.exit(1)

match = sys.argv[1]

elasticSearch = httplib.HTTPConnection(ELASTIC_SEARCH_HOST, ELASTIC_SEARCH_PORT)
elasticSearch.connect()

query = """
{
    \"query\": {
        \"filtered\": {
            \"query\": {
                \"match\": {
                    \"text\": \"%s\"
                }
            }
        }
    }
}""" % match

elasticSearch.request('POST', '/twitter/_search?size=1000000', query)

raw_response = elasticSearch.getresponse()


if raw_response.status == httplib.OK:
    response = json.loads(raw_response.read())
    tweetsList = map(lambda x : json.dumps(x),
            responseToTweetFormat(response))
    for tweet in tweetsList:
        print tweet


elasticSearch.close()
