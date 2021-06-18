import time
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from numpy import *
from random import randint, choice


def build_simple_house(str, map, map_slice, wall_material, beam_material, doorframe_material, floor_material, roof_material, roof_beam_material, wall_under_roof_material, window_material, door_material, flat_roof):
	w = str.x2 - str.x1
	h = str.y2 - str.y1

	roof_altitude = str.altitude+str.height
	roof_height_limit = 0

	rotation_dc = {'s': 0, 'n': 180, 'e': 90, 'w': -90}
	rotation_angle = rotation_dc[str.direction]

	if rotation_angle == 90 or rotation_angle == -90:
		w, h = h, w

	map_slice.rotate(rotation_angle)

	# construction starts here

	build_segment_slice(str, map_slice, 0, 0, w, h, str.altitude, str.height, wall_material, beam_material, floor_material)
	build_roof_beams_slice(str, map_slice, 0, 0, w, h, roof_altitude-1, 'snew', wall_material, beam_material, roof_beam_material)

	segment = (0, 0, w, h)
	segments = [segment]

	#roof gable facing forward

	walls = [
				(segment[0], segment[1], segment[0], segment[3]), # left wall
				(segment[2]-1, segment[1], segment[2]-1, segment[3]), # right wall
			]

	gables = [
				(segment[0], segment[1], segment[2], segment[1]), # top wall
				(segment[0], segment[3]-1, segment[2], segment[3]-1), # bottom wall
			]

	walls, gables = gables, walls

	gen_roof_slice(map_slice, (-1, -1, w+1, h+1), segments, walls, gables, roof_altitude, wall_under_roof_material, roof_beam_material, roof_material, flat_roof)

	# door_x = str.door_x - str.x1
	# door_y = str.door_y - str.y1

	door_x, door_y = int(float(w/2)), h-1
	xc, yc = int(round(w/2)), int(round(h/2))

	build_doorway_slice(str, map_slice, doorframe_material, door_material, door_x, door_y, str.altitude, 's')

	#tried to make it look ok with w/h values of 7, 9, 11

	#front and back windows
	build_windows_slice(str, map_slice, window_material, 0, h-1, w, h-1, door_x, h-1, 'sn', 1, 3, False, str.altitude+2, 2)
	build_windows_slice(str, map_slice, window_material, 0, 0, w, 0, door_x, 0, 'sn', 1, 2, True, str.altitude+2, 2)

	#side windows
	build_windows_slice(str, map_slice, window_material, 0, 0, 0, h, 0, yc, 'ew', 1, 2, True, str.altitude+2, 2)
	build_windows_slice(str, map_slice, window_material, w-1, 0, w-1, h, w-1, yc, 'ew', 1, 2, True, str.altitude+2, 2)

	#top windows
	if not flat_roof:
		build_windows_slice(str, map_slice, window_material, 0, yc, 0, yc, 0, yc, 'ew', 2, 3, True, str.altitude+str.height+1, 1)
		build_windows_slice(str, map_slice, window_material, w-1, yc, w-1, yc, w-1, yc, 'ew', 2, 3, True, str.altitude+str.height+1, 1)


	#torches: front
	map_slice.fill(segment[0], segment[3], str.altitude+3, segment[0]+1, segment[3]+1, str.altitude+4, (50,3))
	map_slice.fill(segment[2]-1, segment[3], str.altitude+3, segment[2], segment[3]+1, str.altitude+4, (50,3))

	#torches: back
	map_slice.fill(segment[0], segment[1]-1, str.altitude+3, segment[0]+1, segment[1], str.altitude+4, (50,4))
	map_slice.fill(segment[2]-1, segment[1]-1, str.altitude+3, segment[2], segment[1], str.altitude+4, (50,4))

	#torches: left
	map_slice.fill(segment[0]-1, segment[1], str.altitude+3, segment[0], segment[1]+1, str.altitude+4, (50,2))
	map_slice.fill(segment[0]-1, segment[3]-1, str.altitude+3, segment[0], segment[3], str.altitude+4, (50,2))

	#torches: right
	map_slice.fill(segment[2], segment[1], str.altitude+3, segment[2]+1, segment[1]+1, str.altitude+4, (50,1))
	map_slice.fill(segment[2], segment[3]-1, str.altitude+3, segment[2]+1, segment[3], str.altitude+4, (50,1))


	#wall torches still require adaptation for 0,0 to w,h coordinate system
	# build_torches_slice(str, map_slice)

	#support will require "real" map?
	# build_support_slice(str, map_slice, beam_material)

	#construction ends here

	map_slice.rotate(-rotation_angle)


