import subprocess
import re
import os
from PIL import Image
import random

import FtpDl

class ImgArea:
	def __init__(self, x_o, y_o, x_c, y_c):
		self.x_coord = int(x_c)
		self.y_coord = int(y_c)
		self.x_offset = int(x_o)
		self.y_offset = int(y_o)

def make_meme(template, imgs, hostname, username, password):
	convert_cmd = "convert " + template + " -alpha extract -negate -threshold 50% "
	convert_cmd += "-define connected-components:verbose=true "
	convert_cmd += "-define connected-components:area-threshold=100 "
	convert_cmd += "-connected-components 8 -auto-level null"

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
		final_imgs = []
		failure = False
		
		for area in areas:
			final_img = None
			while final_img is None or final_img in final_imgs:
				final_img = random.choice(imgs)
			
			FtpDl.loadFile(final_img, hostname, username, password)
			final_imgs.append(final_img)
			
			try:
				final_img = final_img.split("/")
				final_img = final_img[len(final_img) - 1]

				with Image.open(final_img).convert("RGBA") as im:
					im = im.resize((area.x_offset, area.y_offset))

					template_im.paste(im, (area.x_coord, area.y_coord), im)
			except:
				failure = True
				break

		for fi in final_imgs:
			fi = fi.split("/")
			fi = fi[len(fi) - 1]
			os.system("rm -f \"" + fi + "\"")

		if failure:
			return False
		else:
			template_im.save("tmp_meme.png")
			return True














