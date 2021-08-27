import os

from discord.ext import commands
from discord import AllowedMentions
from dotenv import load_dotenv

registered_roles = {}
role_perms = {}

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = commands.Bot(command_prefix='+', help_command=None)

bot.allowed_mentions = AllowedMentions.none()


@bot.event
async def on_ready():
    print("yes")


@bot.command(name='help')
async def help_command(ctx: commands.Context):
    await ctx.reply("""```
+help                              - Shows this message
+invite                            - Shows a bot invite link to add to your server
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


@bot.command(name='role')
@commands.has_permissions(manage_roles=True, mention_everyone=True)
async def role_command(ctx: commands.Context, subcommand: str, *args):
    if subcommand == "set":
        role_name = args[0]

        try:
            role = await commands.RoleConverter().convert(ctx, args[1])

            registered_roles[role_name] = role
            if role_name not in role_perms:
                role_perms[role_name] = []

            await ctx.reply(f"Added role label `{role_name}` => <@&{role.id}>")

        except commands.errors.RoleNotFound:
            await ctx.reply(f"Could not find role \"{args[1]}\"")

    elif subcommand == "remove":
        role_name = args[0]

        try:
            role = registered_roles[role_name]

            del registered_roles[role_name]
            del role_perms[role_name]

            await ctx.reply(f"Removed role label `{role_name}` => <@&{role.id}>")
        except KeyError:
            await ctx.reply(f"Role label `{role_name}` does not exist")

    elif subcommand == "list":
        roles_list = ""

        if registered_roles:
            for role_name in registered_roles:
                roles_list += f"`{role_name}` => <@&{registered_roles[role_name].id}>\n"

            await ctx.reply(roles_list)

        else:
            await ctx.reply("There are no roles currently registered with this bot.")


@bot.command(name='roleperms')
@commands.has_permissions(manage_roles=True, mention_everyone=True)
async def roleperms_command(ctx: commands.Context, subcommand: str, *args):
    pass


@bot.command(name='pingrole')
async def pingrole_command(ctx: commands.Context, role_name: str):
    pass


bot.run(BOT_TOKEN)