def build_temple(str, map, map_slice, wall_material, beam_material, doorframe_material, floor_material, roof_material, wall_under_roof_material, window_material, door_material, flat_roof):
	w = str.x2 - str.x1
	h = str.y2 - str.y1

	rotation_dc = {'s': 0, 'n': 180, 'e': 90, 'w': -90}
	rotation_angle = rotation_dc[str.direction]

	if rotation_angle == 90 or rotation_angle == -90:
		w, h = h, w

	map_slice.rotate(rotation_angle)

	#construction starts here

	door_x, door_y = int(round(w/2)), h-1

	roof_altitude = str.altitude+str.height
	roof_height_limit = 6

	build_segment_slice(str, map_slice, 1, 1, w-1, h-1, str.altitude, str.height, wall_material, beam_material, floor_material)

	#roof

	segment = (1, 1, w-1, h-1)
	# segment = (0, 1, w, h-1)
	segments = [segment]

	walls = [
				(segment[0], segment[1], segment[0], segment[3]), # left wall
				(segment[2]-1, segment[1], segment[2]-1, segment[3]), # right wall
			]

	gables = [
				(segment[0], segment[1], segment[2], segment[1]), # top wall
				(segment[0], segment[3]-1, segment[2], segment[3]-1), # bottom wall
			]

	gen_roof_slice(map_slice, (-1, -1, w+1, h+1), segments, walls, gables, roof_altitude, wall_under_roof_material, beam_material, roof_material, False)


	#front tower and side chambers

	tower_radius = 2
	tower_height = str.height + 8

	map_slice.fill(door_x-tower_radius, h-1-tower_radius*2-1, str.altitude+2, door_x+tower_radius+1, h, str.altitude+tower_height, (0,0))
	build_segment_slice(str, map_slice, door_x-tower_radius, h-1-tower_radius*2-1, door_x+tower_radius+1, h-1, str.altitude, tower_height, wall_material, beam_material, floor_material)
	build_blocks_slice(str, map_slice, door_x-tower_radius, h-1-tower_radius*2-1, door_x+tower_radius+1, h, str.altitude+tower_height-1, 1, wall_material)


	build_segment_slice(str, map_slice, 1, h-1-tower_radius*2-1, door_x-tower_radius+1, h-1, str.altitude, str.height, wall_material, beam_material, floor_material)
	build_segment_slice(str, map_slice, door_x+tower_radius, h-1-tower_radius*2-1, w-1, h-1, str.altitude, str.height, wall_material, beam_material, floor_material)

	build_facade_temple_slice(str, map_slice, 0, 0, w, h, door_x, door_y, str.height, tower_height, 's', wall_material, beam_material, floor_material)

	build_doorway_slice(str, map_slice, doorframe_material, door_material, door_x, door_y-1, str.altitude, 's')

	build_doorway_slice(str, map_slice, doorframe_material, door_material, door_x, door_y-1-tower_radius*2, str.altitude, 'n')
	build_doorway_slice(str, map_slice, doorframe_material, door_material, door_x-tower_radius-2, door_y-1-tower_radius*2, str.altitude, 'n')
	build_doorway_slice(str, map_slice, doorframe_material, door_material, door_x+tower_radius+2, door_y-1-tower_radius*2, str.altitude, 'n')

	#tower access? (scrap or redesign...)
	# map_slice.fill(door_x-tower_radius, door_y-tower_radius*2, str.altitude+str.height-1, door_x-tower_radius+1, h-2, str.altitude+str.height+4, (0,0))
	# map_slice.fill(door_x+tower_radius-1, door_y-tower_radius*2, str.altitude+str.height-1, door_x+tower_radius, h-2, str.altitude+str.height+4, (0,0))
	# map_slice.fill(door_x-tower_radius, door_y-tower_radius*2, str.altitude+str.height-2, door_x+tower_radius, h-2, str.altitude+str.height-1, floor_material)


	#altar
	build_blocks_slice(str, map_slice, door_x-1, 2, door_x+2, 3, str.altitude+1, 3, (43, 5))
	build_blocks_slice(str, map_slice, door_x, 2, door_x+1, 3, str.altitude+2, 1, (0, 0))
	build_blocks_slice(str, map_slice, door_x, 2, door_x+1, 3, str.altitude+4, 1, (44, 5))
	build_blocks_slice(str, map_slice, door_x, 2, door_x+1, 3, str.altitude+2, 1, (47, 0))
	build_blocks_slice(str, map_slice, door_x-1, 3, door_x, 4, str.altitude+2, 1, (50, 3))
	build_blocks_slice(str, map_slice, door_x+1, 3, door_x+2, 4, str.altitude+2, 1, (50, 3))


	#facade windows
	build_windows_slice(str, map_slice, window_material, 0, h-2, door_x, h-2, door_x-tower_radius+1, h-2, 'sn', 1, 3, False, str.altitude+2, 3)
	build_windows_slice(str, map_slice, window_material, door_x, h-2, w, h-2, door_x+tower_radius-1, h-2, 'sn', 1, 3, False, str.altitude+2, 3)

	#side windows
	build_windows_slice(str, map_slice, window_material, 1, 1, 1, h-2, 1, h-4, 'ew', 1, 4, True, str.altitude+2, 3)
	build_windows_slice(str, map_slice, window_material, w-2, 1, w-2, h-2, w-2, h-4, 'ew', 1, 4, True, str.altitude+2, 3)

	#top tower window
	build_windows_slice(str, map_slice, window_material, door_x, h-2, door_x, h-2, door_x, h-2, 'sn', 1, 3, True, str.altitude+str.height+3, 3)

	#back windows on sides of altar
	build_windows_slice(str, map_slice, window_material, 0, 1, door_x, 1, door_x-3, 1, 'sn', 1, 3, True, str.altitude+2, 3)
	build_windows_slice(str, map_slice, window_material, door_x, 1, w, 1, door_x+3, 1, 'sn', 1, 3, True, str.altitude+2, 3)


	#tower roof

	segment = (door_x-tower_radius, h-tower_radius*2-1, door_x+tower_radius+1, h-1)
	segments = [segment]
	gables = []

	if flat_roof:
		walls = [
					(segment[0], segment[1]-1, segment[0], segment[3]+1), # left wall
					(segment[2]-1, segment[1]-1, segment[2]-1, segment[3]+1), # right wall
					(segment[0], segment[1]-1, segment[2], segment[1]-1), # top wall
					(segment[0], segment[3], segment[2], segment[3]), # bottom wall
				]

		gen_roof_slice(map_slice, (-1, -1, w+1, h+1), segments, walls, gables, str.altitude+tower_height, wall_under_roof_material, beam_material, roof_material, True)

	else:
		walls = [
					(segment[0], segment[1], segment[0], segment[3]), # left wall
					(segment[2]-1, segment[1], segment[2]-1, segment[3]), # right wall
					(segment[0], segment[1], segment[2], segment[1]), # top wall
					(segment[0], segment[3]-1, segment[2], segment[3]-1), # bottom wall
				]

		gen_roof_slice(map_slice, (-1, -1, w+1, h+1), segments, walls, gables, str.altitude+tower_height, wall_under_roof_material, beam_material, roof_material, False)


	#torches: front
	map_slice.fill(segment[0], segment[3]+1, str.altitude+3, segment[0]+1, segment[3]+2, str.altitude+4, (50,3))
	map_slice.fill(segment[2]-1, segment[3]+1, str.altitude+3, segment[2], segment[3]+2, str.altitude+4, (50,3))

	map_slice.fill(1, segment[3]+1, str.altitude+3, 2, segment[3]+2, str.altitude+4, (50,3))
	map_slice.fill(w-2, segment[3]+1, str.altitude+3, w-1, segment[3]+2, str.altitude+4, (50,3))

	#torches: front top
	map_slice.fill(segment[0], segment[3]+1, str.altitude+str.height+5, segment[0]+1, segment[3]+2, str.altitude+str.height+6, (50,3))
	map_slice.fill(segment[2]-1, segment[3]+1, str.altitude+str.height+5, segment[2], segment[3]+2, str.altitude+str.height+6, (50,3))

	#torches: back
	map_slice.fill(1, -1, str.altitude+3, 2, 0, str.altitude+4, (50,4))
	map_slice.fill(w-2, -1, str.altitude+3, w-1, 0, str.altitude+4, (50,4))

	#torches: left
	map_slice.fill(-1, 1, str.altitude+3, 0, 2, str.altitude+4, (50,2))
	map_slice.fill(-1, segment[3]-1, str.altitude+3, 0, segment[3], str.altitude+4, (50,2))

	#torches: right
	map_slice.fill(w, 1, str.altitude+3, w+1, 2, str.altitude+4, (50,1))
	map_slice.fill(w, segment[3]-1, str.altitude+3, w+1, segment[3], str.altitude+4, (50,1))


	#construction ends here

	map_slice.rotate(-rotation_angle)


def build_facade_temple_slice(str, map_slice, x1, y1, x2, y2, door_x, door_y, height, tower_height, direction, wall_material, beam_material, floor_material):
	door_dist = 1

	#front

	map_slice.fill(door_x-door_dist-1, y2-1, str.altitude, door_x-door_dist, y2, str.altitude+tower_height-1, beam_material)
	map_slice.fill(door_x+door_dist+1, y2-1, str.altitude, door_x+door_dist+2, y2, str.altitude+tower_height-1, beam_material)

	map_slice.fill(x1+1, y2-1, str.altitude, x1+2, y2, str.altitude+height, beam_material)
	map_slice.fill(x2-2, y2-1, str.altitude, x2-1, y2, str.altitude+height, beam_material)

	#sides

	map_slice.fill(x1, y2-2, str.altitude, x1+1, y2-1, str.altitude+height-1, beam_material)
	map_slice.fill(x1, y1+1, str.altitude, x1+1, y1+2, str.altitude+height-1, beam_material)

	map_slice.fill(x2-1, y2-2, str.altitude, x2, y2-1, str.altitude+height-1, beam_material)
	map_slice.fill(x2-1, y1+1, str.altitude, x2, y1+2, str.altitude+height-1, beam_material)

	map_slice.fill(x1+1, y1, str.altitude, x1+2, y1+1, str.altitude+height, beam_material)
	map_slice.fill(x2-2, y1, str.altitude, x2-1, y1+1, str.altitude+height, beam_material)

	#walls behind pillars (override any beams, since the beams already 'stick out' out of the building)

	map_slice.fill(door_x-door_dist-1, y2-2, str.altitude, door_x-door_dist, y2-1, str.altitude+tower_height-1, wall_material)
	map_slice.fill(door_x+door_dist+1, y2-2, str.altitude, door_x+door_dist+2, y2-1, str.altitude+tower_height-1, wall_material)

	map_slice.fill(x1+1, y2-2, str.altitude, x1+2, y2-1, str.altitude+height, wall_material)
	map_slice.fill(x2-2, y2-2, str.altitude, x2-1, y2-1, str.altitude+height, wall_material)


