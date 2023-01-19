import requests
import json

if __name__=="__main__":
    headers = {"Content-Type": "application/json", "charset":"utf-8","password": "jaimelebio" ,"id_magasin": "1"}
    file = "C:\\Users\\xtian\\OneDrive\\Documents\\CentralSupelec\\projet\\msdocs-flask-postgresql-sample-app\\database\\test.json"
    
    test = open(file)
    aff = json.load(test)
    res = requests.post('https://tickarbone.azurewebsites.net/envoi_json', json=aff,headers=headers)
    if res.ok:
        print(res.json())
        #print(res)