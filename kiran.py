#!/usr/bin/env python3

from discord.ext import commands
import os
import shlex
import collections

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

tasks = {}

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author.display_name}!')

@bot.group()
async def task(ctx):
    if ctx.guild not in tasks:
        tasks[ctx.guild] = []

@task.command()
async def add(ctx, *, arg):
    tasks[ctx.guild].append(arg)
    await ctx.send('Added task ' + arg)
    if len(ctx.message.mentions) > 0:
        await ctx.send(' '.join([user.mention for user in ctx.message.mentions]) + ' You have a new task!')

@task.command()
async def list(ctx):
    if len(tasks[ctx.guild]) == 0:
        await ctx.send('There are no tasks. Yay!')
    else:
        await ctx.send('\n'.join([f'{i + 1}. {task}' for i, task in zip(range(len(tasks[ctx.guild])), tasks[ctx.guild])]))

@task.command()
async def remove(ctx, task_index: int):
    task_index -= 1
    try:
        task = tasks[ctx.guild].pop(task_index)
        await ctx.send('Deleted task ' + task)
    except IndexError:
        await ctx.send('No such task')

@task.command()
async def clear(ctx):
    tasks[ctx.guild].clear()
    await ctx.send('Cleared tasks')

bot.run(os.environ['KIRAN_TOKEN'])
