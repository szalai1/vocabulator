import requests
import sys
import json 

url = "http://localhost:8765"

def createDeck(deckName):
    req = {
        "action": "createDeck",
        "version": 6,
        "params": {
            "deck": deckName 
            }
        }

    resp = requests.post(url, data=json.dumps(req))
    print resp.json()

def createBasicNote(deckName, front, back, audio=None):
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
    resp = requests.post(url, json.dumps(req))
    print resp.json()

print sys.argv

audio = {
    "url": "http://audio.oxforddictionaries.com/en/mp3/ace_1_gb_1_abbr.mp3",
    "filename": "Kace_1_gb_1_abbr.mp3",
    "fields": [
        "Front"
    ]
}
createBasicNote(sys.argv[1], sys.argv[2], sys.argv[3])
