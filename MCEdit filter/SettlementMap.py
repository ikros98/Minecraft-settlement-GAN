import time
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
from numpy import *


def get_block(level, x, y, z):
	return level.blockAt(x,y,z)


def set_block(level, (block, data), x, y, z):
	level.setBlockAt((int)(x),(int)(y),(int)(z), block)
	level.setBlockDataAt((int)(x),(int)(y),(int)(z), data)


def get_block_tuple(level, x, y, z):
	return (level.blockAt(x,y,z), level.blockDataAt(x,y,z))


def restricted_flood_fill(array, xsize, ysize, start_node, replace_value, max_steps):
	steps = 0
	source_value = array[start_node[0], start_node[1]]
	stack = set(((start_node[0], start_node[1]),))
	if replace_value == source_value:
		return steps
	while stack:
		x, y = stack.pop()
		if array[x, y] == source_value:
			array[x, y] = replace_value
			steps += 1
			if steps == max_steps:
				return steps
			else:
				if x > 0:
					stack.add((x - 1, y))
				if x < (xsize - 1):
					stack.add((x + 1, y))
				if y > 0:
					stack.add((x, y - 1))
				if y < (ysize - 1):
					stack.add((x, y + 1))
	return steps


class MapSlice:
	def __init__(self, w, altitude, h, offset, expansion):
		self.w, self.altitude, self.h = w, altitude, h
		self.offset, self.expansion = offset, expansion

		self.blocks = zeros((w+expansion[0], h+expansion[1])).astype(int)
		self.altitudes = zeros((w+expansion[0], h+expansion[1])).astype(int)
		self.level_copy = empty((w+expansion[0], altitude, h+expansion[1]), object)


	def set_block(self, block_data, x, y, z):
		self.level_copy[x+self.offset[0], y, z+self.offset[1]] = block_data


	def fill_block(self, x, y, z, material):
		if x >= -1*self.offset[0] and y >= -1*self.offset[1] and z >= 0 and x < self.w+self.expansion[0]-self.offset[0] and y < self.h+self.expansion[1]-self.offset[1] and z < self.altitude:
			self.set_block(material, x, z, y)
			if material[0] != 0:
				self.blocks[x+self.offset[0],y+self.offset[1]] = material[0]


	def fill(self, x1, y1, z1, x2, y2, z2, material):
		for x in range(max(-1*self.offset[0],x1), min(x2, self.w+self.expansion[0]-self.offset[0])):
			for y in range(max(-1*self.offset[1],y1), min(y2, self.h+self.expansion[1]-self.offset[1])):
				for z in range(max(0,z1), min(z2, self.altitude-1)):

					self.set_block(material, x, z, y)
					if material[0] != 0:
						self.blocks[x+self.offset[0],y+self.offset[1]] = material[0]


	def rotate(self, angle):
		margin_left = self.offset[0]
		margin_top = self.offset[1]
		margin_right = self.expansion[0] - self.offset[0]
		margin_bottom = self.expansion[1] - self.offset[1]

		if angle == 0:
			return True

		elif angle == 90 or angle == -270:
			times = 1
			self.w, self.h = self.h, self.w

			new_margin_left = margin_bottom
			new_margin_top = margin_left
			new_margin_right = margin_top
			new_margin_bottom = margin_right


		elif angle == 270 or angle == -90:
			times = 3
			self.w, self.h = self.h, self.w

			new_margin_left = margin_top
			new_margin_top = margin_right
			new_margin_right = margin_bottom
			new_margin_bottom = margin_left

		else:
			times = 2

			new_margin_left = margin_right
			new_margin_top = margin_bottom
			new_margin_right = margin_left
			new_margin_bottom = margin_top

		self.offset = (new_margin_left, new_margin_top)
		self.expansion = (new_margin_left+new_margin_right, new_margin_top+new_margin_bottom)

		self.level_copy = swapaxes(self.level_copy, -2,-1)

		self.blocks = rot90(self.blocks, k=times)
		self.altitudes = rot90(self.altitudes, k=times)
		self.level_copy = rot90(self.level_copy, k=times)

		#rotate torches, stairs, furnaces, buttons, doors
		#note: requires all 4 directions specified to work, otherwise may crash

		#s -> e -> n -> w (?)

		block_rotation_dc = {
								(50,3):(50,2), (50,2):(50,4), (50,4):(50,1), (50,1):(50,3),
								(67,3):(67,0), (67,0):(67,2), (67,2):(67,1), (67,1):(67,3),
								(61,3):(61,4), (61,4):(61,2), (61,2):(61,5), (61,5):(61,3),
								(143,3):(143,2), (143,2):(143,4), (143,4):(143,1), (143,1):(143,3),

								(64,1):(64,2), (64,2):(64,3), (64,3):(64,0), (64,0):(64,1),
								(64,9):(64,10), (64,10):(64,11), (64,11):(64,8), (64,8):(64,9),
								(193,1):(193,2), (193,2):(193,3), (193,3):(193,0), (193,0):(193,1),
								(193,9):(193,10), (193,10):(193,11), (193,11):(193,8), (193,8):(193,9),
								(194,1):(194,2), (194,2):(194,3), (194,3):(194,0), (194,0):(194,1),
								(194,9):(194,10), (194,10):(194,11), (194,11):(194,8), (194,8):(194,9),
								(195,1):(195,2), (195,2):(195,3), (195,3):(195,0), (195,0):(195,1),
								(195,9):(195,10), (195,10):(195,11), (195,11):(195,8), (195,8):(195,9),
								(196,1):(196,2), (196,2):(196,3), (196,3):(196,0), (196,0):(196,1),
								(196,9):(196,10), (196,10):(196,11), (196,11):(196,8), (196,8):(196,9),
								(197,1):(197,2), (197,2):(197,3), (197,3):(197,0), (197,0):(197,1),
								(197,9):(197,10), (197,10):(197,11), (197,11):(197,8), (197,8):(197,9),
							}

		block_rotation_dc_keys = set(block_rotation_dc.keys())

		for x in range(0, self.level_copy.shape[0]):
			for y in range(0, self.level_copy.shape[1]):
				for z in range(0, self.level_copy.shape[2]):
					if self.level_copy[x,y,z] != None and self.level_copy[x,y,z] in block_rotation_dc_keys:
						for i in xrange(0, times):

							self.level_copy[x,y,z] = block_rotation_dc[self.level_copy[x,y,z]]

		self.level_copy = swapaxes(self.level_copy, -2,-1)


