import subprocess
import re
import os
import multiprocessing
from PIL import Image
import random
import string

import FtpDl

class ImgArea:
	def __init__(self, x_o, y_o, x_c, y_c):
		self.x_coord = int(x_c)
		self.y_coord = int(y_c)
		self.x_offset = int(x_o)
		self.y_offset = int(y_o)

def rand_string(length, characters=string.ascii_letters + string.digits):
    return ''.join(random.choice(characters) for _ in range(length))

def resize_image(hostname, username, password, area, img):
	FtpDl.loadFile(img, hostname, username, password)
	try:
		img = img.split("/")
		img = img[len(img) - 1]
		with Image.open(img).convert("RGBA") as im:
			return (im.resize((area.x_offset, area.y_offset)), (area.x_coord, area.y_coord))
	except:
		print("Error on image: " + img)
		return None

def make_meme(template, imgs, hostname, username, password):
	convert_cmd = "magick " + template + " -alpha extract -negate -threshold 50% "
	convert_cmd += "-define connected-components:verbose=true "
	convert_cmd += "-define connected-components:area-threshold=100 "
	convert_cmd += "-connected-components 8 -auto-level null -quality 50"

	output = str(subprocess.check_output(convert_cmd, shell=True))

	p = re.compile("(\d: (\S+ ){3}srgb\(255,255,255\))")

	areas = []
	for match in re.findall(p, output):
		area_str = match[0].split(" ")[1]

		s = area_str.split("+")
		coords = s[0].split("x")
		offsets = [s[1], s[2]]
		
		tmp_area = ImgArea(coords[0], coords[1], offsets[0], offsets[1])
		areas.append(tmp_area)
		
	with Image.open(template).convert("RGBA") as template_im:
		img_choices = []
		cropped_imgs = []
		with multiprocessing.Pool(len(areas)) as pool:
			for area in areas:
				img_choice = None
				while img_choice is None or img_choice in img_choices:
					img_choice = random.choice(imgs)
				img_choices.append(img_choice)
				pool.apply_async(resize_image, (hostname, username, password, area, img_choice,), callback=lambda x: cropped_imgs.append(x) if x is not None else None)
			pool.close()
			pool.join()
		
		for cropped_img in cropped_imgs:
			template_im.paste(cropped_img[0], cropped_img[1], cropped_img[0])

		for fi in img_choices:
			fi = fi.split("/")
			fi = fi[len(fi) - 1]
			os.system("rm -f \"" + fi + "\"")

		filename = rand_string(length=10) + ".png"
		template_im.save(filename)
		return filename














