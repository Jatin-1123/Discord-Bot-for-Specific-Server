import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()


prefix = '?'
client = commands.Bot(command_prefix=prefix,
                      case_insensitive=True,
                      activity=discord.Game(f'with Whitelisted Players!'),
                      status=discord.Status.do_not_disturb
                      )
client.remove_command('help')


@client.event
async def on_ready():
#    global roles
    print('Bot is Online!')
#    roles = guild.roles()


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please pass in Required Arguments')
    elif isinstance(error, commands.MissingRole):
        await ctx.send('You are not worthy to use this command!')


@client.command()
async def ping(ctx):
    await ctx.send(f'Pong. {round(client.latency * 1000)}ms')


def are_you_capable(ctx):
    categoryRequirement = str(ctx.channel.category).upper() == 'ADMIN THINGS'
    ownerCheck = ctx.author == ctx.guild.owner
    whiteListCheck = any(r.name == 'Whitelister' for r in ctx.author.roles)
    return (categoryRequirement and whiteListCheck) or ownerCheck


@client.command(pass_context=True)
@commands.check(are_you_capable)
async def accept(ctx, member: discord.Member = None, userName=None, age = 16):
    if member and userName is not None:
        if int(age) < 16:
            underAge = True
        else:
            underAge = False
        if discord.utils.get(member.roles, name='Ŕ') and discord.utils.get(member.roles, name='New Member'):
            whiteChannel = discord.utils.get(
                ctx.guild.text_channels, name='console')
            await whiteChannel.send(f'whitelist add {userName}')
            #whiteChannelC = discord.utils.get(
            #    ctx.guild.text_channels, name='console-creative')
            #await whiteChannelC.send(f'whitelist add {userName}')

            await member.add_roles(discord.utils.get(ctx.guild.roles, name='Wolf Cub'))
            await member.remove_roles(discord.utils.get(ctx.guild.roles, name='New Member'))

            appChannel = discord.utils.get(
                ctx.guild.text_channels, name='application')
            async for i in appChannel.history(limit=50, oldest_first=False):
                if i.author == member:
                    messageAccept = i
                    await messageAccept.add_reaction(discord.utils.get(ctx.guild.emojis, name="emoji_10"))
                    break

            logChannel = discord.utils.get(
                ctx.guild.text_channels, name='admin-bots')
            embed = discord.Embed(title=f"{member} Accepted",
                                  colour=discord.Colour(0xec7ddf),
                                  description=f"{ctx.author.mention} Accepted {member.mention}!")
            await logChannel.send(embed=embed)

            if member.display_name != userName:
                await member.edit(nick=userName)

            sendChannel = discord.utils.get(
                ctx.guild.text_channels, name='staff-help')
            await sendChannel.send(
                f'{member.mention} you have been accepted!\n\nIP Address: wolfcraft.mcserver.us\nYou should be seeing a lot more channels in the discord! We have an {(discord.utils.get(ctx.guild.text_channels, name = "in-game-bridge")).mention} where you can talk to players online and vice-versa, a {(discord.utils.get(ctx.guild.text_channels, name = "live-map")).mention} of our world and some other great features!')
            if underAge:
                blacklistChannel = discord.utils.get(
                    ctx.guild.text_channels, name='nsfw')
                overwrite = discord.PermissionOverwrite()
                overwrite.read_messages = False
                await blacklistChannel.set_permissions(member, overwrite=overwrite)
        else:
            await ctx.send(f'Can Not accept {member.mention}({userName}) as they have not read rules, or are not New')


