"""Kiran the Discow Bot."""

import asyncio
import os
import re
import subprocess
import tempfile
import traceback

import discord
from discord.ext import commands
# import sympy
# from sympy.parsing import sympy_parser
from dotenv import load_dotenv
from gtts import gTTS

import c4board

load_dotenv()

with open("bad_words.txt") as bad_words_file:
    BAD_WORDS = [
        re.compile(line, re.IGNORECASE) for line in bad_words_file.read().splitlines()
    ]

SHAME_CHANNEL_PATTERN = re.compile(r".*wall.*of.*shame.*", re.DOTALL | re.IGNORECASE)

discord.opus.load_opus("libopus.so.0")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(intents=intents, command_prefix="!")


async def send_block(destination, content):
    """Send a block of text, splitting into multiple code blocks if necessary."""
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
    """Indicate that we have successfully logged in."""
    print("Logged in as {0.user}".format(bot))


tasks = {}


@bot.command()
async def hello(ctx):
    """Say hello."""
    await ctx.send(f"Hello, {ctx.author.display_name}!")


@bot.group()
async def task(ctx):
    """Manage tasks."""
    if ctx.guild not in tasks:
        tasks[ctx.guild] = []


@task.command()
async def add(ctx, *, new_task: commands.clean_content):
    """Add a new task."""
    tasks[ctx.guild].append(new_task)
    await ctx.send("Added task " + new_task)
    if len(ctx.message.mentions) > 0:
        await ctx.send(
            " ".join(user.mention for user in ctx.message.mentions)
            + " You have a new task!"
        )


@task.command(name="list")
async def list_(ctx):
    """List tasks."""
    if len(tasks[ctx.guild]) == 0:
        await ctx.send("There are no tasks. Yay!")
    else:
        await ctx.send(
            "\n".join(f"{i + 1}. {task}" for i, task in enumerate(tasks[ctx.guild]))
        )


@task.command()
async def remove(ctx, task_index: int):
    """Remove task specified by its index."""
    task_index -= 1
    try:
        tsk = tasks[ctx.guild].pop(task_index)
        await ctx.send("Deleted task " + tsk)
    except IndexError:
        await ctx.send("No such task")


@task.command()
async def clear(ctx):
    """Remove all tasks."""
    tasks[ctx.guild].clear()
    await ctx.send("Cleared tasks")


@bot.command()
async def say(ctx, *, message):
    """Echo the given message."""
    await ctx.send(message)


@bot.command()
async def dance(ctx):
    """Send a dancing cow GIF."""
    await ctx.send(file=discord.File("dance.gif"))


@bot.command()
async def skateboard(ctx):
    """Send a skateboarding cow GIF."""
    await ctx.send(file=discord.File("skateboard.gif"))


# @bot.command(name='sp')
# async def eval_sympy(ctx, *, expression):
#     """Evaluate a SymPy math expression."""
#     try:
#         result = sympy_parser.parse_expr(
#             expression,
#             transformations=sympy_parser.standard_transformations +
#             (sympy_parser.implicit_multiplication_application,
#              sympy_parser.rationalize, sympy_parser.convert_xor))
#     except:
#         await send_block(ctx, traceback.format_exc())
#     else:
#         await send_block(ctx, sympy.pretty(result))


async def _joinvoice(voice_client, channel):
    if voice_client is None:
        await channel.connect()
    else:
        if voice_client.is_playing():
            voice_client.stop()
        await voice_client.move_to(channel)


async def _speak(ctx, lang, tld, message):
    if not ctx.author.voice:
        await ctx.send("You must be in a voice channel in order to use this command.")
        return
    await _joinvoice(ctx.voice_client, ctx.author.voice.channel)
    temp_file = tempfile.TemporaryFile()
    tts = gTTS(message, lang=lang, tld=tld)
    tts.write_to_fp(temp_file)
    temp_file.seek(0)
    source = discord.FFmpegPCMAudio(temp_file, pipe=True)
    ctx.voice_client.play(source)


@bot.command()
async def speak(ctx, *, message: commands.clean_content):
    """Speak the given message."""
    await _speak(ctx, "en", "com", message)


@bot.command()
async def speaklang(ctx, language, *, message: commands.clean_content):
    """Same as !speak but allows you to set the language.

    Use two-letter language codes from https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes.
    """
    await _speak(ctx, language, "com", message)


@bot.command()
async def speakaccent(ctx, tld, *, message: commands.clean_content):
    """Same as !speak but allows you to specify the accent.

    See https://gtts.readthedocs.io/en/latest/module.html#localized-accents for possible values.
    """
    await _speak(ctx, "en", tld, message)


@bot.command()
async def speaklangaccent(ctx, language, tld, *, message: commands.clean_content):
    """Same as !speak but allows you to specify the language and accent.

    See the help for !speaklang and !speakaccent for more info.
    """
    await _speak(ctx, language, tld, message)


@bot.command(aliases=["dc"])
async def disconnect(ctx):
    """Disconnect from voice channel."""
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()


@bot.command()
async def fun(ctx, victim: discord.Member = None):
    """Mystery command."""
    if victim is None:
        victim = ctx.author
    if not victim.voice:
        await ctx.send(
            "You must be in a voice channel in order to use this command."
            if victim == ctx.author
            else "The victim must be in a voice channel in order for this command to work."
        )
        return
    await _joinvoice(ctx.voice_client, victim.voice.channel)
    source = discord.FFmpegOpusAudio("fun.opus", codec="copy")
    ctx.voice_client.play(source)


