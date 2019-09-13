import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
import asyncio
import time
import os
import sys
import wave
import contextlib
import shutil
import requests
import random
import getpass

import FtpDl
import Memer

client = discord.Client()
audio_meme_list = []

cmd_lock = False

hostname = None
username = None
password = None

main_channel_id = None

def is_image(filename):
	return (filename.endswith("jpg") or filename.endswith("jpeg") or filename.endswith("png") or filename.endswith("gif"))

@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
	
	try:
		global audio_meme_list
		global cmd_lock

		global hostname
		global username
		global password

		global main_channel_id

		if cmd_lock:
			return

		cmd_lock = True

		meme_log = client.get_channel(main_channel_id)
		curr_channel = message.channel

		if message.author == client.user:
			return

		author = message.author
		content = message.content

		channel = None
		if author.voice is not None:
			channel = author.voice.channel

		if  (message.attachments or (len(content) > 1 and content[0] is not "-")) and curr_channel == meme_log:
			for item in message.attachments + [content]:
				if ((hasattr(item, "url") and is_image(item.url)) or (item == content and is_image(content))):
					url = None
					if item == content:
						url = content
					else:
						url = item.url
					print(url)
					response = requests.get(url, stream=True)
					image_name = url.split("/")
					image_name = image_name[len(image_name) - 1]

					with open(image_name, "wb") as out_file:
						shutil.copyfileobj(response.raw, out_file)
						out_file.close()
					del response
					
					FtpDl.upload_file(image_name, hostname, username, password)

		if content == "-roll":
			filenames = FtpDl.get_filenames(hostname, username, password)

			filename = random.choice(filenames)

			FtpDl.loadFile(filename, hostname, username, password)

			local_filename = filename.split("/")
			local_filename = local_filename[len(local_filename) - 1]

			await curr_channel.send(file=discord.File(local_filename))
			os.system("rm -f \"" + local_filename + "\"")

		elif content == "-memer":
			filenames = FtpDl.get_filenames(hostname, username, password)

			templates = FtpDl.get_templates(hostname, username, password)
			template = random.choice(templates)
			FtpDl.loadFile("/mnt/public/Bobby_Coulon/Templates/" + template, hostname, username, password)

			Memer.make_meme(template, filenames, hostname, username, password)

			await curr_channel.send(file=discord.File("tmp_meme.png"))

			os.system("rm -f \"null\"")
			os.system("rm -f \"" + template + "\"")
			os.system("rm -f \"tmp_meme.png\"")

		elif content == "-updateAudioMemes":
			files = os.listdir()

			for file in files:
				if file.endswith(".wav"):
					os.system("rm -f \"" + file + "\"")

			FtpDl.loadFiles(hostname, username, password)

			audio_meme_list = []
			files = os.listdir()

			for file in files:
				if file.endswith(".wav"):
					audio_meme_list.append(file)
			
		elif content == "-listAudioMemes":
			audio_meme_list_str = "Audio Meme List:"

			for f in audio_meme_list:
				l = f.replace(".wav", "")
				audio_meme_list_str += ("\n-" + l)

			await curr_channel.send(audio_meme_list_str)

		elif channel is not None and (("-say" in content) or (content.replace("-","") + ".wav" in audio_meme_list)):
			wav_file = None

			if "-say" in message.content:
				to_say = message.content.split("-say ")[1]
				os.system("espeak -w \"tmp.wav\" \"" + to_say + "\"")
				wav_file = "tmp.wav"
			else:
				wav_file = message.content.replace("-", "") + ".wav"

			vc = await channel.connect()

			duration = 0
			with contextlib.closing(wave.open(wav_file, "r")) as f:
				frames = f.getnframes()
				rate = f.getframerate()
				duration = frames / float(rate)

			vc.play(discord.FFmpegPCMAudio(wav_file), after=lambda e: print('done', e))

			time.sleep(duration)

			os.system("rm -f \"tmp.wav\"")

			server = message.guild.voice_client
			await server.disconnect()

		cmd_lock = False

	except Exception as e:
		print(e)
		cmd_lock = False

def main():
	global hostname
	global username
	global password

	global main_channel_id

	if len(sys.argv) != 4:
		print("Usage: $python3 DiscordMemeBot.py <hostname> <username> <token_file>")
		return

	hostname = sys.argv[1]
	username = sys.argv[2]
	password = getpass.getpass()

	token_file = sys.argv[3]
	with open(token_file) as tf:
		client.run(tf.readline().strip())
		main_channel_id = tf.readline().strip()

if __name__ == "__main__":
	main()