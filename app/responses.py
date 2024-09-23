from bs4 import BeautifulSoup
import requests
from datetime import date
import config
import logging

logging.basicConfig(level=logging.INFO, filename="fishbot.log", filemode="w", format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

def get_fish(endpoint, user = None):
    try:
        log.debug("Making a request...")
        url = f"{config.api_url}/{endpoint}"
        params = dict(
            requireName = config.common_name_required,
            requireImage = config.image_required
        )
        if user:
            params["user"] = str(user)
        req = requests.get(url=url, params=params)
        log.debug(f"Response: {req}")

        data = req.json()

        log.debug(f"Data: {data}")
    
        fish = {
            "species": f"{data['genus']} {data['species']}",
            "name": data["name"],
            "image": f"{config.api_url}{data['imageUrl']}",
            "genus": data["familyCommonName"],
        }
        if not data["name"]:
            fish["name"] = None
        if not data["imageUrl"]:
            fish["image"] = None
        log.info(f"Fish: {fish}")
        return fish
    except Exception as e:
        log.error(f"get_fish: {e}")
        if str(e).startswith("HTTPS"):
            raise Exception("HTTPS Error")


def get_fotd_response(user = None):
    if user and not config.personal_fotd_enabled:
        return "Sorry! The !myfotd command is not enabled at the moment."
    try:
        fotd = get_fish("daily", user)

        name = fotd["name"]
        species = fotd["species"]
        image = fotd["image"]
        genus = fotd["genus"]
        today = date.today().strftime("%d/%m/%Y")

        if user:
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
        

def get_random_fish_response(user = None):
    if not config.random_fish_enabled:
        return "Sorry! The !fish command is not enabled at the moment."
    try:
        fish = get_fish("random")

        name = fish["name"]
        species = fish["species"]
        image = fish["image"]
        genus = fish["genus"]

        if user:
            msg_start = f"Hi <@{user}>! "
        else:
            msg_start = ""
        
        if name:
            msg_name = f"**{name}** (*{species}*)"
        else:
            msg_name = f"*{species}*"
        message = f"{msg_start}Your random fish is {msg_name} from the family **{genus}**"

        return {
            "message": message,
            "image": image
        }

    except Exception as e:
        log.error(f"get_random_fish_response: {e}")
        if str(e).startswith("HTTPS"):
            return "Sorry! I can't seem to access the database right now. Please try again later."
        else:
            return "Sorry! There was an internal error handling your request."
    
    
def get_response(input, user):
    if input[1:] == "fotd":
        return get_fotd_response()
    if input[1:] == "myfotd":
        return get_fotd_response(user)
    if input[1:] == "fish":
        return get_random_fish_response(user)
    if input[1:] == "fish-help":
        return """
        Hi! I'm the Fish of the Day bot!
Here's a list of my commands (replace '!' with '?' if you'd rather I DM you the message):
**!fish-help** - Displays this message
**!fotd** - Posts the current global Fish of the Day
**!myfotd** - Posts your current personal Fish of the Day (Does not work in DMs currently)
**!fish** - Posts a random fish

The database I use can be found at https://www.fishbase.se/
"""

if __name__ == '__main__':
    print(get_fotd_response(None))