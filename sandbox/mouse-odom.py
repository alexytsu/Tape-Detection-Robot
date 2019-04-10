import time
import math

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

mouse = open("/dev/input/mice", "rb")  
curtime = 0
distance = 0
distance_x = 0
distance_y = 0

points_x = []
points_y = []

counter = 0

while True:

	counter += 1
	if counter >= 200:
		break

	oldtime = curtime
	curtime = time.time()
	delta = curtime - oldtime

	status, dx, dy = tuple(c for c in mouse.read(3))

	def to_signed(n):
		return n - ((0x80 & n) << 1)

	dx = to_signed(dx)
	dy = to_signed(dy)

	total = math.sqrt(dx**2 + dy**2)/delta
	distance += math.sqrt(dx**2 + dy**2)
	distance_x += dx
	distance_y += dy

	points_x.append(distance_x)
	points_y.append(distance_y)


	print(distance)


	print("y: ", distance_y, "x: ", distance_x)

plt.scatter(points_x, points_y)
plt.show()
#print( "%#02x %f %f" % (status, dx/delta, dy/delta))




