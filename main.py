import discord
from discord import app_commands
from discord.ext import commands
import datetime
import json
import os
from typing import Dict, Any, Optional
import aiohttp

TOKEN = "Your_Token_:)"
SUPPORT_WEBHOOK_URL = "Here put a webhook for a support server where the /suport command will send the messages."
# REMIND THIS IS A PROJECT MADE BY MINDCREATOR9 AND CANT BE RESELED OR DISTRIBUTED AS YOURS. PLEAZE GIVE ME CREDITS FOR EVERYTHING.
# THIS IS NOT MY USUAL METHOD OF MAKING BOTS, BUT THIS WAS AN EXPERIMENT SO I MAKE IT LIKE THIS REALLY FAST AND FOR SHARING IT WITH THE COMMUNITY
# THIS PROJECT IS CURRENTLY ENDED BY OUR TEAM AND IS NO LONGER SUPPORTED / FEEL FREE TO USE THIS BOT AND MODIFY THE CODE. ONLY DONT SHARE IT AS YOURS :)
# We are using Json has database bc is easy and fast for a test. Feel free to change!

#BTW THIS CODE IS A MESS

class Database:
    def __init__(self, file_path: str = "dcutilitytoolsdb.json"):
        self.file_path = file_path
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "guild_config": {},
            "duty_sessions": {},
            "statistics": {}
        }
    

    def _save_data(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)

    def get_guild_config(self, guild_id: str) -> Dict:
        return self.data["guild_config"].get(str(guild_id), {})

    def set_guild_config(self, guild_id: str, config: Dict):
        self.data["guild_config"][str(guild_id)] = config
        self._save_data()

    def get_duty_session(self, user_id: str, guild_id: str) -> Dict:
        key = f"{user_id}-{guild_id}"
        return self.data["duty_sessions"].get(key, None)

    def set_duty_session(self, user_id: str, guild_id: str, session_data: Dict):
        key = f"{user_id}-{guild_id}"
        self.data["duty_sessions"][key] = session_data
        self._save_data()

    def remove_duty_session(self, user_id: str, guild_id: str):
        key = f"{user_id}-{guild_id}"
        if key in self.data["duty_sessions"]:
            del self.data["duty_sessions"][key]
            self._save_data()

def remove_guild_config(self, guild_id: str):
    if str(guild_id) in self.data["guild_config"]:
        del self.data["guild_config"][str(guild_id)]
        self._save_data()

def remove_all_guild_sessions(self, guild_id: str):
    self.data["duty_sessions"] = {
        k: v for k, v in self.data["duty_sessions"].items()
        if not k.endswith(f"-{guild_id}")
    }
    self._save_data()

def remove_user_sessions(self, user_id: str, guild_id: str):
    key = f"{user_id}-{guild_id}"
    if key in self.data["duty_sessions"]:
        del self.data["duty_sessions"][key]
        self._save_data()


class AdminBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.db = Database()
        self.start_time = datetime.datetime.utcnow()

def has_required_permissions():
    async def predicate(interaction: discord.Interaction):
        member = interaction.user
        if any([
            member.guild_permissions.administrator,
            member.guild_permissions.ban_members,
            member.guild_permissions.kick_members,
            member.guild_permissions.manage_channels
        ]):
            return True
            
        embed = discord.Embed(
            title="🚫 Insufficient Permissions",
            description="You need one of the following permissions in a role:\n• Administrator\n• Ban Members\n• Kick Members\n• Manage Channels",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return False
    return app_commands.check(predicate)

def admin_only():
    async def predicate(interaction: discord.Interaction):
        if not (interaction.user.guild_permissions.administrator or interaction.guild.owner_id == interaction.user.id):
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="This command requires Administrator permissions or Server Owner",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)