def build_complex_house(str, map, map_slice, wall_material, beam_material, doorframe_material, floor_material, roof_material, roof_beam_material, wall_under_roof_material, window_material, door_material, flat_roof):
	#either limit roof height, or ensure segments have the same (odd) width/height
	#shouldn't check direction, but structure alignment (direction may depend on door)?

	w = str.x2 - str.x1
	h = str.y2 - str.y1
	m = 1

	rotation_dc = {'s': 0, 'n': 180, 'e': 90, 'w': -90}
	rotation_angle = rotation_dc[str.direction]

	if rotation_angle == 90 or rotation_angle == -90:
		w, h = h, w

	map_slice.rotate(rotation_angle)

	#construction starts here

	roof_altitude = str.altitude+str.height
	roof_height_limit = 0

	segment_break_x = int(round(w * .5))
	segment_break_y = int(round(h * .5))

	segment_a = (m, m, segment_break_x, h-m)
	segment_b = (segment_break_x-1, m, w-m, segment_break_y)

	#segment A (larger, left)
	build_segment_slice(str, map_slice, segment_a[0], segment_a[1], segment_a[2], segment_a[3], str.altitude, str.height, wall_material, beam_material, floor_material)

	#segment B (shorter, right)
	build_segment_slice(str, map_slice, segment_b[0], segment_b[1], segment_b[2], segment_b[3], str.altitude, str.height, wall_material, beam_material, floor_material)

	#rooftop beams
	build_roof_beams_slice(str, map_slice, segment_a[0], segment_a[1], segment_a[2], segment_a[3], roof_altitude-1, 'snew', wall_material, beam_material, roof_beam_material)
	build_roof_beams_slice(str, map_slice, segment_b[0], segment_b[1], segment_b[2], segment_b[3], roof_altitude-1, 'snew', wall_material, beam_material, roof_beam_material)

	#clear space between segments
	map_slice.fill(segment_a[2]-1, segment_b[1]+1, str.altitude+1, segment_a[2], segment_b[3]-1, str.altitude+str.height, (0,0))

	#rooftops

	segments = [segment_a, segment_b]

	walls = [
				(segment_a[0], segment_a[1], segment_a[0], segment_a[3]), # left wall (a)
				(segment_a[0], segment_a[1], segment_b[2], segment_a[1]), # top wall (a/b)
				(segment_a[2]-1, segment_b[3], segment_a[2]-1, segment_a[3]), # right wall (a)
				(segment_b[0], segment_b[3]-1, segment_b[2], segment_b[3]-1), # bottom wall (b)
			]

	gables = [
				(segment_a[0], segment_a[3]-1, segment_a[2], segment_a[3]-1), # bottom wall (a)
				(segment_b[2]-1, segment_b[1], segment_b[2]-1, segment_b[3]), # right wall (b)
			]

	gen_roof_slice(map_slice, (-1, -1, w+1, h+1), segments, walls, gables, roof_altitude, wall_under_roof_material, roof_beam_material, roof_material, flat_roof)


	#door

	door_x = w - 4 - m
	door_y = segment_break_y - 1

	build_doorway_slice(str, map_slice, doorframe_material, door_material, door_x, door_y, str.altitude, 's')


	#front left window (bottom and top)
	build_windows_slice(str, map_slice, window_material, segment_a[0], segment_a[3]-1, segment_a[2], segment_a[3]-1, int(round((segment_a[2]-segment_a[0])/2))+1, segment_a[3]-1, 'sn', 1, 2, True, str.altitude+2, 2)
	if not flat_roof:
		build_windows_slice(str, map_slice, window_material, segment_a[0], segment_a[3]-1, segment_a[2], segment_a[3]-1, int(round((segment_a[2]-segment_a[0])/2))+1, segment_a[3]-1, 'sn', 999, 999, True, str.altitude+str.height+1, 1)

	#back windows (currently there's a remaining beam, and the windows are split in separate sections going around it)
	build_windows_slice(str, map_slice, window_material, segment_a[0], segment_a[1], segment_a[2], segment_a[1], int(round((segment_a[2]-segment_a[0])/2))+1, segment_a[1], 'sn', 1, 2, True, str.altitude+2, 2)
	build_windows_slice(str, map_slice, window_material, segment_b[0], segment_a[1], segment_b[2], segment_a[1], door_x, segment_a[1], 'sn', 1, 2, True, str.altitude+2, 2)

	#left side windows
	build_windows_slice(str, map_slice, window_material, segment_a[0], segment_a[1], segment_a[0], segment_a[3]-1, segment_a[0], segment_a[3]-3, 'ew', 1, 2, True, str.altitude+2, 2)

	#right (short) side windows
	build_windows_slice(str, map_slice, window_material, segment_a[2]-1, segment_b[3]-1, segment_a[2]-1, segment_a[3]-1, segment_a[2]-1, segment_a[3]-3, 'ew', 1, 2, True, str.altitude+2, 2)

	#right end window (bottom and top)
	build_windows_slice(str, map_slice, window_material, segment_b[2]-1, segment_b[1], segment_b[2]-1, segment_b[3], segment_b[2]-1, int(round((segment_b[3]-segment_b[1])/2))+1, 'ew', 1, 2, True, str.altitude+2, 2)
	if not flat_roof:
		build_windows_slice(str, map_slice, window_material, segment_b[2]-1, segment_b[1], segment_b[2]-1, segment_b[3], segment_b[2]-1, int(round((segment_b[3]-segment_b[1])/2))+1, 'ew', 999, 999, True, str.altitude+str.height+1, 1)


	#torches: front
	map_slice.fill(segment_a[0], segment_a[3], str.altitude+3, segment_a[0]+1, segment_a[3]+1, str.altitude+4, (50,3))
	map_slice.fill(segment_a[2]-1, segment_a[3], str.altitude+3, segment_a[2], segment_a[3]+1, str.altitude+4, (50,3))

	#torches: back
	map_slice.fill(segment_a[0], segment_a[1]-1, str.altitude+3, segment_a[0]+1, segment_a[1], str.altitude+4, (50,4))
	map_slice.fill(segment_a[2]-1, segment_a[1]-1, str.altitude+3, segment_a[2], segment_a[1], str.altitude+4, (50,4))
	map_slice.fill(segment_b[2]-1, segment_a[1]-1, str.altitude+3, segment_b[2], segment_a[1], str.altitude+4, (50,4))

	#torches: left
	map_slice.fill(segment_a[0]-1, segment_a[1], str.altitude+3, segment_a[0], segment_a[1]+1, str.altitude+4, (50,2))
	map_slice.fill(segment_a[0]-1, segment_a[3]-1, str.altitude+3, segment_a[0], segment_a[3], str.altitude+4, (50,2))

	#torches: right
	map_slice.fill(segment_b[2], segment_b[1], str.altitude+3, segment_b[2]+1, segment_b[1]+1, str.altitude+4, (50,1))
	map_slice.fill(segment_b[2], segment_b[3]-1, str.altitude+3, segment_b[2]+1, segment_b[3], str.altitude+4, (50,1))

	#torches: side wall
	map_slice.fill(segment_a[2], segment_a[3]-1, str.altitude+3, segment_a[2]+1, segment_a[3], str.altitude+4, (50,1))

	#torches: entrance wall
	map_slice.fill(segment_b[2]-1, segment_b[3], str.altitude+3, segment_b[2], segment_b[3]+1, str.altitude+4, (50,3))


	#construction ends here

	map_slice.rotate(-rotation_angle)


