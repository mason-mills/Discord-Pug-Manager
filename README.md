This is a discord bot to help in team selection for any 4v4 event.
To start, you must edit the .env file and enter a valid Discord token id
You may also use this file to change the bot prefix and change some settings
Brackets are not to be entered when using the commands
The list of commands that are available are:

>setup [name for channel to be recognized as] [voice channel id]
This does the initial database setup on the first use and setups up a voice channel to pick teams from

>tc [name for channel]
This picks two users from that channel to be team captains. It will not pick the same players twice in a row and requires 4 players in the voice channel

>random [name for channel]
This picks two random teams of 4 from the voice channel. It will prioritize players who were not picked recently

>mmr [name for channel]
This picks 8 members from the voice channel and then balances those 8 based on their recorded mmr

>score [name for channel] [Team victory]
ex: >score channel1 Team1 victory
or: >score channel1 Team1
This changes the mmr for the players in the most recent match based on which team has won


Settings:
RequireAdminRole
Requires users to have a certain role to use any commands

RequirePlayerRole
Requires users to have a certain role to be selected for the >random or >mmr