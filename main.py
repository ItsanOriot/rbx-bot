import discord
from discord import app_commands
import requests
import requests_html
import time
import robloxpy.Market.Internal as Market
import robloxpy.User.External as External
import robloxpy.User.Internal as LocalUser
import robloxpy.Utils as Utils
import json

requestCookie = "cookie"

intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def getPassPrice(passid: int):
    passString = ("https://economy.roblox.com/v1/game-pass/%s/game-pass-product-info" % passid)
    passData = requests.get(passString).json()  
    return passData['PriceInRobux']

def getPassCreator(passid: int):
    passString = ("https://economy.roblox.com/v1/game-pass/%s/game-pass-product-info" % passid)
    passData = requests.get(passString).json()  
    return passData['Creator']['Id']

def getCodes(price: int):
    count = 0
    with open("C:/Users/Admin/Desktop/python shit/Selfbot/Final/codes.json", "r") as p:
        codeList = json.load(p)
    for i in codeList:
        if int(codeList[i]) == int(price):
            count+=1
    if count > 0:
        return count
    else:
        return -1
        print("Invalid price. No codes found")

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=806917670473170984))
    print(f'Bot User: {client.user}')

@tree.command(name = "setcookie", description = "sets the cookie of the account with robux", guild=discord.Object(id=806917670473170984))
@app_commands.checks.has_role(842447019909709894)
async def setcookie(interaction, cookie: str):
    LocalUser.SetCookie(cookie)
    global requestCookie
    requestCookie = str(cookie)
    await interaction.response.send_message("Cookie set.", ephemeral = True)
    await interaction.followup.send(Utils.CheckCookie(LocalUser.RawCookie), ephemeral = True)

@tree.command(name = "countcodes", description = "counts all available codes with a certain value", guild=discord.Object(id=806917670473170984))
@app_commands.checks.has_role(842447019909709894)
async def countcodes(interaction, value: str):
    if getCodes(value) > 0:
        await interaction.response.send_message("There are currently %s codes worth that amount" % getCodes(value))
    else:
        await interaction.response.send_message("Invalid price. There are no codes with that price")


@tree.command(name = "redeemrbx", description = "Redeems your robux", guild=discord.Object(id=806917670473170984))
async def redeemrbx(interaction, code: str, passid: int):
    with open("C:/Users/Admin/Desktop/python shit/Selfbot/Final/codes.json", "r") as p:
        codeList = json.load(p)
    if codeList[code] == getPassPrice(passid):
        codeList.pop(code)
        with open("C:/Users/Admin/Desktop/python shit/Selfbot/Final/codes.json", "w") as p:
            p.write(json.dumps(codeList, indent=2)) 
        await interaction.response.send_message("Valid pass. Buying item", ephemeral=True)

        session = requests_html.HTMLSession()
        price_in_robux = getPassPrice(passid)
        creator_id = getPassCreator(passid)
        cookies = {
            '.ROBLOSECURITY': requestCookie,
        }
        def get_csrf_token():
            csrf_token = session.get(
                'https://www.roblox.com/home',
                cookies=cookies).html.xpath('//*[@id="rbx-body"]/meta/@data-token')[0]
            return csrf_token
        headers = {
            'x-csrf-token': get_csrf_token(),
        }
        json_data = {
            'expectedCurrency': 1,
            'expectedPrice': price_in_robux,
            'expectedSellerId': creator_id,
        }
        response = session.post(
            f'https://`economy.roblox.com/v1/purchases/products`/{passid}',
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        if response.ok:
            print("Successful Purchase")
            print(response)
        else:
            print("Purchase Failed")
    else:
        await interaction.response.send_message("Invalid pass price", ephemeral=True)


client.run('YOUR BOT TOKEN')
