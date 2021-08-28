import os
import json
import time

import discord
from discord.ext import commands, tasks
from discord import AllowedMentions, Message
from dotenv import load_dotenv

SAVE_NAME = "data.json"

registered_roles = {}
role_perms = {}
mentioned = {}
timer = time.time()
timer_best = 0

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = commands.Bot(command_prefix='+', help_command=None, activity=discord.Activity(type=discord.ActivityType.watching, name="+help"))

bot.allowed_mentions = AllowedMentions.none()


@tasks.loop(hours=1)
async def data_saver():
    if os.path.isfile(f"{SAVE_NAME}.bak"):
        os.remove(f"{SAVE_NAME}.bak")

    if os.path.isfile(SAVE_NAME):
        os.rename(SAVE_NAME, f"{SAVE_NAME}.bak")

    with open(SAVE_NAME, 'w') as f:
        json.dump([registered_roles, role_perms, mentioned, timer, timer_best], f)

    print(f"{time.asctime()} - data saved to disk")


@bot.event
async def on_ready():
    global registered_roles, role_perms, mentioned, timer, timer_best

    if os.path.isfile(SAVE_NAME):
        with open(SAVE_NAME, 'r') as f:
            bot_data = json.load(f)

            registered_roles = bot_data[0]
            role_perms = bot_data[1]
            mentioned = bot_data[2]
            timer = bot_data[3]
            timer_best = bot_data[4]

    data_saver.start()

    print("Ready")


@bot.event
async def on_message(msg: Message):
    global timer_best

    if msg.author == bot.user:
        return

    for user in msg.mentions:
        user_id = str(user.id)
        channel_id = str(msg.channel.id)

        if user_id not in mentioned:
            mentioned[user_id] = {}

        mentioned[user_id][channel_id] = msg.id

    if msg.content.lower().strip() == "who ping":
        user_id = str(msg.author.id)
        channel_id = str(msg.channel.id)

        if user_id in mentioned and channel_id in mentioned[user_id]:
            src_msg = await msg.channel.fetch_message(mentioned[user_id][channel_id])
            await msg.reply(f"You were last mentioned by <@{src_msg.author.id}> here: {src_msg.jump_url}")
        else:
            await msg.reply("Could not find a recent mention in this channel.")

    await bot.process_commands(msg)

    if bot.user in msg.mentions:
        await msg.add_reaction(bot.get_emoji(881265213972836453))

    # Inside joak
    if msg.guild.id == 717046745149866046 and "amime" in msg.content.lower():
        days = int((time.time() - timer) // 86400)
        if days > timer_best:
            timer_best = days

        await msg.reply(f"<@&811283129544867850> the\n{days} Days\nBest: {timer_best} Days")


@bot.command(name='help')
async def help_command(ctx: commands.Context):
    await ctx.reply("""```
+help                              - Shows this message
+invite                            - Shows a bot invite link to add to your server
+ping                              - Measures Discord API response time
+role
    set <role_name> <@role>        - Adds role label, where custom mention perms can be set
    remove <role_name>             - Removes a role from being pinged entirely via this bot
    list                           - Lists all roles registered via this bot interface
+roleperms
    add|remove <role_name> <@user> - Allows/Prevents a user from pinging a role via this bot
    list <role_name>               - Lists all users allowed to ping a role through this bot
+pingrole <role_name>              - Mentions a role
    ```""")


@bot.command(name='invite')
async def invite_command(ctx: commands.Context):
    await ctx.reply("https://discord.com/api/oauth2/authorize?client_id=880871977382998086&permissions=470080&scope=bot")


@bot.command(name='ping')
async def ping_command(ctx: commands.Context):
    await ctx.reply(f"Pong! {round(bot.latency, 2)}ms")


@bot.command(name='role')
@commands.has_permissions(manage_roles=True, mention_everyone=True)
async def role_command(ctx: commands.Context, subcommand: str, *args):
    if subcommand == "set":
        role_name = f"{ctx.guild.id}-{args[0]}"

        try:
            role = await commands.RoleConverter().convert(ctx, args[1])

            registered_roles[role_name] = role.id
            if role_name not in role_perms:
                role_perms[role_name] = []

            await ctx.reply(f"Added role label `{role_name.split('-', 1)[1]}` => <@&{role.id}>")

        except commands.errors.RoleNotFound:
            await ctx.reply(f"Could not find role \"{args[1]}\"")

    elif subcommand == "remove":
        role_name = f"{ctx.guild.id}-{args[0]}"

        try:
            role = registered_roles[role_name]

            del registered_roles[role_name]
            del role_perms[role_name]

            await ctx.reply(f"Removed role label `{role_name.split('-', 1)[1]}` => <@&{role}>")
        except KeyError:
            await ctx.reply(f"Role label `{role_name.split('-', 1)[1]}` does not exist")

    elif subcommand == "list":
        roles_list = ""

        for role_name in registered_roles:
            if role_name.split('-', 1)[0] == str(ctx.guild.id):
                roles_list += f"`{role_name.split('-', 1)[1]}` => <@&{registered_roles[role_name]}>\n"

        if roles_list:
            await ctx.reply(roles_list)
        else:
            await ctx.reply("There are no roles currently registered with this bot.")


@bot.command(name='roleperms')
@commands.has_permissions(manage_roles=True, mention_everyone=True)
async def roleperms_command(ctx: commands.Context, subcommand: str, role_name: str, *args):
    role_name = f"{ctx.guild.id}-{role_name}"

    if role_name in registered_roles:
        if subcommand == "add":
            try:
                user = await commands.UserConverter().convert(ctx, args[0])

                role_perms[role_name].append(user.id)

                await ctx.reply(f"Granted {user.mention} permissions to mention `{role_name.split('-', 1)[1]}`")

            except commands.errors.UserNotFound:
                await ctx.reply(f"Could not find user \"{args[0]}\"")

        elif subcommand == "remove":
            try:
                user = await commands.UserConverter().convert(ctx, args[0])

                role_perms[role_name].remove(user.id)

                await ctx.reply(f"Removed {user.mention}'s permissions to mention {role_name.split('-', 1)[1]}")
            except commands.errors.UserNotFound:
                await ctx.reply(f"User \"{args[0]}\" either didn't have perms already, or does not exist")

        elif subcommand == "list":
            user_list = f"Users allowed to mention role `{role_name.split('-', 1)[1]}`\n"

            if role_perms[role_name]:
                for user in role_perms[role_name]:
                    user_list += f"<@{user}>\n"

                await ctx.reply(user_list)

            else:
                await ctx.reply(f"No user has been granted permission to mention `{role_name.split('-', 1)[1]}` through this bot.")

    else:
        await ctx.reply(f"Role label `{role_name.split('-', 1)[1]}` does not exist.")


@bot.command(name='pingrole')
async def pingrole_command(ctx: commands.Context, role_name: str):
    role_name = f"{ctx.guild.id}-{role_name}"

    if role_name in registered_roles:
        if ctx.author.id in role_perms[role_name]:
            await ctx.send(f"<@&{registered_roles[role_name]}>", allowed_mentions=AllowedMentions(roles=True))
            await ctx.message.delete()

        else:
            await ctx.reply(f"You do not have permission to mention `{role_name.split('-', 1)[1]}`")

    else:
        await ctx.reply(f"Role label `{role_name.split('-', 1)[1]}` does not exist.")


bot.run(BOT_TOKEN)
