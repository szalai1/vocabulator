import  requests
import json
import sys 

class OxfordAPI:
    def __init__(self):
        self.keys = json.load(open("oxford-dictionary.keys"))
        self.app_id = self.keys["app-id"]
        self.app_key = self.keys["app-key"] 
        self.language = 'en'
        self.headers = {'app_id' : self.app_id, 'app_key' : self.app_key}
        self.base_url = 'https://od-api.oxforddictionaries.com:443/api/v1'
    
    def getWord(self, w):
        w = self.getHeadword(w)
        if w is None:
            return None
        resp = requests.get(self.base_url + "/entries/{lang}/{word}".format(lang=self.language, word=w), headers = self.headers)
        if resp.status_code != 200:
            return None
        try:
            return resp.json()
        except:
            return None

    def getHeadword(self, w):
        resp = requests.get(self.base_url + "/inflections/{lang}/{word}".format(lang=self.language, word=w), headers = self.headers)
        if resp.status_code != 200:
            return None
        try:
            return resp.json()["results"][0]["lexicalEntries"][0]["inflectionOf"][0]["id"]
        except:
            return None
        
    def getSynonymsBySenseID(self, w, senseID):
        resp = requests.get(self.base_url + "/entries/{lang}/{word}/synonyms".format(lang=self.language, word=w), headers = self.header)
        results = [] 
        for i in resp.json()["lexicalEntries"]["entries"]["senses"]:
            if i["id"] == senseID:
                for j in i["synonyms"]:
                    results.append(j["text"])
                return results 
            
def main():
    oxfordAPI = OxfordAPI()
    for w in oxfordAPI.getWord(sys.argv[1])["results"][0]["lexicalEntries"]:
        print w["lexicalCategory"]
        for entry in w["entries"]:
            for sense in entry["senses"]:
                for d in sense["definitions"]:
                    print "\t"+d
                for thLink in sense.get("thesaurusLinks", []):
                    for syn in getSynonymsBySenseID(w["text"], thLink["sense_id"]):
                        print syn
                for example in sense["examples"]:
                    print "\t\t-" + example["text"]
                for subsense in sense["subsenses"]:
                    print "\t\tSUBSENCE"
        print ""
    
main()
#getHeadword(sys.argv[1])
