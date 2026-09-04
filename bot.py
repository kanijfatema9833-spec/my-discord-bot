import os
import threading
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

keep_alive()

import os
import datetime
import discord
from discord import app_commands
from discord.ext import commands

# Intents কনফিগারেশন
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# আপনার প্রদত্ত আইডি-সমূহ
WELCOME_GOODBYE_CHANNEL_ID = 1544323418969743520
AUTO_ROLE_ID = 1544317910011478116
LOGS_CHANNEL_ID = 1544419504933699745

@bot.event
async def on_ready():
    # Slash Commands গ্লোবালি Sync করা
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands successfully.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

        # বটের স্ট্যাটাস Do Not Disturb এবং কাস্টম অ্যাক্টিভিটি সেট করা
    activity = discord.CustomActivity(name="Watching BFTT: YET AGAIN 1B!")
    await bot.change_presence(status=discord.Status.dnd, activity=activity)


    print(f"Logged in as {bot.user.name}")
    print("Bot is active and running!")

# ১. অটো-রোল এবং ওয়েলকাম মেসেজ
@bot.event
async def on_member_join(member):
    # অটো রোল প্রদান
    role = member.guild.get_role(AUTO_ROLE_ID)
    if role:
        try:
            await member.add_roles(role)
        except Exception as e:
            print(f"Failed to add auto role: {e}")

    # ওয়েলকাম মেসেজ পাঠানো
    channel = member.guild.get_channel(WELCOME_GOODBYE_CHANNEL_ID)
    if channel:
        await channel.send(f"Welcome <@{member.mention}> to BFTT: YET AGAIN!")

    # লগ চ্যালেনে মেম্বার জয়েনের লগ
    logs_channel = member.guild.get_channel(LOGS_CHANNEL_ID)
    if logs_channel:
        embed = discord.Embed(title="Member Joined", description=f"{member.name} has joined the server.", color=discord.Color.green(), timestamp=datetime.datetime.now())
        await logs_channel.send(embed=embed)

# ২. গুডবাই মেসেজ এবং লগ
@bot.event
async def on_member_remove(member):
    channel = member.guild.get_channel(WELCOME_GOODBYE_CHANNEL_ID)
    if channel:
        await channel.send(f"Goodbye, {member.name}. Sad to see you go!")

    logs_channel = member.guild.get_channel(LOGS_CHANNEL_ID)
    if logs_channel:
        embed = discord.Embed(title="Member Left", description=f"{member.name} has left the server.", color=discord.Color.red(), timestamp=datetime.datetime.now())
        await logs_channel.send(embed=embed)

# ৩. মেসেজ ডিলিট লগ
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    logs_channel = message.guild.get_channel(LOGS_CHANNEL_ID)
    if logs_channel:
        embed = discord.Embed(title="Message Deleted", description=f"Message by {message.author.mention} deleted in {message.channel.mention}:\n{message.content}", color=discord.Color.orange(), timestamp=datetime.datetime.now())
        await logs_channel.send(embed=embed)

# ৪. মেসেজ এডিট লগ
@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content:
        return
    logs_channel = before.guild.get_channel(LOGS_CHANNEL_ID)
    if logs_channel:
        embed = discord.Embed(title="Message Edited", description=f"Message by {before.author.mention} edited in {before.channel.mention}.", color=discord.Color.blue(), timestamp=datetime.datetime.now())
        embed.add_field(name="Before", value=before.content or "None", inline=False)
        embed.add_field(name="After", value=after.content or "None", inline=False)
        await logs_channel.send(embed=embed)

# ৫. মেম্বার ব্যান লগ
@bot.event
async def on_member_ban(guild, user):
    logs_channel = guild.get_channel(LOGS_CHANNEL_ID)
    if logs_channel:
        embed = discord.Embed(title="Member Banned", description=f"{user.name} has been banned from the server.", color=discord.Color.dark_red(), timestamp=datetime.datetime.now())
        await logs_channel.send(embed=embed)

# ৬. মেম্বার আনব্যান লগ
@bot.event
async def on_member_unban(guild, user):
    logs_channel = guild.get_channel(LOGS_CHANNEL_ID)
    if logs_channel:
        embed = discord.Embed(title="Member Unbanned", description=f"{user.name} has been unbanned.", color=discord.Color.teal(), timestamp=datetime.datetime.now())
        await logs_channel.send(embed=embed)

