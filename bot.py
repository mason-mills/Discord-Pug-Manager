import sqlite3
from sqlite3 import Error
import discord
import discord.client
import logging
import datetime
import sys
from decouple import config
import random
import time
import math
from discord.errors import ClientException

from discord.team import Team




#setting up logger
logging.basicConfig(filename='./logs/bot.log',level=logging.INFO)
logging.info(datetime.datetime.utcnow().isoformat())
logging.info('Logging initialized successfully')

# Hijack output to logger
class StreamToLogger(object):
	"""
	Fake file-like stream object that redirects writes to a logger instance.
	"""
	def __init__(self, logger, log_level=logging.INFO):
		self.logger = logger
		self.log_level = log_level
		self.linebuf = ''

	def write(self, buf):
		for line in buf.rstrip().splitlines():
			self.logger.log(self.log_level, line.rstrip())

	def flush(self):
		pass

stdout_logger = logging.getLogger('STDOUT')
sl = StreamToLogger(stdout_logger, logging.INFO)
sys.stdout = sl

stderr_logger = logging.getLogger('STDERR')
sl = StreamToLogger(stderr_logger, logging.ERROR)
sys.stderr = sl




def create_users_db(conn, tableName):
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS USERS{} 
	([id] INTEGER PRIMARY KEY, [user] str UNIQUE)'''.format(tableName))
	conn.commit()
	return

def store_users(conn,tableName, userid1,userid2):
	c = conn.cursor()
	c.execute('DELETE FROM USERS{};'.format(tableName),)
	c.execute('INSERT INTO USERS{} VALUES (?,?)'.format(tableName),(None, userid1))
	c.execute('INSERT INTO USERS{} VALUES (?,?)'.format(tableName),(None, userid2))
	conn.commit()

def query_users(conn, tableName):
	c = conn.cursor()
	vcMembers = 'None'
	try:
		c.execute('SELECT * FROM USERS{}'.format(tableName))
		vcMembers = c.fetchall()
	except Error as e:
		logging.info(e)
	return vcMembers



def create_users_db_random(conn, tableName):
	c = conn.cursor()
	#([id] INTEGER PRIMARY KEY, [user] STR UNIQUE, [time] DATETIME, [oldtime] DATETIME, [totalGames] int, [gamesWon] int, [mmr] int)'''.format(tableName))
	c.execute('''CREATE TABLE IF NOT EXISTS RANDOM{} 
	([user] STR UNIQUE, [time] DATETIME, [totalGames] int, [gamesWon] int, [mmr] int)'''.format(tableName))
	conn.commit()
	return

def store_users_random(conn,tableName, userid, wasGamePlayed, mmrChange, changeTime):
	c = conn.cursor()
	c.execute('SELECT * FROM RANDOM{} WHERE user=?'.format(tableName), (userid,))
	userTableInfo = c.fetchone()
	normalizedTime = time.time()

	if str(userTableInfo) == "None":
		newMMR = 2000
		if wasGamePlayed == 1:
			newTotalGames = 1
		else:
			newTotalGames = 0
		if mmrChange > 0:
			newGamesWon = 1
		else:
			newGamesWon = 0
		c.execute('INSERT INTO RANDOM{} VALUES (?,?,?,?,?)'.format(tableName),(userid, float(1000000000) ,newTotalGames,newGamesWon,newMMR),)
	else:
		newMMR = userTableInfo[4] + mmrChange
		if newMMR < 1:
			newMMR = 1
		elif newMMR > 4999:
			newMMR = 4999

		if wasGamePlayed == 1:
			newTotalGames = userTableInfo[2] + 1
		else:
			newTotalGames = userTableInfo[2]
		if mmrChange > 0:
			newGamesWon = userTableInfo[3] + 1
		else:
			newGamesWon = userTableInfo[3]
		if changeTime == 1:
			c.execute('REPLACE INTO RANDOM{} VALUES (?,?,?,?,?)'.format(tableName),(userid,normalizedTime,newTotalGames,newGamesWon,newMMR),)
		elif changeTime == 0:
			c.execute('REPLACE INTO RANDOM{} VALUES (?,?,?,?,?)'.format(tableName),(userid,userTableInfo[1],newTotalGames,newGamesWon,newMMR),)
	

