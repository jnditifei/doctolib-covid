import os
import datetime
import requests
import smtplib, ssl

"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

PATH = "./chromedriver"
driver = webdriver.Chrome(PATH)
"""

DISABLE_EMAIL = os.environ.get("DISABLE_EMAIL")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")


#Connexion au compte Doctolib
r = requests.post("https://www.doctolib.fr/login", json={"username":email,"remember":True,"remember_username":True,"password":password,"kind":"patient"})
cookies = r.cookies
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


with open('centers.txt') as centers_txt:
    centers = centers_txt.readlines()

centers = [center.strip() for center in centers
           if not center.startswith("#")] 

def slot_available():
    for center in centers:
        data = requests.get(f"https://www.doctolib.fr/booking/{center}.json").json()["data"]
        visit_motives = [visit_motive for visit_motive in data["visit_motives"]
                         if visit_motive["name"].startswith("1re injection") and 
                         "AstraZeneca" not in visit_motive["name"]]
        if not visit_motives:
            continue
        place = data["places"][0]
            
        start_date = datetime.datetime.today().date().isoformat()
        visit_motive_ids =  visit_motives[0]["id"] 
        practice_ids = place["practice_ids"]
        place_name = place["formal_name"]
        place_address = place["full_address"]
        agendas = data["agendas"]
        for agenda in agendas:
            if agenda["practice_id"] in practice_ids and not agenda["booking_disabled"] and visit_motive_ids in agenda["visit_motive_ids"]:
                agenda_ids = "-".join([str(agenda["id"]) for agenda in agendas])
                availables = requests.get(
                        "https://www.doctolib.fr/availabilities.json",
                        headers= headers,
                        params = {
                                "start_date": start_date,
                                "visit_motive_ids": visit_motive_ids,
                                "agenda_ids": agenda_ids,
                                "practice_ids": practice_ids,
                                "insurance_sector": "public",
                                "destroy_temporary": "true",
                                "limit":4
                        },
                )
                nb_availabilities = availables.json()["total"]
                if nb_availabilities > 0:
                    result = str(nb_availabilities) + " appointments available at " + place_name + " - " + place_address
                    print(result)
                    return agenda_idss, practice_ids, available["slots"][0]["start_date"], visit_motive_ids, data['profile']["id"]
                break


for available in availables.json()["availabilities"]:
    if len(available["slots"]) > 0:
        first_appointment = requests.post(
            "https://www.doctolib.fr/appointments",
            json={"agenda_ids":agenda_ids,"practice_ids":practice_ids,"appointment":{"start_date":available["slots"][0]["start_date"],"visit_motive_ids":visit_motive_ids,"profile_id":data["profile"]["id"],"source_action":"profile"}}
            )
        print(first_appointment)
        break               
        