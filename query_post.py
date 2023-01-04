import requests
import json

if __name__=="__main__":
    headers = {"Content-Type": "application/json", "charset":"utf-8","password": "jaimelebio" ,"id_magasin": "1"}
    file = "C:\\Users\\xtian\\OneDrive\\Documents\\CentralSupelec\\projet\\msdocs-flask-postgresql-sample-app\\database\\test.json"
    
    test = open( "C:\\Users\\xtian\\OneDrive\\Documents\\CentralSupelec\\projet\\msdocs-flask-postgresql-sample-app\\database\\test.json")
    aff = json.load(test)
    res = requests.post('http://localhost:8080/envoi_json', json=aff,headers=headers)
    if res.ok:
        print(res.json())