def query_users_random(conn, tableName):
	c = conn.cursor()
	userList = []
	userTimes = []
	userMMR = []
	try:
		c.execute('SELECT * FROM RANDOM{}'.format(tableName))
		rawData = c.fetchall()
		for i in range(int(len(rawData))):
			userList.append(rawData[i][0])
			userTimes.append(rawData[i][1])

	except Error as e:
		logging.info(e)
	return userList, userTimes

def query_random_by_user(conn, tablename, user):
	c = conn.cursor()
	c.execute('SELECT * FROM RANDOM{} WHERE user = ?'.format(tablename),(user,))
	userdata = c.fetchone()
	return userdata


def create_match_history_db(conn, tableName):
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS MATCHHISTORY{} 
	([id] INTEGER PRIMARY KEY, [identifier] STR, [user1] STR, [user2] STR, [user3] STR, [user4] STR, [user5] STR, [user6] STR, [user7] STR, [user8] STR, [mmr1] int, [mmr2] int, [result] int)'''.format(tableName))
	conn.commit()
	return

def query_match_history(conn, tableName):
	c = conn.cursor()
	c.execute('''SELECT * FROM MATCHHISTORY{}'''.format(tableName))
	matchHistory = c.fetchall()
	return matchHistory

def store_match_history(conn, tableName, identifier, team1, team2, team1mmr, team2mmr):
	c = conn.cursor()
	c.execute('''INSERT INTO MATCHHISTORY{} VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?) '''.format(tableName),(None, identifier, team1[0],team1[1],team1[2],team1[3],team2[0],team2[1],team2[2],team2[3],team1mmr,team2mmr,0))
	conn.commit()
	return

def query_most_recent_match(conn, tableName, identifier):
	c = conn.cursor()
	c.execute('''SELECT * FROM MATCHHISTORY{} WHERE id = (SELECT MAX(id) FROM MATCHHISTORY{}) AND identifier = ?'''.format(tableName, tableName),(identifier,))
	mostRecentMatch = c.fetchone()
	return mostRecentMatch

def update_match_history_victory(conn, tableName, id, result):
	c = conn.cursor()
	c.execute('''UPDATE MATCHHISTORY{} SET result = ? WHERE id = ? '''.format(tableName),(result,id))
	conn.commit()
	return




def create_channels_db(conn, serverID):
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS CHANNELS{0}
	([id] INTEGER PRIMARY KEY, [channel] UNIQUE int, [identifier] UNIQUE str)'''.format(serverID))
	conn.commit()
	return

def store_channel(conn, serverID, channelid, identifier):
	c = conn.cursor()
	c.execute('''INSERT INTO CHANNELS{} VALUES (?,?,?)'''.format(serverID),(None,channelid,identifier))

def query_channels(conn, serverID, identifier):
	channels = 'None'
	c = conn.cursor()
	c.execute('SELECT * FROM CHANNELS{0} WHERE identifier = ?'.format(serverID),(identifier,))
	channels = c.fetchone()
	return channels




def RandomTeamSelecter(conn, guildid, *clientList):
	
	clientList = clientList[0]

	rawUserList, userTimes = query_users_random(conn, str(guildid))
	userList = []
	for i in range(int(len(rawUserList))):
		userList.append(int(rawUserList[i]))
	filteredUserList = []
	filteredTimeList = []
	TeamList = []
	for clientCounter in range(len(clientList)):
		flag = 0
		for userCounter in range(len(userList)):
			if clientList[clientCounter] == userList[userCounter]:
				filteredUserList.append(userList[userCounter])
				filteredTimeList.append(int(userTimes[userCounter]))
				flag = 1
		
		if flag == 0:
			TeamList.append(int(clientList[clientCounter]))

	if len(TeamList) == 8:
		return TeamList
	
	elif len(TeamList) > 8:
		TeamList = random.sample(TeamList, 8)
		return TeamList

	elif len(TeamList) < 8:
		while len(TeamList) < 8:
			usersToAdd = []
			minimumTime = min(filteredTimeList)
			for i in range(1,len(filteredUserList)-1):
				if filteredTimeList[i] == filteredTimeList[minimumTime]:
					usersToAdd.append(filteredTimeList.pop(i))
					poppedValue = filteredTimeList.pop(i)
			
			if len(usersToAdd) > 1:
				random.shuffle(usersToAdd)
			for i in range(len(usersToAdd)):
				if len(TeamList) < 8:
					TeamList.append(usersToAdd[i])



	random.shuffle(TeamList)
	



	return TeamList



