import discord
from discord.ext import commands
from datetime import datetime, timedelta
import pickle

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or('/', '!'), intents=intents)

voice_cooldowns = {}  # Dictionary to store voice cooldowns

# Load user_tracked_users from a pickle file if it exists, otherwise initialize an empty dictionary
try:
    with open('user_tracked_users.pkl', 'rb') as f:
        user_tracked_users = pickle.load(f)
except FileNotFoundError:
    user_tracked_users = {}


class TrackingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='start')
    async def start_monitor(self, ctx, target_user: discord.User, *, nickname: str = None):
        if not nickname:
            await ctx.send("Please include a nickname after the USERID for the user you are targeting!")
            return

        if ctx.author.bot:
            return

        user_id = ctx.author.id
        if user_id not in user_tracked_users:
            user_tracked_users[user_id] = {}

        user_tracked_users[user_id][target_user.id] = {'nickname': nickname}
        await ctx.send(
            f"Now tracking messages and voice from user {target_user.name} ({nickname}). Messages will be sent to your DM.")

        # Save user_tracked_users to the pickle file
        with open('user_tracked_users.pkl', 'wb') as f:
            pickle.dump(user_tracked_users, f)

    @commands.command(name='stop')
    async def stop_monitor(self, ctx, arg1, arg2=None):
        if ctx.author.bot:
            return

        # Determine if the first argument is a stop type or a user
        if arg1 in ['voice', 'messages', 'both']:
            # If only stop type is given and not the user, default to stopping everything
            stop_type = arg1
            target_user = None
        else:
            # Try converting arg1 to a user
            try:
                target_user = await commands.UserConverter().convert(ctx, arg1)
                stop_type = arg2 if arg2 else 'both'
            except commands.UserNotFound:
                await ctx.send(f"Could not find user '{arg1}'.")
                return

        user_id = ctx.author.id

        if target_user:
            if user_id in user_tracked_users and target_user.id in user_tracked_users[user_id]:
                if stop_type == 'both':
                    user_tracked_users[user_id].pop(target_user.id)
                    await ctx.send(f"Stopped tracking {target_user.name}'s messages and voice activity.")
                elif stop_type == 'messages':
                    if 'voice_only' not in user_tracked_users[user_id][target_user.id]:
                        user_tracked_users[user_id][target_user.id]['voice_only'] = True
                    else:
                        user_tracked_users[user_id].pop(target_user.id)
                    await ctx.send(f"Stopped tracking {target_user.name}'s messages.")
                elif stop_type == 'voice':
                    if 'messages_only' not in user_tracked_users[user_id][target_user.id]:
                        user_tracked_users[user_id][target_user.id]['messages_only'] = True
                    else:
                        user_tracked_users[user_id].pop(target_user.id)
                    await ctx.send(f"Stopped tracking {target_user.name}'s voice activity.")

                # Save user_tracked_users to the pickle file
                with open('user_tracked_users.pkl', 'wb') as f:
                    pickle.dump(user_tracked_users, f)
            else:
                await ctx.send(f"Not tracking {target_user.name}.")

        else:
            if user_id in user_tracked_users:
                user_tracked_users[user_id].clear()
                await ctx.send("Stopped tracking messages and voice.")

                # Save user_tracked_users to the pickle file
                with open('user_tracked_users.pkl', 'wb') as f:
                    pickle.dump(user_tracked_users, f)

    @commands.command(name='voice')
    async def voice_monitor(self, ctx, target_user: discord.User, *, nickname: str = None):
        if not nickname:
            await ctx.send("Please include a nickname after the USERID for the user you are targeting!")
            return

        if ctx.author.bot:
            return

        user_id = ctx.author.id
        if user_id not in user_tracked_users:
            user_tracked_users[user_id] = {}

        user_tracked_users[user_id][target_user.id] = {'nickname': nickname, 'voice_only': True}
        await ctx.send(
            f"Now tracking voice activity from user {target_user.name} ({nickname}). Voice activity will be sent to your DM.")

        # Save user_tracked_users to the pickle file
        with open('user_tracked_users.pkl', 'wb') as f:
            pickle.dump(user_tracked_users, f)

    @commands.command(name='messages')
    async def message_monitor(self, ctx, target_user: discord.User, *, nickname: str = None):
        if not nickname:
            await ctx.send("Please include a nickname after the USERID for the user you are targeting!")
            return

        if ctx.author.bot:
            return

        user_id = ctx.author.id
        if user_id not in user_tracked_users:
            user_tracked_users[user_id] = {}

        user_tracked_users[user_id][target_user.id] = {'nickname': nickname, 'messages_only': True}
        await ctx.send(
            f"Now tracking messages from user {target_user.name} ({nickname}). Messages will be sent to your DM.")

        # Save user_tracked_users to the pickle file
        with open('user_tracked_users.pkl', 'wb') as f:
            pickle.dump(user_tracked_users, f)

    def generate_notifyme_embed(self):
        embed = discord.Embed(title="NotifyMe \n", description="Track your friends activity and never miss another exciting message or call!")
        embed.add_field(name="How it works \n \n \n \n \n", value="All commands below are called by using !command 'User ID' nickname \n \n The User ID can be found by right clicking on the targeted users profile picture and clicking copy User ID ",  inline=False)
        embed.add_field(name="!start", value="Start monitoring a user's messages and voice activity.", inline=False)
        embed.add_field(name="!stop", value="Stop monitoring both messages and voice activity. \n \n !stop USERID will stop both messages and voice activity. \n \n !stop USERID voice will stop tracking the users voice activity only \n \n !stop USERID messages will stop tracking messages only", inline=False)
        embed.add_field(name="!voice", value="Start monitoring a user's voice activity only.", inline=False)
        embed.add_field(name="!messages", value="Start monitoring a user's messages only.", inline=False)
        return embed

# Remove the default /help command
bot.remove_command('help')


@bot.command(name='help')
async def help_command(ctx):
    await notifyme_command(ctx)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.add_cog(TrackingCog(bot))


@bot.command(name='notifyme')
async def notifyme_command(ctx):
    tracking_cog = bot.get_cog('TrackingCog')
    embed = tracking_cog.generate_notifyme_embed()
    await ctx.send(embed=embed)


@bot.event
async def on_message(message):
    for user_id, tracked_users in user_tracked_users.items():
        if message.author.id in tracked_users:
            if 'messages_only' in tracked_users[message.author.id] or 'voice_only' not in tracked_users[message.author.id]:
                nickname = tracked_users[message.author.id]['nickname']

                user = await bot.fetch_user(user_id)
                dm_channel = await user.create_dm()
                await dm_channel.send(
                    f'Message from :man_police_officer: {nickname} :man_police_officer:  in {message.guild.name}: {message.content}')

    await bot.process_commands(message)


@bot.event
async def on_voice_state_update(member, before, after):
    for user_id, tracked_users in user_tracked_users.items():
        if member.id in tracked_users and before.channel != after.channel and after.channel is not None:
            if 'voice_only' in tracked_users[member.id] or 'messages_only' not in tracked_users[member.id]:
                nickname = tracked_users[member.id]['nickname']

                if user_id not in voice_cooldowns or (datetime.now() - voice_cooldowns[user_id]) > timedelta(minutes=1):
                    user = await bot.fetch_user(user_id)
                    dm_channel = await user.create_dm()
                    await dm_channel.send(
                        f':microphone: {nickname} has joined voice channel "{after.channel.name}" in {member.guild.name}.')

                    voice_cooldowns[user_id] = datetime.now()  # Update the cooldown time

# Replace 'YOUR_TOKEN' with your actual bot token
bot.run('YOUR_TOKEN')
