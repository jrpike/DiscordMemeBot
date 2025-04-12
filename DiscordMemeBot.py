import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
import asyncio
import time
import os
import sys
import time
import wave
import contextlib
import shutil
import requests
import random
import getpass
import string
import glob

import FtpDl
import Memer

intents = discord.Intents.default()

intents.messages=True
intents.emojis=True
intents.reactions=True
intents.message_content=True
intents.dm_messages=True

client = discord.Client(intents=intents)

class Attribs():
	audio_meme_list = []
	bad_reacts = []

	hostname = None
	username = None
	password = None
	main_channel_id = None
	meme_file_cache_last_updated = 0
	meme_file_cache = []

def is_image(filename):
	filename = filename.lower()
	return (filename.endswith("jpg") or filename.endswith("jpeg") or filename.endswith("png") or filename.endswith("gif"))

def is_video(filename):
	filename = filename.lower()
	filename = filename.replace("https://", "")
	filename = filename.replace("http://", "")
	return (filename.startswith("youtube.com") or filename.startswith("www.youtube.com"))

def is_command(content):
	return len(content) > 1 and content[0] == "-"

def clean_image(filename):
	os.system("rm -f " + filename)

@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
	try:
		if message.author == client.user:
			return

		content = message.content
			
		meme_log = client.get_channel(int(Attribs.main_channel_id))
		
		author = message.author
		attachments = message.attachments
		curr_channel = message.channel

		channel = None
		if author.voice is not None:
			channel = author.voice.channel

		# Continue message in main channel and there is an attachment or non-command content string
		if  (attachments or not is_command(content)) and curr_channel is meme_log:
			
			# Iterate through list of all attachments plus content string
			for item in attachments + [content]:

				# Verify attachment url exists and is an image or content string is a url and image
				if ((hasattr(item, "url") and is_image(item.url)) or (item == content and is_image(content))):
					
					# Set url accordingly
					url = None
					if item == content:
						url = content
					else:
						url = item.url

					# Do http request and strip off filepath to get image name only
					response = requests.get(url, stream=True)
					image_name = url.split("/")
					image_name = image_name[len(image_name) - 1]

					# Write the raw to a local temporary file
					with open(image_name, "wb") as out_file:
						shutil.copyfileobj(response.raw, out_file)
						out_file.close()
					del response
					
					# Random filename
					file_int = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

					# Get original file extension
					file_ext = image_name.split(".")
					file_ext = file_ext[len(file_ext) - 1]

					# Rename with new random filename with original extension
					new_image_name = file_int + "." + file_ext
					os.rename(image_name, new_image_name)

					# Upload the new filename
					FtpDl.upload_file(new_image_name, Attribs.hostname, Attribs.username, Attribs.password)

				if ((hasattr(item, "url") and is_image(item.url)) or (item == content and is_video(content))):
					yt = YouTube(content).streams.filter(progressive=True, file_extension='mp4').order_by("resolution").first().download()
					FtpDl.upload_video(yt, Attribs.hostname, Attribs.username, Attribs.password)

		if content == "-roll":
			filenames = FtpDl.get_filenames(Attribs.hostname, Attribs.username, Attribs.password)

			filename = random.choice(filenames)

			FtpDl.loadFile(filename, Attribs.hostname, Attribs.username, Attribs.password)

			local_filename = filename.split("/")
			local_filename = local_filename[len(local_filename) - 1]

			asyncio.run(curr_channel.send(file=discord.File(local_filename)))
			clean_image(filename)

		elif content.startswith("-memer"):
			userTemplate = False

			curr_time = time.time()
			if (curr_time - Attribs.meme_file_cache_last_updated > 60):
				print("updating cache")
				Attribs.meme_file_cache = FtpDl.get_filenames(Attribs.hostname, Attribs.username, Attribs.password)
				Attribs.meme_file_cache_last_updated = curr_time
			else: 
				print("cache hit")

			templates = FtpDl.get_templates(Attribs.hostname, Attribs.username, Attribs.password)
			template = random.choice(templates)

			if content != "-memer":
				userTemplate = True
				cmd_params = content.split(" ")
				if (len(cmd_params) > 1):
					template = cmd_params[1] + ".png"

			if template not in templates:
				asyncio.run(message.add_reaction(random.choice(Attribs.bad_reacts)))

			else:
				error = True
				while error:
					try:
						FtpDl.loadFile("data/Templates/" + template, Attribs.hostname, Attribs.username, Attribs.password)
						error = False
					except Exception as e:
						print("Couldn't make meme with template: " + template + "... " + str(e))
						asyncio.run(curr_channel.send(template + " seems corrupt"))
						
						template = random.choice(templates)
						if userTemplate:
							break
				
				if not error:
					filename = Memer.make_meme(template, Attribs.meme_file_cache, Attribs.hostname, Attribs.username, Attribs.password)
					asyncio.run(curr_channel.send(file=discord.File(filename)))
					os.system("rm -f \"null\"")
					clean_image(filename)
					
		elif content == "-listTemplates":
			templates = FtpDl.get_templates(Attribs.hostname, Attribs.username, Attribs.password)

			template_list_str = "Template List:"
			for f in templates:
				l = f.lower().replace(".png", "")
				template_list_str += (" " + l)

			asyncio.run(curr_channel.send(template_list_str))

		elif content == "-updateAudioMemes":
			os.system("rm -f *.wav")

			FtpDl.loadFiles(Attribs.hostname, Attribs.username, Attribs.password)

			Attribs.audio_meme_list = []
			files = os.listdir()

			for file in files:
				if file.endswith(".wav"):
					Attribs.audio_meme_list.append(file)
			
		elif content == "-listAudioMemes":
			Attribs.audio_meme_list_str = "Audio Meme List:"

			for f in Attribs.audio_meme_list:
				l = f.replace(".wav", "")
				Attribs.audio_meme_list_str += (" -" + l)

			asyncio.run(curr_channel.send(Attribs.audio_meme_list_str))

		elif content.startswith("-say") or (content.replace("-","") + ".wav" in Attribs.audio_meme_list):
			
			if channel is None:
				asyncio.run(message.add_reaction(random.choice(Attribs.bad_reacts)))
			else:
				wav_file = None

				if content.startswith("-say"):
					to_say = content.split("-say ")[1].replace("-", " dash ")
					os.system("espeak -w \"tmp.wav\" \"" + to_say + "\"")
					wav_file = "tmp.wav"
				else:
					wav_file = content.replace("-", "") + ".wav"

				vc = await channel.connect()

				duration = 0
				with contextlib.closing(wave.open(wav_file, "r")) as f:
					frames = f.getnframes()
					rate = f.getframerate()
					duration = frames / float(rate)

				vc.play(discord.FFmpegPCMAudio(wav_file), after=lambda e: print('done', e))

				await asyncio.sleep(duration)

				os.system("rm -f \"tmp.wav\"")

				server = message.guild.voice_client
				await server.disconnect()

	except Exception as e:
		print(e)

def main():
	if len(sys.argv) != 5:
		print("Usage: $python3 DiscordMemeBot.py <Attribs.hostname> <Attribs.username> <token_file> <Attribs.bad_reacts_file>")
		return

	token = None

	Attribs.hostname = sys.argv[1]
	Attribs.username = sys.argv[2]

	token_file = sys.argv[3]
	with open(token_file) as tf:
		token = tf.readline().strip()
		Attribs.main_channel_id = tf.readline().strip()

	Attribs.password = getpass.getpass()

	Attribs.bad_reacts_file = sys.argv[4]
	with open(Attribs.bad_reacts_file) as f:
		for l in f.readlines():
			Attribs.bad_reacts.append(l.strip())

	client.run(token)

if __name__ == "__main__":
	main()