bot = AdminBot()


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)
        
        embed = discord.Embed(
            title="⏰ Cooldown Active",
            description=f"This command is on cooldown! Try again in:\n`{hours}h {minutes}m {seconds}s`",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

@bot.event
async def on_guild_remove(guild):
    guild_id = str(guild.id)
    bot.db.remove_guild_config(guild_id)
    bot.db.remove_all_guild_sessions(guild_id)
    print(f"🗑️ Cleaned up data for guild: {guild.id}")

@bot.event
async def on_member_remove(member):
    guild_id = str(member.guild.id)
    user_id = str(member.id)
    bot.db.remove_user_sessions(user_id, guild_id)
    print(f"🗑️ Cleaned up data for user: {member.id} in guild: {member.guild.id}")

@bot.event
async def on_guild_channel_delete(channel):
    guild_config = bot.db.get_guild_config(str(channel.guild.id))
    if guild_config and "log_channel_id" in guild_config:
        if guild_config["log_channel_id"] == channel.id:
            bot.db.set_guild_config(str(channel.guild.id), {})
            print(f"🗑️ Removed config for guild {channel.guild.id} due to channel deletion")

def is_owner():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.id == 674681061032198144
    return app_commands.check(predicate)

@bot.event
async def on_ready():
    print(f'🤖 {bot.user} is ready!')
    print('⚡ Syncing commands...')
    try:
        synced = await bot.tree.sync()
        print(f'✅ Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'❌ Error syncing commands: {e}')

@bot.tree.command(name="off-duty", description="End your admin duty session")
@app_commands.describe(summary="What you did during your duty")
@app_commands.checks.cooldown(1, 60)
@has_required_permissions()
async def off_duty(interaction: discord.Interaction, summary: str):
    session = bot.db.get_duty_session(str(interaction.user.id), str(interaction.guild_id))
    if not session:
        return await interaction.response.send_message("❌ You are not on duty!", ephemeral=True)
    
    start_time = datetime.datetime.fromisoformat(session["start_time"])
    duty_type = session["duty_type"]
    duration = datetime.datetime.utcnow() - start_time
    
    embed = discord.Embed(
        title="🏁 Admin Duty Ended",
        description=f"**{interaction.user.name}** has ended their duty session",
        color=discord.Color.red()
    )
    embed.add_field(name="Type", value=duty_type)
    embed.add_field(name="Duration", value=str(duration).split('.')[0])
    embed.add_field(name="Summary", value=summary, inline=False)
    embed.set_footer(text=f"ID: {interaction.user.id}")
    
    bot.db.remove_duty_session(str(interaction.user.id), str(interaction.guild_id))
    
    await interaction.response.send_message("✅ You are now off duty!", ephemeral=True)

    guild_config = bot.db.get_guild_config(str(interaction.guild_id))
    if guild_config and "log_channel_id" in guild_config:
        log_channel = interaction.guild.get_channel(guild_config["log_channel_id"])
        if log_channel:
            await log_channel.send(embed=embed)

@bot.tree.command(name="on-duty", description="Start your admin duty session")
@app_commands.describe(duty_type="In Game / On Discord")
@app_commands.checks.cooldown(1, 60)
@has_required_permissions()
async def on_duty(interaction: discord.Interaction, duty_type: str):
    if bot.db.get_duty_session(str(interaction.user.id), str(interaction.guild_id)):
        return await interaction.response.send_message("❌ You are already on duty!", ephemeral=True)
    
    session_data = {
        "start_time": datetime.datetime.utcnow().isoformat(),
        "duty_type": duty_type
    }
    
    bot.db.set_duty_session(str(interaction.user.id), str(interaction.guild_id), session_data)
    
    embed = discord.Embed(
        title="👮 Admin Duty Started",
        description=f"**{interaction.user.name}** has started their duty session",
        color=discord.Color.green()
    )
    embed.add_field(name="Type", value=duty_type)
    embed.add_field(name="Started at", value=f"<t:{int(datetime.datetime.utcnow().timestamp())}:F>")
    embed.set_footer(text=f"ID: {interaction.user.id}")
    await interaction.response.send_message("✅ You are now on duty!", ephemeral=True)
    guild_config = bot.db.get_guild_config(str(interaction.guild_id))
    if guild_config and "log_channel_id" in guild_config:
        log_channel = interaction.guild.get_channel(guild_config["log_channel_id"])
        if log_channel:
            await log_channel.send(embed=embed)

@bot.tree.command(name="ping", description="View bot status and latency")
@app_commands.checks.cooldown(1, 10)
async def ping(interaction: discord.Interaction):
    ws_latency = round(bot.latency * 1000, 2)
    
    if ws_latency < 100:
        status = ("🟢 Excellent", discord.Color.green())
    elif ws_latency < 200:
        status = ("🟡 Good", discord.Color.yellow())
    else:
        status = ("🔴 Poor", discord.Color.red())
    
    uptime = datetime.datetime.utcnow() - bot.start_time
    
    embed = discord.Embed(
        title="🏓 Pong!",
        color=status[1]
    )
    embed.add_field(name="🔗 WebSocket Latency", value=f"{ws_latency} ms")
    embed.add_field(name="🤖 Bot Name", value=bot.user.name)
    embed.add_field(name="⏱ Uptime", value=str(uptime).split('.')[0])
    embed.add_field(name="Status", value=status[0])
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="support", description="Request support from bot staff")
@app_commands.checks.cooldown(1, 300)
async def support(interaction: discord.Interaction, issue: str):
    try:
        invite = await interaction.channel.create_invite(max_age=0, max_uses=1)
        
        embed = discord.Embed(
            title="📩 New Support Request",
            description=issue,
            color=discord.Color.blue()
        )
        embed.add_field(name="Server", value=f"{interaction.guild.name} ({interaction.guild.id})")
        embed.add_field(name="Members", value=interaction.guild.member_count)
        embed.add_field(name="Requester", value=f"{interaction.user} ({interaction.user.id})")
        embed.add_field(name="Server Invite", value=invite.url)
        
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(SUPPORT_WEBHOOK_URL, session=session)
            await webhook.send(embed=embed)
        
        success_embed = discord.Embed(
            title="✅ Support Request Sent",
            description="Your support request has been successfully sent to our team!",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=success_embed, ephemeral=True)
        
    except discord.Forbidden:
        error_embed = discord.Embed(
            title="❌ Permission Error",
            description="I need permission to create invites in this channel!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=error_embed, ephemeral=True)
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description="An error occurred while processing your support request. Please try again later.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=error_embed, ephemeral=True)

@bot.tree.command(name="info", description="View bot statistics")
@is_owner()
async def info(interaction: discord.Interaction):
    total_users = sum(g.member_count for g in bot.guilds)
    
    embeds = []
    current_embed = discord.Embed(
        title="📊 Bot Statistics",
        color=discord.Color.blue()
    )
    current_embed.add_field(name="Total Servers", value=len(bot.guilds))
    current_embed.add_field(name="Total Users", value=total_users)
    
    server_info = ""
    for guild in bot.guilds:
        server_info += f"**{guild.name}** ({guild.id})\n"
        server_info += f"Members: {guild.member_count}\n"
        server_info += f"Owner: {guild.owner}\n\n"
        
        if len(server_info) > 1000:
            current_embed.add_field(name="Servers", value=server_info, inline=False)
            embeds.append(current_embed)
            current_embed = discord.Embed(color=discord.Color.blue())
            server_info = ""
    
    if server_info:
        current_embed.add_field(name="Servers", value=server_info, inline=False)
        embeds.append(current_embed)
    
    await interaction.response.send_message(embeds=embeds)

@bot.tree.command(name="config", description="Configure bot settings for your server")
@admin_only()
@app_commands.describe(
    action="Choose what to do with the logging channel",
    log_channel="Select a channel for logging (only needed for 'set' action)"
)
@app_commands.choices(action=[
    app_commands.Choice(name="view", value="view"),
    app_commands.Choice(name="set", value="set"),
    app_commands.Choice(name="remove", value="remove")
])
async def config(
    interaction: discord.Interaction,
    action: str,
    log_channel: Optional[discord.TextChannel] = None
):
    guild_id = str(interaction.guild_id)
    
    if action == "view":
        current_config = bot.db.get_guild_config(guild_id)
        if current_config and "log_channel_id" in current_config:
            channel = interaction.guild.get_channel(current_config["log_channel_id"])
            if channel:
                embed = discord.Embed(
                    title="⚙️ Current Configuration",
                    description=f"Log Channel: {channel.mention}",
                    color=discord.Color.blue()
                )
            else:
                embed = discord.Embed(
                    title="⚠️ Configuration Error",
                    description="The configured channel no longer exists!",
                    color=discord.Color.orange()
                )
        else:
            embed = discord.Embed(
                title="ℹ️ Configuration Status",
                description="No log channel configured!",
                color=discord.Color.grey()
            )
        await interaction.response.send_message(embed=embed)

    elif action == "set":
        if not log_channel:
            embed = discord.Embed(
                title="❌ Error",
                description="You must specify a channel when using the 'set' action!",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        config_data = {
            "log_channel_id": log_channel.id
        }
        bot.db.set_guild_config(guild_id, config_data)
        
        embed = discord.Embed(
            title="✅ Configuration Updated",
            description=f"Log channel set to {log_channel.mention}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

        try:
            test_embed = discord.Embed(
                title="🔔 Channel Configuration",
                description="This channel has been successfully configured for duty logs!",
                color=discord.Color.green()
            )
            await log_channel.send(embed=test_embed)
        except discord.Forbidden:
            warning_embed = discord.Embed(
                title="⚠️ Permission Warning",
                description="I don't have permission to send messages in the configured channel!",
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=warning_embed)

    elif action == "remove":
        bot.db.set_guild_config(guild_id, {})
        embed = discord.Embed(
            title="🗑️ Configuration Removed",
            description="Log channel configuration has been removed",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)


def is_dev():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.id != 674681061032198144:
            embed = discord.Embed(
                title="🔒 Developer Only",
                description="This command is restricted to the bot developer.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)

class GlobalMessageModal(discord.ui.Modal, title="Global Message"):
    title_input = discord.ui.TextInput(
        label="Title",
        placeholder="Enter message title",
        required=True,
        max_length=256
    )
    content = discord.ui.TextInput(
        label="Content",
        placeholder="Enter message content",
        required=True,
        style=discord.TextStyle.paragraph
    )
    footer = discord.ui.TextInput(
        label="Footer",
        placeholder="Enter footer text",
        required=True
    )
    image_url = discord.ui.TextInput(
        label="Image URL",
        placeholder="Enter image URL (optional)",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=self.title_input.value,
            description=self.content.value,
            color=discord.Color.blue()
        )
        embed.set_footer(text=self.footer.value)
        if self.image_url.value:
            embed.set_image(url=self.image_url.value)

        sent_count = 0
        for guild in interaction.client.guilds:
            try:
                await guild.owner.send(embed=embed)
                sent_count += 1
            except:
                continue

        await interaction.response.send_message(
            f"✅ Message sent to {sent_count} server owners!", ephemeral=True
        )

@bot.tree.command(name="global_message", description="Send a global message to all server owners")
@is_dev()
async def global_message(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_modal(GlobalMessageModal())
    else:
        await interaction.response.send_message(
            "This command can only be used in DMs!", ephemeral=True
        )

@bot.tree.command(name="list_onduty", description="View all active staff members on duty")
@has_required_permissions()
async def list_onduty(interaction: discord.Interaction):
    guild_sessions = {
        k: v for k, v in bot.db.data["duty_sessions"].items()
        if k.endswith(f"-{interaction.guild_id}")
    }
    
    if not guild_sessions:
        embed = discord.Embed(
            title="📋 Active Duty List",
            description="No staff members are currently on duty.",
            color=discord.Color.blue()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    embed = discord.Embed(
        title="📋 Active Duty List",
        color=discord.Color.blue()
    )
    
    for key, session in guild_sessions.items():
        user_id = key.split('-')[0]
        member = interaction.guild.get_member(int(user_id))
        if member:
            start_time = datetime.datetime.fromisoformat(session["start_time"])
            duration = datetime.datetime.utcnow() - start_time
            embed.add_field(
                name=f"👤 {member.name}",
                value=f"Type: {session['duty_type']}\n"
                    f"Started: <t:{int(start_time.timestamp())}:R>\n"
                    f"Duration: {str(duration).split('.')[0]}",
                inline=False
            )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


if __name__ == "__main__":
    print('Starting bot...')
    bot.run(TOKEN)
