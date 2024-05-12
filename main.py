import os
import configparser
from telethon import TelegramClient, events
from pymongo import MongoClient
from bson.objectid import ObjectId
from telethon import types      





print("Initializing configuration...")
config = configparser.ConfigParser()
config.read('config.ini')
API_ID = config.get('default', 'api_id')
API_HASH = config.get('default', 'api_hash')
BOT_TOKEN = config.get('default', 'bot_token')
DATABASE_NAME = config.get('default', "db_name")
COLLECTION_NAME = config.get('default', "collection_name")
client = TelegramClient('Bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
# Connect to MongoDB
url = config.get('default', "MONGO_URI")
cluster = MongoClient(url)
db = cluster[DATABASE_NAME]
HexaDb = db[COLLECTION_NAME]


@client.on(events.NewMessage(pattern="(?i)/start"))
async def start(event):
    sender = await event.get_sender()
    SENDER = sender.id
    text = "hi i am Hexa details. A bot to store datas of tournament of Hexa battle. CREATED BY:- R3AP3R editz ( @R3AP3Redit )"
    await client.send_message(SENDER, text)



@client.on(events.NewMessage(pattern="(?i)/add"))
async def add(event):
    sender = await event.get_sender()
    SENDER = sender.id
    list_of_words = event.message.text.split(" ")
    collection = HexaDb
    uid = list_of_words[1]
    win = int(list_of_words[2])
    team = list_of_words[3]
    post_dict = {"uid": uid, "win": win, "team": team}
    collection.insert_one(post_dict)

    text = "deatils of the player {} has been added".format(uid)
    
    await client.send_message(SENDER, text)  #SENDER




@client.on(events.NewMessage(pattern="(?i)/list(?: (.*))?$"))
async def select(event):
    sender = await event.get_sender()
    SENDER = sender.id
    
    team_name = event.pattern_match.group(1)
    collection = HexaDb
    
    if team_name:
        results = collection.find({"team": team_name})
    else:
        results = collection.find({})
    
    message = create_message_select_query(results)
    
    try:
        chat_id = await event.get_input_chat()
        await client.send_message(chat_id, message, parse_mode='html')
    except Exception as e:
        print(f"Error sending message: {e}")




@client.on(events.NewMessage(pattern=r"/adl (\d+)"))
async def adl(event):
    win_number = int(event.pattern_match.group(1))
    collection = HexaDb
    
    results = collection.find({"win": win_number})
    
    message = create_message_adl_query(results)
    
    try:
        chat_id = await event.get_input_chat()
        await client.send_message(chat_id, message, parse_mode='html')
    except Exception as e:
        print(f"Error sending message: {e}")









@client.on(events.NewMessage(pattern="(?i)/win"))
async def update(event):
    sender = await event.get_sender()
    SENDER = sender.id
    list_of_words = event.message.text.split(" ")
    collection = HexaDb
    _id = ObjectId(list_of_words[1])
    uid = list_of_words[2]
    win = int(list_of_words[3])
    team = list_of_words[4]
    new_post_dict = {"uid": uid, "win": win, "team": team}
    collection.update_one({"win": win}, {"$set": new_post_dict})
    text = "players with wins {} correctly updated".format(win)
    await client.send_message(SENDER, text, parse_mode='html')







@client.on(events.NewMessage(pattern="(?i)/remove"))
async def delete(event):
    sender = await event.get_sender()
    SENDER = sender.id
    list_of_words = event.message.text.split(" ")
    collection = HexaDb
    uid = list_of_words[1]
    collection.delete_one({"uid": uid})
    text = "player {} has been knocked out".format(uid)
    await client.send_message(SENDER, text, parse_mode='html')




           







@client.on(events.NewMessage(pattern="(?i)/in"))
async def select(event):
    sender = await event.get_sender()
    SENDER = sender.id
    list_of_words = event.message.text.split(" ")
    collection = HexaDb
    if len(list_of_words) > 1:
        field = list_of_words[1]
        values_to_check = list_of_words[2:]
        
        params = {field: {"$in": values_to_check}}
        results = collection.find(params)
        message = create_message_select_query(results)
        await client.send_message(SENDER, message, parse_mode='html')




def create_message_select_query(results):
    text = ""
    for res in results:
        uid = res["uid"]
        if "win" in res:  # Check if "win" key exists in the dictionary
            win = res["win"]
        else:
            win = "N/A"
        
        if "team" in res:  # Check if "team" key exists in the dictionary
            team = res["team"]
        else:
            team = "N/A"
        
        text += f"<b>{uid}</b> | <b>{win}</b> | <b>{team}</b>\n"
        
    message = "<b>Received 📖</b> Information about participants:\n\n" + text
    return message


def create_message_adl_query(results):
    text = ""
    for res in results:
        uid = res["uid"]
        team = res["team"]
        text += f"<b>{uid}</b> | <b>{team}</b>\n"
        
    if text:
        message = f"<b>Participants who were added by admin with admin code: {win_number} are:</b>\n\n" + text
    else:
        message = f"No participants found who were added by admin with admin code {win_number} ."
        
    return message


# def create_message_select_query(results):
#   text = ""
#    for res in results:
#      #  id = res["_id"]
#        uid = res["uid"]
#        win = res["win"]
#        team = res["team"]
#        text += "<b>"+ str(uid) +"</b> | " + "<b>"+ str(win)+"</b> | " + "<b>"+ str(team)+"</b> | " + "</b>\n"
#        #   text += "<b>"+ str(id) +"</b> | " + "<b>"+ str(uid) +"</b> | " + "<b>"+ str(win)+"</b> | " + "<b>"+ str(team)+"</b> | " + "</b>\n"
#    message = "<b>Received 📖 </b> Information about participants:\n\n"+text
#    return message
        

client.run_until_disconnected()