def build_garden_house(str, map, map_slice, wall_material, beam_material, doorframe_material, floor_material, roof_material, roof_beam_material, wall_under_roof_material, window_material, door_material, flat_roof):
	#either limit roof height, or ensure segments have the same (odd) width/height
	#shouldn't check direction, but structure alignment (direction may depend on door)?

	w = str.x2 - str.x1
	h = str.y2 - str.y1
	m = 1

	rotation_dc = {'s': 0, 'n': 180, 'e': 90, 'w': -90}
	rotation_angle = rotation_dc[str.direction]

	if rotation_angle == 90 or rotation_angle == -90:
		w, h = h, w

	map_slice.rotate(rotation_angle)

	#construction starts here

	roof_altitude = str.altitude+str.height
	roof_height_limit = 0

	segment_break_x = int(round(w * .5))
	segment_break_y = int(round(h * .5))
	# segment_break_y = int(round(h * .7))

	segment_a = (m, m, segment_break_x, h-m)
	segment_b = (segment_break_x-1, m, w-m, segment_break_y)

	#segment A (larger, left)
	build_segment_slice(str, map_slice, segment_a[0], segment_a[1], segment_a[2], segment_a[3], str.altitude, str.height, wall_material, beam_material, floor_material)

	#segment B (shorter, right)
	build_segment_slice(str, map_slice, segment_b[0], segment_b[1], segment_b[2], segment_b[3], str.altitude, str.height, wall_material, beam_material, floor_material)

	#rooftop beams
	build_roof_beams_slice(str, map_slice, segment_a[0], segment_a[1], segment_a[2], segment_a[3], roof_altitude-1, 'snew', wall_material, beam_material, roof_beam_material)
	build_roof_beams_slice(str, map_slice, segment_b[0], segment_b[1], segment_b[2], segment_b[3], roof_altitude-1, 'snew', wall_material, beam_material, roof_beam_material)

	#clear space between segments
	map_slice.fill(segment_a[2]-1, segment_b[1]+1, str.altitude+1, segment_a[2], segment_b[3]-1, str.altitude+str.height, (0,0))

	#rooftops

	segments = [segment_a, segment_b]

	walls = [
				(segment_a[0], segment_a[1], segment_a[0], segment_a[3]), # left wall (a)
				(segment_a[0], segment_a[1], segment_b[2], segment_a[1]), # top wall (a/b)
				(segment_a[2]-1, segment_b[3], segment_a[2]-1, segment_a[3]), # right wall (a)
				(segment_b[0], segment_b[3]-1, segment_b[2], segment_b[3]-1), # bottom wall (b)
			]

	gables = [
				(segment_a[0], segment_a[3]-1, segment_a[2], segment_a[3]-1), # bottom wall (a)
				(segment_b[2]-1, segment_b[1], segment_b[2]-1, segment_b[3]), # right wall (b)
			]

	gen_roof_slice(map_slice, (-1, -1, w+1, h+1), segments, walls, gables, roof_altitude, wall_under_roof_material, roof_beam_material, roof_material, flat_roof)


	#garden

	map_slice.fill(segment_a[2], segment_b[3], str.altitude, segment_b[2], segment_a[3], str.altitude+2, beam_material)
	map_slice.fill(segment_a[2], segment_b[3], str.altitude+1, segment_b[2]-1, segment_a[3]-1, str.altitude+2, (2,0))
	map_slice.fill(segment_a[2], segment_b[3], str.altitude+2, segment_b[2]-1, segment_a[3]-1, str.altitude+3, (38,8))

	#door

	door_x = 3 + m
	door_y = h - 2

	build_doorway_slice(str, map_slice, doorframe_material, door_material, door_x, door_y, str.altitude, 's')

	#garden door

	garden_door_x = w - 4 - m
	garden_door_y = segment_break_y - 1

	build_doorway_slice(str, map_slice, doorframe_material, door_material, garden_door_x, garden_door_y, str.altitude+1, 's')


	#front left window (top)
	if not flat_roof:
		build_windows_slice(str, map_slice, window_material, segment_a[0], segment_a[3]-1, segment_a[2], segment_a[3]-1, int(round((segment_a[2]-segment_a[0])/2))+1, segment_a[3]-1, 'sn', 999, 999, True, str.altitude+str.height+1, 1)

	#back windows (currently there's a remaining beam, and the windows are split in separate sections going around it)
	build_windows_slice(str, map_slice, window_material, segment_a[0], segment_a[1], segment_a[2], segment_a[1], int(round((segment_a[2]-segment_a[0])/2))+1, segment_a[1], 'sn', 1, 2, True, str.altitude+2, 2)
	build_windows_slice(str, map_slice, window_material, segment_b[0], segment_a[1], segment_b[2], segment_a[1], door_x, segment_a[1], 'sn', 1, 2, True, str.altitude+2, 2)

	#left side windows
	build_windows_slice(str, map_slice, window_material, segment_a[0], segment_a[1], segment_a[0], segment_a[3]-1, segment_a[0], segment_a[3]-3, 'ew', 1, 2, True, str.altitude+2, 2)

	#right (short) side windows
	build_windows_slice(str, map_slice, window_material, segment_a[2]-1, segment_b[3]-1, segment_a[2]-1, segment_a[3]-1, segment_a[2]-1, segment_a[3]-3, 'ew', 1, 2, True, str.altitude+2, 2)

	#right end window (bottom and top)
	build_windows_slice(str, map_slice, window_material, segment_b[2]-1, segment_b[1], segment_b[2]-1, segment_b[3], segment_b[2]-1, int(round((segment_b[3]-segment_b[1])/2))+1, 'ew', 1, 2, True, str.altitude+2, 2)
	if not flat_roof:
		build_windows_slice(str, map_slice, window_material, segment_b[2]-1, segment_b[1], segment_b[2]-1, segment_b[3], segment_b[2]-1, int(round((segment_b[3]-segment_b[1])/2))+1, 'ew', 999, 999, True, str.altitude+str.height+1, 1)


	#torches: front
	map_slice.fill(segment_a[0], segment_a[3], str.altitude+3, segment_a[0]+1, segment_a[3]+1, str.altitude+4, (50,3))
	map_slice.fill(segment_a[2]-1, segment_a[3], str.altitude+3, segment_a[2], segment_a[3]+1, str.altitude+4, (50,3))

	#torches: back
	map_slice.fill(segment_a[0], segment_a[1]-1, str.altitude+3, segment_a[0]+1, segment_a[1], str.altitude+4, (50,4))
	map_slice.fill(segment_a[2]-1, segment_a[1]-1, str.altitude+3, segment_a[2], segment_a[1], str.altitude+4, (50,4))
	map_slice.fill(segment_b[2]-1, segment_a[1]-1, str.altitude+3, segment_b[2], segment_a[1], str.altitude+4, (50,4))

	#torches: left
	map_slice.fill(segment_a[0]-1, segment_a[1], str.altitude+3, segment_a[0], segment_a[1]+1, str.altitude+4, (50,2))
	map_slice.fill(segment_a[0]-1, segment_a[3]-1, str.altitude+3, segment_a[0], segment_a[3], str.altitude+4, (50,2))

	#torches: right
	map_slice.fill(segment_b[2], segment_b[1], str.altitude+3, segment_b[2]+1, segment_b[1]+1, str.altitude+4, (50,1))
	map_slice.fill(segment_b[2], segment_b[3]-1, str.altitude+3, segment_b[2]+1, segment_b[3], str.altitude+4, (50,1))

	#torches: side wall
	map_slice.fill(segment_a[2], segment_a[3]-1, str.altitude+3, segment_a[2]+1, segment_a[3], str.altitude+4, (50,1))

	#torches: entrance wall
	map_slice.fill(segment_b[2]-1, segment_b[3], str.altitude+3, segment_b[2], segment_b[3]+1, str.altitude+4, (50,3))


	#construction ends here

	map_slice.rotate(-rotation_angle)


