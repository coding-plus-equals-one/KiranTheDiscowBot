#!/usr/bin/env python3

import discord
import os
import shlex
import collections

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
        if message.content.startswith('!'):
            args = collections.deque(shlex.split(message.clean_content[1:]))
            command = args.popleft()
            if command == 'hello':
                await message.channel.send(f'Hello, {message.author.display_name}!')
            elif command == 'task':
                if message.guild not in tasks:
                    tasks[message.guild] = []
                subcommand = args.popleft()
                if subcommand == 'add':
                    task_name = args.popleft()
                    tasks[message.guild].append(task_name)
                    await message.channel.send('Added task ' + task_name)
                    if len(message.mentions) > 0:
                        await message.channel.send(' '.join([user.mention for user in message.mentions]) + ' You have a new task!')
                elif subcommand == 'list':
                    if len(tasks[message.guild]) == 0:
                        await message.channel.send('There are no tasks. Yay!')
                    else:
                        await message.channel.send('\n'.join([f'{i + 1}. {task}' for i, task in zip(range(len(tasks[message.guild])), tasks[message.guild])]))
                elif subcommand == 'remove':
                    task_index = int(args.popleft()) - 1
                    task = tasks[message.guild].pop(task_index)
                    await message.channel.send('Deleted task ' + task)
                elif subcommand == 'clear':
                    tasks[message.guild].clear()
                    await message.channel.send('Cleared tasks')
    except:
        pass

client.run(os.environ['KIRAN_TOKEN'])
