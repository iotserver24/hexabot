import configparser
from pymongo import MongoClient
from bson.objectid import ObjectId
from pyrogram import Client, filters

print("Initializing configuration...")
config = configparser.ConfigParser()
config.read('config.ini')

API_ID = config.get('default', 'api_id')
API_HASH = config.get('default', 'api_hash')
BOT_TOKEN = config.get('default', 'bot_token')
DATABASE_NAME = config.get('default', "db_name")
COLLECTION_NAME = config.get('default', "collection_name")

# Initialize Pyrogram client
pyro_client = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Connect to MongoDB
url = config.get('default', "MONGO_URI")
cluster = MongoClient(url)
db = cluster[DATABASE_NAME]
HexaDb = db[COLLECTION_NAME]

# Command handlers
@pyro_client.on_message(filters.command("start"))
async def start_command(client, message):
    SENDER = message.chat.id
    text = "Hi, I am Hexa details bot. I store data of Hexa battle tournaments. Created by R3AP3R editz."
    await pyro_client.send_message(SENDER, text)

@pyro_client.on_message(filters.command("add"))
async def add_command(client, message):
    SENDER = message.chat.id
    list_of_words = message.text.split(" ")
    uid = list_of_words[1]
    win = int(list_of_words[2])
    team = list_of_words[3]
    post_dict = {"uid": uid, "win": win, "team": team}
    collection = HexaDb
    collection.insert_one(post_dict)
    text = "Details of the player have been inserted!"
    await pyro_client.send_message(SENDER, text)

@pyro_client.on_message(filters.command("list"))
async def list_command(client, message):
    SENDER = message.chat.id
    list_of_words = message.text.split(" ")
    collection = HexaDb
    if len(list_of_words) > 1:
        team = list_of_words[1]
        results = collection.find({"team": team})
    else:
        results = collection.find({})
    message = create_message_select_query(results)
    await pyro_client.send_message(SENDER, message, parse_mode='html')

@pyro_client.on_message(filters.command("win"))
async def win_command(client, message):
    SENDER = message.chat.id
    list_of_words = message.text.split(" ")
    collection = HexaDb
    _id = ObjectId(list_of_words[1])
    uid = list_of_words[2]
    win = int(list_of_words[3])
    team = list_of_words[4]
    new_post_dict = {"uid": uid, "win": win, "team": team}
    collection.update_one({"_id": _id}, {"$set": new_post_dict})
    text = "Player with _id {} has been updated.".format(_id)
    await pyro_client.send_message(SENDER, text)

@pyro_client.on_message(filters.command("remove"))
async def remove_command(client, message):
    SENDER = message.chat.id
    list_of_words = message.text.split(" ")
    collection = HexaDb
    uid = list_of_words[1]
    collection.delete_one({"uid": uid})
    text = "User {} has been removed.".format(uid)
    await pyro_client.send_message(SENDER, text)

@pyro_client.on_message(filters.command("in"))
async def in_command(client, message):
    SENDER = message.chat.id
    list_of_words = message.text.split(" ")
    collection = HexaDb
    if len(list_of_words) > 1:
        field = list_of_words[1]
        values_to_check = list_of_words[2:]
        params = {field: {"$in": values_to_check}}
        results = collection.find(params)
        message = create_message_select_query(results)
        await pyro_client.send_message(SENDER, message, parse_mode='html')

def create_message_select_query(results):
    text = ""
    for res in results:
        _id = res["_id"]
        uid = res["uid"]
        win = res["win"]
        team = res["team"]
        text += "<b>" + str(_id) + "</b> | " + "<b>" + str(uid) + "</b> | " + "<b>" + str(win) + "</b> | " + "<b>" + str(team) + "</b> | " + "\n"
    message = "<b>Received 📖 </b> Information about participants:\n\n" + text
    return message

# Run Pyrogram client
pyro_client.run()
