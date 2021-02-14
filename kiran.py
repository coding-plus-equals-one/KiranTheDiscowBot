#!/usr/bin/env python3

import discord
import os

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

tasks = {}

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # print(message.content)

    try:
        if message.content == '!hello':
            await message.channel.send(f'Hello, {message.author.display_name}!')
        elif message.content.startswith('!task '):
            subcommand = message.clean_content.split(' ', 1)[1]
            if message.guild not in tasks:
                tasks[message.guild] = []
            if subcommand.startswith('add '):
                task_name = subcommand.split(' ', 1)[1]
                tasks[message.guild].append(task_name)
                await message.channel.send('Added task ' + task_name)
                if len(message.mentions) > 0:
                    await message.channel.send(' '.join([user.mention for user in message.mentions]) + ' You have a new task!')
            elif subcommand == 'list':
                if len(tasks[message.guild]) == 0:
                    await message.channel.send('There are no tasks. Yay!')
                else:
                    await message.channel.send('\n'.join([f'{i + 1}. {task}' for i, task in zip(range(len(tasks[message.guild])), tasks[message.guild])]))
            elif subcommand.startswith('remove '):
                task_index = int(subcommand.split(' ', 1)[1]) - 1
                task = tasks[message.guild].pop(task_index)
                await message.channel.send('Deleted task ' + task)
            elif subcommand == 'clear':
                tasks[message.guild].clear()
                await message.channel.send('Cleared tasks')
    except:
        pass

client.run(os.environ['KIRAN_TOKEN'])
