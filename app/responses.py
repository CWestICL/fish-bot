from bs4 import BeautifulSoup
import requests
from datetime import date
from dateutil import parser 
import config
import json
import logging

logging.basicConfig(level=logging.INFO, filename="fishbot.log", filemode="w", format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

def get_fish():
    try:
        log.debug("Making a request...")
        url = f"{config.api_url}/random"
        params = dict(
            requireName = config.common_name_required,
            requireImage = config.image_required
        )
        req = requests.get(url=url, params=params)
        log.debug(f"Response: {req}")

        data = req.json()

        log.debug(f"Data: {data}")
    
        fish = {
            "species": f"{data['genus']} {data['species']}",
            "name": data['name'],
            "image": f"{config.api_url}{data['imageUrl']}",
            "genus": data['familyCommonName'],
        }
        if not data['name']:
            fish['name'] = None
        if not data['imageUrl']:
            fish['image'] = None
        log.info(f"Fish: {fish}")
        return fish
    except Exception as e:
        log.error(f"get_fish: {e}")
        if str(e).startswith("HTTPS"):
            raise Exception("HTTPS Error")

    
def get_suitable_fish():
    fish = get_fish()
    if config.comname_required and not fish["hasName"]:
        log.info("Fish has no common name! Trying again...")
        return get_suitable_fish()
    elif config.image_required and not fish["hasImage"]:
        log.info("Fish has no image! Trying again...")
        return get_suitable_fish()
    else:
        log.info("Suitable fish found!")
        return fish
    

def get_fotd():
    try:
        fotd = {
            "fish": get_fish(),
            "date": date.today().strftime("%b %d %Y")
        }
        log.debug(f"New FotD: {fotd}")
    except Exception as e:
        log.error(f"get_fotd: {e}")
        if str(e).startswith("HTTPS"):
            raise Exception('HTTPS error')

    return fotd
    

def set_fotd(owner):
    try:
        if read_fotd_json():
            data = read_fotd_json()
            log.info(f"Loaded FotD from JSON: {data}")
            if owner not in data:
                log.info(f"No FotD set for {owner}! Getting new FotD...")
                fotd = get_fotd()
            elif not data[owner]['fish'] or not data[owner]['date']:
                log.info(f"No suitable FotD set for {owner}! Getting new FotD...")
                fotd = get_fotd()
            else:
                fotd_date = parser.parse(data[owner]["date"])
                if date.today() != fotd_date.date():
                    log.info("Date mismatch! Getting new FotD...")
                    fotd = get_fotd()
                else:
                    fotd = data[owner]
        else:
            log.info(f"No json file found, generating new fish...")
            fotd = get_fotd()

        write_fotd_json(owner, fotd)
        return fotd

    except Exception as e:
        log.error(f"set_fotd: {e}")


def write_fotd_json(owner, fotd):
    if read_fotd_json():
        fish_dict = read_fotd_json()
    else:
        fish_dict = {}
    fish_dict[owner] = fotd
    with open("fotd.json", "w") as outfile:
        json.dump(fish_dict, outfile)


def read_fotd_json():
    try:
        with open("fotd.json", "r") as openfile:
            json_obj = json.load(openfile)
        return json_obj
    except Exception as e:
        log.error(f"read_fotd_json: {e}")
        return None



def get_fotd_response(user):
    if not user:
        user = 'fishbot'
    try:
        fotd = set_fotd(str(user))

        name = fotd["fish"]["name"]
        species = fotd["fish"]["species"]
        image = fotd["fish"]["image"]
        genus = fotd["fish"]["genus"]
        today = parser.parse(fotd["date"]).date()

        if user != 'fishbot':
            msg_start = f"Hi <@{user}>! Your personal"
        else:
            msg_start = "The global"
        
        if name:
            msg_name = f"**{name}** (*{species}*)"
        else:
            msg_name = f"*{species}*"
        message = f"{msg_start} Fish of the Day for {today} is {msg_name} from the family **{genus}**"

        return {
            "message": message,
            "image": image
        }

    except Exception as e:
        log.error(f"get_fotd_response: {e}")
        if str(e).startswith("HTTPS"):
            return "Sorry! I can't seem to access the database right now. Please try again later."
        else:
            return "Sorry! There was an internal error handling your request."
    
    
def get_response(input, user):
    if input[1:] == "fotd":
        return get_fotd_response(None)
    if input[1:] == "fish":
        return get_fotd_response(user)
    if input[1:] == "fish-help":
        return """
        Hi! I'm the Fish of the Day bot!
Here's a list of my commands:
**!fish-help** - Displays this message
**!fotd** - Posts the current Fish of the Day
**!fish** - Posts a random fish

Be patient, it sometime takes me a little while to find a suitable fish!

The database I use can be found at https://www.fishbase.se/
"""

if __name__ == '__main__':
    print(get_fotd_response(None))
    print(get_fotd_response('monster_misfire'))
    print(get_fotd_response(None))
    print(get_fotd_response('hol'))
    print(get_fotd_response('monster_misfire'))
    print(get_fotd_response('hol'))