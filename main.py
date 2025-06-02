import random
import discord
from discord.ext import commands
from discord import app_commands

ROLES = ["Flex", "Controller", "Sentinel", "Duelist", "Initiator"]
DEFAULT_ELO = 1000
chum_points = {}
match_assignments = {}  # Stores role assignments per channel

# ELO system functions
def get_user_points(user_id):
    if user_id not in chum_points:
        chum_points[user_id] = {role: DEFAULT_ELO for role in ROLES}
    return chum_points[user_id]

def calculate_elo(winner_elo, loser_elo, k=32):
    expected_win = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    new_winner_elo = winner_elo + k * (1 - expected_win)
    new_loser_elo = loser_elo + k * (0 - (1 - expected_win))
    return round(new_winner_elo), round(new_loser_elo)

# Cog containing all commands
class RoleAssigner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("✅ RoleAssigner cog initialized")
        self.bot.tree.add_command(self.randomroles)


    # Slash command to assign random roles
    @app_commands.command(name="randomroles", description="Assign random Valorant roles to 5 users.")
    @app_commands.describe(
        user1="First user", user2="Second user", user3="Third user",
        user4="Fourth user", user5="Fifth user"
    )
    async def randomroles(self, interaction: discord.Interaction,
                          user1: discord.Member,
                          user2: discord.Member,
                          user3: discord.Member,
                          user4: discord.Member,
                          user5: discord.Member):
        users = [user1, user2, user3, user4, user5]
        assigned_roles = random.sample(ROLES, len(users))

        match_assignments[interaction.channel_id] = list(zip(users, assigned_roles))

        response = "**🎲 Random Role Assignment:**\n"
        for user, role in zip(users, assigned_roles):
            response += f"- {user.mention} → **{role}**\n"
        await interaction.response.send_message(response)

    # !chum command
    @commands.command()
    async def chum(self, ctx, member: discord.Member = None):
        print(f"[DEBUG] ctx: {ctx}")
        print(f"[DEBUG] ctx type: {type(ctx)}")
        print(f"[DEBUG] member: {member}")
        print(f"[DEBUG] member type: {type(member)}")
        member = member or ctx.author
        points = get_user_points(member.id)
        msg = f"**{member.display_name}'s Chum Points:**\n"
        for role, elo in points.items():
            msg += f"{role}: {elo}\n"
        await ctx.send(msg)

    # !update_chum (admin only)
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def update_chum(self, ctx, member: discord.Member, role: str, delta: int):
        role = role.capitalize()
        if role not in ROLES:
            await ctx.send(f"Invalid role. Choose from: {', '.join(ROLES)}")
            return
        points = get_user_points(member.id)
        points[role] += delta
        await ctx.send(f"{member.display_name}'s {role} chum points updated to {points[role]}.")

    # !chum_leaderboard
    @commands.command()
    async def chum_leaderboard(self, ctx, role: str):
        role = role.capitalize()
        if role not in ROLES:
            await ctx.send(f"Invalid role. Choose from: {', '.join(ROLES)}")
            return
        leaderboard = sorted(
            ((ctx.guild.get_member(uid), pts[role]) for uid, pts in chum_points.items() if ctx.guild.get_member(uid)),
            key=lambda x: x[1], reverse=True
        )
        msg = f"**Chum Points Leaderboard for {role}:**\n"
        for i, (member, elo) in enumerate(leaderboard[:10], 1):
            msg += f"{i}. {member.display_name}: {elo}\n"
        await ctx.send(msg)

    # !reset_leaderboard
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reset_leaderboard(self, ctx):
        chum_points.clear()
        await ctx.send("Chum points leaderboard has been reset.")

    # !neatqueue_result
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def neatqueue_result(self, ctx,
                               winners: commands.Greedy[discord.Member],
                               losers: commands.Greedy[discord.Member]):
        if ctx.channel.id not in match_assignments:
            await ctx.send("No prior /randomroles found for this channel.")
            return

        assignments = dict(match_assignments[ctx.channel.id])
        game_result = {
            "winners": [(m, assignments[m]) for m in winners if m in assignments],
            "losers": [(m, assignments[m]) for m in losers if m in assignments]
        }

        for winner, role in game_result["winners"]:
            for loser, loser_role in game_result["losers"]:
                winner_points = get_user_points(winner.id)
                loser_points = get_user_points(loser.id)
                w_elo, l_elo = winner_points[role], loser_points[loser_role]
                new_w, new_l = calculate_elo(w_elo, l_elo)
                winner_points[role] = new_w
                loser_points[loser_role] = new_l

        await ctx.send("Chum points updated based on last assigned roles.")

# === Bot Setup ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")
    print("Registered prefix commands:")
    for command in bot.commands:
        print(f"- {command.name}: {command.callback.__module__}.{command.callback.__name__}")

bot.add_cog(RoleAssigner(bot))
bot.run("MTM3NjY0NTkxNDE0MzM1OTE0Ng.Ga07Iz.kkVr2Jbl72KQ-1pIi4dHenmFNXFuPmTVnX7TUM")