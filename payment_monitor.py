from imbox import Imbox
import datetime
from datetime import datetime
from pytz import timezone
import pytz
import discord
import asyncio
from discord import Webhook, RequestsWebhookAdapter
from discord.ext import commands
import json

#establish discord py tings
client = discord.Client()
bot = commands.Bot(command_prefix='$')

#open settings json
with open('settings.json') as json_file:
    settings = json.load(json_file)

# grab info from settings.json

email, password = settings['email'], settings['password']

#set up sick dates

def get_pst_day():
    date_format='%m/%d/%Y %H:%M:%S'
    date_format1 = '%m/%d/%Y'
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(timezone('US/Pacific'))
    pstDateTime=date.strftime(date_format)
    pstDateTime2 = date.strftime(date_format1)
    return pstDateTime, pstDateTime2

#set up sending the message to discord when payment detected

async def executeWebhook(platform, amount, sent_from):
    embed = discord.Embed(title=f"{platform.title()} Payment Detected")
    if platform == 'Zelle':
        embed.color = 0x6A0DAD
        embed.set_thumbnail(url="https://play-lh.googleusercontent.com/F4U2pL8z-Ic5FzCfe1xVXMWRvff6oEBIzDsyGRc4mE3bIUPiCfhuXXXvTOfcpVglKqs")
    elif platform == 'Cashapp':
        embed.color = 0x00D632
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Square_Cash_app_logo.svg/1024px-Square_Cash_app_logo.svg.png")
    elif platform == 'Venmo':
        embed.color = 0xADD8E6
        embed.set_thumbnail(url="https://icon2.cleanpng.com/20180418/cie/kisspng-venmo-money-payment-square-cash-paypal-5ad71dd1ecb0b7.8007833515240473139695.jpg")
    embed.add_field(name="**Platform**", value=platform, inline=False)
    embed.add_field(name="**Amount**", value=f"${amount}", inline=False)
    embed.add_field(name="**Sent From**", value=sent_from, inline=False)
    embed.set_footer(text=get_pst_day()[0])
    channel = bot.get_channel(int(settings['monitor_channel_id']))
    await channel.send(embed=embed)
    
#emailSession = Imbox("imap.gmail.com",
 #   username="tobiasejohansena365@gmail.com", # put email
  #  password="oopupbbuopdstogg", # put app password
   # ssl=True,
    #ssl_context=None,
 #   starttls=False,
#)

# emails sent_from to check from (only these emails formats are supported)

emailCheck = ['cash@square.com', 'no-reply@alertsp.chase.com', 'venmo@venmo.com']

@bot.event
async def on_ready():
    while True:
        try:
            print('checking')
            emailSession = Imbox("imap.gmail.com",
                username=email, # put email
                password=password, # put app password
                ssl=True,
                ssl_context=None,
                starttls=False,
            )
            messages1 = emailSession.messages(unread=True)
            if len(messages1) > 0:
                #zelle
                sent_from = messages1[-1][1].sent_from[0]['email']
                # if messages1[-1][1].sent_from[0]['email'] == 'no-reply@alertsp.chase.com':
                if sent_from in emailCheck:
                    parse = messages1[-1][1].subject.strip('Fwd: ').split(' ')
                    money, first_name, last_name = parse[-1].strip('$'), parse[0], parse[1]
                    if sent_from == 'cash@square.com' and parse[0] != "You":
                        money = [x for x in parse if '$' in x][0].strip('$')
                        await executeWebhook('Cashapp', money, f"{first_name} {last_name}")
                    elif sent_from == 'no-reply@alertsp.chase.com':
                        await executeWebhook('Zelle', money, f'{first_name} {last_name}')
                    elif sent_from == 'venmo@venmo.com':
                        await executeWebhook('Venmo', money, f'{first_name} {last_name}')
                    emailSession.mark_seen(messages1[-1][0])
                
                else:
                    emailSession.mark_seen(messages1[-1][0])
                    print('no match email | Read')
                
                
        except Exception as e:
            print("Error: " + str(e))
            emailSession.mark_seen(messages1[-1][0])

        await asyncio.sleep(10)

@bot.command()
async def daily(ctx):
    emailSession = Imbox("imap.gmail.com",
        username=email, # put email
        password=password, # put app password
        ssl=True,
        ssl_context=None,
        starttls=False,
    )
    # grab inbox messages
    imbox_messages_received_on_date = emailSession.messages(date__on=datetime.now(pytz.timezone("US/Pacific")))
    cashapp, zelle, venmo = [], [], []
    
    # add all payments to list(s)
    for uid, message in imbox_messages_received_on_date:
        try:
            parse = message.subject.split(' ')
            if message.sent_from[0]['email'] == 'cash@square.com' and parse[0] != 'You':
                dollar_amount = [x for x in parse if '$' in x][0].strip('$')
                cashapp.append(float(dollar_amount))
            elif message.sent_from[0]['email'] == 'no-reply@alertsp.chase.com':
                dollar_amount = float(message.subject.split(' ')[-1].strip('$'))
                zelle.append(dollar_amount)
            elif message.sent_from[0]['email'] == 'venmo@venmo.com':
                dollar_amount = float(message.subject.split(' ')[-1].strip('$'))
                venmo.append(dollar_amount)
        except Exception as e:
            print("Error: " + str(e))

    # create sick cool looking embed for info

    embed = discord.Embed(title=f"Payment Report for {get_pst_day()[1]}", color=0xADD8E6)

    embed.description = f"**Cashapp:** {len(cashapp)} Payments Received\n**Zelle:** {len(zelle)} Payments Received\n**Venmo:** {len(venmo)} Payments Received\n**Total Payments**: {len(cashapp) + len(zelle) + len(venmo)}"
    embed.add_field(name="**Cashapp**", value=f"${round(sum(cashapp), 2)}", inline=True)
    embed.add_field(name="**Zelle**", value=f"${round(sum(zelle), 2)}", inline=True)
    embed.add_field(name="**Venmo**", value=f"${round(sum(venmo), 2)}", inline=True)
    embed.add_field(name="**Total**", value=f"${round(sum(cashapp) + sum(zelle) + sum(venmo), 2)}", inline=False)
    embed.add_field(name="**Average $/payment**", value=f'${round(sum(zelle + venmo + cashapp) / len(zelle + venmo + cashapp), 2)}', inline=False)
    await ctx.send(embed=embed)


if __name__ == "__main__":
    bot.run(settings["bot_token"])