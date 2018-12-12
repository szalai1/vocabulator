import  requests
import json
import sys 

keys = json.load(open("oxford-dictionary.keys"))
app_id = keys["app-id"]
app_key = keys["app-key"] 
language = 'en'
headers = {'app_id' : app_id, 'app_key' : app_key}
base_url = 'https://od-api.oxforddictionaries.com:443/api/v1'

def getWord(w):
    resp = requests.get(base_url + "/entries/{lang}/{word}".format(lang=language, word=w), headers = headers)
    return resp.json()

#urlFR = 'https://od-api.oxforddictionaries.com:443/api/v1/stats/frequency/word/'  + language + '/?corpus=nmc&lemma=' + word_id.lower()


print json.dumps(getWord(sys.argv[1]))
