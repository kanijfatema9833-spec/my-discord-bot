import os
import datetime
import discord
from discord import app_commands
from discord.ext import commands

# Intents কনফিগারেশন
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# আপনার প্রদত্ত ID-সমূহ
WELCOME_GOODBYE_CHANNEL_ID = 1544323418969743520  # welcome-and-goodbye
AUTO_ROLE_ID = 1544317910011478116               # Member
LOGS_CHANNEL_ID = 1544419504933699745             # Private Logs Channel

@bot.event
async def on_ready():
    # Slash Commands গ্লোবালি Sync করা
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

    # বটকে Do Not Disturb মোডে রাখা এবং "Watching BFTT: YET AGAIN 1B!" স্ট্যাটাস সেট করা
    activity = discord.Activity(type=discord.ActivityType.watching, name="BFTT: YET AGAIN 1B!")
    await bot.change_presence(status=discord.Status.dnd, activity=activity)
    
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('Bot is active and moderation tools are loaded!')

# --- WELCOME & AUTO ROLE EVENTS ---

@bot.event
async def on_member_join(member):
    # Welcome Message
    channel = bot.get_channel(WELCOME_GOODBYE_CHANNEL_ID)
    if channel:
        await channel.send(f'Welcome {member.mention} to BFTT: YET AGAIN!')
    
    # Auto Role
    role = member.guild.get_role(AUTO_ROLE_ID)
    if role:
        try:
            await member.add_roles(role)
        except discord.Forbidden:
            print("Role hierarchy issue: Make sure the bot's role is HIGHER than the Member role.")

@bot.event
async def on_member_remove(member):
    # Goodbye Message
    channel = bot.get_channel(WELCOME_GOODBYE_CHANNEL_ID)
    if channel:
        await channel.send(f'Goodbye {member.name} from BFTT: YET AGAIN!')

# --- HELPER FUNCTION FOR LOGGING ---

async def send_log(guild, embed):
    log_channel = guild.get_channel(LOGS_CHANNEL_ID)
    if log_channel:
        await log_channel.send(embed=embed)

# --- SLASH MODERATION COMMANDS ---

# ১. /clear <amount>
@bot.tree.command(name="clear", description="মেসেজ ডিলিট করার কমান্ড")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int = 5):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    
    embed = discord.Embed(title="Messages Cleared", color=discord.Color.blue(), timestamp=datetime.datetime.utcnow())
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
    embed.add_field(name="Channel", value=interaction.channel.mention, inline=True)
    embed.add_field(name="Amount", value=f"{len(deleted)} messages", inline=False)
    
    await send_log(interaction.guild, embed)
    await interaction.followup.send(f'{len(deleted)} টি মেসেজ মুছে ফেলা হয়েছে।', ephemeral=True)

# ২. /warn <user> <reason>
@bot.tree.command(name="warn", description="ইউজারকে সতর্কবার্তা (Warning) দেওয়ার জন্য")
@app_commands.checks.has_permissions(kick_members=True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.send(f"You have been warned in {interaction.guild.name} for: {reason}")
    except discord.Forbidden:
        pass
    
    embed = discord.Embed(title="User Warned", color=discord.Color.gold(), timestamp=datetime.datetime.utcnow())
    embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=True)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    
    await send_log(interaction.guild, embed)
    await interaction.response.send_message(f"{member.mention}-কে সতর্কবার্তা দেওয়া হয়েছে।")

# ৩. /timeout <user> <minutes> <reason>
@bot.tree.command(name="timeout", description="নির্দিষ্ট সময়ের জন্য ইউজারকে টাইমআউট করার জন্য")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason provided"):
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    
    embed = discord.Embed(title="User Timed Out", color=discord.Color.orange(), timestamp=datetime.datetime.utcnow())
    embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=True)
    embed.add_field(name="Duration", value=f"{minutes} minutes", inline=True)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    
    await send_log(interaction.guild, embed)
    await interaction.response.send_message(f"{member.mention}-কে {minutes} মিনিটের জন্য টাইমাউট করা হয়েছে।")

# ৪. /kick <user> <reason>
@bot.tree.command(name="kick", description="ইউজারকে সার্ভার থেকে কিক করার জন্য")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    
    embed = discord.Embed(title="User Kicked", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
    embed.add_field(name="User", value=f"{member.name} ({member.id})", inline=True)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    
    await send_log(interaction.guild, embed)
    await interaction.response.send_message(f"{member.name}-কে সার্ভার থেকে কিক করা হয়েছে।")

# ৫. /ban <user> <reason>
@bot.tree.command(name="ban", description="ইউজারকে স্থায়ীভাবে ব্যান করার জন্য")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.ban(reason=reason)
    
    embed = discord.Embed(title="User Banned", color=discord.Color.dark_red(), timestamp=datetime.datetime.utcnow())
    embed.add_field(name="User", value=f"{member.name} ({member.id})", inline=True)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    
    await send_log(interaction.guild, embed)
    await interaction.response.send_message(f"{member.name}-কে স্থায়ীভাবে ব্যান করা হয়েছে।")

# ৬. /unban <user_id>
@bot.tree.command(name="unban", description="ব্যান করা মেম্বারের ব্যান তুলে নেওয়ার জন্য")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: str):
    user = await bot.fetch_user(int(user_id))
    await interaction.guild.unban(user)
    
    embed = discord.Embed(title="User Unbanned", color=discord.Color.green(), timestamp=datetime.datetime.utcnow())
    embed.add_field(name="User", value=f"{user.name} ({user.id})", inline=True)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
    
    await send_log(interaction.guild, embed)
    await interaction.response.send_message(f"{user.name}-এর ব্যান তুলে নেওয়া হয়েছে।")

# Koyeb Environment Variable থেকে টোকেন গ্রহণ করবে
bot.run(os.environ['DISCORD_TOKEN'])

