import requests
import argparse
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
        resp = requests.get(self.base_url + "/entries/{lang}/{word}/synonyms".format(lang=self.language, word=w), headers = self.headers)
        results = [] 
        js = {}
        try: 
            js = resp.json()
        except :
            return [] 
        for r in js["results"]:
            for l in r["lexicalEntries"]:
                for e in l["entries"]:
                    for s in e["senses"]:
                        if s["id"] == senseID:
                            for j in s["synonyms"]:
                                results.append(j["text"])
        return results
    
class AnkiAPI:
    def __init__(self, host):
        self.url = host
    
    def createDefinitionCard(self, deckName, front, back, audio=None):
        req = {
            "action": "addNote",
            "version": 6,
            "params": {
                "note": {
                    "deckName": deckName,
                    "modelName": "Basic",
                    "fields": {
                        "Front": front, 
                        "Back": back, 
                    },
                    "options": {
                        "allowDuplicate": False
                    },
                    "tags": [],
                    "audio": audio,
                },
            }
        }
        resp = requests.post(self.url, json.dumps(req))


            
def getWordCards(word):
    card_template = u"""<strong>{word}</strong><br>
    <p align="left">
<b> Definition ({category}) </b>: {definition}<br>
<b>Synonyms:</b> <i>{synonyms}</i><br>
Examples:<br>
</p>
<ul align="left">
{examples}
</ul>
"""
    subsense_template = u"""
<b> {subsense_def}</b>
<ul align="left">{subsense_examples}</ul>
"""
    oxfordAPI = OxfordAPI()
    headWord = oxfordAPI.getHeadword(word)
    if headWord is None:
       raise Exception("no such word") 
    wordData = oxfordAPI.getWord(headWord)
    if wordData is None: 
       raise Exception("no response") 
    for w in wordData["results"][0]["lexicalEntries"]:
        category = w["lexicalCategory"]
        for entry in w["entries"]:
            for sense in entry["senses"]:
                definition = "\n>> ".join(sense["definitions"])
                syns = [] 
                examples = ""
                for thLink in sense.get("thesaurusLinks", []):
                    syns += oxfordAPI.getSynonymsBySenseID(thLink["entry_id"], thLink["sense_id"])
                for example in sense.get("examples", []):
                    examples += u'<li>' + example["text"] + u'</li>'
                subsense_text = ""
                for subsense in sense.get("subsenses", []):
                    sub_def = u', '.join(subsense["definitions"])
                    sub_examples = u'<li>'.join(map(lambda ex: ex['text']+"</li>", subsense.get("examples", [])))
                    for thLink in subsense.get("thesaurusLinks", []):
                        syns+=oxfordAPI.getSynonymsBySenseID(thLink["entry_id"], thLink["sense_id"])
                    subsense_text +=  subsense_template.format(subsense_def=sub_def,subsense_examples=sub_examples)
                syns = ", ".join(syns)
                card_text = card_template.format(word=headWord, category=category,definition=definition, synonyms=syns,examples=examples)
                if subsense_text != "":
                    card_text += subsense_text
                yield card_text
   
def responseOK():
    resp = raw_input("do you want to add this card to your deck? (y or n): ")
    if resp[0] == 'y' or resp[0] == 'Y':
        return True
    return False

def main():
    argp = argparse.ArgumentParser(description="vocabulator")
    argp.add_argument('word', metavar='1', type=str, help='the word')
    argp.add_argument('--deck', default="words")
    argp.add_argument('--host', default="http://localhost:8765")
    args = argp.parse_args()
    anki = AnkiAPI(args.host)
    try:
        for wordCard in getWordCards(args.word):
            print wordCard
            if responseOK():
                anki.createDefinitionCard(args.deck, wordCard, wordCard) 
                print "card has been added"
    except Exception as e:
        print e

    
main()
