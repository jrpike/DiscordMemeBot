# DiscordMemeBot

A simple Discord bot designed to interface with a user-facing FTP server.

Features:
- Plays .wav files in a user's channel
	- Files should be stored in "/mnt/public/username/AudioMemes/"
	- "-filename" (filename should not include ".wav" extension in command) plays audio
	- "-updateAudioMemes" updates local files from the FTP server (should be run initially and after adding any new files)
	- "-listAudioMemes" lists currently local, available to run audio commands
- Stores images posted to the main (see notes section) chat log in "/mnt/public/username/MemeDownloads/"
- Generates random memes by combining templates with previously stored images (via feature above)
	- "-memer" will generate a random meme
	- "-memer my_template" will use the template with filename "my_template.png"
	- "-listTemplates" will post a list of all templates
	- Templates are drawn from /mnt/public/username/Templates/

Notes:
- The "token_file" parameter should point to a plaintext file with the following format (without "LINE X:"):
	- LINE 1: bot_token
	- LINE 2: main_channel_id
- Only images (.jpg, .jpeg, .png, or .gif only) posted to the main channel will be uploaded to the FTP server
- Incorrectly formatted commands (e.g. no such template) will be reacted to with a random emoji from the "bad_reacts_file"