def build_blacksmith_house(str, map, map_slice, wall_material, beam_material, doorframe_material, floor_material, roof_material, roof_beam_material, wall_under_roof_material, window_material, door_material, flat_roof):
	#either limit roof height, or ensure segments have the same (odd) width/height
	#shouldn't check direction, but structure alignment (direction may depend on door)?

	w = str.x2 - str.x1
	h = str.y2 - str.y1
	m = 1

	rotation_dc = {'s': 0, 'n': 180, 'e': 90, 'w': -90}
	rotation_angle = rotation_dc[str.direction]

	if rotation_angle == 90 or rotation_angle == -90:
		w, h = h, w

	map_slice.rotate(rotation_angle)

	#construction starts here

	roof_altitude = str.altitude+str.height+2
	roof_height_limit = 0

	segment_break_x = int(round(w * .5))
	segment_break_y = int(round(h * .5))
	# segment_break_y = int(round(h * .7))

	segment_a = (m, m, segment_break_x, h-m)
	segment_b = (segment_break_x-1, m, w-m, segment_break_y)

	#segment A (larger, left)
	build_segment_slice(str, map_slice, segment_a[0], segment_a[1], segment_a[2], segment_a[3], str.altitude, str.height+2, wall_material, beam_material, floor_material)

	#segment B (shorter, right)
	# build_segment_slice(str, map_slice, segment_b[0], segment_b[1], segment_b[2], segment_b[3], str.altitude, str.height, wall_material, beam_material, floor_material)

	#rooftop beams
	build_roof_beams_slice(str, map_slice, segment_a[0], segment_a[1], segment_a[2], segment_a[3], roof_altitude-1, 'snew', wall_material, beam_material, roof_beam_material)
	# build_roof_beams_slice(str, map_slice, segment_b[0], segment_b[1], segment_b[2], segment_b[3], roof_altitude-1, 'snew', wall_material, beam_material, roof_beam_material)

	#clear space between segments
	# map_slice.fill(segment_a[2]-1, segment_b[1]+1, str.altitude+1, segment_a[2], segment_b[3]-1, str.altitude+str.height, (0,0))


	#furnace section

	map_slice.fill(segment_a[2], segment_a[1], str.altitude, segment_b[2], segment_a[3]-1, str.altitude+2, (4,0))
	map_slice.fill(segment_a[2]+1, segment_a[3]-1, str.altitude+1, segment_b[2]-1, segment_a[3], str.altitude+2, (67,3))

	map_slice.fill(segment_b[2]-1, segment_a[1], str.altitude+2, segment_b[2], segment_a[3]-1, str.altitude+3, (139,0))
	map_slice.fill(segment_a[2], segment_a[1], str.altitude+2, segment_b[2]-1, segment_a[1]+1, str.altitude+3, (139,0))


	#furnace roof

	map_slice.fill(segment_a[2], segment_a[1], str.altitude+str.height-1, segment_b[2], segment_a[3]-1, str.altitude+str.height, (4,0))
	map_slice.fill(segment_a[2], segment_a[1], str.altitude+str.height, segment_b[2], segment_a[3]-1, str.altitude+str.height+1, (44,0))


	#furnace roof supports

	map_slice.fill(segment_b[2]-1, segment_a[3]-2, str.altitude+2, segment_b[2], segment_a[3]-1, str.altitude+str.height-1, (139,0))
	map_slice.fill(segment_a[2], segment_a[3]-2, str.altitude+2, segment_a[2]+1, segment_a[3]-1, str.altitude+str.height-1, (139,0))

	map_slice.fill(segment_b[2]-1, segment_a[1], str.altitude+2, segment_b[2], segment_a[1]+1, str.altitude+str.height-1, (139,0))
	map_slice.fill(segment_a[2], segment_a[1], str.altitude+2, segment_a[2]+1, segment_a[1]+1, str.altitude+str.height-1, (139,0))


	#furnace

	chimney_height = str.height+3

	map_slice.fill(segment_b[2]-5, segment_a[1]+2, str.altitude+1, segment_b[2]-2, segment_a[1]+5, str.altitude+chimney_height, (43,5))
	map_slice.fill(segment_b[2]-4, segment_a[1]+3, str.altitude+chimney_height-1, segment_b[2]-3, segment_a[1]+4, str.altitude+chimney_height, (44,5))

	map_slice.fill(segment_b[2]-5, segment_a[1]+5, str.altitude+1, segment_b[2]-2, segment_a[1]+6, str.altitude+5, (43,5))
	map_slice.fill(segment_b[2]-4, segment_a[1]+5, str.altitude+3, segment_b[2]-3, segment_a[1]+6, str.altitude+4, (61,3))

	#door

	door_x = segment_break_x - 1
	door_y = h - 5 - m

	build_doorway_slice(str, map_slice, doorframe_material, door_material, door_x, door_y, str.altitude+1, 'e')


	#rooftops

	# segments = [segment_a, segment_b]
	segments = [segment_a]

	walls = [
				(segment_a[0], segment_a[1], segment_a[0], segment_a[3]), # left wall (a)
				(segment_a[2]-1, segment_a[1], segment_a[2]-1, segment_a[3]), # right wall (a)
			]

	gables = [
				(segment_a[0], segment_a[1], segment_a[2], segment_a[1]), # top wall (a)
				(segment_a[0], segment_a[3]-1, segment_a[2], segment_a[3]-1), # bottom wall (a)
			]

	gen_roof_slice(map_slice, (-1, -1, w+1, h+1), segments, walls, gables, roof_altitude, wall_under_roof_material, roof_beam_material, roof_material, flat_roof)


	#front window (bottom and top)
	build_windows_slice(str, map_slice, window_material, segment_a[0], segment_a[3]-1, segment_a[2], segment_a[3]-1, int(round((segment_a[2]-segment_a[0])/2))+1, segment_a[3]-1, 'sn', 1, 2, True, str.altitude+2+1, 2)
	if not flat_roof:
		build_windows_slice(str, map_slice, window_material, segment_a[0], segment_a[3]-1, segment_a[2], segment_a[3]-1, int(round((segment_a[2]-segment_a[0])/2))+1, segment_a[3]-1, 'sn', 999, 999, True, str.altitude+str.height+2+1, 1)

	#back window (bottom and top)
	build_windows_slice(str, map_slice, window_material, segment_a[0], segment_a[1], segment_a[2], segment_a[1]+1, int(round((segment_a[2]-segment_a[0])/2))+1, segment_a[3]-1, 'sn', 1, 2, True, str.altitude+2+1, 2)
	if not flat_roof:
		build_windows_slice(str, map_slice, window_material, segment_a[0], segment_a[1], segment_a[2], segment_a[1]+1, int(round((segment_a[2]-segment_a[0])/2))+1, segment_a[3]-1, 'sn', 999, 999, True, str.altitude+str.height+2+1, 1)

	#left side windows
	build_windows_slice(str, map_slice, window_material, segment_a[0], segment_a[1], segment_a[0], segment_a[3]-1, segment_a[0], segment_a[3]-3, 'ew', 1, 2, True, str.altitude+2+1, 2)

	#raised floor
	map_slice.fill(segment_a[0]+1, segment_a[1]+1, str.altitude+1, segment_a[2]-1, segment_a[3]-1, str.altitude+2, floor_material)


	#torches: front
	map_slice.fill(segment_a[0], segment_a[3], str.altitude+4, segment_a[0]+1, segment_a[3]+1, str.altitude+5, (50,3))
	map_slice.fill(segment_a[2]-1, segment_a[3], str.altitude+4, segment_a[2], segment_a[3]+1, str.altitude+5, (50,3))

	#torches: back
	map_slice.fill(segment_a[0], segment_a[1]-1, str.altitude+4, segment_a[0]+1, segment_a[1], str.altitude+5, (50,4))
	map_slice.fill(segment_a[2]-1, segment_a[1]-1, str.altitude+4, segment_a[2], segment_a[1], str.altitude+5, (50,4))

	#torches: left
	map_slice.fill(segment_a[0]-1, segment_a[1], str.altitude+4, segment_a[0], segment_a[1]+1, str.altitude+5, (50,2))
	map_slice.fill(segment_a[0]-1, segment_a[3]-1, str.altitude+4, segment_a[0], segment_a[3], str.altitude+5, (50,2))

	#torches: side wall
	map_slice.fill(segment_a[2], segment_a[3]-1, str.altitude+4, segment_a[2]+1, segment_a[3], str.altitude+5, (50,1))


	#construction ends here

	map_slice.rotate(-rotation_angle)



