import asyncio
import discord
import requests
import youtube_dl


prefix = "q"
client = discord.Client()


def getCoinFace():
	coinFaces = ['Yazı', 'Tura']
	return random.choice(coinFaces)


def getYoutubeLink(messageText):
	# Ignore 'play '
	linkText = messageText[5:]
	if len(linkText.split()) > 1:
		# Search for video if more than one word after !play
		return searchYoutube(linkText)

	else:
		# If the standard beginnings of the link aren't there, just search youtube with the text
		if linkText[:4] != 'www.' and linkText[:11] != 'http://www.' and linkText[:12] != 'https://':
			return searchYoutube(linkText)

		# Otherwise, append http:// and try the youtube link
		else:
			linkText = 'http://' + linkText

			testLink = requests.get(linkText)
			if testLink.status_code == 200:
				return testLink

			else:
				return ('404 page not found. Usage: !play cantina theme or '
				+ '!play http://www.youtube.com/watch?v=FWO5Ai_a80M')

# Will return the link to youtube's first result
def searchYoutube(searchText):
	searchUrl = ('https://www.googleapis.com/youtube/v3/search?order=relevance'
				+ '&part=snippet&type=video&searchmaxResults=1&key=GOOGLE_API_KEY_HERE'
				+ searchText)

	searchPage = requests.get(searchUrl)

	if searchPage.status_code == 200:
		searchPage = searchPage.json()

		# Check number of search results using search parameters
		if searchPage['pageInfo']['totalResults'] != 0:
			videoId = searchPage['items'][0]['id']['videoId']
			return 'http://www.youtube.com/watch?v=' + videoId

		# If no results, return error message
		else:
			return ('No results found. Usage: !play cantina theme or ' + '!play http://www.youtube.com/watch?v=FWO5Ai_a80M')

	else:
		return ('404 Page not found. Usage: !play cantina theme or ' + '!play http://www.youtube.com/watch?v=FWO5Ai_a80M')




@client.event
async def on_ready():
	print(f'Herkese benden çay! {client.user}')


@client.event
async def on_message(message):
	# If the message author isn't the bot and the message starts with the
	# command prefix ('!' by default), check if command was executed
	if message.author.id != process.env.BOT_ID and message.content.startswith(prefix):
		# Remove prefix and change to lowercase so commands aren't case-sensitive
		message.content = message.content[1:].lower()

		# Shuts the bot down - only usable by the bot owner specified in config
		if message.content.startswith('kapat') and message.author.id == config.OWNERID:
			await client.send_message(message.channel, 'kapanıyor!')
			await client.logout()
			await client.close()

		# Help Message, sends a personal message with a list of all the commands
		# and how to use them correctly
		elif message.content.startswith('f1'):
			await client.send_message(message.channel, 'Sana özel mesaj gönderiyorum')
			await client.send_message(message.author, helpMessage.helpMessage)


		# Searches the second word following pythonhelp in python docs
		elif message.content.startswith('f1python'):
			messagetext = message.content
			split = messagetext.split(' ')
			if len(split) > 1:
				messagetext = split[1]
				await client.send_message(message.channel, 'https://docs.python.org/3/search.html?q=' + messagetext)

		# Messages a random chuck norris joke - do not use, they're bloody terrible
		elif message.content.startswith('sakayap'):
			chuckJoke = requests.get('http://api.icndb.com/jokes/random?')
			if chuckJoke.status_code == 200:
				chuckJoke = chuckJoke.json()['value']['joke']
				await client.send_message(message.channel, chuckJoke)

		# Random coin flip
		elif message.content.startswith('yazıtura'):
			await client.send_message(message.channel, getCoinFace())

		########## VOICE COMMANDS ##########

		# Will join the voice channel of the message author if they're in a channel
		# and the bot is not currently connected to a voice channel
		elif message.content.startswith('sesegel'):
			if message.author.voice_channel != None and client.is_voice_connected(message.server) != True:
				global currentChannel
				global player
				global voice
				currentChannel = client.get_channel(message.author.voice_channel.id)
				voice = await client.join_voice_channel(currentChannel)

			elif message.author.voice_channel == None:
				await client.send_message(message.channel, 'Sen gir ben geliyorum!')

			else:
				await client.send_message(message.channel, 'Zaten kanala bağlıyım!')

		# Will leave the current voice channel
		elif message.content.startswith('utandır'):
			if client.is_voice_connected(message.server):
				currentChannel = client.voice_client_in(message.server)
				await currentChannel.disconnect()

		# Will play music using the following words as search parameters or use the
		# linked video if a link is provided
		elif message.content.startswith('şarkı çal'):
			if message.author.voice_channel != None:
				if client.is_voice_connected(message.server) == True:
					try:
						if player.is_playing() == False:
							print('not playing')
							player = await voice.create_ytdl_player(youtubeLink.getYoutubeLink(message.content))
							player.start()
							await client.send_message(message.channel, ':musical_note: Currently Playing: ' + player.title)

						else:
							print('çalıyor')

					except NameError:
						print('Isım hatası')
						player = await voice.create_ytdl_player(youtubeLink.getYoutubeLink(message.content))
						player.start()
						await client.send_message(message.channel, ':musical_note: Currently Playing: ' + player.title)

				else:
					await client.send_message(message.channel, 'Şu an ses kanalında değilim, gelmem için -qsesegel- yazmalısın')

			else:
				await client.send_message(message.channel, 'Önce sen gir ses kanalına, ben de gelcem, gelmem için -qsesegel yaz.')

		# Will pause the audio player
		elif message.content.startswith('dur'):
			try:
				player.pause()

			except NameError:
				await client.send_message(message.channel, 'Zaten çalmıyordum ki')

		# Will resume the audio player
		elif message.content.startswith('devamet'):
			try:
				player.resume()

			except NameError:
				await client.send_message(message.channel, 'Bir şey çalmıyordu ki devam edeyim...')

		# Will stop the audio player
		elif message.content.startswith('kapat'):
			try:
				player.stop()

			except NameError:
				await client.send_message(message.channel, 'Şu an bir şey çalmıyorum!')

client.run(process.env.BOT_TOKEN)