# --- Member Audit (Role Change, Timeout, Kick) ---
@bot.event
async def on_member_update(before, after):
    logs_channel = before.guild.get_channel(LOGS_CHANNEL_ID)
    if not logs_channel:
        return

    # Role Added / Removed
    if before.roles != after.roles:
        added = [r.name for r in after.roles if r not in before.roles]
        removed = [r.name for r in before.roles if r not in after.roles]
        if added:
            embed = discord.Embed(title="Role Added", description=f"Role **{', '.join(added)}** added to {after.mention}", color=discord.Color.green(), timestamp=datetime.datetime.now())
            await logs_channel.send(embed=embed)
        if removed:
            embed = discord.Embed(title="Role Removed", description=f"Role **{', '.join(removed)}** removed from {after.mention}", color=discord.Color.orange(), timestamp=datetime.datetime.now())
            await logs_channel.send(embed=embed)

    # Timeout / Untimeout
    if before.timed_out_until != after.timed_out_until:
        if after.timed_out_until:
            embed = discord.Embed(title="Member Timeouted", description=f"{after.mention} has been timed out until {after.timed_out_until.strftime('%Y-%m-%d %H:%M:%S')}", color=discord.Color.red(), timestamp=datetime.datetime.now())
        else:
            embed = discord.Embed(title="Member Untimeouted", description=f"Timeout removed for {after.mention}", color=discord.Color.green(), timestamp=datetime.datetime.now())
        await logs_channel.send(embed=embed)

# --- Role Events ---
@bot.event
async def on_guild_role_create(role):
    logs_channel = role.guild.get_channel(LOGS_CHANNEL_ID)
    if logs_channel:
        embed = discord.Embed(title="Role Created", description=f"Role **{role.name}** was created.", color=discord.Color.blue(), timestamp=datetime.datetime.now())
        await logs_channel.send(embed=embed)

@bot.event
async def on_guild_role_delete(role):
    logs_channel = role.guild.get_channel(LOGS_CHANNEL_ID)
    if logs_channel:
        embed = discord.Embed(title="Role Deleted", description=f"Role **{role.name}** was deleted.", color=discord.Color.dark_red(), timestamp=datetime.datetime.now())
        await logs_channel.send(embed=embed)

# --- Channel Events ---
@bot.event
async def on_guild_channel_create(channel):
    logs_channel = channel.guild.get_channel(LOGS_CHANNEL_ID)
    if logs_channel:
        embed = discord.Embed(title="Channel Created", description=f"Channel {channel.mention} (**{channel.name}**) was created.", color=discord.Color.green(), timestamp=datetime.datetime.now())
        await logs_channel.send(embed=embed)

@bot.event
async def on_guild_channel_delete(channel):
    logs_channel = channel.guild.get_channel(LOGS_CHANNEL_ID)
    if logs_channel:
        embed = discord.Embed(title="Channel Deleted", description=f"Channel **{channel.name}** was deleted.", color=discord.Color.red(), timestamp=datetime.datetime.now())
        await logs_channel.send(embed=embed)


# --- মডারেশন এবং অন্যান্য স্ল্যাশ কমান্ডসমূহ ---

@bot.tree.command(name="say", description="Makes the bot say something")
@app_commands.describe(message="The message you want the bot to say")
async def say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

@bot.tree.command(name="kick", description="Kicks a member from the server")
@app_commands.describe(member="The member to kick", reason="Reason for kicking")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"Kicked {member.mention} for: {reason}", ephemeral=True)

@bot.tree.command(name="ban", description="Bans a member from the server")
@app_commands.describe(member="The member to ban", reason="Reason for banning")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"Banned {member.mention} for: {reason}", ephemeral=True)

@bot.tree.command(name="timeout", description="Timeouts a member")
@app_commands.describe(member="The member to timeout", minutes="Duration in minutes", reason="Reason")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason provided"):
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await interaction.response.send_message(f"Timed out {member.mention} for {minutes} minutes.", ephemeral=True)

# বট রান করার জন্য টোকেন লোড করা
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: DISCORD_TOKEN environment variable not found.")
