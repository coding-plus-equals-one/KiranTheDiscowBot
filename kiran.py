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
import tempfile

load_dotenv()

with open('bad_words.txt') as bad_words_file:
    BAD_WORDS = [re.compile(line, re.IGNORECASE) for line in bad_words_file.read().splitlines()]

SHAME_CHANNEL_PATTERN = re.compile(r'.*wall.*of.*shame.*', re.DOTALL | re.IGNORECASE)

discord.opus.load_opus('libopus.so.0')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(intents=intents, command_prefix='!')

async def send_block(destination, content):
    paginator = commands.Paginator()
    try:
        paginator.add_line(content)
    except RuntimeError:
        for line in content.splitlines():
            paginator.add_line(line)
    for page in paginator.pages:
        await destination.send(page)

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

@bot.command(help='Send skateboarding cow GIF')
async def skateboard(ctx):
    await ctx.send(file=discord.File('skateboard.gif'))

@bot.command(help='Evaluate a SymPy expression')
async def sp(ctx, *, expression):
    try:
        result = sympy_parser.parse_expr(expression, transformations=sympy_parser.standard_transformations
                                         + (sympy_parser.implicit_multiplication_application,
                                            sympy_parser.rationalize,
                                            sympy_parser.convert_xor))
    except:
        await send_block(ctx, traceback.format_exc())
    else:
        await send_block(ctx, sympy.pretty(result))

async def _joinvoice(voice_client, channel):
    if voice_client is None:
        await channel.connect()
    else:
        if voice_client.is_playing():
            voice_client.stop()
        await voice_client.move_to(channel)

async def _speak(ctx, lang, tld, message):
    if not ctx.author.voice:
        await ctx.send("You must be in a voice channel.")
        return
    await _joinvoice(ctx.voice_client, ctx.author.voice.channel)
    fp = tempfile.TemporaryFile()
    tts = gTTS(message, lang=lang, tld=tld)
    tts.write_to_fp(fp)
    fp.seek(0)
    source = discord.FFmpegPCMAudio(fp, pipe=True)
    ctx.voice_client.play(source)

@bot.command(help='Speak the given message')
async def speak(ctx, *, message: commands.clean_content):
    await _speak(ctx, 'en', 'com', message)

@bot.command(help='Same as !speak but allows you to set the language\n\n'
             'Use two-letter language codes from https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes.')
async def speaklang(ctx, language, *, message: commands.clean_content):
    await _speak(ctx, language, 'com', message)

@bot.command(help='Same as !speak but allows you to specify the accent\n\n'
             'See https://gtts.readthedocs.io/en/latest/module.html#localized-accents for possible values.')
async def speakaccent(ctx, tld, *, message: commands.clean_content):
    await _speak(ctx, 'en', tld, message)

@bot.command(help="Same as !speak but allows you to specify the language and accent\n\n"
             'See the help for !speaklang and !speakaccent for more info.')
async def speaklangaccent(ctx, language, tld, *, message: commands.clean_content):
    await _speak(ctx, language, tld, message)

@bot.command(help='Disconnect from voice channel')
async def disconnect(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()

@bot.event
async def on_command_error(ctx, error):
    await send_block(ctx, ''.join(traceback.format_exception(
        etype=type(error), value=error, tb=error.__traceback__
    )))

@bot.event
async def on_message(message):
    try:
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
        if 'muted' in message.channel.name.lower() and message.author.voice and not message.content.startswith('!'):
            await _joinvoice(message.guild.voice_client, message.author.voice.channel)
            fp = tempfile.TemporaryFile()
            tts = gTTS(message.author.display_name + ' said: ' + message.clean_content)
            tts.write_to_fp(fp)
            fp.seek(0)
            source = discord.FFmpegPCMAudio(fp, pipe=True)
            message.guild.voice_client.play(source)
    except:
        await send_block(message.channel, traceback.format_exc())
    await bot.process_commands(message)

bot.run(os.environ['KIRAN_TOKEN'])
