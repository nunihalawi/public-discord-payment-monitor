from imbox import Imbox
import datetime
from datetime import date
import time
import discord
from discord.ext import commands
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from lmxl import etree, html

async def start():
    while True:
        try:
            date = str(datetime.date.today())
            to_be_added = False
            print('checking')
            emailSession = Imbox("imap.gmail.com",
                # insert email and pw here
                username="",
                password="",
                ssl=True,
                ssl_context=None,
                starttls=False,
            )
            messages1 = emailSession.messages(unread=True)
            if len(messages1) > 0:
                #zelle
                if messages1[-1][1].sent_from[0]['email'] == 'no-reply@alertsp.chase.com':
                    embed = discord.Embed(title="Zelle Payment Detected", color=0x7aff7f)
                    money_parse = messages1[-1][1].body['plain'][0].split('<b>Amount:</b>')
                    money = money_parse[1].split(' ')[1]
                    name_parse = messages1[-1][1].body['plain'][0].split('<td align="left" style="vertical-align:top; font-family: Arial, Helvetica, sans-serif; font-size: 12px; color: #000000; padding: 0px 0px 20px 0px;">')
                    first_last = name_parse[1].split(' ')
                    #value = soup.find(class_='ammount').get_text()
                    embed.add_field(name="**Platform**", value="Zelle", inline=True)
                    embed.add_field(name="**Amount**", value=f'{money}', inline=False)
                    embed.add_field(name="**Sent To**", value=f'{first_last[0]} {first_last[1]}',inline=False)
                    embed.set_footer(text='Created by hate#2158', icon_url='https://i.pinimg.com/originals/b2/7d/2d/b27d2d22ab6b6c7d9e7dfd862d607786.jpg')
                    embed.set_thumbnail(url="https://play-lh.googleusercontent.com/F4U2pL8z-Ic5FzCfe1xVXMWRvff6oEBIzDsyGRc4mE3bIUPiCfhuXXXvTOfcpVglKqs")
                    emailSession.mark_seen(messages1[-1][0])
                    async with aiohttp.ClientSession() as session:  
                        webhook = Webhook.from_url('', adapter=AsyncWebhookAdapter(session))
                        await webhook.send(embed=embed)
                    refund = False
                    to_be_added = True
                    print('zelle payment detected')
                # cashapp parser
                elif messages1[-1][1].sent_from[0]['email'] == 'cash@square.com' and messages1[-1][1].body['plain'][0].split(' ')[0] != "Shaza":
                    money = messages1[-1][1].body['plain'][0].split(' ')[3]
                    sender_first_name = messages1[-1][1].body['plain'][0].split(' ')[5]
                    sender_last_name = messages1[-1][1].body['plain'][0].split(' ')[6]
                    link = messages1[-1][1].body['plain'][0].split(' ')[-1]
                    print(messages1[-1][1].body['plain'][0].split(' '))
                    embed=discord.Embed(title=("Cashapp Payment Detected"), color=0x7aff7f)
                    embed.add_field(name="**Platform**", value="Cashapp", inline=True)
                    embed.add_field(name="**Amount**", value=money, inline=False)
                    embed.add_field(name="**Sender**",value=f'{sender_first_name} {sender_last_name}',inline=False)
                    embed.set_footer(text='Created by hate#2158', icon_url='https://i.pinimg.com/originals/b2/7d/2d/b27d2d22ab6b6c7d9e7dfd862d607786.jpg')
                    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Square_Cash_app_logo.svg/1024px-Square_Cash_app_logo.svg.png")
                    async with aiohttp.ClientSession() as session:  
                        webhook = Webhook.from_url('', adapter=AsyncWebhookAdapter(session))
                        await webhook.send(embed=embed)
                    emailSession.mark_seen(messages1[-1][0])
                    refund = False
                    to_be_added = True
                    print('cashapp payment detected')
                #cashapp refunding
                elif messages1[-1][1].body['plain'][0].split(' ')[0] == 'Shaza':
                    name = messages1[-1][1].body['plain'][0].split(' ')
                    money = messages1[-1][1].body['plain'][0].split(' ')[3]
                    print(messages1[-1][1].body['plain'][0].split(' '))
                    embed=discord.Embed(title="Cashapp Refund Detected", color=0x7aff7f)
                    embed.add_field(name="**Platform**", value="Cashapp", inline=True)
                    embed.add_field(name="**Amount**", value=money, inline=False)
                    embed.add_field(name="**Sent To**",value=f'{name[5]} {name[6]}',inline=False)
                    embed.set_footer(text='Created by hate#2158', icon_url='https://i.pinimg.com/originals/b2/7d/2d/b27d2d22ab6b6c7d9e7dfd862d607786.jpg')
                    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Square_Cash_app_logo.svg/1024px-Square_Cash_app_logo.svg.png")
                    emailSession.mark_seen(messages1[-1][0])
                    async with aiohttp.ClientSession() as session:  
                        webhook = Webhook.from_url('', adapter=AsyncWebhookAdapter(session))
                        await webhook.send(embed=embed)
                    print('cashapp refund detected')
                    to_be_added = True
                    refund = True
                elif messages1[-1][1].sent_from[0]['email'] == 'service@paypal.com':
                    print('paypal money detected')
                    names = messages1[-1][1].body['plain'][0].split(';margin:0" dir="ltr"><span>')[1]
                    premoney = messages1[-1][1].body['plain'][0]
                    page_html =  etree.tostring(html.fromstring(premoney ), encoding='unicode', pretty_print=True)
                    soup = BeautifulSoup(page_html, 'html.parser')
                    names1,names2 = names.split(' ')[0],names.split(' ')[1]
                    results = soup.find(id='preHeader').text.split('$')[1]
                    embed=discord.Embed(title="PayPal Payment Detected", color=0x7aff7f)
                    embed.add_field(name="**Platform**", value="PayPal", inline=True)
                    embed.add_field(name="**Amount**", value=results, inline=False)
                    embed.add_field(name="**Sent From**",value=f'{names1} {names2}',inline=False)
                    embed.set_thumbnail(url='https://www.freepnglogos.com/uploads/paypal-logo-png-7.png')
                    emailSession.mark_seen(messages1[-1][0])
                    async with aiohttp.ClientSession() as session:  
                        webhook = Webhook.from_url('https://discord.com/api/webhooks/939363792117182485/UG7Y-PfhFrnxS71yC2ow6izti1ai2dF7pXkUD36YCzmBZqFm2n_zvbg5lyaqQYzTWzny', adapter=AsyncWebhookAdapter(session))
                        await webhook.send(embed=embed)
    
        except Exception as e:
            print("Error: " + str(e))
            emailSession.mark_seen(messages1[-1][0])

        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(start())