def TeamBalancer(players, MMRs):
	score = 10000
	mmrGoal = sum(MMRs)/2
	maxMMRIndex = MMRs.index(max(MMRs))
	teamIndex = [0,1,2,3]
	for i1 in range(len(players)-1):
		for i2 in range(len(players)-2):
			for i3 in range(len(players)-3):
				if i1 != i2 and i1 != i3 and i2 != i3:
					mmrScore = abs(MMRs[i1] + MMRs[i2] + MMRs[i3] + MMRs[len(players)-1] - mmrGoal)
					if mmrScore < score:
						teamIndex = [i1,i2,i3,len(players)-1]
						score = mmrScore
	
	for i in range(len(players)-2):
		if i not in teamIndex:
			teamIndex.append(i)

	logging.info('teamIndex: ' + str(teamIndex))
	return teamIndex


def adjustMMR(conn, messageArg, winner):
	identifier = messageArg.content.split(" ")[1]
	previousMatch = query_most_recent_match(conn, messageArg.guild.id, identifier)
	
	#do not score a match that has already been resolved
	if previousMatch[12] != 0:
		response = "I'm sorry, it appears that my most recent match for that lobby was already scored."
		return response

	if winner == 1:
		winningMMR = previousMatch[10]
		losingMMR = previousMatch[11]
	else:
		winningMMR = previousMatch[11]
		losingMMR = previousMatch[10]
	
	teamDiff = (winningMMR/losingMMR)**-2*30
	for i in range(2,10):
		userData = query_random_by_user(conn, messageArg.guild.id, previousMatch[i])
		userMMR = int(userData[4])
		if (i <= 5 and winner == 1) or (i > 5 and winner == 2):
			mmrChange = math.ceil(teamDiff*2000/userMMR)
			logging.info(mmrChange)
		else:
			mmrChange = math.floor(-teamDiff*userMMR/2000)
			logging.info(mmrChange)
		if mmrChange > 75:
			mmrChange = 75
		elif mmrChange < -75:
			mmrChange = -75
		store_users_random(conn, messageArg.guild.id, previousMatch[i], 1, mmrChange, 1)
	conn.commit()
	
	update_match_history_victory(conn, messageArg.guild.id, previousMatch[0], winner)

	if winner == 1:
		response = "Congratulations Team1 on the victory"
	else:
		response = "Congratulations Team2 on the victory"
	return response

def matchDraw(conn, messageArg):
	identifier = messageArg.content.split(" ")[1]
	logging.info('1')
	if query_most_recent_match(conn, messageArg.guild.id, identifier)[12] == 0:
		logging.info('2')
		dbId = query_most_recent_match(conn, messageArg.guild.id, identifier)[0]
		logging.info('3')
		logging.info('dbID = ' + str(dbId))
		update_match_history_victory(conn, messageArg.guild.id, str(dbId), int(3))
		response = 'The draw has been recorded.'
		
	else:
		response = "I'm sorry, it appears that my most recent match for that lobby was already scored."
	
	return response





