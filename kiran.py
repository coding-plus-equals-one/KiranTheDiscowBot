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
import subprocess

load_dotenv()

with open('bad_words.txt') as bad_words_file:
    BAD_WORDS = [
        re.compile(line, re.IGNORECASE)
        for line in bad_words_file.read().splitlines()
    ]

SHAME_CHANNEL_PATTERN = re.compile(r'.*wall.*of.*shame.*',
                                   re.DOTALL | re.IGNORECASE)

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
        await ctx.send(' '.join(user.mention
                                for user in ctx.message.mentions) +
                       ' You have a new task!')


@task.command(help='List tasks')
async def list(ctx):
    if len(tasks[ctx.guild]) == 0:
        await ctx.send('There are no tasks. Yay!')
    else:
        await ctx.send('\n'.join(f'{i + 1}. {task}'
                                 for i, task in enumerate(tasks[ctx.guild])))


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


@bot.command(help='Evaluate a SymPy math expression')
async def sp(ctx, *, expression):
    try:
        result = sympy_parser.parse_expr(
            expression,
            transformations=sympy_parser.standard_transformations +
            (sympy_parser.implicit_multiplication_application,
             sympy_parser.rationalize, sympy_parser.convert_xor))
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
        await ctx.send(
            "You must be in a voice channel in order to use this command.")
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


@bot.command(
    help='Same as !speak but allows you to set the language\n\n'
    'Use two-letter language codes from https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes.'
)
async def speaklang(ctx, language, *, message: commands.clean_content):
    await _speak(ctx, language, 'com', message)


@bot.command(
    help='Same as !speak but allows you to specify the accent\n\n'
    'See https://gtts.readthedocs.io/en/latest/module.html#localized-accents for possible values.'
)
async def speakaccent(ctx, tld, *, message: commands.clean_content):
    await _speak(ctx, 'en', tld, message)


@bot.command(
    help="Same as !speak but allows you to specify the language and accent\n\n"
    'See the help for !speaklang and !speakaccent for more info.')
async def speaklangaccent(ctx, language, tld, *,
                          message: commands.clean_content):
    await _speak(ctx, language, tld, message)


