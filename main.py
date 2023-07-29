import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
from database import Database
import time
import datetime as dt

intent = nextcord.Intents.default()
bot = commands.Bot(intents=intent)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.slash_command(description="Submit a challenge entry")
async def add_submission(interaction: nextcord.Interaction,title: str = SlashOption(required=True, description="The title for your submission"), repo_url: str = SlashOption(required=True, description="The URL to the code repository for submission Note: The URL must start with https://"), language: str = SlashOption(required=True, description="The langage that your code is in"), comments: str = SlashOption(required=False, description="Add any other comments here")):
    challenge_id = Database.get_challenge(interaction.guild_id)
    submission_id = Database.add_submission(user_id = interaction.user.id, repo_url=repo_url, language=language, comments=comments, title=title, challenge_id=challenge_id, server_id=interaction.guild_id, username=interaction.user.name)
    leaderboard_channel, challenges_channel, submissions_channel = Database.get_settings(interaction.guild_id)
    text_channel = bot.get_channel(submissions_channel)
    await text_channel.send(f"Title: **{title}**\n\nSubmitter: {interaction.user.name}\n\nRepository URL: {repo_url}\n\nLanguage: {language}\n\nComments: {comments}\n\nSubmission ID: {submission_id}")
    await interaction.response.send_message("Submission added!", ephemeral=True)

@bot.slash_command(description="Add a challenge")
async def add_challenge(interatction: nextcord.Interaction):
    pass

@add_challenge.subcommand(description="Add an auto generated challenge")
async def auto_generated(interaction: nextcord.Interaction, start_time: str = SlashOption(required=True, description="The start time for the challenge in the timezone UTC/GMT-0 and the format YYYY-MM-DD HH:MM:SS"), end_time: str = SlashOption(required=True, description="The end time for the challenge in the timezone UTC/GMT-0 and the format YYYY-MM-DD HH:MM:SS")):
    starting_time = int(time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S")))
    ending_time = int(time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M:%S")))
    title, description = Database.add_challenge(interaction.guild_id, start_time=starting_time, end_time=ending_time, use_auto_generated_challenge=True)
    leaderboard_channel, challenges_channel, submissions_channel = Database.get_settings(interaction.guild_id)
    guild = bot.get_guild(interaction.guild_id)
    await guild.create_scheduled_event(entity_type=nextcord.ScheduledEventEntityType.external, metadata=nextcord.EntityMetadata(location='Your IDE'),start_time=dt.datetime.fromtimestamp(starting_time), end_time=dt.datetime.fromtimestamp(ending_time), name=title, description=description)
    text_channel = bot.get_channel(challenges_channel)
    await text_channel.send(f"**{title}**\n{description}")
    await interaction.response.send_message("Challenge added!", ephemeral=True)

@add_challenge.subcommand(description="Add a custom challenge")
async def custom(interaction: nextcord.Interaction, start_time: str = SlashOption(required=True, description="The start time for the challenge in the timezone UTC/GMT-0 and the format YYYY-MM-DD HH:MM:SS"), end_time: str = SlashOption(required=True, description="The end time for the challenge in the timezone UTC/GMT-0 and the format YYYY-MM-DD HH:MM:SS"), title: str = SlashOption(required=True, description="The title for the challenge"), description: str = SlashOption(required=True, description="The description for the challenge")):
    starting_time = int(time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S")))
    ending_time = int(time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M:%S")))
    title, description = Database.add_challenge(interaction.guild_id, start_time=starting_time, end_time=ending_time, use_auto_generated_challenge=False, title=title, description=description)
    leaderboard_channel, challenges_channel, submissions_channel = Database.get_settings(interaction.guild_id)
    guild = bot.get_guild(interaction.guild_id)
    await guild.create_scheduled_event(entity_type=nextcord.ScheduledEventEntityType.external, metadata=nextcord.EntityMetadata(location='Your IDE'),start_time=dt.datetime.fromtimestamp(starting_time), end_time=dt.datetime.fromtimestamp(ending_time), name=title, description=description)
    text_channel = bot.get_channel(challenges_channel)
    await text_channel.send(f"**{title}**\n{description}")
    await interaction.response.send_message("Challenge added!", ephemeral=True)

@bot.slash_command(description="Get the leaderboard")
async def leaderboard(interaction: nextcord.Interaction):
    leaderboard_channel, challenges_channel, submissions_channel = Database.get_settings(interaction.guild_id)
    challenge_id = Database.get_challenge(interaction.guild_id)
    leaderboard = Database.get_leaderboard(challenge_id)
    usernames = []
    scores = []

    for i in range(0,5):
        try:
            usernames.append(leaderboard[i][0])
            if leaderboard[i][1] == None:
                scores.append(0)
            else:
                scores.append(leaderboard[i][1])
        except IndexError:
            usernames.append("N/A")
            scores.append("N/A")

    text_channel = bot.get_channel(leaderboard_channel)
    await text_channel.send(f"1st: {usernames[0]} - {scores[0]} pts\n2nd: {usernames[1]} - {scores[1]} pts\n3rd: {usernames[2]} - {scores[2]} pts\n4th: {usernames[3]} - {scores[3]} pts\n5th: {usernames[4]} - {scores[4]} pts")
    await interaction.response.send_message("Leaderboard sent!", ephemeral=True)

@bot.slash_command(description="Get your score")
async def score(interaction: nextcord.Interaction):
    challenge_id = Database.get_challenge(interaction.guild_id)
    score = Database.get_score(challenge_id=challenge_id, user_id=interaction.user.id)
    await interaction.send(f"Your score is {score[0]}!", ephemeral=True)

@bot.slash_command(description="Approve a submission")
async def approve(interaction: nextcord.Interaction, submission_id: str = SlashOption(required=True, description="The ID of the submission to approve"), points: int = SlashOption(required=True, description="The number of points to give")):
    Database.update_score(submission_id=submission_id,points_to_add=points)
    await interaction.response.send_message("Submission approved!", ephemeral=True)

@bot.slash_command(description="Configure where leaderboard, challenges, and submissions channels are")
async def settings(interaction: nextcord.Interaction, leaderboard_channel: nextcord.TextChannel = SlashOption(required=True, description="The channel where the leaderboard will be posted"), challenges_channel: nextcord.TextChannel = SlashOption(required=True, description="The channel where challenges will be posted"), submissions_channel: nextcord.TextChannel = SlashOption(required=True, description="The channel where submissions will be posted")):
    Database.configure(interaction.guild_id, leaderboard_channel.id, challenges_channel.id, submissions_channel.id)
    await interaction.response.send_message("Configured!", ephemeral=True)

if __name__ == '__main__':
    try:
        import settings
        bot.run(settings.discord_api_key)
    
    except ImportError:
        print("You need to create a settings.py file with your Discord API key in it!")
        exit(1)

    except:
        print("Something went wrong!")
        exit(1)