# def gen_flat_roof_slice(str, map_slice, x1, y1, x2, y2, altitude, roof_material, roof_material_edge):
	# map_slice.fill(x1+1, y1+1, altitude, x2-1, y2-1, altitude+1, roof_material)

	# for x in xrange(x1, x2):
		# map_slice.fill(x, y1, altitude+1, x+1, y1+1, altitude+2, roof_material_edge)
		# map_slice.fill(x, y2-1, altitude+1, x+1, y2, altitude+2, roof_material_edge)

	# for y in xrange(y1, y2):
		# map_slice.fill(x1, y, altitude+1, x1+1, y+1, altitude+2, roof_material_edge)
		# map_slice.fill(x2-1, y, altitude+1, x2, y+1, altitude+2, roof_material_edge)


def gen_roof_slice(map_slice, area, segments, walls, gables, altitude, wall_under_roof_material, roof_beam_material, roof_material, flat_roof):
	#general roof-generating algorithm
	#how to let it cross box boundaries without errors?

	#add max height!

	area_w, area_h = area[2]-area[0], area[3]-area[1]

	# walls = walls + gables
	# gables = []

	points_inside = zeros((area_w, area_h), dtype=bool)
	for segment in segments:
		for x in xrange(segment[0], segment[2]):
			for y in xrange(segment[1], segment[3]):
				points_inside[x-area[0],y-area[1]] = True

	wall_points = zeros((area_w, area_h), dtype=bool)
	for wall in walls:
		if wall[0] == wall[2]:
			for y in xrange(wall[1], wall[3]):
				wall_points[wall[0]-area[0],y-area[1]] = True
		elif wall[1] == wall[3]:
			for x in xrange(wall[0], wall[2]):
				wall_points[x-area[0],wall[1]-area[1]] = True

	gable_points = zeros((area_w, area_h), dtype=bool)
	for gable in gables:
		if gable[0] == gable[2]:
			for y in xrange(gable[1], gable[3]):
				gable_points[gable[0]-area[0],y-area[1]] = True
		elif gable[1] == gable[3]:
			for x in xrange(gable[0], gable[2]):
				gable_points[x-area[0],gable[1]-area[1]] = True

	roof_heights = zeros((area_w, area_h)).astype(int)
	for x in xrange(0, area_w):
		for y in xrange(0, area_h):
			roof_heights[x, y] = 99999


	if flat_roof:
		slope_modifier = 0
	else:
		slope_modifier = 1


	if roof_material[0] == 179: #red sandstone
		roof_decoration_material = (182, 0)
		roof_decoration_material2 = (179, 0)
	elif roof_material[0] == 24: #sandstone
		roof_decoration_material = (44, 1)
		roof_decoration_material2 = (24, 0)
	elif roof_material == (43,5) or roof_material[0] == 98: #slab
		roof_decoration_material = (44, 5)
		roof_decoration_material2 = roof_material
	else: #else (stone?)
		roof_decoration_material = (44, 0)
		roof_decoration_material2 = roof_material


	for wall in walls:
		if wall[0] == wall[2]:
			for y in xrange(area[1], area[3]):
				cf_dist = 0
				if y < wall[1]:
					cf_dist = abs(wall[1] - y)
				elif y > wall[3]:
					cf_dist = abs(wall[3] - y)

				for x in xrange(wall[0], area[2]):
					dist = max(cf_dist, abs(x - wall[0]))
					roof_heights[x-area[0],y-area[1]] = min(dist * slope_modifier, roof_heights[x-area[0],y-area[1]])

				for x in xrange(wall[2], area[0], -1):
					dist = max(cf_dist, abs(x - wall[2]))
					roof_heights[x-area[0],y-area[1]] = min(dist * slope_modifier, roof_heights[x-area[0],y-area[1]])

		elif wall[1] == wall[3]:
			for x in xrange(area[0], area[2]):
				cf_dist = 0
				if x < wall[0]:
					cf_dist = abs(wall[0] - x)
				elif x > wall[2]:
					cf_dist = abs(wall[2] - x)

				for y in xrange(wall[1], area[3]):
					dist = max(cf_dist, abs(y - wall[1]))
					roof_heights[x-area[0],y-area[1]] = min(dist * slope_modifier, roof_heights[x-area[0],y-area[1]])

				for y in xrange(wall[3], area[1], -1):
					dist = max(cf_dist, abs(y - wall[3]))
					roof_heights[x-area[0],y-area[1]] = min(dist * slope_modifier, roof_heights[x-area[0],y-area[1]])


	if flat_roof:

		for x in xrange(area[0], area[2]):
			for y in xrange(area[1], area[3]):
				if wall_points[x-area[0], y-area[1]] or gable_points[x-area[0], y-area[1]]:
					map_slice.fill(x, y, altitude-1+roof_heights[x-area[0],y-area[1]], x+1, y+1, altitude-1+roof_heights[x-area[0],y-area[1]]+1, roof_material)
					map_slice.fill(x, y, altitude-1+roof_heights[x-area[0],y-area[1]]+1, x+1, y+1, altitude-1+roof_heights[x-area[0],y-area[1]]+2, roof_decoration_material)
				elif points_inside[x-area[0], y-area[1]]:
					map_slice.fill(x, y, altitude-1+roof_heights[x-area[0],y-area[1]], x+1, y+1, altitude-1+roof_heights[x-area[0],y-area[1]]+1, roof_material)


		all_walls = walls + gables

		for wall in all_walls:
			if wall[0] == wall[2]:
				x = wall[0]
				mid_y = int(round (float(max(wall[3], wall[1]) + min(wall[3], wall[1])) / 2 ))

				for y in range(wall[1], mid_y):
					if (wall[1] - y) % 2 == 0:
						map_slice.fill(x, y, altitude-1+roof_heights[x-area[0],y-area[1]]+1, x+1, y+1, altitude-1+roof_heights[x-area[0],y-area[1]]+2, roof_decoration_material2)

				for y in range(mid_y, wall[3]):
					if (wall[3] - y) % 2 == 1:
						map_slice.fill(x, y, altitude-1+roof_heights[x-area[0],y-area[1]]+1, x+1, y+1, altitude-1+roof_heights[x-area[0],y-area[1]]+2, roof_decoration_material2)

			elif wall[1] == wall[3]:
				y = wall[1]
				mid_x = int(round (float(max(wall[2], wall[0]) + min(wall[2], wall[0])) / 2 ))

				for x in range(wall[0], mid_x):
					if (wall[0] - x) % 2 == 0:
						map_slice.fill(x, y, altitude-1+roof_heights[x-area[0],y-area[1]]+1, x+1, y+1, altitude-1+roof_heights[x-area[0],y-area[1]]+2, roof_decoration_material2)

				for x in range(mid_x, wall[2]):
					if (wall[2] - x) % 2 == 1:
						map_slice.fill(x, y, altitude-1+roof_heights[x-area[0],y-area[1]]+1, x+1, y+1, altitude-1+roof_heights[x-area[0],y-area[1]]+2, roof_decoration_material2)


		wall_decoration_material = (179, 0)

		for gable in gables:
			if gable[0] == gable[2]:
				facing_modifier = 1 if points_inside[gable[0]-area[0]-1, int((gable[1]+gable[3])/2)-area[1]] else -1
				x = gable[0] + facing_modifier

				if facing_modifier == 1:
					wall_decoration_material = (143, 1)
				else:
					wall_decoration_material = (143, 2)

				for y in xrange(gable[1], gable[3]):
					height_ref = roof_heights[gable[0]-area[0], y-area[1]]

					map_slice.fill(x, y, altitude-1-1, x+1, y+1, altitude+9999, (0,0))
					map_slice.fill(x, y, altitude-1, x+1, y+1, altitude-1+1+height_ref, wall_decoration_material)
					map_slice.fill(x, y, altitude-1-1, x+1, y+1, altitude-1+height_ref, (0,0))

			elif gable[1] == gable[3]:
				facing_modifier = 1 if points_inside[int((gable[0]+gable[2])/2)-area[0], gable[1]-area[1]-1] else -1
				y = gable[1] + facing_modifier

				if facing_modifier == 1:
					wall_decoration_material = (143, 3)
				else:
					wall_decoration_material = (143, 4)

				for x in xrange(gable[0], gable[2]):
					height_ref = roof_heights[x-area[0], gable[1]-area[1]]

					# print "x: %i, y: %i, area[0]: %i, area[1]: %i, area[2]: %i, area[3]: %i" % (x, y, area[0], area[1], area[2], area[3])

					map_slice.fill(x, y, altitude-1-1, x+1, y+1, altitude+9999, (0,0))
					map_slice.fill(x, y, altitude-1, x+1, y+1, altitude-1+1+height_ref, wall_decoration_material)
					map_slice.fill(x, y, altitude-1-1, x+1, y+1, altitude-1+height_ref, (0,0))


	else:
		roof_depth = int(round(max(0, slope_modifier-1)))

		for x in xrange(area[0], area[2]):
			for y in xrange(area[1], area[3]):
				if wall_points[x-area[0], y-area[1]]:
					map_slice.fill(x, y, altitude, x+1, y+1, altitude+1, roof_material)

				elif points_inside[x-area[0], y-area[1]]:
					map_slice.fill(x, y, altitude+roof_heights[x-area[0],y-area[1]]-1-roof_depth, x+1, y+1, altitude+1+roof_heights[x-area[0],y-area[1]], roof_material)

					if gable_points[x-area[0], y-area[1]]:
						map_slice.fill(x, y, altitude, x+1, y+1, altitude+roof_heights[x-area[0],y-area[1]]-roof_depth, wall_under_roof_material)


		for x in xrange(area[0], area[2]):
			for y in xrange(area[1], area[3]):
				if not points_inside[x-area[0], y-area[1]]:
					xd, yd = x-area[0], y-area[1]

					roof_height = -99999
					nearest_points = [(xd-1,yd-1), (xd-1,yd), (xd-1,yd+1), (xd,yd-1), (xd,yd+1), (xd+1,yd-1), (xd+1,yd), (xd+1,yd+1)]

					for xp, yp in nearest_points:
						if xp > 0 and yp > 0 and xp < area_w and yp < area_h and (wall_points[xp, yp] or gable_points[xp, yp]):
							roof_height = max(roof_height, roof_heights[xp,yp]-1)

					map_slice.fill(x, y, altitude+roof_height-roof_depth, x+1, y+1, altitude+1+roof_height, roof_material)


		for gable in gables:
			if gable[0] == gable[2]:
				facing_modifier = 1 if points_inside[gable[0]-area[0]-1, int((gable[1]+gable[3])/2)-area[1]] else -1
				x = gable[0] + facing_modifier

				for y in xrange(gable[1], gable[3]):
					height_ref = roof_heights[gable[0]-area[0], y-area[1]]

					map_slice.fill(x, y, altitude-1-roof_depth, x+1, y+1, altitude+9999, (0,0))
					map_slice.fill(x, y, altitude-roof_depth, x+1, y+1, altitude+1+height_ref, roof_material)
					map_slice.fill(x, y, altitude-1-roof_depth, x+1, y+1, altitude+height_ref-roof_depth, (0,0))

			elif gable[1] == gable[3]:
				facing_modifier = 1 if points_inside[int((gable[0]+gable[2])/2)-area[0], gable[1]-area[1]-1] else -1
				y = gable[1] + facing_modifier

				for x in xrange(gable[0], gable[2]):
					height_ref = roof_heights[x-area[0], gable[1]-area[1]]

					# print "x: %i, y: %i, area[0]: %i, area[1]: %i, area[2]: %i, area[3]: %i" % (x, y, area[0], area[1], area[2], area[3])

					map_slice.fill(x, y, altitude-1-roof_depth, x+1, y+1, altitude+9999, (0,0))
					map_slice.fill(x, y, altitude-roof_depth, x+1, y+1, altitude+1+height_ref, roof_material)
					map_slice.fill(x, y, altitude-1-roof_depth, x+1, y+1, altitude+height_ref-roof_depth, (0,0))


