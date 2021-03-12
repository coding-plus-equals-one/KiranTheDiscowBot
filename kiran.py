#!/usr/bin/env python3

import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(intents=intents, command_prefix='!')

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

tasks = {}

@bot.command(brief='Say hello')
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author.display_name}!')

@bot.group(brief='Manage tasks')
async def task(ctx):
    if ctx.guild not in tasks:
        tasks[ctx.guild] = []

@task.command(brief='Add new task')
async def add(ctx, *, arg: commands.clean_content):
    tasks[ctx.guild].append(arg)
    await ctx.send('Added task ' + arg)
    if len(ctx.message.mentions) > 0:
        await ctx.send(' '.join([user.mention for user in ctx.message.mentions]) + ' You have a new task!')

@task.command(brief='List tasks')
async def list(ctx):
    if len(tasks[ctx.guild]) == 0:
        await ctx.send('There are no tasks. Yay!')
    else:
        await ctx.send('\n'.join([f'{i + 1}. {task}' for i, task in zip(range(len(tasks[ctx.guild])), tasks[ctx.guild])]))

@task.command(brief='Remove task specified by its number')
async def remove(ctx, task_index: int):
    task_index -= 1
    try:
        task = tasks[ctx.guild].pop(task_index)
        await ctx.send('Deleted task ' + task)
    except IndexError:
        await ctx.send('No such task')

@task.command(brief='Remove all tasks')
async def clear(ctx):
    tasks[ctx.guild].clear()
    await ctx.send('Cleared tasks')

@bot.command(brief='Echo the arguments')
async def say(ctx, *, arg):
    await ctx.send(arg)

@bot.command(brief='Send dancing cow GIF')
async def dance(ctx):
    await ctx.send(file=discord.File('dance.gif'))
brief='Send dancing cow GIF'
bot.run(os.environ['KIRAN_TOKEN'])
