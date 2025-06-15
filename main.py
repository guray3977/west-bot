import discord
from discord.ext import commands
import asyncio
import os
import json
from datetime import datetime
import logging

# Import cogs
from cogs.moderation import ModerationCog
from cogs.roleplay import RoleplayCog
from cogs.events import EventsCog
from cogs.admin import AdminCog
from utils.database import Database
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RollexsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description='Rollexs West RP Bot - Comprehensive Discord Bot for Role-Playing Community Management'
        )
        
        self.db = Database()
        self.config = Config()
        
    async def setup_hook(self):
        """Setup hook called when bot is starting up"""
        # Load cogs
        await self.add_cog(ModerationCog(self))
        await self.add_cog(RoleplayCog(self))
        await self.add_cog(EventsCog(self))
        await self.add_cog(AdminCog(self))
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f'{self.user} has logged in!')
        
        # Set bot status to streaming
        await self.change_presence(
            activity=discord.Streaming(
                name="Rollexs 💝 West",
                url="https://twitch.tv/rollexs"
            )
        )
        
        logger.info("Bot status set to streaming: Rollexs 💝 West")
    
    async def on_member_join(self, member):
        """Handle new member joins"""
        try:
            # Get auto-role from config
            auto_role_id = self.config.get_auto_role()
            if auto_role_id:
                role = member.guild.get_role(auto_role_id)
                if role:
                    await member.add_roles(role)
                    logger.info(f"Added auto-role {role.name} to {member}")
            
            # Log member join
            await self.log_action(
                member.guild,
                "Üye Katıldı",
                f"{member.mention} sunucuya katıldı.",
                discord.Color.green()
            )
        except Exception as e:
            logger.error(f"Error in on_member_join: {e}")
    
    async def on_member_remove(self, member):
        """Handle member leaves"""
        try:
            await self.log_action(
                member.guild,
                "Üye Ayrıldı",
                f"{member} sunucudan ayrıldı.",
                discord.Color.orange()
            )
        except Exception as e:
            logger.error(f"Error in on_member_remove: {e}")
    
    async def on_message(self, message):
        """Handle message events for auto-moderation"""
        if message.author.bot:
            return
        
        # Check for profanity, spam, or links
        from utils.moderation import check_message_content
        violation = await check_message_content(message.content)
        
        if violation:
            try:
                await message.delete()
                
                # Send warning to user
                embed = discord.Embed(
                    title="⚠️ Uyarı",
                    description=f"Mesajınız {violation} nedeniyle silindi.",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed, delete_after=5)
                
                # Log the action
                await self.log_action(
                    message.guild,
                    "Mesaj Silindi",
                    f"{message.author.mention} kullanıcısının mesajı {violation} nedeniyle silindi.\n"
                    f"Kanal: {message.channel.mention}",
                    discord.Color.red()
                )
                
            except Exception as e:
                logger.error(f"Error deleting message: {e}")
        
        await self.process_commands(message)
    
    async def log_action(self, guild, title, description, color):
        """Log actions to the designated log channel"""
        try:
            log_channel_id = self.config.get_log_channel(guild.id)
            if log_channel_id:
                channel = guild.get_channel(log_channel_id)
                if channel:
                    embed = discord.Embed(
                        title=title,
                        description=description,
                        color=color,
                        timestamp=datetime.now()
                    )
                    await channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Error logging action: {e}")

# Run the bot
async def main():
    bot = RollexsBot()
    
    # Get token from environment
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set!")
        return
    
    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
