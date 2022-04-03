if __name__ == "__main__":
	from PIL import Image
	import numpy as np
	import sys

	from place.colors import RedditColor
	
	if len(sys.argv) > 1:
		new_fname = sys.argv[1].rsplit('.', 1)[0] + '.txt'
		img = Image.open(sys.argv[1])

		array = np.array(img)

		with open(new_fname, "w") as f:
			for x in range(array.shape[0]):
				for y in range(array.shape[1]):
					clr = array[x][y]
					if len(clr) > 3 and clr[3] != 255:
						f.write("-1 ")
						continue
					color = RedditColor.closest(clr[0], clr[1], clr[2])
					f.write(f"{color.value} ")
				f.write("\n")