def helpFunction(botPrefix, messageArg):
	arg2 = ' '
	if len(messageArg.content.split(' ')) > 1:
		arg2 = messageArg.content.lower().split(' ')[1]
	else:
		arg2 = ' '

	if arg2 != ' ':
		if arg2 == 'score':
			response = '''The score command is used to record the result of the previous match and then alter the MMR of any participating players. 
```{}score [Room name] [Team1/Team2/Draw]```
Room name must match the name the voice channel was given during setup. This name cannot have any spaces. 
The last part of the command is which team won or 'draw' if the match ended in a draw. 
The command will ignore anything typed after the third space. 
An example of using this command:
```{}score Room1 Team1```'''.format(botPrefix, botPrefix)

		elif arg2 == 'help':
			response = '''This is the help command. Use it and any of the other available commands to get a short explanation and an example'''
		
		elif arg2 == 'tc':
			response = '''tc stands for Team Captain. This command picks two random users connected to a voice channel 
```{}tc [Room name]```
Room name must match the name the voice channel was given during setup. This name cannot have any spaces. 
The command will ignore anything typed after the second space. An example of this command:
```{}tc Room1```'''.format(botPrefix, botPrefix)
		
		elif arg2 == 'random':
			response = '''The Random command will pick two sets of four users connected to the room identified
```{}random [Room name]```
Room name must match the name the voice channel was given during setup. This name cannot have any spaces. 
This command will prioritize users who have not been picked recently. This timer will also affect the MMR command. 
The command will ignore anything typed after the second space. 
An example of this command:
```{}random Room1```'''.format(botPrefix, botPrefix)
		
		elif arg2 == 'mmr':
			response = '''The MMR command will pick two sets of four users and balance them based on their recorded mmr based on any previous matches
```{}MMR [Room name]```
Room name must match the name the voice channel was given during setup. This name cannot have any spaces. 
This command will prioritize users who have not been picked recently. This timer will also affect the Random command. 
This command may not be used for the same room again until a score is entered with the Score command
The command will ignore anything typed after the second space. 
An example of this command:
```{}MMR Room1```'''.format(botPrefix, botPrefix)

		elif arg2 == 'setup':
			response = '''The Setup command sets the name that will be used to identify a voice channel
```{}Setup [Room name] [Voice Channel id]```
The Room name will be the permanent name used to identify the room in the future. It MAY NOT contain spaces.
The Voice Channel id is the number that Discord uses to identify the voice channel that will be used. It should appear to be a random number roughly 18 digits in length.
The command will ignore anything typed after the third space.
An example of this command:
```{}Setup Room1 012345678910111213```'''.format(botPrefix, botPrefix)

	else:
		response = '''Hello! I am a discord bot used to pick two random teams of 4 from a voice channel. My available commands are 
```{}help [command]

{}Setup [Room name] [Voice Channel id]

{}tc [Room name]

{}random [Room name]

{}MMR [Room name]

{}score [Room name] [Team1/Team2/Draw]```'''.format(botPrefix,botPrefix,botPrefix,botPrefix,botPrefix,botPrefix)

	return response
		