class Map:
	def is_corner(self, x1y1_alt, x2y1_alt, x1y2_alt, x2y2_alt):
		if x1y1_alt != x2y1_alt and x1y1_alt != x1y2_alt:
			return True
		if x2y1_alt != x1y1_alt and x2y1_alt != x2y2_alt:
			return True
		if x1y2_alt != x1y1_alt and x1y2_alt != x2y2_alt:
			return True
		if x2y2_alt != x2y1_alt and x2y2_alt != x1y2_alt:
			return True
		return False


	def is_cliff(self, x1y1_alt, x2y1_alt, x1y2_alt, x2y2_alt):
		if abs(x1y1_alt - x2y1_alt) > 1 and abs(x1y2_alt - x2y2_alt) > 1:
			return True
		if abs(x1y1_alt - x1y2_alt) > 1 and abs(x2y1_alt - x2y2_alt) > 1:
			return True
		return False


	def is_2cliff(self, x1y1_alt, x2y1_alt, x1y2_alt, x2y2_alt):
		if abs(x1y1_alt - x2y1_alt) > 2 and abs(x1y2_alt - x2y2_alt) > 2:
			return True
		if abs(x1y1_alt - x1y2_alt) > 2 and abs(x2y1_alt - x2y2_alt) > 2:
			return True
		return False


	def is_corner_or_cliff(self, x1y1_alt, x2y1_alt, x1y2_alt, x2y2_alt):
		return self.is_corner(x1y1_alt, x2y1_alt, x1y2_alt, x2y2_alt) or self.is_cliff(x1y1_alt, x2y1_alt, x1y2_alt, x2y2_alt)


	def is_corner_or_2cliff(self, x1y1_alt, x2y1_alt, x1y2_alt, x2y2_alt):
		return self.is_corner(x1y1_alt, x2y1_alt, x1y2_alt, x2y2_alt) or self.is_2cliff(x1y1_alt, x2y1_alt, x1y2_alt, x2y2_alt)


	def __init__(self, level, box, impassable_blocks, wood_blocks, leaf_blocks, decorative_blocks, clear_decorations, clear_trees, roads_can_cross_corners, change_map, splice_map, roof_setting, start_time):
		self.level = level
		self.box = box

		self.x, self.y = box.minx, box.minz
		self.w, self.h = box.maxx-box.minx, box.maxz-box.minz

		self.impassable_blocks = impassable_blocks
		self.wood_blocks = wood_blocks
		self.leaf_blocks = leaf_blocks
		self.decorative_blocks = decorative_blocks

		#used for scoring (any score for elevation/distance below these values will be 0)
		self.max_building_altitude_difference = 16
		self.max_building_distance = 256

		self.change_map, self.splice_map = change_map, splice_map
		self.roof_setting = roof_setting

		self.setup(start_time, clear_decorations, clear_trees)

		self.tree_area, self.tree_probabilities = self.get_tree_data()
		self.sand_area, self.sand_probabilities = self.get_sand_data()
		self.tree_percentage, self.sand_percentage = self.tree_area * 100, self.sand_area * 100

		self.setup_occupied_positions()

		self.grid_corner_check = self.is_corner_or_2cliff

		self.altitudes_original = copy(self.altitudes)

		if change_map:
			#modify map - right now the actual filter is mostly arbitrary/hand-picked to effectively expand building space
			print("  Optimizing space for structure placement...")

			altitudes_original = copy(self.altitudes)
			altitudes_original_copy = copy(self.altitudes)

			for i in xrange(10):
				self.clear_corners(self.impassable_blocks, self.is_corner_or_cliff)
				self.clear_corners(self.impassable_blocks, self.is_corner_or_cliff)
				self.blur(self.impassable_blocks, self.is_corner_or_cliff)
			for i in xrange(10):
				self.clear_corners4_iter(self.impassable_blocks, self.is_cliff, 0)


			altitudes_new = copy(self.altitudes)
			self.altitudes = altitudes_original
			self.apply_lowest_altitudes(altitudes_new)

			altitudes_changed = copy(self.altitudes)
			self.altitudes = altitudes_original_copy

			self.altitudes = altitudes_changed

			print("  Done. (time elapsed: %i s)" % (time.time() - start_time))


		self.collect_positions()
		self.road_points = set([])

		self.roads_can_cross_corners = roads_can_cross_corners
		self.setup_grid(self.roads_can_cross_corners, self.impassable_blocks, self.grid_corner_check)


	def setup(self, start_time, clear_decorations, clear_trees):
		print("  Generating heightmap...")

		self.blocks = zeros((self.w, self.h)).astype(int)
		self.altitudes = zeros((self.w, self.h)).astype(int)
		self.trees = empty((self.w,self.h), object)
		self.leaves = zeros((self.w, self.h), dtype=bool)

		box = self.box
		level = self.level

		for x in xrange(box.minx, box.maxx):
			for z in xrange(box.minz, box.maxz):
				for y in xrange(box.maxy, box.miny, -1):

					block = get_block(level, x, y, z)
					if block != 0:
						if block in self.wood_blocks or block in self.leaf_blocks or (clear_decorations and block in self.decorative_blocks):
							block_data = get_block_tuple(level, x, y, z)
							if block_data != None and block_data[0] in self.wood_blocks:
								self.trees[x-self.x,z-self.y] = block_data
							if block_data != None and block_data[0] in self.leaf_blocks:
								self.leaves[x-self.x,z-self.y] = True

							if clear_trees:
								set_block(level, (0, 0), x, y, z)
								if get_block(level, x, y+1, z) in self.decorative_blocks:
									set_block(level, (0, 0), x, y+1, z)
						elif not block in self.decorative_blocks:
							self.altitudes[x-self.x,z-self.y] = int(y)
							self.blocks[x-self.x,z-self.y] = int(block)
							break

		print("  Done. (time elapsed: %i s)" % (time.time() - start_time))


	def setup_occupied_positions(self):
		self.occupied_by_building = set()
		self.occupied_by_farm = set()
		self.occupied_by_plaza = set()
		self.occupied_by_road = set()
		self.occupied_by_bridge = set()
		self.occupied_by_any = set()

		# self.unoccupied = set()
		# for x in xrange(0, self.w):
			# for y in xrange(0, self.h):
				# self.unoccupied.add((x,y))

		self.occupied_by_impassable = set()
		for x in xrange(0, self.w):
			for y in xrange(0, self.h):
				if self.blocks[x,y] in self.impassable_blocks:
					self.occupied_by_impassable.add((x,y))



	def is_corner(self, x1y1_alt, x2y1_alt, x1y2_alt, x2y2_alt):
		if x1y1_alt != x2y1_alt and x1y1_alt != x1y2_alt:
			return True
		elif x2y1_alt != x1y1_alt and x2y1_alt != x2y2_alt:
			return True
		elif x1y2_alt != x1y1_alt and x1y2_alt != x2y2_alt:
			return True
		elif x2y2_alt != x2y1_alt and x2y2_alt != x1y2_alt:
			return True
		return False


	def blur(self, impassable_blocks, corner_check):
		new_altitudes = copy(self.altitudes)

		for x in xrange(1, self.w-2):
			for y in xrange(1, self.h-2):
				neighbour_values = []
				for xd in (-1, 1):
					for yd in (-1,1):
						if (xd != 0 or yd != 0):

							neighbour_value = float(self.altitudes[x+xd,y+yd])
							neighbour_values.append(neighbour_value)

				average_value = sum(neighbour_values) / len(neighbour_values)
				rounded_value = int(round(average_value))

				if not corner_check(rounded_value, self.altitudes[x+1,y], self.altitudes[x,y+1], self.altitudes[x+1,y+1]):
					new_altitudes[x,y] = rounded_value

		self.altitudes = new_altitudes


	def clear_corners_random(self, impassable_blocks, corner_check):
		points = []
		for x in xrange(1, self.w-3):
			for y in xrange(1, self.h-3):
				points.append((x,y))

		shuffle(points)

		for x, y in points:
			x1, x2, y1, y2 = x, x+1, y, y+1

			corner = corner_check(self.altitudes[x1,y1], self.altitudes[x2,y1], self.altitudes[x1,y2], self.altitudes[x2,y2])

			if corner:

				neighbour_altitudes = set()
				for xd, yd in [(-1,-1), (-1,1), (1,-1), (1,1)]:
					neighbour_altitude = self.altitudes[x1+xd,y1+yd]
					if neighbour_altitude == self.altitudes[x1,y1] - 1:
						neighbour_altitudes.add(neighbour_altitude)
				for candidate_altitude in neighbour_altitudes:
					if not corner_check(candidate_altitude, self.altitudes[x2,y1], self.altitudes[x1,y2], self.altitudes[x2,y2]):
						self.altitudes[x1,y1] = candidate_altitude
						break

				neighbour_altitudes = set()
				for xd, yd in [(-1,-1), (-1,1), (1,-1), (1,1)]:
					neighbour_altitude = self.altitudes[x2+xd,y1+yd]
					if neighbour_altitude == self.altitudes[x2,y1] - 1:
						neighbour_altitudes.add(neighbour_altitude)
				for candidate_altitude in neighbour_altitudes:
					if not corner_check(self.altitudes[x1,y1], candidate_altitude, self.altitudes[x1,y2], self.altitudes[x2,y2]):
						self.altitudes[x2,y1] = candidate_altitude
						break

				neighbour_altitudes = set()
				for xd, yd in [(-1,-1), (-1,1), (1,-1), (1,1)]:
					neighbour_altitude = self.altitudes[x1+xd,y2+yd]
					if neighbour_altitude == self.altitudes[x1,y2] - 1:
						neighbour_altitudes.add(neighbour_altitude)
				for candidate_altitude in neighbour_altitudes:
					if not corner_check(self.altitudes[x1,y1], self.altitudes[x2,y1], candidate_altitude, self.altitudes[x2,y2]):
						self.altitudes[x1,y2] = candidate_altitude
						break

				neighbour_altitudes = set()
				for xd, yd in [(-1,-1), (-1,1), (1,-1), (1,1)]:
					neighbour_altitude = self.altitudes[x2+xd,y2+yd]
					if neighbour_altitude == self.altitudes[x2,y2] - 1:
						neighbour_altitudes.add(neighbour_altitude)
				for candidate_altitude in neighbour_altitudes:
					if not corner_check(self.altitudes[x1,y1], self.altitudes[x2,y1], self.altitudes[x1,y2], candidate_altitude):
						self.altitudes[x2,y2] = candidate_altitude
						break


	def clear_corners(self, impassable_blocks, corner_check):
		for x in xrange(1, self.w-3):
			for y in xrange(1, self.h-3):
				x1, x2, y1, y2 = x, x+1, y, y+1

				corner = corner_check(self.altitudes[x1,y1], self.altitudes[x2,y1], self.altitudes[x1,y2], self.altitudes[x2,y2])

				if corner:
					neighbour_altitudes = set()
					for xd, yd in [(-1,-1), (-1,1), (1,-1), (1,1)]:
						neighbour_altitude = self.altitudes[x1+xd,y1+yd]
						if neighbour_altitude == self.altitudes[x1,y1] - 1:
							neighbour_altitudes.add(neighbour_altitude)
					for candidate_altitude in neighbour_altitudes:
						if not corner_check(candidate_altitude, self.altitudes[x2,y1], self.altitudes[x1,y2], self.altitudes[x2,y2]):
							self.altitudes[x1,y1] = candidate_altitude
							break

					neighbour_altitudes = set()
					for xd, yd in [(-1,-1), (-1,1), (1,-1), (1,1)]:
						neighbour_altitude = self.altitudes[x2+xd,y1+yd]
						if neighbour_altitude == self.altitudes[x2,y1] - 1:
							neighbour_altitudes.add(neighbour_altitude)
					for candidate_altitude in neighbour_altitudes:
						if not corner_check(self.altitudes[x1,y1], candidate_altitude, self.altitudes[x1,y2], self.altitudes[x2,y2]):
							self.altitudes[x2,y1] = candidate_altitude
							break

					neighbour_altitudes = set()
					for xd, yd in [(-1,-1), (-1,1), (1,-1), (1,1)]:
						neighbour_altitude = self.altitudes[x1+xd,y2+yd]
						if neighbour_altitude == self.altitudes[x1,y2] - 1:
							neighbour_altitudes.add(neighbour_altitude)
					for candidate_altitude in neighbour_altitudes:
						if not corner_check(self.altitudes[x1,y1], self.altitudes[x2,y1], candidate_altitude, self.altitudes[x2,y2]):
							self.altitudes[x1,y2] = candidate_altitude
							break

					neighbour_altitudes = set()
					for xd, yd in [(-1,-1), (-1,1), (1,-1), (1,1)]:
						neighbour_altitude = self.altitudes[x2+xd,y2+yd]
						if neighbour_altitude == self.altitudes[x2,y2] - 1:
							neighbour_altitudes.add(neighbour_altitude)
					for candidate_altitude in neighbour_altitudes:
						if not corner_check(self.altitudes[x1,y1], self.altitudes[x2,y1], self.altitudes[x1,y2], candidate_altitude):
							self.altitudes[x2,y2] = candidate_altitude
							break


	def clear_corners4_iter(self, impassable_blocks, corner_check, required_reduction):
		new_altitudes = copy(self.altitudes)

		for x in xrange(1, self.w-3):
			for y in xrange(1, self.h-3):
				x1, x2, y1, y2 = x, x+1, y, y+1

				corner = corner_check(self.altitudes[x1,y1], self.altitudes[x2,y1], self.altitudes[x1,y2], self.altitudes[x2,y2])

				if corner:
					if not corner_check(self.altitudes[x1,y1]-1, self.altitudes[x2,y1]-1, self.altitudes[x1,y2], self.altitudes[x2,y2]):
						new_altitudes[x1,y1] = self.altitudes[x1,y1] - 1
						new_altitudes[x2,y1] = self.altitudes[x2,y1] - 1

					elif not corner_check(self.altitudes[x1,y1], self.altitudes[x2,y1], self.altitudes[x1,y2]-1, self.altitudes[x2,y2]-1):
						new_altitudes[x1,y2] = self.altitudes[x1,y2] - 1
						new_altitudes[x2,y2] = self.altitudes[x2,y2] - 1

					elif not corner_check(self.altitudes[x1,y1]-1, self.altitudes[x2,y1], self.altitudes[x1,y2]-1, self.altitudes[x2,y2]):
						new_altitudes[x1,y1] = self.altitudes[x1,y1] - 1
						new_altitudes[x1,y2] = self.altitudes[x1,y2] - 1

					elif not corner_check(self.altitudes[x1,y1], self.altitudes[x2,y1]-1, self.altitudes[x1,y2], self.altitudes[x2,y2]-1):
						new_altitudes[x2,y1] = self.altitudes[x2,y1] - 1
						new_altitudes[x2,y2] = self.altitudes[x2,y2] - 1


		changed_altitudes = copy(self.altitudes)

		for x in xrange(1, self.w-2):
			for y in xrange(1, self.h-2):

				x1, x2, y1, y2 = x, x+1, y, y+1

				old_x1y1 = self.altitudes[x1,y1]
				old_x2y1 = self.altitudes[x2,y1]
				old_x1y2 = self.altitudes[x1,y2]
				old_x2y2 = self.altitudes[x2,y2]

				x1y1 = new_altitudes[x1,y1]
				x2y1 = new_altitudes[x2,y1]
				x1y2 = new_altitudes[x1,y2]
				x2y2 = new_altitudes[x2,y2]

				if corner_check(old_x1y1, old_x2y1, old_x1y2, old_x2y2) and not corner_check(x1y1, x2y1, x1y2, x2y2):
					old_corners_around = 0
					new_corners_around = 0

					for xd in xrange(-1, 1):
						for yd in xrange(-1, 1):
							if (xd != 0 or yd != 0):

								if corner_check(self.altitudes[x1+xd,y1+yd], self.altitudes[x2+xd,y1+yd], self.altitudes[x1+xd,y2+yd], self.altitudes[x2+xd,y2+yd]):
									old_corners_around += 1

								if corner_check(new_altitudes[x1+xd,y1+yd], new_altitudes[x2+xd,y1+yd], new_altitudes[x1+xd,y2+yd], new_altitudes[x2+xd,y2+yd]):
									new_corners_around += 1


					if new_corners_around <= old_corners_around - required_reduction:
						changed_altitudes[x1,y1] = new_altitudes[x1,y1]
						changed_altitudes[x2,y1] = new_altitudes[x2,y1]
						changed_altitudes[x1,y2] = new_altitudes[x1,y2]
						changed_altitudes[x2,y2] = new_altitudes[x2,y2]


		self.altitudes = changed_altitudes


	def apply_lowest_altitudes(self, new_altitudes):
		changed_altitudes = copy(self.altitudes)
		for x in xrange(1, self.w-2):
			for y in xrange(1, self.h-2):
				changed_altitudes[x,y] = min(self.altitudes[x,y], new_altitudes[x,y])

		self.altitudes = changed_altitudes


	def get_slice(self, x1, y1, x2, y2, margin, copy_original):
		box = self.box
		level = self.level

		w = x2 - x1
		h = y2 - y1

		altitude = level.Height

		space_left = max(0, x1)
		space_top = max(0, y1)
		space_right = max(0, self.w - x2)
		space_bottom = max(0, self.h - y2)

		offset_x = min(margin, space_left)
		offset_y = min(margin, space_top)
		expansion_x = offset_x + min(margin, space_right)
		expansion_y = offset_y + min(margin, space_bottom)

		offset = (offset_x, offset_y)
		expansion = (expansion_x, expansion_y)

		slice = MapSlice(w, altitude, h, offset, expansion)

		if copy_original:
			for xd in xrange(-offset[0], w+expansion[0]-offset[0]):
				for zd in xrange(-offset[1], h+expansion[1]-offset[1]):

					slice.blocks[xd+offset[0],zd+offset[1]] = self.blocks[x1+xd, y1+zd]
					slice.altitudes[xd+offset[0],zd+offset[1]] = self.altitudes[x1+xd, y1+zd]

					# for y in xrange(box.maxy, box.miny, -1):
					for y in xrange(level.Height-1, box.miny, -1):
						slice.level_copy[xd+offset[0], y, zd+offset[1]] = get_block_tuple(level, self.x+x1+xd, y, self.y+y1+zd)

		return slice


	def paste_slice(self, slice, x1, y1, x2, y2, override):
		if x2-x1 != slice.w or y2-y1 != slice.h:
			print " !Trying to paste a slice of map with wrong dimensions!"
		else:
			box = self.box
			level = self.level

			for xd in xrange(-slice.offset[0], slice.w+slice.expansion[0]-slice.offset[0]):
				for zd in xrange(-slice.offset[1], slice.h+slice.expansion[1]-slice.offset[1]):

					slice_block = slice.blocks[xd+slice.offset[0],zd+slice.offset[1]]

					if override or slice_block != 0:
						self.blocks[x1+xd, y1+zd] = slice.blocks[xd+slice.offset[0],zd+slice.offset[1]]
						self.altitudes[x1+xd, y1+zd] = slice.altitudes[xd+slice.offset[0],zd+slice.offset[1]]

						# for y in xrange(box.maxy, box.miny, -1):
						for y in xrange(level.Height-1, box.miny, -1):
							slice_level_block = slice.level_copy[xd+slice.offset[0], y, zd+slice.offset[1]]
							if slice_level_block != None and (slice_level_block[0] != 50 or get_block(level, self.x+x1+xd, y, self.y+y1+zd) == 0): # do not place torches on occupied spots
								set_block(level, slice_level_block, self.x+x1+xd, y, self.y+y1+zd)


	def paste_slice_section(self, slice, x1, y1, x2, y2, override):
		# only used for splicing maps the same size, works differently than paste_slice
		box = self.box
		level = self.level

		for x in xrange(x1, x2):
			for z in xrange(y1, y2):

				slice_block = slice.blocks[x, z]

				if override or slice_block != 0:
					self.blocks[x, z] = slice.blocks[x, z]
					self.altitudes[x, z] = slice.altitudes[x, z]

					# for y in xrange(box.maxy, box.miny, -1):
					for y in xrange(level.Height-1, box.miny, -1):
						slice_level_block = slice.level_copy[x, y, z]
						if slice_level_block != None:
							set_block(level, slice_level_block, self.x+x, y, self.y+z)


	def get_tree_data(self):
		tree_frequency = {}
		tree_probabilities = {}
		for x in xrange(0, self.w):
			for y in xrange(0, self.h):
				value = self.trees[x,y]
				if value != None:
					if value not in tree_frequency.keys():
						tree_frequency[value] = 0
					tree_frequency[value] += 1
		tree_total = sum(tree_frequency.values())
		for k, v in tree_frequency.items():
			tree_probabilities[k] = float(v) / float(tree_total)
		tree_area = float(tree_total) / float(self.w * self.h)
		return tree_area, tree_probabilities


	def get_sand_data(self):
		sand_frequency = {}
		sand_probabilities = {}
		for x in xrange(0, self.w):
			for y in xrange(0, self.h):

				value = get_block_tuple(self.level, self.x+x, self.altitudes[x,y], self.y+y)
				if value in ((12,0), (12,1), (24,0), (179,0)):
					if value not in sand_frequency.keys():
						sand_frequency[value] = 0
					sand_frequency[value] += 1

				# print " %s versus %s" % (str(value), str(self.blocks[x,y]))

		sand_total = sum(sand_frequency.values())
		for k, v in sand_frequency.items():
			sand_probabilities[k] = float(v) / float(sand_total)
		sand_area = float(sand_total) / float(self.w * self.h)
		return sand_area, sand_probabilities


	def get_local_sand_data(self, x1, y1, x2, y2, cat, subcat):
		sand_frequency = {}
		sand_probabilities = {}
		for x in xrange(x1, x2):
			for y in xrange(y1, y2):

				approximate_value = self.blocks[x,y]
				if approximate_value in (12, 24, 179):
					for y_step in range(self.altitudes[x,y], self.box.miny, -1):
						value = get_block_tuple(self.level, self.x+x, y_step, self.y+y)
						if value not in self.decorative_blocks and value not in self.leaf_blocks and value != (0,0):
							if value in ((12,0), (12,1), (24,0), (179,0)):
								if value not in sand_frequency.keys():
									sand_frequency[value] = 0
								sand_frequency[value] += 1
							break

				# print "%s (%s): %s vs %s" % (cat, subcat, str(value), str(self.blocks[x,y]))

		sand_total = sum(sand_frequency.values())
		for k, v in sand_frequency.items():
			sand_probabilities[k] = float(v) / float(sand_total)
		w, h = (x2-x1), (y2-y1)
		sand_area = float(sand_total) / float(w * h)
		return sand_area, sand_probabilities



	def clear_tree(self, x, y, nearest_tree_table, altitudes):
		if x >= 0 and x < self.w and y >= 0 and y < self.h and self.trees[x,y] != None:

			# distance = 4
			distance = 6

			for x2 in xrange(max(0,x-distance), min(self.w,x+distance+1)):
				for y2 in xrange(max(0,y-distance), min(self.h,y+distance+1)):

					if self.leaves[x2,y2] and nearest_tree_table[x2,y2] == (x, y):

						for y_step in range(altitudes[x2,y2]+1, self.box.maxy):
							block = get_block(self.level, self.x+x2, y_step, self.y+y2)

							if (block in self.wood_blocks or block in self.leaf_blocks):
								set_block(self.level, (0,0), self.x+x2, y_step, self.y+y2)
								if get_block(self.level, self.x+x2, y_step+1, self.y+y2) in self.decorative_blocks:
									set_block(self.level, (0, 0), self.x+x2, y_step+1, self.y+y2)

			self.trees[x,y] = None

			self.clear_tree(x-1, y, nearest_tree_table, altitudes)
			self.clear_tree(x+1, y, nearest_tree_table, altitudes)
			self.clear_tree(x, y-1, nearest_tree_table, altitudes)
			self.clear_tree(x, y+1, nearest_tree_table, altitudes)
			self.clear_tree(x-1, y-1, nearest_tree_table, altitudes)
			self.clear_tree(x-1, y+1, nearest_tree_table, altitudes)
			self.clear_tree(x+1, y-1, nearest_tree_table, altitudes)
			self.clear_tree(x+1, y+1, nearest_tree_table, altitudes)


	def leaf_removal_cleanup(self, altitudes):
		# since the tree-clearing function isn't perfect (there's no way to determine which leaf belongs to which tree), this should clear up most of the remaining floating leaves

		# use only if nearby trees have been removed?

		for x in xrange(0, self.w):
			for y in xrange(0, self.h):
				if self.leaves[x,y] != None or self.trees[x,y] != None:

					for y_step in range(altitudes[x,y]+1, self.box.maxy):

						block = get_block(self.level, self.x+x, y_step, self.y+y)

						if (block in self.wood_blocks or block in self.leaf_blocks):
							# print "leaf/tree block found!"

							# single_leaf_block = False

							# air_below = False
							# air_above = False

							log_nearby = False # within 6 tiles horizontally, 4 tiles vertically

							for_loop_running = True

							for xd in xrange(-6, 6):
								for yd in xrange(-6, 6):
									if x+xd > 0 and y+yd > 0 and x+xd < self.w and y+yd < self.h:
										for y_step_d in xrange(0, 3):
											try:
												block_d = get_block(self.level, self.x+x+xd, y_step+y_step_d, self.y+y+yd)
												if block_d in self.wood_blocks:
													log_nearby = True
													for_loop_running = False
													break

												block_d = get_block(self.level, self.x+x+xd, y_step-y_step_d, self.y+y+yd)
												if block_d in self.wood_blocks:
													log_nearby = True
													for_loop_running = False
													break

											except:
												print "(bug) y_step_d reaches out of the box", y_step, y_step_d
												pass

									if not for_loop_running:
										break
								if not for_loop_running:
									break

							if not log_nearby:
								set_block(self.level, (0,0), self.x+x, y_step, self.y+y)


						elif block in self.decorative_blocks:
							#clear up floating decorative blocks left after clearing trees (e.g. cocoa plants in jungle biomes)
							#(needs to make sure blocks away from settlement don't get cleared... is a check for floating in air enough?)

							block_below = 0
							if y_step > altitudes[x,y]:
								block_below = get_block(self.level, self.x+x, y_step-1, self.y+y)


							block_above = 0
							if y_step < self.box.maxy-1:
								block_above = get_block(self.level, self.x+x, y_step+1, self.y+y)

							if block_below == 0 and block_above == 0:
								set_block(self.level, (0,0), self.x+x, y_step, self.y+y)


	def collect_positions(self):
		self.positions = set()
		for x in xrange(self.w):
			for y in xrange(self.h):
				# self.positions.add((x,y))
				if not self.blocks[x,y] in self.impassable_blocks:
					self.positions.add((x,y))


	def setup_grid(self, roads_can_cross_corners, impassable_blocks, corner_check):
		grid = zeros((self.w, self.h)).astype(int)
		corners = zeros((self.w, self.h)).astype(int)

		# prevent roads from crossing water, lava and ice
		for x in xrange(1, self.w-1):
			for y in xrange(1, self.h-1):
				if self.blocks[x,y] in impassable_blocks:
					grid[x,y] = 1
					grid[x-1,y] = 1
					grid[x+1,y] = 1
					grid[x,y-1] = 1
					grid[x,y+1] = 1
					grid[x-1,y-1] = 1
					grid[x+1,y-1] = 1
					grid[x-1,y+1] = 1
					grid[x+1,y+1] = 1

		# prevent roads from climbing up slopes at corners
		for x in xrange(0, self.w-2):
			for y in xrange(0, self.h-2):
				x1, x2, y1, y2 = x, x+1, y, y+1

				corner = corner_check(self.altitudes[x1,y1], self.altitudes[x2,y1], self.altitudes[x1,y2], self.altitudes[x2,y2])

				if corner:
					corners[x1,y1] = 1
					corners[x2,y1] = 1
					corners[x1,y2] = 1
					corners[x2,y2] = 1
					if not roads_can_cross_corners:
						grid[x1,y1] = 1
						grid[x2,y1] = 1
						grid[x1,y2] = 1
						grid[x2,y2] = 1

		self.grid = grid
		self.corners = corners


	def update_grid_for_structure(self, structure, road_distance):
		if structure.cat == "bridge":
			if structure.direction in "sn":
				for x in xrange(max(0,structure.x1), min(self.w,structure.x2)):
					for y in xrange(max(0,structure.y1-road_distance), min(self.h,structure.y2+road_distance)):
						self.grid[x,y] = 1
			else:
				for x in xrange(max(0,structure.x1-road_distance), min(self.w,structure.x2+road_distance)):
					for y in xrange(max(0,structure.y1), min(self.h,structure.y2)):
						self.grid[x,y] = 1
		else:
			for x in xrange(max(0,structure.x1-road_distance), min(self.w,structure.x2+road_distance)):
				for y in xrange(max(0,structure.y1-road_distance), min(self.h,structure.y2+road_distance)):
					self.grid[x,y] = 1

		if structure.cat == "bridge":
			if structure.direction in "sn":
				self.grid[structure.center_x,structure.y1-1] = 0
				# self.grid[structure.center_x,structure.y2+1] = 0
				self.grid[structure.center_x,structure.y2] = 0
			else:
				self.grid[structure.x1-1,structure.center_y] = 0
				# self.grid[structure.x2+1,structure.center_y] = 0
				self.grid[structure.x2,structure.center_y] = 0
		else:
			entry_path = structure.get_entry_path_default()
			for x, y in entry_path:
				self.grid[x,y] = 0


	def update_entire_grid(self, structures, road_distance):
		self.setup_grid(self.roads_can_cross_corners, self.impassable_blocks)
		for structure in structures:
			self.update_grid_for_structure(structure, road_distance)


	def fits_inside(self, x1, y1, x2, y2):
		if x1 >= 0 and x2 <= self.w and y1 >= 0 and y2 <= self.h:
			return True
		return False


	def get_distance(self, x1, y1, x2, y2):
		return sqrt( (x2 - x1)**2 + (y2 - y1)**2 )


	def box_collision(self, a_x1, a_y1, a_x2, a_y2, b_x1, b_y1, b_x2, b_y2):
		return not (b_x1 > a_x2 or b_x2 < a_x1 or b_y1 > a_y2 or b_y2 < a_y1)


	def box_collision_ignore_edges(self, a_x1, a_y1, a_x2, a_y2, b_x1, b_y1, b_x2, b_y2):
		return not (b_x1 >= a_x2 or b_x2 <= a_x1 or b_y1 >= a_y2 or b_y2 <= a_y1)


	def box_distance(self, x1, y1, x1b, y1b, x2, y2, x2b, y2b):
		left = x2b < x1
		right = x1b < x2
		bottom = y2b < y1
		top = y1b < y2
		if top and left:
			return self.get_distance(x1, y1b, x2b, y2)
		elif left and bottom:
			return self.get_distance(x1, y1, x2b, y2b)
		elif bottom and right:
			return self.get_distance(x1b, y1, x2, y2b)
		elif right and top:
			return self.get_distance(x1b, y1b, x2, y2)
		elif left:
			return x1 - x2b
		elif right:
			return x2 - x1b
		elif bottom:
			return y1 - y2b
		elif top:
			return y2 - y1b
		else:
			return 0


	def get_altitudes(self, x1, y1, x2, y2):
		altitudes = set()
		for x in range(x1, x2):
			for y in range(y1, y2):
				altitudes.add(self.altitudes[x,y])
		return min(altitudes), max(altitudes)


	def get_edge_altitudes(self, x1, y1, x2, y2, margin):
		# fails if x1=x2 or y1=y2
		altitudes = set()
		for x in range(x1, x2):
			for y in range(y1, y1+margin):
				altitudes.add(self.altitudes[x,y])
			for y in range(y2-margin, y2):
				altitudes.add(self.altitudes[x,y])
		for y in range(y1, y2):
			for x in range(x1, x1+margin):
				altitudes.add(self.altitudes[x,y])
			for x in range(x2-margin, x2):
				altitudes.add(self.altitudes[x,y])

		return min(altitudes), max(altitudes)


	def altitude_difference(self, x1, y1, x2, y2):
		altitude_lowest, altitude_highest = self.get_altitudes(x1, y1, x2, y2)
		return altitude_highest - altitude_lowest


	def collides(self, x1, y1, x2, y2, collider_blocks):
		for x in range(x1, x2):
			for y in range(y1, y2):
				if self.blocks[x,y] in collider_blocks:
					return True
		return False


	def occupied(self, x1, y1, x2, y2, occupied_positions):
		for x in range(x1, x2):
			for y in range(y1, y2):
				if (x,y) in occupied_positions:
					return True
		return False


	def clear_space(self, x, y, z):
		for y_step in range(z, self.box.maxy):
			set_block(self.level, (0,0), self.x+x, y_step, self.y+y)


	def clear_space_range(self, x, y, z1, z2):
		for y_step in range(z1, z2):
			set_block(self.level, (0,0), self.x+x, y_step, self.y+y)


	def clear_space_relative_to_surface(self, x, y, z):
		for y_step in range(self.altitudes[x,y]+z, self.box.maxy):
			set_block(self.level, (0,0), self.x+x, y_step, self.y+y)


	# def drop_blocks_to_level(self, x, y, z):
		# # if z >= self.altitudes[x,y]:
		# if z >= self.altitudes_original[x,y]:
			# return None
		# else:
			# top_blocks = []
			# for y_step in range(self.altitudes[x,y], self.box.maxy):
			# # for y_step in range(self.altitudes_original[x,y], self.box.maxy):
				# block = get_block_tuple(self.level, self.x+x, y_step, self.y+y)
				# if block != (0, 0):
					# top_blocks.append(block)
				# else:
					# break

			# self.clear_space(x, y, z)

			# for y_step in range(z, self.box.maxy):
				# if top_blocks:
					# block = top_blocks.pop(0)
					# set_block(self.level, block, self.x+x, y_step, self.y+y)
				# else:
					# break


	# def drop_blocks_to_level(self, x, y, z):
		# if z >= self.altitudes_original[x,y]:
			# return None
		# else:
			# top_blocks = []
			# for y_step in range(self.altitudes_original[x,y], self.box.maxy):
				# block = get_block_tuple(self.level, self.x+x, y_step, self.y+y)
				# top_blocks.append(block)

			# for y_step in range(z, self.box.maxy):
				# if top_blocks:
					# block = top_blocks.pop(0)
					# set_block(self.level, block, self.x+x, y_step, self.y+y)
				# else:
					# break


	def drop_blocks_to_level(self, x, y, z):
		if z >= self.altitudes_original[x,y]:
			return None
		else:
			top_blocks = []
			break_point = z

			for y_step in range(self.altitudes_original[x,y], self.box.maxy):
				block = get_block_tuple(self.level, self.x+x, y_step, self.y+y)

				# may cause leaves to 'slide down' trees

				if block != (0, 0):
				# if block != (0, 0) and not block in self.leaf_blocks: 
					top_blocks.append(block)
				else:
					break_point = y_step
					break

			for y_step in range(z, self.box.maxy):
				if top_blocks:
					block = top_blocks.pop(0)
					set_block(self.level, block, self.x+x, y_step, self.y+y)
				else:
					# self.clear_space(x, y, min(self.box.maxy, y_step))
					self.clear_space_range(x, y, y_step, break_point)
					break


	def place_fences(self, blocks_updated, reserved_materials, impassable_blocks, materials, fence_conversion, wood_source):

		# brace yourselves: horrible, horrible code ahead

		map = self
		fence_map = zeros((map.w, map.h)).astype(int)

		if wood_source in fence_conversion.keys():
			fence_block = fence_conversion[wood_source]
		else:
			fence_block = (85,0)

		for x in xrange(1, map.w-1):
			for y in xrange(1, map.h-1):
				if blocks_updated[x,y] not in reserved_materials and not blocks_updated[x,y] in impassable_blocks:
				# if blocks_updated[x,y] not in reserved_materials and not blocks_updated[x,y] in impassable_blocks and not (x,y) in map.occupied_by_any:

					near_road = False
					road_altitude = -999
					for position_d in [(-2,0,'e'), (0,-2,'w'), (0,2,'n'), (2,0,'s'), (-2,-2,'s'), (-2,2,'e'), (2,2,'n'), (2,-2,'w')]:
						if x+position_d[0] > 0 and y+position_d[1] > 0 and x+position_d[0] < map.w and y+position_d[1] < map.h and blocks_updated[x+position_d[0], y+position_d[1]] == materials['road'][0]:
							near_road = True
							road_altitude = map.altitudes[x+position_d[0], y+position_d[1]]
							fence_direction = position_d[2]
							break

					if near_road and road_altitude <= map.altitudes[x,y]:
						clear_space = True
						for x2 in xrange(max(0,x-1), min(map.w,x+2)):
							for y2 in xrange(max(0,y-1), min(map.h,y+2)):
								# if blocks_updated[x2,y2] == materials['road'][0] or blocks_updated[x2,y2] in reserved_materials:
								if blocks_updated[x2,y2] == materials['road'][0] or blocks_updated[x2,y2] in reserved_materials or (x2,y2) in map.occupied_by_building or (x2,y2) in map.occupied_by_farm:
								# if blocks_updated[x2,y2] == materials['road'][0] or blocks_updated[x2,y2] in reserved_materials or (x2,y2) in map.occupied_by_building or (x2,y2) in map.occupied_by_any:
									clear_space = False
									break
							if not clear_space:
								break

						if clear_space:
							faces_away = True
							x_d, y_d = 0, 0

							if fence_direction == 'n':
								increment_x, increment_y = 0, -1
							elif fence_direction == 's':
								increment_x, increment_y = 0, 1
							elif fence_direction == 'e':
								increment_x, increment_y = 1, 0
							elif fence_direction == 'w':
								increment_x, increment_y = -1, 0

							for i in xrange(10):
								x_d += increment_x
								y_d += increment_y

								if x+x_d <= 0 or x+x_d >= map.w or y+y_d <= 0 or y+y_d >= map.h:
									faces_away = True
									break
								elif map.altitudes[x+x_d,y+y_d] <= map.altitudes[x,y] - 2:
									faces_away = True
									break
								elif map.blocks[x+x_d,y+y_d] in reserved_materials or map.blocks[x+x_d,y+y_d] == materials['road'][0]:
									faces_away = False
									break

							if faces_away:
								fence_map[x,y] = map.altitudes[x,y]


		for x in xrange(1, map.w-1):
			for y in xrange(1, map.h-1):
				if fence_map[x,y] != 0:
					alt = fence_map[x,y]

					# add a fence if the segment forms a line or a bend with at least 3 other segments of same height
					# double-check and fix fence materials?
					# make sure fences don't align with buildings
					# fences can currently cross into buildings (e.g. crossing temple columns)

					# idea: do not generate within building areas, unless connecting another fence segment to building?

					required_neighbours = [
							((-1,0), (-2,0)),
							((1,0), (2,0)),
							((0,1), (0,2)),
							((0,-1), (0,1)),

							((-1,0), (1,0)),
							((0,-1), (0,-2)),

							((-1,0), (0,-1)),
							((-1,0), (0,1)),
							((1,0), (0,-1)),
							((1,0), (0,1)),
						]

					for position_a, position_b in required_neighbours:
						if x+min(position_a[0],position_b[0]) > 0 and x+max(position_a[0],position_b[0]) < map.w and y+min(position_a[1],position_b[1]) > 0 and y+max(position_a[1],position_b[1]) < map.h:
							if fence_map[x+position_a[0],y+position_a[1]] == alt and fence_map[x+position_b[0],y+position_b[1]] == alt:
								map.fill_block(x, y, map.altitudes[x,y]+1, fence_block)
								map.fill_block(x+position_a[0], y+position_a[1], map.altitudes[x,y]+1, fence_block)
								map.fill_block(x+position_b[0], y+position_b[1], map.altitudes[x,y]+1, fence_block)


	def complete_path(self, points, road_material):
		for x, y in points:
			self.occupied_by_road.add((x,y))
			self.occupied_by_any.add((x,y))


	def fill_block_relative_to_surface(self, x, y, z, material):
		set_block(self.level, material, self.x+x, self.altitudes[x,y]+z, self.y+y)
		self.blocks[x,y] = material[0] # only if it's the same or higher than altitude?
		# if material[0] == 0:
			# self.positions.discard((x,y))


	def fill_block(self, x, y, z, material):
		set_block(self.level, material, self.x+x, z, self.y+y)
		if material[0] != 0:
			self.blocks[x,y] = material[0]
			# self.positions.discard((x,y))


	def fill(self, x1, y1, z1, x2, y2, z2, material):
		for x in range(x1, x2):
			for y in range(y1, y2):
				for z in range(z1, z2):
					set_block(self.level, material, self.x+x, z, self.y+y)
					if material[0] != 0:
						self.blocks[x,y] = material[0]
						# self.positions.discard((x,y))


	def mark_as_occupied(self, x1, y1, x2, y2, target_set):
		for x in range(x1, x2):
			for y in range(y1, y2):

				if (x,y) not in target_set:
					target_set.add((x,y))
					self.occupied_by_any.add((x,y))
					# self.unoccupied.remove((x,y))
					self.positions.discard((x,y))


	def map_settlement_space(self, structures, road_material):
		self.settlement_space = set([])

		rectangular_gradient = True

		margin = 4
		outer_margin = 8

		self.impact_map = zeros((self.w, self.h)).astype(float)
		self.target_altitudes = copy(self.altitudes_original)

		for structure in structures:
			for x in xrange(max(0, structure.x1-margin), min(self.w, structure.x2+margin)):
				for y in xrange(max(0, structure.y1-margin), min(self.h, structure.y2+margin)):
					self.settlement_space.add((x,y))

			for x in xrange(max(0, structure.x1-outer_margin), min(self.w, structure.x2+outer_margin)):
				for y in xrange(max(0, structure.y1-outer_margin), min(self.h, structure.y2+outer_margin)):

					if (x >= structure.x1-margin and x <= structure.x2+margin) and (y >= structure.y1-margin and y <= structure.y2+margin):
						self.impact_map[x,y] = max(self.impact_map[x,y], 1)
						self.target_altitudes[x,y] = min(self.target_altitudes[x,y], structure.altitude)

					else:
						if x < structure.x1-margin:
							distance_from_edge_x = abs(structure.x1-margin - x)
						elif x > structure.x2+margin:
							distance_from_edge_x = abs(structure.x2+margin - x)
						else:
							distance_from_edge_x = 0

						if y < structure.y1-margin:
							distance_from_edge_y = abs(structure.y1-margin - y)
						elif y > structure.y2+margin:
							distance_from_edge_y = abs(structure.y2+margin - y)
						else:
							distance_from_edge_y = 0


						if rectangular_gradient:
							distance_from_edge = max(distance_from_edge_x, distance_from_edge_y)
						else:
							distance_from_edge = (distance_from_edge_x + distance_from_edge_y)/2

						distance_gradient = float(distance_from_edge) / float(outer_margin - margin)
						impact_value = 1 - distance_gradient


						self.impact_map[x,y] = max(self.impact_map[x,y], impact_value)
						self.target_altitudes[x,y] = min(self.target_altitudes[x,y], structure.altitude)


		for map_x, map_y in self.occupied_by_road:

			for x in xrange(max(0, map_x-margin), min(self.w, map_x+1+margin)):
				for y in xrange(max(0, map_y-margin), min(self.h,map_y+1+margin)):
					self.settlement_space.add((x,y))


			for x in xrange(max(0, map_x-outer_margin), min(self.w, map_x+1+outer_margin)):
				for y in xrange(max(0, map_y-outer_margin), min(self.h, map_y+1+outer_margin)):

					if (x >= map_x-margin and x <= map_x+1+margin) and (y >= map_y-margin and y <= map_y+1+margin):
						self.impact_map[x,y] = max(self.impact_map[x,y], 1)
						self.target_altitudes[x,y] = min(self.target_altitudes[x,y], self.altitudes[map_x,map_y])

					else:
						if x < map_x-margin:
							distance_from_edge_x = abs(map_x-margin - x)
						elif x > map_x+1+margin:
							distance_from_edge_x = abs(map_x+1+margin - x)
						else:
							distance_from_edge_x = 0

						if y < map_y-margin:
							distance_from_edge_y = abs(map_y-margin - y)
						elif y > map_y+1+margin:
							distance_from_edge_y = abs(map_y+1+margin - y)
						else:
							distance_from_edge_y = 0

						if rectangular_gradient:
							distance_from_edge = max(distance_from_edge_x, distance_from_edge_y)
						else:
							distance_from_edge = (distance_from_edge_x + distance_from_edge_y)/2

						distance_gradient = float(distance_from_edge) / float(outer_margin - margin)
						impact_value = 1 - distance_gradient

						self.impact_map[x,y] = max(self.impact_map[x,y], impact_value)
						self.target_altitudes[x,y] = min(self.target_altitudes[x,y], self.altitudes[map_x,map_y])


	def splice_map_altitudes(self):
		altitudes_final = copy(self.altitudes)

		for x in xrange(0, self.w):
			for y in xrange(0, self.h):

				if (x,y) not in self.settlement_space:
					reference_altitude = self.altitudes_original[x,y]
					target_altitude = self.altitudes[x,y]

					if self.impact_map[x,y] > 0:
						new_altitude = (reference_altitude * (1 - self.impact_map[x,y])) + (target_altitude * self.impact_map[x,y])
						new_altitude = int(round(new_altitude))
						altitudes_final[x,y] = new_altitude
					else:
						altitudes_final[x,y] = reference_altitude

		self.altitudes = altitudes_final


	def apply_terrain_deformation(self):
		for x in xrange(0, self.w):
			for y in xrange(0, self.h):
				self.drop_blocks_to_level(x, y, self.altitudes[x,y])


	def generate_roads(self, road_material):
		for x, y in self.occupied_by_road:
			self.fill_block_relative_to_surface(x, y, 0, road_material)
			self.clear_space_relative_to_surface(x, y, 1)


	def expand_roads(self, road_material, reserved_materials):
		blocks_copy = copy(self.blocks)
		blocks_updated = copy(self.blocks)

		for x in xrange(1, self.w-1):
			for y in xrange(1, self.h-1):
				if self.blocks[x,y] == road_material[0]:
					for x2 in xrange(x-1, x+2):
						for y2 in xrange(y-1, y+2):
							if self.altitudes[x2,y2] == self.altitudes[x,y] and not self.blocks[x2,y2] in reserved_materials:
								self.fill_block(x2, y2, self.altitudes[x,y], road_material)
								self.clear_space(x2, y2, self.altitudes[x,y]+1)
								self.blocks[x2,y2] = blocks_copy[x2,y2]
								blocks_updated[x2,y2] = road_material[0]

		self.blocks = blocks_updated


	def add_road_ramps(self, road_material, reserved_materials):
		blocks_updated = copy(self.blocks)

		for x in xrange(1, self.w-1):
			for y in xrange(1, self.h-1):
				if self.blocks[x,y] == road_material[0]:

					for x2 in xrange(x-1, x+2):
						for y2 in xrange(y-1, y+2):
							if self.altitudes[x2,y2] == self.altitudes[x,y] and not self.blocks[x2,y2] in reserved_materials:

								try:
									if blocks_updated[x2,y2+1] == road_material[0] and self.altitudes[x2,y2] < self.altitudes[x2,y2+1]:
										self.fill_block(x2, y2, self.altitudes[x2,y2]+1, (109,2))
								except:
									pass

								try:
									if blocks_updated[x2,y2-1] == road_material[0] and self.altitudes[x2,y2] < self.altitudes[x2,y2-1]:
										self.fill_block(x2, y2, self.altitudes[x2,y2]+1, (109,3))
								except:
									pass

								try:
									if blocks_updated[x2+1,y2] == road_material[0] and self.altitudes[x2,y2] < self.altitudes[x2+1,y2]:
										self.fill_block(x2, y2, self.altitudes[x2,y2]+1, (109,0))
								except:
									pass

								try:
									if blocks_updated[x2-1,y2] == road_material[0] and self.altitudes[x2,y2] < self.altitudes[x2-1,y2]:
										self.fill_block(x2, y2, self.altitudes[x2,y2]+1, (109,1))
								except:
									pass