with open("cowsay_manual.txt") as cowsay_manual_file:
    COWSAY_MANUAL = cowsay_manual_file.read()


@bot.command(help=COWSAY_MANUAL)
async def cowsay(ctx, *args):
    """The original cowsay command."""
    proc = await asyncio.create_subprocess_exec(
        "cowsay",
        *args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    await send_block(ctx, (await proc.communicate())[0].decode())


@bot.command()
async def cowthink(ctx, *args):
    """Variation of cowsay.

    https://manpages.debian.org/buster/cowsay/cowsay.6.en.html
    """
    proc = await asyncio.create_subprocess_exec(
        "cowthink",
        *args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    await send_block(ctx, (await proc.communicate())[0].decode())


async def cowsay_block(block):
    """Wrap a block of text with cowsay."""
    proc = await asyncio.create_subprocess_exec(
        "cowsay", "-n", stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    return (await proc.communicate(block.encode()))[0].decode()


# @bot.command()
# async def cowsaysp(ctx, *, expression):
#     """Evaluate a SymPy math expression and cowsay the result."""
#     try:
#         result = sympy_parser.parse_expr(
#             expression,
#             transformations=sympy_parser.standard_transformations +
#             (sympy_parser.implicit_multiplication_application,
#              sympy_parser.rationalize, sympy_parser.convert_xor))
#     except:
#         await send_block(ctx, cowsay_block(traceback.format_exc()))
#     else:
#         await send_block(ctx, cowsay_block(sympy.pretty(result)))


@bot.command()
async def c4(ctx):  # pylint: disable=invalid-name
    """Play Four in a Row."""
    board = c4board.C4Board()
    msg = await ctx.send(board)

    async def add_reactions():
        for i in range(c4board.BOARD_WIDTH):
            await msg.add_reaction(
                str(i) + "\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}"
            )

    asyncio.create_task(add_reactions())

    def check(payload):
        if payload.message_id != msg.id:
            return False
        if payload.event_type == "REACTION_ADD" and payload.user_id == bot.user.id:
            return False
        emoji = str(payload.emoji)
        try:
            return (
                len(emoji) == 3
                and int(emoji[0]) < c4board.BOARD_WIDTH
                and emoji[1:]
                == "\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}"
            )
        except ValueError:
            return False

    pending = {
        asyncio.create_task(bot.wait_for("raw_reaction_add", check=check)),
        asyncio.create_task(bot.wait_for("raw_reaction_remove", check=check)),
    }

    try:
        while True:
            done, pending = await asyncio.wait(
                pending, timeout=300, return_when=asyncio.FIRST_COMPLETED
            )
            if not done:
                return
            for done_task in done:
                payload = done_task.result()
                move_result = board.move(int(str(payload.emoji)[0]))
                if move_result != c4board.MoveResult.INVALID:
                    await msg.edit(content=board)
                    if move_result == c4board.MoveResult.YELLOW_WIN:
                        await ctx.send("Yellow won!")
                        return
                    if move_result == c4board.MoveResult.RED_WIN:
                        await ctx.send("Red won!")
                        return
                    if move_result == c4board.MoveResult.DRAW:
                        await ctx.send("It's a draw!")
                        return

                if payload.event_type == "REACTION_ADD":
                    pending.add(
                        asyncio.create_task(
                            bot.wait_for("raw_reaction_add", check=check)
                        )
                    )
                else:
                    pending.add(
                        asyncio.create_task(
                            bot.wait_for("raw_reaction_remove", check=check)
                        )
                    )
    finally:
        for pending_task in pending:
            pending_task.cancel()


@bot.event
async def on_error(ctx, error):
    """Send errors to the text channel."""
    await send_block(
        ctx,
        "".join(
            traceback.format_exception(
                etype=type(error), value=error, tb=error.__traceback__
            )
        ),
    )


@bot.event
async def on_command_error(ctx, error):
    """Send command errors to the text channel."""
    await send_block(
        ctx,
        "".join(
            traceback.format_exception(
                etype=type(error), value=error, tb=error.__traceback__
            )
        ),
    )


@bot.event
async def on_message(message):
    """Check for bad words and speak things in the muted channel."""

    async def bad_word_check():
        if any(
            bad_word.search(message.clean_content) is not None for bad_word in BAD_WORDS
        ):
            shame_channel = message.channel
            try:
                for channel in message.guild.text_channels:
                    if SHAME_CHANNEL_PATTERN.fullmatch(channel.name):
                        shame_channel = channel
                        break
            except AttributeError:
                pass  # Message has no guild
            await shame_channel.send(
                "{} SAID A BAD WORD".format(message.author.display_name.upper())
            )

    async def speak_muted():
        if (
            not isinstance(message.channel, discord.DMChannel)
            and "muted" in message.channel.name.lower()
            and message.author.voice
            and not message.content.startswith("!")
        ):
            await _joinvoice(message.guild.voice_client, message.author.voice.channel)
            temp_file = tempfile.TemporaryFile()
            tts = gTTS(
                re.split(r"\W+", message.author.display_name, maxsplit=1)[0]
                + " said: "
                + message.clean_content
            )
            tts.write_to_fp(temp_file)
            temp_file.seek(0)
            source = discord.FFmpegPCMAudio(temp_file, pipe=True)
            message.guild.voice_client.play(source)

    await asyncio.gather(bad_word_check(), speak_muted(), bot.process_commands(message))


bot.run(os.environ["KIRAN_TOKEN"])