#main function
def botFunc():
	#sql setup
	global conn
	conn = sqlite3.connect('PUGS4.db')

	#discord setup
	TOKEN = config('TOKEN')
	intents = discord.Intents().all()
	botPrefix = config('PREFIX')
	client = discord.Client(intents=intents)



	#tc command
	async def SelectCaptain(conn, messageArg, botPrefix):
		row = 'None'
		identifier = messageArg.content.split(' ')[1]
		try:
			row = query_channels(conn, messageArg.guild.id, identifier)
		except sqlite3.OperationalError as e:
			if str(e) == 'sqlite3.OperationalError: no such table: {}'.format(messageArg.guild.id):
				await messageArg.channel.send('Something went wrong. Please make sure that the channel is setup appropriately')
				logging.info(e)
				return
			else:
				await messageArg.channel.send('Something went wrong.')
				logging.error(e)
				return

		if row == str('None'):
			await messageArg.channel.send('This command was not properly setup. For clarification please refer to `{}help`').format(botPrefix)
			return
		
		
		voiceChannelName = int(row[1])
		voice_channel = client.get_channel(row[1])
		clientList = voice_channel.members
		oldData = query_users(conn, str(voiceChannelName))
		response = 'The users selcted are: '
		flag1 = 0
		flag2 = 0
		
		#select two users who cannot be the users stored in the db and must be different
		if(len(clientList) > 3):
			if(len(oldData) > 1):
				while flag1 == 0:
					randomNumber = random.randint(0,len(clientList)-1)
					client1 = str(clientList[randomNumber])
					if(client1 == oldData[0][1] or client1 == oldData[1][1]):
						flag1 = 0
					else:
						response += client1 + ' and '
						flag1 = 1
				while flag2 == 0:
					randomNumber = random.randint(0,len(clientList)-1)
					client2 = str(clientList[randomNumber])
					if(client2 == oldData[0][1] or client2 == oldData[1][1] or client2 == client1):
						flag2 = 0
					else:
						response += client2
						flag2 = 1
				await messageArg.channel.send(response)
				store_users(conn,str(voiceChannelName),client1,client2)
				logging.info(response)
			else: 
				randomNumber = random.randint(0,len(clientList)-1)
				client1 = str(clientList[randomNumber])
				response += client1 + ' and '
				while flag2 == 0:
					randomNumber = random.randint(0,len(clientList)-1)
					client2 = str(clientList[randomNumber])
					if(client2 == client1):
						flag2 = 0
					else:
						response += client2
						flag2 = 1
				await messageArg.channel.send(response)
				store_users(conn,str(voiceChannelName),client1,client2)
				logging.info(response)

		else:
			await messageArg.channel.send('There are not enough users in that voice channel')
		return


	#random command
	async def RandomTeams(channelid, messageArg):
		playerRole = str(config('WhitelistedPlayerRole'))
		if playerRole != '':
			playerRole = discord.utils.find(lambda r: r.name == playerRole, messageArg.guild.roles)
		playerRoleSetting = str(config('RequirePlayerRole'))
		voice_channel = client.get_channel(channelid)
		clientList = voice_channel.members
		clientIDs = []

		if len(clientList) > 7:
			if playerRoleSetting.lower() == 'yes':
				clientListTemp = clientList
				clientList = []
				for clients in clientListTemp:
					if playerRole in clients.roles:
						clientList.append(clients)

		for clients in clientList:
			clientIDs.append(str(clients.id))
		if (len(clientList) > 7):
			for clientCounter in clientIDs:
				store_users_random(conn, str(messageArg.guild.id), clientCounter, 0, 0, 0)
			conn.commit()
			players = RandomTeamSelecter(conn, str(messageArg.guild.id), clientIDs)
			playerID = []
			for playerIntegerID in players:
				playerID.append(client.get_user(playerIntegerID))
			x = [*range(8)]
			random.shuffle(x)
			
			response = '''Team 1:
```
{}
{}
{}
{}```
Team 2:
```
{}
{}
{}
{}```'''.format(playerID[x[0]],playerID[x[1]],playerID[x[2]],playerID[x[3]],playerID[x[4]],playerID[x[5]],playerID[x[6]],playerID[x[7]])
			for i in range(len(players)):
				store_users_random(conn, messageArg.guild.id, players[i], 0, 0, 1)
			conn.commit()
			await messageArg.channel.send(response)

		#if there are less than 8 users in the voice channel
		else:
			await messageArg.channel.send('There are not enough players in the voice channel')

		
	#mmr command
	async def MMRTeams(channelid, messageArg):
		playerRole = str(config('WhitelistedPlayerRole'))
		if playerRole != '':
			playerRole = discord.utils.find(lambda r: r.name == playerRole, messageArg.guild.roles)
		playerRoleSetting = str(config('RequirePlayerRole'))
		

		voice_channel = client.get_channel(channelid)
		clientList = voice_channel.members
		clientIDs = []
		playerMMR = []
		identifier = messageArg.content.split(" ")[1]

		#don't start a new match if the old match is still ongoing or unresolved
		if query_most_recent_match(conn, messageArg.guild.id, identifier)[12] == 0:
			await messageArg.channel.send('''I am unable to pick new teams for this lobby while the previous match is still ongoing. If you wish to end the last match, please type:
```{}score {} Team1/Team2/Draw``` replacing Team1/Team2/Draw with the winning team or a draw if the match could not be completed'''.format(botPrefix, identifier))
			return

		if len(clientList) > 7:
			if playerRoleSetting.lower() == 'yes':
				clientListTemp = clientList
				clientList = []
				for clients in clientListTemp:
					if playerRole in clients.roles:
						clientList.append(clients)


		for clients in clientList:
			clientIDs.append(str(clients.id))
			
		if (len(clientList) > 7):
			for clientCounter in clientIDs:
				store_users_random(conn, str(messageArg.guild.id), clientCounter, 0, 0, 0)
			conn.commit()
			players = RandomTeamSelecter(conn, str(messageArg.guild.id), clientIDs)


			playerID = []
			for playerIntegerID in players:
				MMROfThisPlayer = query_random_by_user(conn, str(messageArg.guild.id), str(playerIntegerID))[4]
				playerMMR.append(MMROfThisPlayer)
				playerID.append(client.get_user(playerIntegerID))

			x = TeamBalancer(players, playerMMR)
			
			for i in range(8):
				if i not in x:
					x.append(i)

			response = '''Team 1:
```
{}
{}
{}
{}```
Team 2:
```
{}
{}
{}
{}```'''.format(playerID[x[0]],playerID[x[1]],playerID[x[2]],playerID[x[3]],playerID[x[4]],playerID[x[5]],playerID[x[6]],playerID[x[7]])


			team1 = []
			team2 = []
			xLen = len(x)
			team1mmr = 0
			team2mmr = 0

			for i in range(int(xLen/2)):
				team1.append(players[x[i]])
				team2.append(players[x[i+int(xLen/2)]])
				team1mmr += playerMMR[x[i]]
				team2mmr += playerMMR[x[i+int(xLen/2)]]
			
			team1mmr = math.ceil(team1mmr/(int(xLen/2)))
			team2mmr = math.ceil(team2mmr/(int(xLen/2)))

			for i in range(len(players)):
				store_users_random(conn, messageArg.guild.id, players[i], 0, 0, 0)
			conn.commit()
			store_match_history(conn, messageArg.guild.id,identifier,team1,team2,team1mmr,team2mmr)
			await messageArg.channel.send(response)

		#if there are less than 8 users in the voice channel
		else:
			await messageArg.channel.send('There are not enough players in the voice channel')




	async def messageFunc(message):
		if message.author == client.user:
			return

		elif (message.content.lower().startswith(botPrefix + 'tc')):
			await SelectCaptain(conn, message, botPrefix)
		
		elif message.content.lower().startswith(botPrefix + 'setup'):
			identifier = message.content.split(' ')[1]
			vcChannelId = message.content.split(' ')[2]
			create_channels_db(conn, str(message.guild.id))
			store_channel(conn, str(message.guild.id), str(vcChannelId), identifier)
			create_users_db(conn, str(vcChannelId))
			create_users_db_random(conn, str(message.guild.id))
			create_match_history_db(conn, str(message.guild.id))
			await message.channel.send("Setup successful")

		elif (message.content.lower().startswith(botPrefix + 'random')):
			identifier = message.content.split(' ')[1]
			vcChannelId = query_channels(conn, message.guild.id, identifier)
			#query_channels returns a row. query_channels[1] contains the channelid
			await RandomTeams(vcChannelId[1], message)

		elif (message.content.lower().startswith(botPrefix + 'help')):
			response = helpFunction(botPrefix, message)
			await message.channel.send(response)

		elif str(config('RequireAdminRoleForMMRAndScore')).lower() == 'yes':
			MMRRole = str(config('WhitelistedMMRRole'))
			MMRRole = discord.utils.find(lambda r: r.name == MMRRole, message.guild.roles)
			if MMRRole in message.author.roles:
				await messageFuncPart2(message)
		
		elif str(config('RequireAdminRoleForMMRAndScore')).lower() != 'yes':
			await messageFuncPart2(message)
		
		
		
		return


	async def messageFuncPart2(message):
		if (message.content.lower().startswith(botPrefix + 'mmr')):
			identifier = message.content.split(' ')[1]
			vcChannelId = query_channels(conn, message.guild.id, identifier)
			await MMRTeams(vcChannelId[1], message)

		elif (message.content.lower().startswith(botPrefix + 'score')):
			identifier = message.content.split(' ')[1]
			startLength = len(botPrefix + 'score ' + identifier) + 1
			messageEnd = message.content[startLength:]
			if message.content.split(' ')[2].lower() == ('team1'):
				response = adjustMMR(conn, message, 1)
			elif message.content.split(' ')[2].lower() == ('team2'):
				response = adjustMMR(conn, message, 2)
			elif message.content.split(' ')[2].lower() == ('draw'):
				response = matchDraw(conn, message)
			
			await message.channel.send(response)
		
		return







	@client.event
	async def on_ready():
		logging.info('Logged in as')
		logging.info(client.user.name)
		logging.info(client.user.id)
		logging.info('------')


	@client.event
	async def on_message(message):
		if str(config('RequireAdminRole')).lower() == 'yes':
			adminRole = str(config('WhitelistedAdminRole'))
			adminRole = discord.utils.find(lambda r: r.name == adminRole, message.guild.roles)
			if adminRole in message.author.roles:
				await messageFunc(message)
		else:
			await messageFunc(message)
			




	try:
		client.run(TOKEN)
	except Exception as e:
		logging.exception('In-loop exception:')



if __name__ == '__main__':
	botFunc()
