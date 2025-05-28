import discord
import random
from discord import app_commands
from discord.ext import commands

# Define the list of roles
ROLES = ["Controller", "Duelist", "Initiator", "Sentinel", "Flex"]

class RoleAssigner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(self.randomroles)

    @app_commands.command(name="randomroles", description="Assign random Valorant roles to 5 users.")
    @app_commands.describe(
        user1="First user",
        user2="Second user",
        user3="Third user",
        user4="Fourth user",
        user5="Fifth user"
    )
    async def randomroles(self, interaction: discord.Interaction,
                          user1: discord.Member,
                          user2: discord.Member,
                          user3: discord.Member,
                          user4: discord.Member,
                          user5: discord.Member):

        users = [user1, user2, user3, user4, user5]
        assigned_roles = random.sample(ROLES, len(users))

        response = "**🎲 Random Role Assignment:**\n"
        for user, role in zip(users, assigned_roles):
            response += f"- {user.mention} → **{role}**\n"

        await interaction.response.send_message(response)

# Setup the bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} commands to Discord.")
    print(f"Logged in as {bot.user}!")

bot.add_cog(RoleAssigner(bot))

bot.run("MTM3NjY0NTkxNDE0MzM1OTE0Ng.Ga07Iz.kkVr2Jbl72KQ-1pIi4dHenmFNXFuPmTVnX7TUM")