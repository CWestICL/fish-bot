from bs4 import BeautifulSoup
import requests
from datetime import date

fotd = {}

def get_fish():
    try:
        print("Making a request...")
        fish_page = requests.get("https://www.fishbase.se/summary/RandomSpecies.php")
        print(fish_page)

        soup = BeautifulSoup(fish_page.text, "html.parser")

        sciname_div = soup.find("div", {"id": "ss-sciname"})
        sciname_parts = sciname_div.findAll("a")
        sciname = f"{sciname_parts[0].text} {sciname_parts[1].text}"

        comname = sciname_div.find("span", {"class": "sheader2"}).text.strip()
        has_name = True
        if not comname:
            comname = None
            has_name = False

        image_div = soup.find("div", {"id": "ss-photo"})
        has_image = True
        if not image_div:
            image_div = soup.find("div", {"id": "ss-photo-full"})
            has_image = False

        image_html = image_div.find("img")
        image_url = image_html["src"]
        image = f"https://www.fishbase.se{image_url}"

        fish = {
            "species": sciname,
            "hasName": has_name,
            "name": comname,
            "hasImage": has_image,
            "image": image
        }
        print("Fish:",fish)
        return fish
    except Exception as e:
        print(e)

    
def get_fish_with_image():
    print("get_fotd triggered")
    fish = get_fish()
    #if fish["hasName"] and fish["hasImage"]:
    if fish["hasImage"]:
        return fish
    else:
        return get_fish_with_image()
    

def set_fotd():
    print("set_fotd triggered")
    global fotd
    fotd = {
        "fish": get_fish_with_image(),
        "date": date.today()
    }

def get_fotd_response():
    print("get_response triggered")
    global fotd
    print("before fotd:", fotd)
    if date.today() != fotd["date"]:
        fotd = set_fotd()
    print("after:", fotd)
    try:
        name = fotd["fish"]["name"]
        species = fotd["fish"]["species"]
        image = fotd["fish"]["image"]
        today = fotd["date"]

        if name:
            return {
                "message": f"The **Fish of the Day** for {today} is {name} (*{species}*)",
                "image": image
            }
        else:
            return {
                "message": f"The **Fish of the Day** for {today} is *{species}*",
                "image": image
            }
    
    except Exception as e:
        print(e)
        return "Sorry! I can't seem to access the database right now. Please try again later."
    

def get_random_response():
    try:
        fish = get_fish_with_image()
        name = fish["name"]
        species = fish["species"]
        image = fish["image"]

        if name:
            return {
                "message": f"Your random fish is {name} (*{species}*)",
                "image": image
            }
        else:
            return {
                "message": f"Your random fish is *{species}*",
                "image": image
            }
    
    except Exception as e:
        print(e)
        return "Sorry! I can't seem to access the database right now. Please try again later."
    
def get_response(input: str):
    if input[1:] == "fotd":
        return get_fotd_response()
    if input[1:] == "fish":
        return get_random_response()
    if input[1:] == "fish-help":
        return """
        Hi! I'm the Fish of the Day bot!
Here's a list of my commands (replace '!' with '?' if you'd rather I DM you the message):
**!fish-help** - Displays this message
**!fotd** - Posts the current Fish of the Day
**!fish** - Posts a random fish

Be patient, it sometime takes me a little while to find a suitable fish!

The database I use can be found at https://www.fishbase.se/
"""
    