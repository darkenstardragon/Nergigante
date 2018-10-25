import random
import asyncio
import aiohttp
import json
import discord
from discord import Game
from discord.ext.commands import Bot

BOT_PREFIX = ("?", "!")
client = Bot(command_prefix=BOT_PREFIX)


async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(6)

@client.event
async def on_message(message):

    # to make sure bot doesn't reply to itself
    if message.author == client.user:
        return

    # test function
    if message.content == "?test":
        msg = "Hello! {0.author.mention}".format(message)
        await client.send_message(message.channel, msg)

    # ?cr command
    if message.content.split()[0].lower() in ["?create", "!create", "!cr", "?cr"]:
        global LFG_CHANNEL_ID
        await client.send_message(message.channel, 'สวัสดี {0.author.mention} ... ข้าสร้าง LFG ของเจ้าไว้ที่ <#%s> เรียบร้อยแล้ว'.format(message) % LFG_CHANNEL_ID)
        list_message = message.content.split()
        if len(list_message) >= 4:
            sessionID = list_message[1]
            voice_channel = list_message[2]
            description = " ".join(list_message[3:])
            userID = message.server.get_member(message.author.id)
            embed = embedCreate(str(message.author.mention), getUrl(userID), sessionID, description, voice_channel)
            await client.send_message(discord.Object(id=LFG_CHANNEL_ID), embed=embed)

            messages = []
            async for msg in client.logs_from(discord.Object(id=LFG_CHANNEL_ID), limit=50):
                messages.append(msg)
                break
            for msg in messages:
                await client.add_reaction(msg, emoji="🔁")
                await client.add_reaction(msg,  emoji='\U0001F5D1')

        else:
            await client.send_message(message.channel, "แต่ว่าคำสั่งที่เจ้าใส่มาจะต้องเป็นรูปแบบ `?cr [sessionID] [voice channel] [คำอธิบาย..]` เท่านั้นนะ!".format(message))

    # ?channel command
    if message.content.split()[0].lower() in ["?channel", "!channel"]:
        list_message = message.content.split()
        if len(list_message) >= 2:
            LFG_CHANNEL_ID = list_message[1]
            await client.send_message(message.channel, "ต่อไปนี้ข้าจะโพสต์ LFG ลงที่ <#%s> ล่ะนะ!".format(message) % LFG_CHANNEL_ID)
        else:
            client.send_message(message.channel,"คำสั่งที่เจ้าใส่มาจะต้องเป็นรูปแบบ `?channel [channelID]` เท่านั้นนะ!".format(message))

    # ?clear command
    if message.content.split()[0].lower() in ["?clear", "!clear"]:
        list_message = message.content.split()
        if len(list_message) >= 2:
            count = int(list_message[1])
            if count >= 1:
                async for message in client.logs_from(message.channel, limit=50):
                    if count == 0:
                        msg = message
                        break
                    count -= 1
                await client.delete_message(msg)
            else:
                await client.send_message(message.channel, "the second parameter must be 1 or above")
        else:
            client.send_message(message.channel, "the command should be in form of `?clear [order]`")

    # ?addreaction command
    if message.content.split()[0].lower() in ["?addreaction", "!addreaction"]:
        list_message = message.content.split()
        if len(list_message) >= 2:
            count = int(list_message[1])
            if count >= 0:
                messages = []
                async for msg in client.logs_from(message.channel, limit=count):
                    messages.append(msg)
                for msg in messages:
                    await client.add_reaction(msg, emoji="🔁")
            else:
                await client.send_message(message.channel, "the second parameter must be 0 or above")
        else:
            client.send_message(message.channel, "the command should be in form of `?addreaction [order]`")

    # banned word detector
    for word in message.content.split():
        if(word.lower() in ["dick", "d1ck", "d!ck"]):
            lewd_responses = ["T-That's lewd {0.author.mention}".format(message)] * 5 + \
            ["R-Rawr don't say that word here >///< {0.author.mention}".format(message)] * 5 + \
            ["You are really lewd, aren't you? -////- {0.author.mention}".format(message)] * 5 + \
            ["R-Rawr... so lewd u////u".format(message)] * 5 + \
            ["Y-Yes please... I want your dick in my maw o//w//o".format(message)]
            await client.send_message(message.channel, random.choice(lewd_responses))