def build_windows_slice(str, map_slice, window_material, x1, y1, x2, y2, xc, yc, direction, window_padding, space_from_center, add_central_window, altitude, window_height):
	# windows (assuming building w/h are odd)
	# prevent windows from being generated if there are blocks outside?

	windows = []

	if direction == 'sn':
		for i, x in enumerate(range(xc+space_from_center, x2-2)):
			if i % (1+window_padding) == 0:
				if (x > 0 and x < map_slice.w):
					windows.append((x, y2))

		for i, x in enumerate(range(xc-space_from_center, x1+1, -1)):
			if i % (1+window_padding) == 0:
				if (x > 0 and x < map_slice.w):
					windows.append((x, y2))

		if add_central_window:
			windows.append((xc, yc))


	elif direction == 'ew':
		for i, y in enumerate(range(yc+space_from_center, y2-2)):
			if i % (1+window_padding) == 0:
				if (y > 0 and y < map_slice.h):
					windows.append((x2, y))

		for i, y in enumerate(range(yc-space_from_center, y1+1, -1)):
			if i % (1+window_padding) == 0:
				if (y > 0 and y < map_slice.h):
					windows.append((x2, y))

		if add_central_window:
			windows.append((xc, yc))


	# for x, y in windows:
		# window_blocked = False
		# for x2 in xrange(max(0,x-1), min(map_slice.w,x+1)):
			# for y2 in xrange(max(0,y-1), min(map_slice.h,y+1)):
				# if map_slice.altitudes[x2,y2] > str.altitude:
					# window_blocked = True

		# if not window_blocked or window_height > str.altitude+3:
			# for y_step in xrange(str.altitude+1, str.altitude+str.height):
				# for i in xrange(0, window_height):
					# map_slice.fill_block(x, y, altitude+i, window_material)

	for x, y in windows:
		for y_step in xrange(str.altitude+1, str.altitude+str.height):
			for i in xrange(0, window_height):
				map_slice.fill_block(x, y, altitude+i, window_material)


def build_segment_slice(str, map_slice, x1, y1, x2, y2, altitude, height, wall_material, beam_material, floor_material):
	map_slice.fill(x1, y1, altitude, x2, y2, altitude+1, floor_material)
	map_slice.fill(x1, y1, altitude+1, x2, y2, altitude+height, wall_material)
	map_slice.fill(x1+1, y1+1, altitude+1, x2-1, y2-1, altitude+height, (0,0))

	for y_step in xrange(altitude+1, altitude+height):
		map_slice.fill_block(x1, y1, y_step, beam_material)
		map_slice.fill_block(x1, y2-1, y_step, beam_material)
		map_slice.fill_block(x2-1, y1, y_step, beam_material)
		map_slice.fill_block(x2-1, y2-1, y_step, beam_material)


