#!/usr/bin/env python3

import discord
import os

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

tasks = []

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        await message.channel.send(f'Hello, {message.author.display_name}!')
    elif message.content.startswith('!addTask '):
        tasks.append(message.content.split(' ', 1)[1])
    elif message.content.startswith('!tasks'):
        await message.channel.send('\n'.join(tasks))

client.run(os.environ['KIRAN_TOKEN'])
