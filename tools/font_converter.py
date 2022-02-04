# Copyright (c) 2022 VirusRushTheater

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import numpy as np
import PIL
import requests
import io
import os
import locale
import argparse
from collections import Counter
from typing import Tuple, Union

"""
A class to convert monospaced character bitmaps into SSD1306 headers.
"""
class FontConverter:
	
	def __init__(self):
		self.font_bytes = None

	def loadImage(self,
		url_or_path : str,
		font_size : Union[Tuple[int, int], str]
	):
		"""
		Loads an image from an URL or a file path in your PC and splices them
		into glyphs.
		"""
		is_remote = url_or_path.startswith("http")
		if is_remote:
			fontreq = requests.get(url_or_path)
			if fontreq.status_code != 200:
				raise requests.HTTPError(f"Could not download the remote image. Error {fontreq.status_code}")
			with io.BytesIO(fontreq.content) as fd:
				font_image = np.array(PIL.Image.open(fd))
		else:
			font_image = np.array(PIL.Image.open(url_or_path))
		
		if isinstance(font_size, tuple):
			assert(len(font_size) == 2)
		elif isinstance(font_size, str):
			font_size = tuple(map(int, font_size.lower().split("x")))
			assert(len(font_size) == 2)
		else:
			raise ValueError("font_size is not a tuple or a WxH string.")

		INVERT = False
		INVERT_COLORS = True

		pixvalue_counter = Counter(font_image.flat)
		if pixvalue_counter[1] > pixvalue_counter[0]:
			font_image = (1 - font_image)

		# If the font goes in more than one row, concatenate them using the font size data
		font_strip = np.hstack(np.reshape(font_image, (-1, font_size[1], font_image.shape[1])))
		# Adapt them in a Numpy Array so the dimensions go (character, column, pixel)
		# They may be higher than 8 but we'll fix that soon.
		font_glyphs = np.reshape(font_strip, (font_size[1], -1, font_size[0]))

		# Justify to a height that is multiple of 8
		if (font_glyphs.shape[0] % 8) > 0:
			col_rem = 8 - (font_glyphs.shape[0] % 8)
			font_glyphs = np.pad(font_glyphs, ((0, col_rem), (0, 0), (0, 0)))

		# Concatentate the glyphs so we get only fonts with height 8.
		font_gfxbytes = np.reshape(font_glyphs, (-1, 8, *font_glyphs.shape[1:]))
		self.font_shapeinfo = font_gfxbytes.shape
		font_gfxbytes = np.hstack(font_gfxbytes.transpose((0,1,3,2)))

		if INVERT == True:
			font_gfxbytes = font_gfxbytes[:, ::-1, ::-1]
		font_gfxbytes = np.transpose(font_gfxbytes.T, (1, 0, 2))

		# Sum their pixel dimension so it's one byte per 8 pixels height.
		self.font_bytes = np.sum(font_gfxbytes * np.array([[[1,2,4,8,16,32,64,128]]]), axis=2).astype(np.uint8)

	def createFontFiles(self,
		filename : str,
		font_name : str = None
	):
		"""
		"""
		if self.font_bytes is None:
			raise Exception("You have to run loadImage first.")
		
		no_ext_name = os.path.splitext(filename)[0]
		if font_name is None:
			font_name = os.path.basename(no_ext_name)
		
		header_file_name = no_ext_name + ".h"
		source_file_name = no_ext_name + ".c"

		# Header file only includes some command to reference it in other places.
		# The contents will be in our .c file which you should include in your
		# build too, or copy to another C file.
		with open(header_file_name, "w") as fd:
			fd.writelines([
				'#include "ssd1306_gfx.h"',
				'',
				f'extern const ssd1306_mono_font_t* {font_name};'
			])
		
		# Hex representation of all the Numpy array information, conserving
		# the array shape so we can present a tidy header file.
		fontdata_bytes = np.vectorize("0x{:02x}".format)(self.font_bytes)

		# Converts them into lines of bytes (columns)
		sourcedata_lines_pre = [', '.join(glyph) + "," for glyph in fontdata_bytes.T]
		sourcedata_lines_pre.append(sourcedata_lines_pre.pop()[:-1])

		# Comment lines, assuming character data starts from the space (0x20)
		# character.
		comment_lines = [f'\t// 0x{i:02x} ({chr(i)})' for i in range(0x20, 0x20 + len(sourcedata_lines_pre))]
		sourcedata_lines = ["\t" + i + j for i, j in zip(sourcedata_lines_pre, comment_lines)]

		# Skip data is used to use smaller sets of fonts that don't necessarily
		# start on 0x20, and have skips (for example a font you want only to
		# include numbers and letters and not the symbols in between.)
		# It's difficult to explain, sorry.
		skip_data = [
			(0x20, 0x20 + len(sourcedata_lines_pre) - 1)
		]
		skip_data_lines = ['\t' + ', '.join(i) + ',' for i in np.vectorize("0x{:02x}".format)(skip_data)]

		# Assemble the source code here.
		with open(source_file_name, "w") as fd:
			fd.writelines([
				f'#include "{header_file_name}"',
				'',
				'const unsigned char font_data [] = {',
			] + sourcedata_lines + [
				'};',
				'',
				'const unsigned char font_skipdata [] = {',
			] + skip_data_lines + [
				'0x00, 0x00\t//End',
				'};',
				'',
				'const ssd1306_mono_font_t font_struct = {',
				'\t.font_data = font_data,',
				'\t.skip_data =	font_skipdata,',
				'',
				f'\t.font_rows = {self.font_shapeinfo[0]},',
				f'\t.font_width = {self.font_shapeinfo[3]},',
				f'\t.bytes_per_character = {self.font_bytes.shape[0]}',
				'};',
				'',
				f'const ssd1306_mono_font_t* {font_name} = &font_struct;',
				''
			]
			)

# Working it as an executable.
if __name__ == '__main__':
	argp = argparse.ArgumentParser(description="Bitmap font converter")
	argp.add_argument("font_size", help="Size in WxH of each glyph")
	argp.add_argument("url_or_path", help="Path or URL to the image to be converted to font")

	args = argp.parse_args()

	z = FontConverter()
	z.loadImage(args.font_size)
	z.createFontFiles(args.url_or_path)