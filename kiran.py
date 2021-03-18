#!/usr/bin/env python3

import discord
from discord.ext import commands
import os
import sympy
from sympy.parsing import sympy_parser
import traceback
from dotenv import load_dotenv
import re
from gtts import gTTS

load_dotenv()

with open('bad_words.txt') as bad_words_file:
    BAD_WORDS = [re.compile(line, re.IGNORECASE) for line in bad_words_file.read().splitlines()]

SHAME_CHANNEL_PATTERN = re.compile(r'.*wall.*of.*shame.*', re.DOTALL | re.IGNORECASE)

discord.opus.load_opus('libopus.so.0')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(intents=intents, command_prefix='!')

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

tasks = {}

@bot.command(help='Say hello')
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author.display_name}!')

@bot.group(help='Manage tasks')
async def task(ctx):
    if ctx.guild not in tasks:
        tasks[ctx.guild] = []

@task.command(help='Add new task')
async def add(ctx, *, new_task: commands.clean_content):
    tasks[ctx.guild].append(new_task)
    await ctx.send('Added task ' + new_task)
    if len(ctx.message.mentions) > 0:
        await ctx.send(' '.join(user.mention for user in ctx.message.mentions) + ' You have a new task!')

@task.command(help='List tasks')
async def list(ctx):
    if len(tasks[ctx.guild]) == 0:
        await ctx.send('There are no tasks. Yay!')
    else:
        await ctx.send('\n'.join(f'{i + 1}. {task}' for i, task in enumerate(tasks[ctx.guild])))

@task.command(help='Remove task specified by its number')
async def remove(ctx, task_index: int):
    task_index -= 1
    try:
        task = tasks[ctx.guild].pop(task_index)
        await ctx.send('Deleted task ' + task)
    except IndexError:
        await ctx.send('No such task')

@task.command(help='Remove all tasks')
async def clear(ctx):
    tasks[ctx.guild].clear()
    await ctx.send('Cleared tasks')

@bot.command(help='Echo the given message')
async def say(ctx, *, message):
    await ctx.send(message)

@bot.command(help='Send dancing cow GIF')
async def dance(ctx):
    await ctx.send(file=discord.File('dance.gif'))

@bot.command(help='Evaluate a SymPy expression')
async def sp(ctx, *, expression):
    try:
        result = sympy_parser.parse_expr(expression, transformations=sympy_parser.standard_transformations
                                         + (sympy_parser.implicit_multiplication_application,
                                            sympy_parser.rationalize,
                                            sympy_parser.convert_xor))
    except:
        await ctx.send('```\n{}\n```'.format(traceback.format_exc()))
    else:
        await ctx.send('```\n{}\n```'.format(sympy.pretty(result)))

@bot.command(help='Speak the given message')
async def speak(ctx, *, message: commands.clean_content):
    if not ctx.author.voice:
        await ctx.send("You must be in a voice channel.")
        return
    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()
    else:
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        await ctx.voice_client.move_to(ctx.author.voice.channel)
    tts = gTTS(message, lang='en')
    tts.save('message.mp3')
    source = discord.FFmpegPCMAudio('message.mp3')
    ctx.voice_client.play(source)

@bot.event
async def on_command_error(ctx, error):
    await ctx.send('```\n{}\n```'.format(''.join(traceback.format_exception(
        etype=type(error), value=error, tb=error.__traceback__
    ))))

@bot.event
async def on_message(message):
    if any(bad_word.search(message.clean_content) is not None for bad_word in BAD_WORDS):
        shame_channel = message.channel
        try:
            for channel in message.guild.text_channels:
                if SHAME_CHANNEL_PATTERN.fullmatch(channel.name):
                    shame_channel = channel
                    break
        except AttributeError:
            pass
        await shame_channel.send('{} SAID A BAD WORD'.format(message.author.display_name.upper()))
    await bot.process_commands(message)

bot.run(os.environ['KIRAN_TOKEN'])
