import os

from discord.ext import commands
from dotenv import load_dotenv

registered_roles = {}
role_perms = {}

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = commands.Bot(command_prefix='+', help_command=None)


@bot.event
async def on_ready():
    print("yes")


@bot.command(name='help')
async def help_command(ctx: commands.Context):
    await ctx.send("""```
+help                              - Shows this message
+invite                            - Shows a bot invite link to add to your server
+role
    set <role_name> <@role>        - Defines a new role, where custom mention perms can be set
    remove <role_name>             - Removes a role from being pinged entirely via this bot
    list                           - Lists all roles registered via this bot interface
+roleperms
    add|remove <role_name> <@user> - Allows/Prevents a user from pinging a role via this bot
    list <role_name>               - Lists all users allowed to ping a role through this bot
+pingrole <role_name>              - Mentions a role
    ```""")


@bot.command(name='invite')
async def invite_command(ctx: commands.Context):
    await ctx.send("https://discord.com/api/oauth2/authorize?client_id=880871977382998086&permissions=470080&scope=bot")


@bot.command(name='role')
@commands.has_permissions(manage_roles=True, mention_everyone=True)
async def role_command(ctx: commands.Context, subcommand: str, *args):
    pass


@bot.command(name='roleperms')
@commands.has_permissions(manage_roles=True, mention_everyone=True)
async def roleperms_command(ctx: commands.Context, subcommand: str, *args):
    pass


@bot.command(name='pingrole')
async def pingrole_command(ctx: commands.Context, role_name: str):
    pass


bot.run(BOT_TOKEN)
