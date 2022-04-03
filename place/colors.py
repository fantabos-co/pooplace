import math

from enum import Enum
from typing import Dict, Tuple

_color_map : Dict[int, Tuple[int, int, int]] = {
	1:  (190, 0, 57),
	2:  (255, 69, 0),
	3:  (255, 168, 0),
	4:  (255, 214, 53),
	5:  (255, 248, 184),
	6:  (0, 163, 104),
	7:  (0, 204, 120),
	8:  (126, 237, 86),
	9:  (0, 117, 111),
	10: (0, 158, 170),
	11: (0, 204, 192),
	12: (36, 80, 164),
	13: (54, 144, 234),
	14: (81, 233, 244),
	15: (73, 58, 193),
	16: (106, 92, 255),
	17: (148, 179, 255),
	18: (129, 30, 159),
	19: (180, 74, 192),
	20: (228, 171, 255),
	21: (222, 16, 127),
	22: (255, 56, 129),
	23: (255, 153, 170),
	24: (109, 72, 47),
	25: (156, 105, 38),
	26: (255, 180, 112),
	27: (0, 0, 0),
	28: (81, 82, 82),
	29: (137, 141, 144),
	30: (212, 215, 217),
	31: (255, 255, 255)
}

_FLT = 0xFF

def unpack(color:int) -> Tuple[int, int, int]:
	r = color & _FLT
	g = (color >> 8) & _FLT
	b = (color >> 16) & _FLT
	return (r, g, b)

def pack(r:int, g:int, b:int) -> int:
	return (
		(_FLT & r) |
		((_FLT & g) << 8) |
		((_FLT & b) << 16)
	)

class RedditColor(Enum):
	DARK_RED = 1            #BE0039
	RED = 2                 #FF4500
	ORANGE = 3              #FFA800
	YELLOW = 4              #FFD635
	PALE_YELLOW = 5			#FFF8B8
	DARK_GREEN = 6          #00A368
	GREEN = 7               #00CC78
	LIGHT_GREEN = 8         #7EED56
	DARK_TEAL = 9           #00756F
	TEAL = 10               #009EAA
	LIGHT_TEAL = 11			#00CCC0
	DARK_BLUE = 12          #2450A4
	BLUE = 13               #3690EA
	CYAN = 14               #51E9F4
	INDIGO = 15             #493AC1
	PERIWINKLE = 16         #6A5CFF
	LAVENDER = 17			#94B3FF
	DARK_PURPLE = 18        #811E9F
	PURPLE = 19             #B44AC0
	PALE_PURPLE = 20		#E4ABFF
	MAGENTA = 21			#DE107F
	PINK = 22               #FF3881
	LIGHT_PINK = 23         #FF99AA
	DARK_BROWN = 24         #6D482F
	BROWN = 25              #9C6926
	BEIGE = 26				#FFB470
	BLACK = 27              #000000
	DARK_GREY = 28			#515252
	GREY = 29               #898D90
	LIGHT_GREY = 30         #D4D7D9
	WHITE = 31              #FFFFFF

	@classmethod
	def closest(cls, r, g, b):
		closest_color = None
		color_distance = None
		for color in cls:
			cr, cg, cb = color.to_tuple()
			color_diff = math.sqrt((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2)
			if color_distance is None or color_diff < color_distance:
				color_distance = color_diff
				closest_color = color
		return closest_color

	def to_tuple(self):
		return _color_map[self.value]

