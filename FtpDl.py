import pysftp
import datetime
import os

hostname = "10.0.0.170"
u = "Bobby_Coulon"

now = datetime.datetime.now()

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None   

def loadFile(filename, h, u, p):
	with pysftp.Connection(host=h, username=u, password=p, cnopts=cnopts) as sftp:
		sftp.get(filename)

def loadFiles(h, u, p):
	with pysftp.Connection(host=h, username=u, password=p, cnopts=cnopts) as sftp:
		sftp.cwd("data/" + u + "/AudioMemes/")

		files = sftp.listdir()

		wav_list = []
		for file in files:
			if file.endswith(".wav"):
				sftp.get(file)
				wav_list.append(file)

		return wav_list

def upload_file(filename, h, u, p):
	with pysftp.Connection(host=h, username=u, password=p, cnopts=cnopts) as sftp:
		date_str = now.strftime("%Y-%m-%d")
		date_dir = "data/" + u + "/MemeDownloads/" + date_str

		if not sftp.isdir(date_dir):
			sftp.mkdir(date_dir, mode=777)

		sftp.cwd(date_dir)
		sftp.put(filename)
		os.system("rm -f \"" + filename + "\"")

def upload_video(filename, h, u, p):
	with pysftp.Connection(host=h, username=u, password=p, cnopts=cnopts) as sftp:
		v_dir = "data/" + u + "/VideoDownloads/"

		if not sftp.isdir(v_dir):
			sftp.mkdir(v_dir, mode=777)

		sftp.cwd(v_dir)
		sftp.put(filename)
		os.system("rm -f \"" + filename + "\"")

def get_filenames(h, u, p):
	with pysftp.Connection(host=h, username=u, password=p, cnopts=cnopts) as sftp:
		base_dir = "data/" + u + "/MemeDownloads/"

		sftp.cwd(base_dir)
		date_dirs = sftp.listdir()

		meme_files = []

		for date_dir in date_dirs:
			sftp.cwd(date_dir)
			ms = sftp.listdir()

			meme_files += [base_dir + date_dir + "/" + m for m in ms]

			sftp.cwd("..")

		return meme_files

def get_templates(h, u, p):
	with pysftp.Connection(host=h, username=u, password=p, cnopts=cnopts) as sftp:
		base_dir = "data/" + u + "/Templates/"

		sftp.cwd(base_dir)
		templates = sftp.listdir()
		
		return templates
