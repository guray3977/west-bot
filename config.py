import json
import os
from typing import Dict, Optional

class Config:
    def __init__(self):
        self.config_file = "data/config.json"
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create default config
                default_config = {
                    "guilds": {},
                    "auto_role": None,
                    "admin_roles": [],
                    "moderator_roles": [],
                    "nickname_role_id": 1359605832236404776
                }
                self.save_config(default_config)
                return default_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return {"guilds": {}, "auto_role": None, "admin_roles": [], "moderator_roles": []}
    
    def save_config(self, config: Dict = None):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            config_to_save = config or self.config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_guild_config(self, guild_id: int) -> Dict:
        """Get configuration for a specific guild"""
        guild_id_str = str(guild_id)
        if guild_id_str not in self.config["guilds"]:
            self.config["guilds"][guild_id_str] = {
                "log_channel": None,
                "announcement_channel": None,
                "auto_role": None,
                "admin_roles": [],
                "moderator_roles": []
            }
            self.save_config()
        return self.config["guilds"][guild_id_str]
    
    def set_log_channel(self, guild_id: int, channel_id: int):
        """Set log channel for a guild"""
        guild_config = self.get_guild_config(guild_id)
        guild_config["log_channel"] = channel_id
        self.save_config()
    
    def get_log_channel(self, guild_id: int) -> Optional[int]:
        """Get log channel for a guild"""
        guild_config = self.get_guild_config(guild_id)
        return guild_config.get("log_channel")
    
    def set_auto_role(self, guild_id: int, role_id: int):
        """Set auto role for new members"""
        guild_config = self.get_guild_config(guild_id)
        guild_config["auto_role"] = role_id
        self.save_config()
    
    def get_auto_role(self, guild_id: int = None) -> Optional[int]:
        """Get auto role"""
        if guild_id:
            guild_config = self.get_guild_config(guild_id)
            return guild_config.get("auto_role")
        return self.config.get("auto_role")
    
    def add_admin_role(self, guild_id: int, role_id: int):
        """Add admin role"""
        guild_config = self.get_guild_config(guild_id)
        if role_id not in guild_config["admin_roles"]:
            guild_config["admin_roles"].append(role_id)
            self.save_config()
    
    def add_moderator_role(self, guild_id: int, role_id: int):
        """Add moderator role"""
        guild_config = self.get_guild_config(guild_id)
        if role_id not in guild_config["moderator_roles"]:
            guild_config["moderator_roles"].append(role_id)
            self.save_config()
    
    def is_admin(self, member) -> bool:
        """Check if member is admin"""
        if member.guild_permissions.administrator:
            return True
        
        guild_config = self.get_guild_config(member.guild.id)
        admin_roles = guild_config.get("admin_roles", [])
        
        for role in member.roles:
            if role.id in admin_roles:
                return True
        return False
    
    def is_moderator(self, member) -> bool:
        """Check if member is moderator or admin"""
        if self.is_admin(member):
            return True
        
        guild_config = self.get_guild_config(member.guild.id)
        moderator_roles = guild_config.get("moderator_roles", [])
        
        for role in member.roles:
            if role.id in moderator_roles:
                return True
        return False
    
    def get_nickname_role_id(self) -> int:
        """Get the role ID for automatic nickname changes"""
        return self.config.get("nickname_role_id", 1359605832236404776)