def build_roof_beams_slice(str, map_slice, x1, y1, x2, y2, altitude, directions, wall_material, beam_material, roof_beam_material):
	# beam underneath rooftops on sides of house

	if beam_material != wall_material and roof_beam_material != beam_material:
		#only extend vertical beams under slopes

		map_slice.fill(x1, y1, altitude, x1+1, y1+1, altitude+2, beam_material)
		map_slice.fill(x1, y2-1, altitude, x1+1, y2, altitude+2, beam_material)
		map_slice.fill(x2-1, y1, altitude, x2, y1+1, altitude+2, beam_material)
		map_slice.fill(x2-1, y2-1, altitude, x2, y2, altitude+2, beam_material)

	else:
		#add horizontal beams (default situation)

		if directions == 's' or directions == 'n' or directions == 'sn' or directions == 'snew':
			for x in xrange(x1, x2):
				map_slice.fill(x, y1, altitude, x+1, y1+1, altitude+1, roof_beam_material)
				map_slice.fill(x, y2-1, altitude, x+1, y2, altitude+1, roof_beam_material)

		if directions == 'e' or directions == 'w' or directions == 'ew' or directions == 'snew':
			for y in xrange(y1, y2):
				map_slice.fill(x1, y, altitude, x1+1, y+1, altitude+1, roof_beam_material)
				map_slice.fill(x2-1, y, altitude, x2, y+1, altitude+1, roof_beam_material)


def build_blocks_slice(str, map_slice, x1, y1, x2, y2, altitude, height, material):
	map_slice.fill(x1, y1, altitude, x2, y2, altitude+height, material)


def build_doorway_slice(str, map_slice, beam_material, door_material, door_x, door_y, altitude, direction):
	# door opening

	map_slice.fill_block(door_x, door_y, altitude+1, (0,0))
	map_slice.fill_block(door_x, door_y, altitude+2, (0,0))

	# door frame and torches

	map_slice.fill_block(door_x, door_y, altitude+3, beam_material)

	if  direction == 'n':
		for y_step in xrange(altitude+1, altitude+4):
			map_slice.fill_block(door_x+1, door_y, y_step, beam_material)
			map_slice.fill_block(door_x-1, door_y, y_step, beam_material)

		map_slice.fill_block(door_x+1, door_y-1, altitude+2, (50,4))
		map_slice.fill_block(door_x-1, door_y-1, altitude+2, (50,4))

		map_slice.fill_block(door_x+1, door_y+1, altitude+2, (50,3))
		map_slice.fill_block(door_x-1, door_y+1, altitude+2, (50,3))

		map_slice.fill_block(door_x, door_y, altitude+1, (door_material[0],3))
		map_slice.fill_block(door_x, door_y, altitude+2, (door_material[0],11))

	elif direction == 's':
		for y_step in xrange(altitude+1, altitude+4):
			map_slice.fill_block(door_x+1, door_y, y_step, beam_material)
			map_slice.fill_block(door_x-1, door_y, y_step, beam_material)

		map_slice.fill_block(door_x+1, door_y+1, altitude+2, (50,3))
		map_slice.fill_block(door_x-1, door_y+1, altitude+2, (50,3))

		map_slice.fill_block(door_x+1, door_y-1, altitude+2, (50,4))
		map_slice.fill_block(door_x-1, door_y-1, altitude+2, (50,4))

		map_slice.fill_block(door_x, door_y, altitude+1, (door_material[0],1))
		map_slice.fill_block(door_x, door_y, altitude+2, (door_material[0],9))

	elif direction == 'e':
		for y_step in xrange(altitude+1, altitude+4):
			map_slice.fill_block(door_x, door_y-1, y_step, beam_material)
			map_slice.fill_block(door_x, door_y+1, y_step, beam_material)

		map_slice.fill_block(door_x+1, door_y-1, altitude+2, (50,1))
		map_slice.fill_block(door_x+1, door_y+1, altitude+2, (50,1))

		map_slice.fill_block(door_x-1, door_y-1, altitude+2, (50,2))
		map_slice.fill_block(door_x-1, door_y+1, altitude+2, (50,2))

		map_slice.fill_block(door_x, door_y, altitude+1, (door_material[0],0))
		map_slice.fill_block(door_x, door_y, altitude+2, (door_material[0],8))

	elif direction == 'w':
		for y_step in xrange(altitude+1, altitude+4):
			map_slice.fill_block(door_x, door_y-1, y_step, beam_material)
			map_slice.fill_block(door_x, door_y+1, y_step, beam_material)

		map_slice.fill_block(door_x-1, door_y-1, altitude+2, (50,2))
		map_slice.fill_block(door_x-1, door_y+1, altitude+2, (50,2))

		map_slice.fill_block(door_x+1, door_y-1, altitude+2, (50,1))
		map_slice.fill_block(door_x+1, door_y+1, altitude+2, (50,1))

		map_slice.fill_block(door_x, door_y, altitude+1, (door_material[0],2))
		map_slice.fill_block(door_x, door_y, altitude+2, (door_material[0],10))


def build_windows(str, map, window_material):
	# windows (assuming building w/h are odd)
	# prevent windows from being generated if there are blocks outside?

	windows = []
	window_padding = 1

	for i, x in enumerate(range(str.center_x+3, str.x2-2)):
		if i % (1+window_padding) == 0:
			if (x > 0 and x < map.w):
				windows.append((x, str.y2-1))
				windows.append((x, str.y1))

	for i, x in enumerate(range(str.center_x-3, str.x1+1, -1)):
		if i % (1+window_padding) == 0:
			if (x > 0 and x < map.w):
				windows.append((x, str.y2-1))
				windows.append((x, str.y1))

	for i, y in enumerate(range(str.center_y+3, str.y2-2)):
		if i % (1+window_padding) == 0:
			if (y > 0 and y < map.h):
				windows.append((str.x2-1,y))
				windows.append((str.x1,y))

	for i, y in enumerate(range(str.center_y-3, str.y1+1, -1)):
		if i % (1+window_padding) == 0:
			if (y > 0 and y < map.h):
				windows.append((str.x2-1,y))
				windows.append((str.x1,y))


	if str.direction != 'w':
		windows.append((str.x1, str.center_y))
	if str.direction != 'e':
		windows.append((str.x2-1, str.center_y))
	if str.direction != 'n':
		windows.append((str.center_x, str.y1))
	if str.direction != 's':
		windows.append((str.center_x, str.y2-1))

	for x, y in windows:
		window_blocked = False
		for x2 in xrange(max(0,x-1), min(map.w,x+1)):
			for y2 in xrange(max(0,y-1), min(map.h,y+1)):
				if map.altitudes[x2,y2] > str.altitude:
					window_blocked = True

		if not window_blocked:
			# for y_step in xrange(str.altitude+1, str.altitude+str.height):
				# map.fill_block(x, y, y_step, beam_material)

			map.fill_block(x, y, str.altitude+2, window_material)
			map.fill_block(x, y, str.altitude+3, window_material)


def build_support(str, map, beam_material):
	for x, y in [(str.x1+1,str.y1+1), (str.x1+1,str.y2-2), (str.x2-2,str.y1+1), (str.x2-2,str.y2-2)]:
		for y_step in xrange(map.altitudes[x,y], str.altitude):
			# map.fill_block(x, y, y_step, floor_material)
			map.fill_block(x, y, y_step, beam_material)


def get_materials_roof(source, direction, stairs):
	if stairs:
		if direction == 's' or direction == 'n':
			return (53, 2), (53, 7), (53, 3), (53, 6), (0, 0), (5, 0)
		else:
			return (53, 0), (53, 5), (53, 1), (53, 4), (0, 0), (5, 0)
	else:
		return source, source, source, source, source, source