@client.command(pass_context=True)
@commands.check(are_you_capable)
@commands.has_role('Whitelister')
async def reject(ctx, member: discord.Member = None, *, reason=None):
    if member is not None:
        if discord.utils.get(member.roles, name='Ŕ'):
            appChannel = discord.utils.get(
                ctx.guild.text_channels, name='applications')
            async for i in appChannel.history(limit=50, oldest_first=False):
                if i.author == member:
                    messageReject = i
                    await messageReject.add_reaction(discord.utils.get(ctx.guild.emojis, name="emoji_11"))
                    break

            logChannel = discord.utils.get(
                ctx.guild.text_channels, name='admin-bots')
            embed = discord.Embed(title=f"{member} Rejected",
                                  colour=discord.Colour(0xec7ddf),
                                  description=f"{ctx.author.mention} Rejected {member.mention}{'.' if reason is None else f' because {reason}'}")
            await logChannel.send(embed=embed)

            rejectChannel = await member.create_dm()
            await rejectChannel.send(
                f'You were NOT accepted in in Wolf Craft{"." if reason is None else f" because {reason}"}')

            await member.kick()


@client.command(aliases=['help', 'halp'])
@commands.check(are_you_capable)
async def sendHelp(ctx):
    embed = discord.Embed(title="__General Commands__",
                          colour=discord.Colour(0x7a72e4),
                          description="Commands for Wolfcraft are :\n\n\n")

    embed.add_field(name=":one: ?accept @user <Minecraft Username> <__optional__ Age>",
                    value="> Accept an User into Wolfcraft! They must have \"Ŕ\" Role, Indicating they Have indeed read the Rules.\n\n> __**Usage Examples:**__\n> ?accept <@!437491079869104138> PhoenixGamer90 10\n> \tThis will accept <@!437491079869104138>, whitelist `PhoenixGamer90 and Remove <@!437491079869104138> Permission to view <#710762105401376829> even with the role!\n\n",
                    inline = False)
    embed.add_field(name=":two: ?reject @user <__optional__ Reason>",
                    value="> Reject an User's Application!\n\n> __**Usage Examples:**__\n> ?reject <@!437491079869104138> A reason Here\n> \tThis will Reject <@!437491079869104138> and kick them from Discord, After letting them know in a DM.\n\n",
                    inline = False)
    embed.add_field(name=":three: ?unwhitelist <Minecraft Username>",
                    value="Unwhitelists a User from BOTH Creative AND Survival Server!\n\n> __**Usage Examples:**__\n> ?unwhitelist PhoenixGamer90\n> \tThis will unwhitelist a User from the server (Can be used to stop people from joining, in case of Rule Break.)",
                    inline = False)
    embed.add_field(name=":four: ?ban @user <Minecraft Username> <__optional__ Reason>",
                    value="Bans a User from BOTH Creative AND Survival Server!\n\n> __**Usage Examples:**__\n> ?ban <@!437491079869104138> PhoenixGamer90 For Doing Things\n> \tThis will Ban <@!437491079869104138> from the servers and Discord",
                    inline = False)
    msg = await ctx.fetch_message(758213497867468861)
    await msg.edit(embed=embed)


@client.command()
@commands.check(are_you_capable)
async def unwhitelist(ctx, userName):
    whiteChannelC = discord.utils.get(ctx.guild.text_channels, name='console-creative')
    await whiteChannel.send(f'whitelist remove {userName}')

    whiteChannel = discord.utils.get(ctx.guild.text_channels, name='console')
    await whiteChannel.send(f'whitelist remove {userName}')


@client.command()
@commands.check(are_you_capable)
async def ban(ctx, member: discord.Member, userName, *, reason = None):
    if reason is None:
        reason = "Ban Hammer Has Spoken"
    whiteChannelC = discord.utils.get(ctx.guild.text_channels, name='console-creative')
    await whiteChannel.send(f'ban username {reason}')

    whiteChannel = discord.utils.get(ctx.guild.text_channels, name='console')
    await whiteChannel.send(f'ban username {reason}')

    await member.Ban(reason = reason)


# @client.command()
# async def updateColorRoles(ctx):
#     l = ctx.guild.roles
#     for i in l:
#         if i == 


client.run(os.getenv('BOT_TOKEN'))