@bot.command(help='Disconnect from voice channel')
async def disconnect(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()


@bot.command(help="Mystery command")
async def fun(ctx, victim: discord.Member = None):
    if victim is None:
        victim = ctx.author
    if not victim.voice:
        await ctx.send(
            "The victim must be in a voice channel in order to use this command.")
        return
    await _joinvoice(ctx.voice_client, victim.voice.channel)
    source = discord.FFmpegOpusAudio('fun.opus', codec='copy')
    ctx.voice_client.play(source)


@bot.command(help="""The original cowsay command

Manual:
cowsay(1)		    General Commands Manual		     cowsay(1)

NAME
       cowsay/cowthink - configurable speaking/thinking cow (and a bit more)

SYNOPSIS
       cowsay  [-e  eye_string] [-f cowfile] [-h] [-l] [-n] [-T tongue_string]
       [-W column] [-bdgpstwy]

DESCRIPTION
       Cowsay generates an ASCII picture of a cow saying something provided by
       the  user.   If run with no arguments, it accepts standard input, word-
       wraps the message given at about 40 columns, and prints the cow	saying
       the given message on standard output.

       To  aid in the use of arbitrary messages with arbitrary whitespace, use
       the -n option.  If it is specified, the given message will not be word-
       wrapped.	  This is possibly useful if you want to make the cow think or
       speak in figlet(6).  If -n is specified, there must not be any command-
       line arguments left after all the switches have been processed.

       The -W specifies roughly (where the message should be wrapped.  The de‐
       fault is equivalent to -W 40 i.e. wrap words at or before the 40th col‐
       umn.

       If  any	command-line  arguments	 are left over after all switches have
       been processed, they become the cow's message.  The  program  will  not
       accept standard input for a message in this case.

       There are several provided modes which change the appearance of the cow
       depending on its particular emotional/physical state.   The  -b	option
       initiates  Borg	mode;  -d  causes  the	cow to appear dead; -g invokes
       greedy mode; -p causes a state of paranoia to come  over	 the  cow;  -s
       makes  the  cow	appear thoroughly stoned; -t yields a tired cow; -w is
       somewhat the opposite of -t, and initiates wired mode; -y brings on the
       cow's youthful appearance.

       The  user  may  specify	the  -e option to select the appearance of the
       cow's eyes, in which case the first  two	 characters  of	 the  argument
       string eye_string will be used.	The default eyes are 'oo'.  The tongue
       is similarly configurable through -T and tongue_string; it must be  two
       characters  and does not appear by default.  However, it does appear in
       the 'dead' and 'stoned' modes.  Any configuration done  by  -e  and  -T
       will be lost if one of the provided modes is used.

       The  -f option specifies a particular cow picture file (``cowfile'') to
       use.  If the cowfile spec contains '/' then it will be interpreted as a
       path  relative to the current directory.	 Otherwise, cowsay will search
       the path specified in the COWPATH environment variable.	 To  list  all
       cowfiles on the current COWPATH, invoke cowsay with the -l switch.

       If  the program is invoked as cowthink then the cow will think its mes‐
       sage instead of saying it.

COWFILE FORMAT
       A cowfile is made up of a simple block of perl(1) code, which assigns a
       picture	of a cow to the variable $the_cow.  Should you wish to custom‐
       ize the eyes or the tongue of the cow, then  the	 variables  $eyes  and
       $tongue may be used.  The trail leading up to the cow's message balloon
       is composed of the character(s) in the $thoughts variable.   Any	 back‐
       slashes	must  be reduplicated to prevent interpolation.	 The name of a
       cowfile should end with .cow, otherwise it is assumed not to be a  cow‐
       file.   Also, at-signs (``@'') must be backslashed because that is what
       Perl 5 expects.

COMPATIBILITY WITH OLDER VERSIONS
       What older versions? :-)

       Version 3.x is fully backward-compatible with 2.x versions.  If	you're
       still  using  a 1.x version, consider upgrading.	 And tell me where you
       got the older versions, since I didn't exactly put them up  for	world-
       wide access.

       Oh,  just  so  you  know,  this	manual	page documents version 3.02 of
       cowsay.

ENVIRONMENT
       The COWPATH environment variable, if present, will be  used  to	search
       for  cowfiles.  It contains a colon-separated list of directories, much
       like PATH or MANPATH.  It should always contain	the  /usr/share/cowsay
       directory,  or  at  least a directory with a file called default.cow in
       it.

FILES
       /usr/share/cowsay holds a sample set of cowfiles.  If your  COWPATH  is
       not explicitly set, it automatically contains this directory.

BUGS
       If there are any, please notify the author at the address below.

AUTHOR
       Tony  Monroe  (tony@nog.net),  with suggestions from Shannon Appel (ap‐
       pel@CSUA.Berkeley.EDU)  and  contributions  from	 Anthony  Polito  (as‐
       polito@CSUA.Berkeley.EDU).

SEE ALSO
       perl(1), wall(1), nwrite(1), figlet(6)

				    $Date$			     cowsay(1)

COWS:
apt                fox           sheep
bud-frogs          ghostbusters  skeleton
bunny              gnu           snowman
calvin             hellokitty    stegosaurus
cheese             kangaroo      stimpy
cock               kiss          suse
cower              koala         three-eyes
daemon             kosh          turkey
default            luke-koala    turtle
dragon-and-cow     mech-and-cow  tux
dragon             milk          unipony
duck               moofasa       unipony-smaller
elephant           moose         vader
elephant-in-snake  pony          vader-koala
eyes               pony-smaller  www
flaming-sheep      ren""")
async def cowsay(ctx, *args):
    await send_block(
        ctx,
        subprocess.run(('cowsay', ) + args,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       universal_newlines=True).stdout)


@bot.command(help='Variation of cowsay\n\n'
             'https://manpages.debian.org/buster/cowsay/cowsay.6.en.html')
async def cowthink(ctx, *args):
    await send_block(
        ctx,
        subprocess.run(('cowthink', ) + args,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       universal_newlines=True).stdout)


def cowsay_block(block):
    return subprocess.run(['cowsay', '-n'],
                          input=block,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          universal_newlines=True).stdout


@bot.command(help='Evaluate a SymPy math expression and cowsay the result')
async def cowsaysp(ctx, *, expression):
    try:
        result = sympy_parser.parse_expr(
            expression,
            transformations=sympy_parser.standard_transformations +
            (sympy_parser.implicit_multiplication_application,
             sympy_parser.rationalize, sympy_parser.convert_xor))
    except:
        await send_block(ctx, cowsay_block(traceback.format_exc()))
    else:
        await send_block(ctx, cowsay_block(sympy.pretty(result)))


@bot.event
async def on_command_error(ctx, error):
    await send_block(
        ctx, ''.join(
            traceback.format_exception(etype=type(error),
                                       value=error,
                                       tb=error.__traceback__)))


@bot.event
async def on_message(message):
    try:
        if any(
                bad_word.search(message.clean_content) is not None
                for bad_word in BAD_WORDS):
            shame_channel = message.channel
            try:
                for channel in message.guild.text_channels:
                    if SHAME_CHANNEL_PATTERN.fullmatch(channel.name):
                        shame_channel = channel
                        break
            except AttributeError:
                pass
            await shame_channel.send('{} SAID A BAD WORD'.format(
                message.author.display_name.upper()))
        if not isinstance(
                message.channel, discord.DMChannel
        ) and 'muted' in message.channel.name.lower(
        ) and message.author.voice and not message.content.startswith('!'):
            await _joinvoice(message.guild.voice_client,
                             message.author.voice.channel)
            fp = tempfile.TemporaryFile()
            tts = gTTS(message.author.display_name + ' said: ' +
                       message.clean_content)
            tts.write_to_fp(fp)
            fp.seek(0)
            source = discord.FFmpegPCMAudio(fp, pipe=True)
            message.guild.voice_client.play(source)
    except:
        await send_block(message.channel, traceback.format_exc())
    await bot.process_commands(message)


bot.run(os.environ['KIRAN_TOKEN'])
