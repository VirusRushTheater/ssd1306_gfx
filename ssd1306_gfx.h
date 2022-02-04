/*
 * Copyright (c) 2022 VirusRushTheater
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
*/

#ifndef __SSD1306_GFX_H
#define __SSD1306_GFX_H

#include "ssd1306_gfx_config.h"

// Common data types are more comfortable to be defined that way.
#ifndef uint8_t
typedef unsigned char uint8_t;
#endif
#ifndef size_t
typedef unsigned int size_t;
#endif

/* ===============
 * SSD1306 OPCODES
 */

// Control byte to send commands.
#define SSD1306_CONTROLBYTE				0x00
#define SSD1306_DATABYTE				0x40

// SSD1306 commands
#define SSD1306_BRIGHTNESS				0x81
#define SSD1306_DISPLAYALLON_RESUME		0xA4
#define SSD1306_DISPLAYALLON			0xA5
#define SSD1306_NORMALDISPLAY			0xA6
#define SSD1306_INVERTDISPLAY			0xA7
#define SSD1306_DISPLAYOFF				0xAE
#define SSD1306_DISPLAYON				0xAF
#define SSD1306_SETDISPLAYOFFSET		0xD3
#define SSD1306_MEMSCANMODE				0xDA
#define SSD1306_SETVCOMDETECT			0xDB
#define SSD1306_SETDISPLAYCLOCKDIV		0xD5
#define SSD1306_SETPRECHARGE			0xD9
#define SSD1306_SETMULTIPLEX			0xA8
#define SSD1306_SETLOWCOLUMN			0x00
#define SSD1306_SETHIGHCOLUMN			0x10
#define SSD1306_SETSTARTLINE(ROW_N)		(0x40 + ROW_N)
#define SSD1306_MEMADDRESSINGMODE		0x20
#define SSD1306_COLUMNADDR				0x21
#define SSD1306_PAGEADDR				0x22

// Horizontal flipping (aka. commons)
#define SSD1306_ROWLEFTTORIGHT			0xA1
#define SSD1306_ROWRIGHTTOLEFT			0xA0

// Vertical flipping (aka. segments)
#define SSD1306_COLUPTODOWN				0xC8
#define SSD1306_COLDOWNTOUP				0xc0

#define SSD1306_DISABLESCROLL			0x2E
#define SSD1306_CHARGEPUMP				0x8D
#define SSD1306_EXTERNALVCC				0x01
#define SSD1306_SWITCHCAPVCC			0x02 

/* ========================
 * Configuration assertions
 */
// Wrong number of pixels height
#if ((SSD1306_CONF_LCDHEIGHT != 32) && (SSD1306_CONF_LCDHEIGHT != 64))
#error SSD1306_CONF_LCDHEIGHT can be 32 or 64 pixels height. Set up your config definitions.
#endif

#if (SSD1306_CONF_LCDWIDTH != 128)
#error SSD1306_CONF_LCDWIDTH is not 128. Set up your config definitions.
#endif

/* ========================
 * Structures
 */

/**
 * Base handler for a SSD1306 display.
 */
struct _ssd1306_i2c_t
{
	uint8_t		address;
	uint8_t		invert_display;

	int			height;
	int			width;

	int			row_byteshift;
	size_t		buffer_size;
	uint8_t		buffer[SSD1306_CONF_LCDWIDTH * SSD1306_CONF_LCDHEIGHT / 8];
};
typedef struct _ssd1306_i2c_t 	ssd1306_i2c_t;

/**
 * Base structure of generated monospace fonts.
 */
struct _ssd1306_mono_font_t
{
	uint8_t* font_data;
	char* skip_data;

	uint8_t font_rows;
	uint8_t font_width;
	uint8_t bytes_per_character;
};
typedef struct _ssd1306_mono_font_t ssd1306_mono_font_t;

#endif //__SSD1306_GFX_H