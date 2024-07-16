from bs4 import BeautifulSoup
import requests
from datetime import date
from dateutil import parser 
import config
import json

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
            print("Fish missing common name!")
            comname = None
            has_name = False

        image_div = soup.find("div", {"id": "ss-photo"})
        if not image_div:
            image_div = soup.find("div", {"id": "ss-photo-full"})

        has_image = True
        if "No image available for this species" in str(soup.find("div", {"id": "ss-photomap-container"})):
            print("Fish missing image!")
            has_image = False

        image_html = image_div.find("img")
        image_url = image_html["src"]
        image = f"https://www.fishbase.se{image_url}"

        genus_divs = soup.find_all("div", {"class": "smallSpace"})
        genus_div = None
        genus = None
        for div in genus_divs:
            if "Etymology:" in div.text.strip():
                genus_div = div
        
        if genus_div:
            genus_div_str = genus_div.text.strip().split("Etymology:")[0]
            print(f"HTML: {genus_div_str}")

            genus_div_str = genus_div_str.replace("(","*(")
            genus_div_str = genus_div_str.replace(")",")*")
            x = genus_div_str.split("*")
            res = []
            for i in x:
                if i.startswith("(") and i.endswith(")") and not i.startswith("(Ref"):
                    res.append(i[1:-1])
            genus = res[-1]
            print(f"Genus: {genus}")

        fish = {
            "species": sciname,
            "hasName": has_name,
            "name": comname,
            "hasImage": has_image,
            "image": image,
            "genus": genus,
        }
        print(f"Fish: {fish}")
        return fish
    except Exception as e:
        print(f"Error: {e}")
        if str(e).startswith("HTTPS"):
            raise Exception("HTTPS Error")

    
def get_fish_with_image(isFotd):
    fish = get_fish()
    if isFotd and config.comname_required_fotd and not fish["hasName"]:
        print("Fish has no common name! Trying again...")
        return get_fish_with_image(isFotd)
    elif isFotd and config.image_required_fotd and not fish["hasImage"]:
        print("Fish has no image! Trying again...")
        return get_fish_with_image(isFotd)
    elif not isFotd and config.comname_required_fish and not fish["hasName"]:
        print("Fish has no common name! Trying again...")
        return get_fish_with_image(isFotd)
    elif not isFotd and config.image_required_fish and not fish["hasImage"]:
        print("Fish has no image! Trying again...")
        return get_fish_with_image(isFotd)
    else:
        print("Suitable fish found!")
        return fish
    

def set_fotd():
    try:
        fotd = {
            "fish": get_fish_with_image(True),
            "date": date.today().strftime("%b %d %Y")
        }
        print(f"New FotD: {fotd}")
    except Exception as e:
        print(f"Error: {e}")
        fotd = {
            "fish": None,
            "date": None
        }
        print("FOTD couldn't be set at startup.")

    write_fotd_json(fotd)
    return fotd


def write_fotd_json(fotd):
    with open("fotd.json", "w") as outfile:
        json.dump(fotd, outfile)


def read_fotd_json():
    with open("fotd.json", "r") as openfile:
        json_obj = json.load(openfile)
    return json_obj


def get_fotd_response():
    try:
        fotd = read_fotd_json()
        print(f"Current FotD: {fotd}")
        if not fotd["fish"] or not fotd["date"]:
            print("No FotD set! Getting new FotD...")
            fotd = set_fotd()
        
        fotd_date = parser.parse(fotd["date"])

        if date.today() != fotd_date.date() or not fotd["fish"]:
            print("Date mismatch! Getting new FotD...")
            fotd = set_fotd()

        name = fotd["fish"]["name"]
        species = fotd["fish"]["species"]
        image = fotd["fish"]["image"]
        genus = fotd["fish"]["genus"]
        today = fotd["date"]

        if name.lower() == "whale shark":
            return {
                "message": f"It actually happened! The Fish of the Day for {today} is **{name}** (*{species}*)",
                "image": image
            }
        elif name:
            return {
                "message": f"The Fish of the Day for {today} is **{name}** (*{species}*)",
                "image": image
            }
        else:
            if genus:
                return {
                    "message": f"The Fish of the Day for {today} is *{species}*, from the family **{genus}**",
                    "image": image
                }
            else:
                return {
                    "message": f"The Fish of the Day for {today} is *{species}*",
                    "image": image
                }
    
    except Exception as e:
        if str(e).startswith("HTTPS"):
            return "Sorry! I can't seem to access the database right now. Please try again later."
        else:
            return "Sorry! There was an internal error handling your request."
    

def get_random_response(user):
    if not config.fish_enabled:
        return "Sorry! The !fish command is not enabled at the moment."
    try:
        fish = get_fish_with_image(False)
        name = fish["name"]
        species = fish["species"]
        image = fish["image"]
        genus = fish["genus"]

        if name:
            fish_message = f"**{name}** (*{species}*)"
        else:
            if genus:
                fish_message= f"*{species}*, from the family **{genus}**"
            else:
                fish_message= f"*{species}*"
        
        if user:
            if name.lower() == "whale shark":
                return {
                    "message": f"Hi <@{user}>! You actually did it! Your random fish is {fish_message}",
                    "image": image
                }
            else:
                return {
                    "message": f"Hi <@{user}>! Your random fish is {fish_message}",
                    "image": image
                }
        else:
            if name.lower() == "whale shark":
                return {
                    "message": f"No one will believe you! Your random fish is {fish_message}",
                    "image": image
                }
            else:
                return {
                    "message": f"Your random fish is {fish_message}",
                    "image": image
                }
    
    except Exception as e:
        if str(e).startswith("HTTPS"):
            return "Sorry! I can't seem to access the database right now. Please try again later."
        else:
            return "Sorry! There was an internal error handling your request."
    
def get_response(input, user):
    if input[1:] == "fotd":
        return get_fotd_response()
    if input[1:] == "fish":
        return get_random_response(user)
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

if __name__ == '__main__':
    try:
        read_fotd_json()
    except:
        set_fotd()
    print(get_fotd_response())