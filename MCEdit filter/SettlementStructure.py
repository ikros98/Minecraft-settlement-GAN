import time
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from numpy import *
from random import randint, choice
from SettlementMap import restricted_flood_fill, set_block, get_block, get_block_tuple
from SettlementStructureDetails import *


class Structure:
	def __init__(self, map, structures, x1, y1, x2, y2, height, entry_distance, reserved_space, direction, cat, subcat, materials, start_time):
		#cat - short for 'category' (house, plaza, farm...)
		#subcat - short for 'subcategory' (none, complex house, temple...)

		self.cat = cat
		self.subcat = subcat
		self.map = map

		self.direction = direction
		self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

		self.height = height
		self.entry_distance = entry_distance
		self.reserved_space = reserved_space

		if self.cat == 'farm' or self.cat == 'plaza':
			self.entry_distance = 2
			self.reserved_space = 1

		self.materials = materials

		self.center_x, self.center_y = int(round((self.x2+self.x1)/2)), int(round((self.y2+self.y1)/2))
		self.door_x, self.door_y = self.center_x, self.center_y

		self.structures = structures

		self.has_distance_data = False


		if self.cat == 'bridge':
			self.extend_bridge()
			self.center_x, self.center_y = int(round((self.x2+self.x1)/2)), int(round((self.y2+self.y1)/2))

		else:
			#position doors (currently hard-coded for various subcategories of buildings)

			if self.direction == 'w':
				self.door_x = self.x1
			elif self.direction == 'e':
				self.door_x = self.x2 - 1
			elif self.direction == 'n':
				self.door_y = self.y1
			elif self.direction == 's':
				self.door_y = self.y2 - 1

			if self.subcat == 'complex house':
				if self.direction == 's':
					self.door_x = self.x2 - 5
				elif self.direction == 'n':
					self.door_x = self.x1 + 4
				elif self.direction == 'w':
					self.door_y = self.y2 - 5
				elif self.direction == 'e':
					self.door_y = self.y1 + 4

			elif self.subcat == 'blacksmith house':
				if self.direction == 's':
					self.door_x = self.x2 - 5
				elif self.direction == 'n':
					self.door_x = self.x1 + 4
				elif self.direction == 'w':
					self.door_y = self.y2 - 5
				elif self.direction == 'e':
					self.door_y = self.y1 + 4

			if self.subcat == 'garden house':
				if self.direction == 's':
					self.door_x = self.x1 + 4
				elif self.direction == 'n':
					self.door_x = self.x2 - 5
				elif self.direction == 'w':
					self.door_y = self.y1 + 4
				elif self.direction == 'e':
					self.door_y = self.y2 - 5


		self.large = self.height > 6

		exit_space_sides = 1
		exit_space_ahead = 2
		front_space = 3

		self.exit_x1, self.exit_y1, self.exit_x2, self.exit_y2 = self.get_exit_space(exit_space_sides, exit_space_ahead)
		self.front_x1, self.front_y1, self.front_x2, self.front_y2 = self.get_exit_space(exit_space_sides, front_space)
		self.outer_x1, self.outer_y1, self.outer_x2, self.outer_y2 = max(0,self.x1-self.reserved_space), max(0,self.y1-self.reserved_space), min(self.map.w,self.x2+self.reserved_space), min(self.map.h,self.y2+self.reserved_space)

		if not self.map.fits_inside(self.front_x1, self.front_y1, self.front_x2, self.front_y2):
			self.front_x1, self.front_y1 = self.exit_x1, self.exit_y1
			self.front_x2, self.front_y2 = self.exit_x2, self.exit_y2


		if self.cat == 'bridge':
			if self.direction in 'sn':
				self.altitude = max(map.altitudes[self.center_x, self.y1], map.altitudes[self.center_x, self.y2-1])
			else:
				self.altitude = max(map.altitudes[self.x1, self.center_y], map.altitudes[self.x2-1, self.center_y])
		else:
			self.altitude = self.map.altitudes[max(0,min(self.map.w-1,self.door_x)), max(0,min(self.map.h-1,self.door_y))]


		self.other_entry_points = []
		if self.cat == "plaza":
			for point in [(self.center_x, self.y1), (self.center_x, self.y2-1), (self.x1, self.center_y), (self.x2-1, self.center_y)]:
				if point[0] != self.door_x or point[1] != self.door_y:
					self.other_entry_points.append(point)

		self.templates = self.get_templates()


	def get_templates(self):
		#templates = 'suggestions' for future buildings (increases 'layout' scores for future matches)

		map = self.map
		entry_distance = self.entry_distance
		reserved_space = self.reserved_space
		templates = []

		padding = 1

		extent_neighbour = 8
		extent_plaza = 6

		extent_corner = 10
		margin_corner = 4


		if self.cat == 'plaza':

			template_west = (max(0,self.x1-entry_distance-reserved_space-extent_neighbour), self.y1+padding, max(0,self.x1-entry_distance-reserved_space), self.y2-padding, 'e', 'house')
			template_east = (min(map.w,self.x2+entry_distance+reserved_space), self.y1+padding, min(map.w,self.x2+entry_distance+reserved_space+extent_neighbour), self.y2-padding, 'w', 'house')
			template_north = (self.x1+padding, max(0,self.y1-entry_distance-reserved_space-extent_neighbour), self.x2-padding, max(0,self.y1-entry_distance-reserved_space), 's', 'house')
			template_south = (self.x1+padding, min(map.h,self.y2+entry_distance+reserved_space), self.x2-padding, min(map.h,self.y2+entry_distance+reserved_space+extent_neighbour), 'n', 'house')

			templates.append(template_west)
			templates.append(template_east)
			templates.append(template_north)
			templates.append(template_south)

			templates.append(template_west)
			templates.append(template_east)
			templates.append(template_north)
			templates.append(template_south)


		elif self.cat == 'house':

			if self.direction == 's':
				template_left_area = (max(0,self.x1-reserved_space-extent_neighbour), self.y1+padding, max(0,self.x1-reserved_space), self.y2-padding, 'sw', 'house')
				template_right_area = (min(map.w,self.x2+reserved_space), self.y1+padding, min(map.w,self.x2+reserved_space+extent_neighbour), self.y2-padding, 'se', 'house')
				templates.append(template_left_area)
				templates.append(template_right_area)

				if self.height > 6:
					template_plaza = (self.x1+padding, min(map.h,self.y2+entry_distance+reserved_space), self.x2-padding, min(map.h,self.y2+entry_distance+reserved_space+extent_plaza), 'n', 'plaza')
					templates.append(template_plaza)

				else:
					template_ahead = (self.x1+padding, min(map.h,self.y2+entry_distance+reserved_space), self.x2-padding, min(map.h,self.y2+entry_distance+reserved_space+extent_neighbour), 'n', 'house')
					templates.append(template_ahead)

					template_corner_left = (max(0,self.x1-reserved_space-extent_corner), min(map.h,self.y2+entry_distance-margin_corner), max(0,self.x1-reserved_space), min(map.h,self.y2+entry_distance+margin_corner), 'e', 'house')
					template_corner_right = (min(map.w,self.x2+reserved_space), min(map.h,self.y2+entry_distance-margin_corner), min(map.w,self.x2+reserved_space+extent_corner), min(map.h,self.y2+entry_distance+margin_corner), 'w', 'house')
					templates.append(template_corner_left)
					templates.append(template_corner_right)


			elif self.direction == 'n':
				template_left_area = (max(0,self.x1-reserved_space-extent_neighbour), self.y1+padding, max(0,self.x1-reserved_space), self.y2-padding, 'nw', 'house')
				template_right_area = (min(map.w,self.x2+reserved_space), self.y1+padding, min(map.w,self.x2+reserved_space+extent_neighbour), self.y2-padding, 'ne', 'house')
				templates.append(template_left_area)
				templates.append(template_right_area)

				if self.height > 6:
					template_plaza = (self.x1+padding, max(0,self.y1-entry_distance-reserved_space), self.x2-padding, max(0,self.y1-entry_distance-reserved_space-extent_plaza), 's', 'plaza')
					templates.append(template_plaza)

				else:
					template_ahead = (self.x1+padding, max(0,self.y1-entry_distance-reserved_space-extent_neighbour), self.x2-padding, max(0,self.y1-entry_distance-reserved_space), 's', 'house')
					templates.append(template_ahead)

					template_corner_left = (max(0,self.x1-reserved_space-extent_corner), max(0,self.y1-entry_distance-margin_corner), max(0,self.x1-reserved_space), max(0,self.y1-entry_distance+margin_corner), 'e', 'house')
					template_corner_right = (min(map.w,self.x2+reserved_space), max(0,self.y1-entry_distance-margin_corner), min(map.w,self.x2+reserved_space+extent_corner), max(0,self.y1-entry_distance+margin_corner), 'w', 'house')
					templates.append(template_corner_left)
					templates.append(template_corner_right)


			elif self.direction == 'w':
				template_left_area = (self.x1+padding, max(0,self.y1-reserved_space-extent_neighbour), self.x2-padding, max(0,self.y1-reserved_space), 'wn', 'house')
				template_right_area = (self.x1+padding, min(map.h,self.y2+reserved_space), self.x2-padding, min(map.h,self.y2+reserved_space+extent_neighbour), 'ws', 'house')
				templates.append(template_left_area)
				templates.append(template_right_area)

				if self.height > 6:
					template_plaza = (max(0,self.x1-reserved_space-entry_distance-extent_plaza), self.y1+padding, max(0,self.x1-entry_distance-reserved_space), self.y2-padding, 'e', 'plaza')
					templates.append(template_plaza)

				else:
					template_ahead = (max(0,self.x1-entry_distance-reserved_space-extent_neighbour), self.y1+padding, max(0,self.x1-entry_distance-reserved_space), self.y2-padding, 'e', 'house')
					templates.append(template_ahead)

					template_corner_left = (max(0,self.x1-entry_distance-margin_corner), max(0,self.y1-reserved_space-extent_corner), max(0,self.x1-entry_distance+margin_corner), max(0,self.y1-reserved_space), 's', 'house')
					template_corner_right = (max(0,self.x1-entry_distance-margin_corner), min(map.h,self.y2+reserved_space), max(0,self.x1-entry_distance+margin_corner), min(map.h,self.y2+reserved_space+extent_corner), 'n', 'house')
					templates.append(template_corner_left)
					templates.append(template_corner_right)


			elif self.direction == 'e':
				template_left_area = (self.x1+padding, max(0,self.y1-reserved_space-extent_neighbour), self.x2-padding, max(0,self.y1-reserved_space), 'en', 'house')
				template_right_area = (self.x1+padding, min(map.h,self.y2+reserved_space), self.x2-padding, min(map.h,self.y2+reserved_space+extent_neighbour), 'es', 'house')
				templates.append(template_left_area)
				templates.append(template_right_area)

				if self.height > 6:
					template_plaza = (min(map.w,self.x2+entry_distance+reserved_space), self.y1+padding, min(map.w,self.x2+entry_distance+reserved_space+extent_plaza), self.y2-padding, 'w', 'plaza')
					templates.append(template_plaza)

				else:
					template_ahead = (min(map.w,self.x2+entry_distance+reserved_space), self.y1+padding, min(map.w,self.x2+entry_distance+reserved_space+extent_neighbour), self.y2-padding, 'w', 'house')
					templates.append(template_ahead)

					template_corner_left = (min(map.w,self.x2+entry_distance-margin_corner), max(0,self.y1-reserved_space-extent_corner), min(map.w,self.x2+entry_distance+margin_corner), max(0,self.y1-reserved_space), 's', 'house')
					template_corner_right = (min(map.w,self.x2+entry_distance-margin_corner), min(map.h,self.y2+reserved_space), min(map.w,self.x2+entry_distance+margin_corner), min(map.h,self.y2+reserved_space+extent_corner), 'n', 'house')
					templates.append(template_corner_left)
					templates.append(template_corner_right)


		return templates


	def count_template_matches(self):
		#can go over 1 if overlaps with multiple templates (this is intentional)
		matches = 0

		for structure in self.structures:
			for template in structure.templates:
				x1, y1, x2, y2, directions, cat = template

				if cat == self.cat and self.direction in directions:
					if self.map.box_collision(x1, y1, x2, y2, self.x1, self.y1, self.x2, self.y2) and (self.cat != 'house' or self.map.box_collision(x1-1,y1-1,x2+1,y2+1, self.door_x, self.door_y, self.door_x+1, self.door_y+1)):
						intersection = float( max(0, min(x2, self.x2) - max(x1, self.x1)) * max(0, min(y2, self.y2) - max(y1, self.y1)) )
						overlap = intersection / float(((x2-x1)*(y2-y1)) + ((self.x2-self.x1)*(self.y2-self.y1)) - intersection)

						matches += overlap

		return matches


	def fits_inside(self):
		if self.map.fits_inside(self.x1, self.y1, self.x2, self.y2) and self.map.fits_inside(self.exit_x1, self.exit_y1, self.exit_x2, self.exit_y2):
			entry_point = self.get_entry_point()
			if self.map.fits_inside(entry_point[0], entry_point[1], entry_point[0]+1, entry_point[1]+1):
				return True
		return False


	def collides(self, x1, y1, x2, y2):
		return self.map.occupied(x1, y1, x2, y2, self.map.occupied_by_building) or self.map.occupied(x1, y1, x2, y2, self.map.occupied_by_impassable)


	def collides_structures(self, x1, y1, x2, y2):
		for structure in self.structures:
			if structure.cat != 'plaza' and self.map.box_collision_ignore_edges(x1, y1, x2, y2, structure.x1, structure.y1, structure.x2, structure.y2):
				return True
		return False


	def collides_structures_all(self, x1, y1, x2, y2):
		for structure in self.structures:
			if self.map.box_collision_ignore_edges(x1, y1, x2, y2, structure.x1, structure.y1, structure.x2, structure.y2):
				return True
		return False


	def collides_terrain_or_structures(self, x1, y1, x2, y2):
		return self.collides_structures(x1, y1, x2, y2) or self.collides(x1, y2, x2, y2)


	def collides_road(self, x1, y1, x2, y2):
		return self.map.occupied(x1, y1, x2, y2, self.map.occupied_by_any)


	def get_entry_point(self):
		if self.direction == 's':
			return self.door_x, self.door_y + self.entry_distance
		elif self.direction == 'n':
			return self.door_x, self.door_y - self.entry_distance
		elif self.direction == 'e':
			return self.door_x + self.entry_distance, self.door_y
		elif self.direction == 'w':
			return self.door_x - self.entry_distance, self.door_y


	def get_other_entry_points(self):
		adjusted_entry_points = []

		for point in self.other_entry_points:
			if self.center_x == point[0] and self.center_y > point[1]:
				adjusted_entry_points.append((point[0], point[1] - self.entry_distance))
			elif self.center_x == point[0] and self.center_y < point[1]:
				adjusted_entry_points.append((point[0], point[1] +  self.entry_distance))
			elif self.center_y == point[1] and self.center_x > point[0]:
				adjusted_entry_points.append((point[0] -  self.entry_distance, point[1]))
			elif self.center_y == point[1] and self.center_x < point[0]:
				adjusted_entry_points.append((point[0] +  self.entry_distance, point[1]))

		return [point for point in adjusted_entry_points if self.map.fits_inside(point[0], point[1], point[0]+1, point[1]+1)]


	def get_entry_path_default(self):
		path = []
		if self.direction == 's':
			for y in xrange(self.door_y, self.door_y + self.entry_distance + 1):
				path.append((self.door_x, y))
		elif self.direction == 'n':
			for y in xrange(self.door_y, self.door_y - self.entry_distance - 1, -1):
				path.append((self.door_x, y))
		elif self.direction == 'e':
			for x in xrange(self.door_x, self.door_x + self.entry_distance + 1):
				path.append((x, self.door_y))
		elif self.direction == 'w':
			for x in xrange(self.door_x, self.door_x - self.entry_distance - 1, -1):
				path.append((x, self.door_y))
		return path


	def get_entry_path(self, entry_point):
		path = []

		if entry_point[1] > self.center_y and entry_point[0] >= self.x1 and entry_point[0] <= self.x2:
			for y in xrange(0, self.entry_distance + 1):
				path.append((entry_point[0], entry_point[1] - y))
		elif entry_point[1] < self.center_y and entry_point[0] >= self.x1 and entry_point[0] <= self.x2:
			for y in xrange(0, self.entry_distance + 1):
				path.append((entry_point[0], entry_point[1] + y))
		elif entry_point[0] > self.center_x and entry_point[1] >= self.y1 and entry_point[1] <= self.y2:
			for x in xrange(0, self.entry_distance + 1):
				path.append((entry_point[0] - x, entry_point[1]))
		elif entry_point[0] < self.center_x and entry_point[1] >= self.y1 and entry_point[1] <= self.y2:
			for x in xrange(0, self.entry_distance + 1):
				path.append((entry_point[0] + x, entry_point[1]))


		if self.subcat == 'complex house':
			if self.direction == 's':
				for y in xrange(self.door_y, (self.y1+self.y2)/2, -1):
					path.append((self.door_x, y))
			elif self.direction == 'n':
				for y in xrange(self.door_y, (self.y1+self.y2)/2, 1):
					path.append((self.door_x, y))
			elif self.direction == 'e':
				for x in xrange(self.door_x, (self.x1+self.x2)/2, -1):
					path.append((x, self.door_y))
			elif self.direction == 'w':
				for x in xrange(self.door_x, (self.x1+self.x2)/2, 1):
					path.append((x, self.door_y))


		return path


	def update_distance_data(self):
		pointA = self.get_entry_point()

		pointB = self.get_entry_point()
		source = self
		shortest_point_distance = (self.map.w + self.map.h)

		for structure in self.structures:
			#do not reward short distance between 2 bridges
			if structure != self and structure.cat != 'farm' and not (structure.cat == 'bridge' and self.cat == 'bridge'):
				structure_entry_points = structure.get_other_entry_points()
				structure_entry_points.append(structure.get_entry_point())

				for structure_point in structure_entry_points:
					topdown_distance = self.map.get_distance(pointA[0], pointA[1], structure_point[0], structure_point[1])
					altitude_difference = abs(self.map.altitudes[pointA[0],pointA[1]] - self.map.altitudes[structure_point[0],structure_point[1]])

					point_distance = topdown_distance * (1 + altitude_difference)

					if point_distance < shortest_point_distance:
						pointB = structure_point
						source = structure
						shortest_point_distance = point_distance

		self.has_distance_data = True
		self.distance_data = (shortest_point_distance, pointA, pointB, source)

		return self.distance_data


	def get_distance_of_structure(self):
		pointA = self.get_entry_point()
		shortest_point_distance = (self.map.w + self.map.h)

		for structure in self.structures:
			#do not reward short distance between 2 bridges
			if structure != self and structure.cat != 'farm' and not (structure.cat == 'bridge' and self.cat == 'bridge'):
				structure_entry_points = structure.get_other_entry_points()
				structure_entry_points.append(structure.get_entry_point())

				for structure_point in structure_entry_points:
					topdown_distance = self.map.get_distance(pointA[0], pointA[1], structure_point[0], structure_point[1])
					altitude_difference = abs(self.map.altitudes[pointA[0],pointA[1]] - self.map.altitudes[structure_point[0],structure_point[1]])
					point_distance = topdown_distance * (1 + altitude_difference)

					if point_distance < shortest_point_distance:
						shortest_point_distance = point_distance

		return shortest_point_distance


	def get_exit_space(self, space_sides, space_ahead):
		if self.direction == 's':
			exit_x1 = self.door_x - space_sides
			exit_x2 = self.door_x + space_sides + 1
			exit_y1 = self.door_y
			exit_y2 = self.door_y + space_ahead + 1
		elif self.direction == 'n':
			exit_x1 = self.door_x - space_sides
			exit_x2 = self.door_x + space_sides + 1
			exit_y1 = self.door_y - space_ahead
			exit_y2 = self.door_y + 1
		elif self.direction == 'w':
			exit_x1 = self.door_x - space_ahead
			exit_x2 = self.door_x + 1
			exit_y1 = self.door_y - space_sides
			exit_y2 = self.door_y + space_sides + 1
		elif self.direction == 'e':
			exit_x1 = self.door_x
			exit_x2 = self.door_x + space_ahead + 1
			exit_y1 = self.door_y - space_sides
			exit_y2 = self.door_y + space_sides + 1

		return exit_x1, exit_y1, exit_x2, exit_y2


	def doesnt_block_entrance(self):
		for structure in self.structures:
			if structure != self:
				if self.map.box_collision(self.x1, self.y1, self.x2, self.y2, structure.front_x1, structure.front_y1, structure.front_x2, structure.front_y2):
					return False
		return True


	def can_exit_smoothly(self):
		return self.map.altitude_difference(self.exit_x1, self.exit_y1, self.exit_x2, self.exit_y2) == 0 and not self.collides(self.front_x1, self.front_y1, self.front_x2, self.front_y2)


	def acceptable(self):
		outer_x1, outer_y1, outer_x2, outer_y2 = self.outer_x1, self.outer_y1, self.outer_x2, self.outer_y2
		return self.fits_inside() and (self.cat == 'farm' or self.can_exit_smoothly()) and not self.collides_structures(outer_x1, outer_y1, outer_x2, outer_y2) and not self.collides_road(max(0,self.x1-1), max(0,self.y1-1), min(self.map.w,self.x2+1), min(self.map.h,self.y2+1)) and not self.collides(outer_x1, outer_y1, outer_x2, outer_y2)


	def in_front_of_road_scaled(self):
		entry_point = self.get_entry_point()
		if entry_point in self.map.occupied_by_road or entry_point in self.map.occupied_by_farm:

			if self.direction in 'ns':
				w = float(self.x2 - self.x1)
				road_tiles = 0
				for x in xrange(self.x1, self.x2):
					if (x,entry_point[1]) in self.map.occupied_by_road or (x,entry_point[1]) in self.map.occupied_by_farm:
						road_tiles += 1
				return float(road_tiles) / w

			if self.direction in 'ew':
				h = float(self.y2 - self.y1)
				road_tiles = 0
				for y in xrange(self.y1, self.y2):
					if (entry_point[0],y) in self.map.occupied_by_road or (entry_point[0],y) in self.map.occupied_by_farm:
						road_tiles += 1
				return float(road_tiles) / h

		return 0


	def has_easy_access_to_roads(self):
		#approximated: check collisions with impassable terrain some distance ahead

		map = self.map
		distance = 10

		steps = 0
		if self.direction == 's':
			for y in xrange(self.door_y, min(map.h, self.door_y+distance)):
				if (self.door_x, y+1) in map.occupied_by_plaza or (self.door_x, y+1) in map.occupied_by_road or map.grid[self.door_x, y] == 0:
					steps += 1
				else:
					break
		elif self.direction == 'n':
			for y in xrange(self.door_y, max(0, self.door_y-distance), -1):
				if (self.door_x, y-1) in map.occupied_by_plaza or (self.door_x, y-1) in map.occupied_by_road or map.grid[self.door_x, y] == 0:
					steps += 1
				else:
					break
		elif self.direction == 'e':
			for x in xrange(self.door_x, min(map.w, self.door_x+distance)):
				if (x+1, self.door_y) in map.occupied_by_plaza or (x+1, self.door_y) in map.occupied_by_road or map.grid[x, self.door_y] == 0:
					steps += 1
				else:
					break
		elif self.direction == 'w':
			for x in xrange(self.door_x, max(0, self.door_x-distance), -1):
				if (x-1, self.door_y) in map.occupied_by_plaza or (x-1, self.door_y) in map.occupied_by_road or map.grid[x, self.door_y] == 0:
					steps += 1
				else:
					break

		return float(steps) / float(distance)


	def get_elevation_score(self):
		outer_x1, outer_y1, outer_x2, outer_y2 = self.outer_x1, self.outer_y1, self.outer_x2, self.outer_y2
		altitude_lowest, altitude_highest = self.map.get_edge_altitudes(outer_x1, outer_y1, outer_x2, outer_y2, 2)
		altitude_difference = max(abs(self.altitude - altitude_highest), abs(self.altitude - altitude_lowest))

		return 1. - (float(min(self.map.max_building_altitude_difference, altitude_difference)) / float(self.map.max_building_altitude_difference))


	def get_layout_score(self):
		return self.count_template_matches()


	def get_access_score(self):
		return self.has_easy_access_to_roads()


	def get_distance_score(self):
		return (1. - (float(min(self.map.max_building_distance, self.get_distance_of_structure())) / float(self.map.max_building_distance))) ** 2


	def get_in_front_of_road_score(self):
		return self.in_front_of_road_scaled()


	def generate(self):
		map = self.map


		#added as a test: change altitudes underneath houses
		if self.cat == 'house':
			for x in xrange(self.x1, self.x2):
				for y in xrange(self.y1, self.y2):
					map.altitudes[x,y] = self.altitude


		# self.map_slice = map.get_slice(self.x1, self.y1, self.x2, self.y2, 1, True)
		self.map_slice = map.get_slice(self.x1, self.y1, self.x2, self.y2, 1, False)


		#mark positions as occupied by structures
		if self.cat == 'house':
			map.mark_as_occupied(self.x1, self.y1, self.x2, self.y2, self.map.occupied_by_building)

		elif self.cat == 'farm':
			map.mark_as_occupied(self.x1, self.y1, self.x2, self.y2, self.map.occupied_by_farm)

		elif self.cat == 'plaza':
			rounded = abs(self.x2-self.x1) >= 13 and abs(self.y2-self.y1) >= 13
			if rounded:
				map.mark_as_occupied(self.x1, self.y1+1, self.x2, self.y2-1, self.map.occupied_by_plaza)
				map.mark_as_occupied(self.x1+1, self.y1, self.x2-1, self.y2, self.map.occupied_by_plaza)
			else:
				map.mark_as_occupied(self.x1, self.y1, self.x2, self.y2, self.map.occupied_by_plaza)

		elif self.cat == 'bridge':
			map.mark_as_occupied(self.x1, self.y1, self.x2, self.y2, self.map.occupied_by_bridge)


	def generate_details(self, classic_farms, tree_area, tree_probabilities, plank_conversion, log_conversion, fence_conversion, stairs_conversion, door_conversion, wood_source):
		map = self.map
		map_slice = self.map_slice

		# map.paste_slice(self.map_slice, self.x1, self.y1, self.x2, self.y2)

		#clear space
		if self.cat == 'plaza' or self.cat == 'farm':
			for x in range(self.x1, self.x2):
				for y in range(self.y1, self.y2):
					map.clear_space(x, y, self.altitude+1)


		#buildings
		if self.cat == 'house':

			sandstone_conversion = {
										(12,0): (24,0),
										(12,1): (179,0),
									}

			sandstone2_conversion = {
										(12,0): (24,2),
										(12,1): (179,2),
									}

			#select basic style for building

			if map.roof_setting == 2:
				#all roofs are flat: materials are the best available type of sandstone, or stone if sand is rare

				wooden_building = False
				flat_roof = True

				sand_keys = sorted(map.sand_probabilities.keys(), key=lambda k: map.sand_probabilities[k], reverse=True)

				if len(sand_keys) > 0 and map.sand_percentage >= 10:
					sandstone_building = True
					sand_source = sand_keys[0]
				else:
					sandstone_building = False
					sand_source = (0, 0)

			else:
				#roofs depend on location (unless roof_setting == 1): determine if the building is located in a sandy area ("desert")

				if map.roof_setting == 1:
					local_sand_percentage = 0
					sand_keys = []
				else:
					local_sand_area, local_sand_probabilities = map.get_local_sand_data(self.x1, self.y1, self.x2, self.y2, self.cat, self.subcat)
					local_sand_percentage = local_sand_area * 100
					sand_keys = sorted(local_sand_probabilities.keys(), key=lambda k: local_sand_probabilities[k], reverse=True)


				if local_sand_percentage >= 50:
					#flat roof: choose sandstone as material

					sandstone_building = True
					flat_roof = True
					wooden_building = False

					sand_keys = sorted(local_sand_probabilities.keys(), key=lambda k: local_sand_probabilities[k], reverse=True)
					if len(sand_keys) > 0:
						sand_source = sand_keys[0]
					else:
						sandstone_building = False
						sand_source = (0, 0)

				else:
					#gable roof: choose stone or wood as material depending on building type and level of forestation

					flat_roof = False
					sandstone_building = False
					sand_source = (0, 0)

					if map.tree_percentage >= 10:
						stone_chance_minor, stone_chance_major = 10, 25
					elif map.tree_percentage >= 5:
						stone_chance_minor, stone_chance_major = 20, 50
					else:
						stone_chance_minor, stone_chance_major = 30, 75

					if self.subcat == 'temple' or self.subcat == 'blacksmith_house':
						stone_chance = stone_chance_major
					else:
						stone_chance = stone_chance_minor

					wooden_building = randint(0, 100) >= stone_chance


			#determine building materials

			if wood_source in log_conversion.keys() and wood_source in plank_conversion.keys() and wood_source in door_conversion:
				wood_beam = log_conversion[wood_source]
				wood_floor = plank_conversion[wood_source]
				wood_wall = plank_conversion[wood_source]
				wood_roof = plank_conversion[wood_source]
				door_material = door_conversion[wood_source]
			else:
				wood_beam = (17, 0)
				wood_floor = (5, 0)
				wood_wall = (5, 0)
				wood_roof = (5, 0)
				door_material = (64, 0)


			if sand_source in sandstone_conversion.keys() and sand_source in sandstone2_conversion.keys():
				sandstone_wall = sandstone_conversion[sand_source]
				sandstone_beam = sandstone2_conversion[sand_source]
				sandstone_doorframe = (159, 0)
			else:
				sandstone_building = False
				sandstone_wall = (4, 0)
				sandstone_beam = (43, 0)
				sandstone_doorframe = (98, 0)


			if flat_roof:
				if sandstone_building:
					floor_material = wood_floor
					wall_material = sandstone_wall
					wall_under_roof_material = sandstone_beam
					roof_beam_material = sandstone_beam
					roof_material = sandstone_beam
					window_material = (20, 0)
					beam_material = sandstone_beam
					doorframe_material = sandstone_doorframe

				else:
					floor_material = wood_floor
					wall_material = (4, 0)
					wall_under_roof_material = (4, 0)
					roof_beam_material = (4, 0)
					roof_material = (43, 0)
					window_material = (20, 0)
					beam_material = (98, 0)
					doorframe_material = (98, 0)

			else:
				if wooden_building:
					floor_material = wood_floor
					wall_material = wood_wall
					wall_under_roof_material = wood_wall
					beam_material = wood_beam
					doorframe_material = wood_beam
					roof_beam_material = wood_beam
					roof_material = wood_roof
					window_material = (20, 0)

				else:
					floor_material = wood_floor
					wall_material = (4, 0)
					wall_under_roof_material = (4, 0)
					roof_beam_material = (4, 0)
					roof_material = wood_roof
					window_material = (20, 0)
					beam_material = (98, 0)
					doorframe_material = (98, 0)


			if self.subcat == 'temple':
				build_temple(self, map, map_slice, wall_material, beam_material, doorframe_material, floor_material, roof_material, wall_under_roof_material, window_material, door_material, flat_roof)

			elif self.subcat == 'complex house':
				build_complex_house(self, map, map_slice, wall_material, beam_material, doorframe_material, floor_material, roof_material, roof_beam_material, wall_under_roof_material, window_material, door_material, flat_roof)

			elif self.subcat == 'garden house':
				build_garden_house(self, map, map_slice, wall_material, beam_material, doorframe_material, floor_material, roof_material, roof_beam_material, wall_under_roof_material, window_material, door_material, flat_roof)

			elif self.subcat == 'blacksmith house':
				build_blacksmith_house(self, map, map_slice, wall_material, beam_material, doorframe_material, floor_material, roof_material, roof_beam_material, wall_under_roof_material, window_material, door_material, flat_roof)

			else:
				build_simple_house(self, map, map_slice, wall_material, beam_material, doorframe_material, floor_material, roof_material, roof_beam_material, wall_under_roof_material, window_material, door_material, flat_roof)


			# map.paste_slice(map_slice, self.x1, self.y1, self.x2, self.y2, True)
			map.paste_slice(map_slice, self.x1, self.y1, self.x2, self.y2, False)


			#support for uneven terrain

			bottom_blocks = {}

			for x in xrange(self.x1, self.x2):
				for y in xrange(self.y1, self.y2):
					bottom_block = get_block_tuple(map.level, map.x+x, self.altitude, map.y+y)
					bottom_blocks[(x,y)] = bottom_block

			bottom_block_keys = set(bottom_blocks.keys())


			if self.subcat == 'temple':
				#supporting reverse stone pyramid

				for x in xrange(self.x1, self.x2):
					for y in xrange(self.y1, self.y2):
						for y_step in xrange(map.altitudes[x,y], self.altitude):
							depth = self.altitude - y_step - 2

							if x > self.x1+depth and y > self.y1+depth and x < self.x2-depth and y < self.y2-depth:
								set_block(map.level, (98,1), map.x+x, y_step, map.y+y)


			else:
				#supporting beams

				for x in xrange(self.x1, self.x2):
					for y in xrange(self.y1, self.y2):
						bottom_block = bottom_blocks[(x,y)]

						if bottom_block != (0, 0) and not bottom_block in map.decorative_blocks:
							empty_space_2_blocks_away_vertical = False
							empty_space_2_blocks_away_horizontal = False

							for xd in (-2,2):
								if ((x+xd,y) in bottom_block_keys and bottom_blocks[(x+xd,y)] != bottom_block and bottom_blocks[(x+xd/2,y)] == bottom_block) or ((x+xd/2,y) in bottom_block_keys and bottom_blocks[(x+xd/2,y)] == bottom_block and not (x+xd,y) in bottom_block_keys):
									empty_space_2_blocks_away_horizontal = True
							for yd in (-2,2):
								if ((x,y+yd) in bottom_block_keys and bottom_blocks[(x,y+yd)] != bottom_block and bottom_blocks[(x,y+yd/2)] == bottom_block) or ((x,y+yd/2) in bottom_block_keys and bottom_blocks[(x,y+yd/2)] == bottom_block and not (x,y+yd) in bottom_block_keys):
									empty_space_2_blocks_away_vertical = True

							add_support = empty_space_2_blocks_away_vertical and empty_space_2_blocks_away_horizontal

							if add_support:
								for y_step in xrange(self.altitude-1, map.altitudes[x,y], -1):
									terrain_block = get_block(map.level, map.x+x, y_step, map.y+y)

									if terrain_block == 0:
										map.fill_block(x, y, y_step, beam_material)
									else:
										break



		#generate well
		elif self.cat == 'plaza':

			well_xr = 2
			well_yr = 2
			well_x1, well_x2, well_y1, well_y2 = self.center_x-well_xr, self.center_x+well_xr+1, self.center_y-well_yr, self.center_y+well_yr+1

			#well
			map.fill(well_x1, well_y1, self.altitude+1, well_x2, well_y2, self.altitude+2, (98, 1))
			map.fill(well_x1+1, well_y1+1, self.altitude+1, well_x2-1, well_y2-1, self.altitude+2, (8, 0))

			#plaza

			rounded = abs(self.x2-self.x1) >= 13 and abs(self.y2-self.y1) >= 13 #make this a structure feature?

			if not rounded:
				for x in xrange(self.x1, self.x2):
					for y in xrange(self.y1, self.y2):
						#always generate plaza itself regardless of terrain altitude
						map.fill_block(x, y, self.altitude, self.materials['plaza'])
						#support for uneven terrain (sometimes doesn't generate entire plaza)
						for y_step in xrange(map.altitudes[x,y], self.altitude+1):
							map.fill_block(x, y, y_step, self.materials['plaza'])

			else:
				for x in xrange(self.x1+1, self.x2-1):
					for y in xrange(self.y1, self.y2):
						map.fill_block(x, y, self.altitude, self.materials['plaza'])
						for y_step in xrange(map.altitudes[x,y], self.altitude+1):
							map.fill_block(x, y, y_step, self.materials['plaza'])
				for x in xrange(self.x1, self.x2):
					for y in xrange(self.y1+1, self.y2-1):
						map.fill_block(x, y, self.altitude, self.materials['plaza'])
						for y_step in xrange(map.altitudes[x,y], self.altitude+1):
							map.fill_block(x, y, y_step, self.materials['plaza'])

			#roof
			map.fill(well_x1, well_y1, self.altitude+2, well_x1+1, well_y1+1, self.altitude+4, (139, 0))
			map.fill(well_x2-1, well_y1, self.altitude+2, well_x2, well_y1+1, self.altitude+4, (139, 0))
			map.fill(well_x1, well_y2-1, self.altitude+2, well_x1+1, well_y2, self.altitude+4, (139, 0))
			map.fill(well_x2-1, well_y2-1, self.altitude+2, well_x2, well_y2, self.altitude+4, (139, 0))

			if wood_source in log_conversion.keys() and wood_source in plank_conversion.keys():
				wood_roof = plank_conversion[wood_source]
			else:
				wood_roof = (5, 0)

			map.fill(well_x1, well_y1, self.altitude+4, well_x2, well_y2, self.altitude+5, wood_roof)
			map.fill(well_x1+1, well_y1+1, self.altitude+5, well_x2-1, well_y2-1, self.altitude+6, wood_roof)

			#stairs
			map.fill(well_x1-1, well_y1+1, self.altitude+1, well_x1, well_y2-1, self.altitude+2, (109, 0))
			map.fill(well_x2, well_y1+1, self.altitude+1, well_x2+1, well_y2-1, self.altitude+2, (109, 1))
			map.fill(well_x1+1, well_y1-1, self.altitude+1, well_x2-1, well_y1, self.altitude+2, (109, 2))
			map.fill(well_x1+1, well_y2, self.altitude+1, well_x2-1, well_y2+1, self.altitude+2, (109, 3))


		#generate farm
		elif self.cat == 'farm':
			if wood_source in log_conversion.keys():
				wood_beam = log_conversion[wood_source]
			else:
				wood_beam = (17, 0)

			crops_block = choice([(59, 7), (59, 7), (141,7), (142,7)])

			if classic_farms:
				#similar to default Minecraft villages

				map.fill(self.x1, self.y1, self.altitude+1, self.x2, self.y2, self.altitude+2, wood_beam)
				map.fill(self.x1+1, self.y1+1, self.altitude+1, self.x2-1, self.y2-1, self.altitude+2, self.materials['farm'])
				map.fill(self.x1+1, self.y1+1, self.altitude+2, self.x2-1, self.y2-1, self.altitude+3, crops_block)

				if self.direction == 'n' or self.direction == 's':
					for x in xrange(self.x1+1, self.x2-1):
						if x % 3 == 0:
							map.fill(x, self.y1+1, self.altitude+1, x+1, self.y2-1, self.altitude+2, (8, 0))
							map.fill(x, self.y1+1, self.altitude+2, x+1, self.y2-1, self.altitude+3, (0, 0))

				if self.direction == 'e' or self.direction == 'w':
					for y in xrange(self.y1+1, self.y2-1):
						if y % 3 == 0:
							map.fill(self.x1+1, y, self.altitude+1, self.x2-1, y+1, self.altitude+2, (8, 0))
							map.fill(self.x1+1, y, self.altitude+2, self.x2-1, y+1, self.altitude+3, (0, 0))

				#support for uneven terrain
				for x in xrange(self.x1, self.x2):
					for y in xrange(self.y1, self.y2):
						for y_step in xrange(map.altitudes[x,y], self.altitude+1):
							map.fill_block(x, y, y_step, wood_beam)

			else:
				#fenced-off farmland area

				if wood_source in fence_conversion.keys():
					wood_fence = fence_conversion[wood_source]
				else:
					wood_fence = (85, 0)

				#support for uneven terrain
				for x in xrange(self.x1, self.x2):
					for y in xrange(self.y1, self.y2):
						# for y_step in xrange(map.altitudes[x,y]+1, self.altitude+1):
						for y_step in xrange(map.altitudes[x,y], self.altitude+1):
							map.fill_block(x, y, y_step, wood_beam)

				#actual farm
				map.fill(self.x1, self.y1, self.altitude+1, self.x2, self.y2, self.altitude+2, wood_fence)

				map.fill(self.x1+1, self.y1+1, self.altitude, self.x2-1, self.y2-1, self.altitude+1, self.materials['farm'])
				map.fill(self.x1+1, self.y1+1, self.altitude+1, self.x2-1, self.y2-1, self.altitude+2, crops_block)

				#water pools
				for x in xrange(self.x1+1, self.x2-1):
					for y in xrange(self.y1+1, self.y2-1):
						if (self.center_x-x) % 4 == 0 and (self.center_y-y) % 4 == 0 and (map.get_distance(x,y,self.door_x,self.door_y) > 1):
							map.fill(x, y, self.altitude, x+1, y+1, self.altitude+1, (8, 0))
							map.fill(x, y, self.altitude+1, x+1, y+1, self.altitude+2, (0, 0))

				#entrance
				map.fill(self.door_x, self.door_y, self.altitude+1, self.door_x+1, self.door_y+1, self.altitude+2, (0, 0))


		#generate bridge
		elif self.cat == 'bridge':

			if wood_source in log_conversion.keys() and wood_source in plank_conversion.keys() and wood_source in fence_conversion.keys() and wood_source in stairs_conversion.keys():
				wood_beam = log_conversion[wood_source]
				wood_plank = plank_conversion[wood_source]
				wood_fence = fence_conversion[wood_source]
			else:
				wood_beam = (17, 0)
				wood_plank = (5, 0)
				wood_fence = (85, 0)

			if wood_source in stairs_conversion.keys():
				stairs_n = (stairs_conversion[wood_source][0], 2)
				stairs_s = (stairs_conversion[wood_source][0], 3)
				stairs_e = (stairs_conversion[wood_source][0], 1)
				stairs_w = (stairs_conversion[wood_source][0], 0)
			else:
				stairs_n = (53, 2)
				stairs_s = (53, 3)
				stairs_e = (53, 1)
				stairs_w = (53, 0)

			# width = 1
			width = 2

			override_blocks = set([0, 8, 9, 10, 11, 79])
			override_blocks.add(wood_plank[0])
			override_blocks.add(self.materials['road'][0])

			if self.direction in 'sn':
				#steps (base)
				map.fill(self.x1-width+1, self.y1+1, self.altitude, self.x2+width-1, self.y1+2, self.altitude+1, wood_plank)
				map.fill(self.x1-width+1, self.y2-2, self.altitude, self.x2+width-1, self.y2-1, self.altitude+1, wood_plank)

				#steps
				map.fill(self.x1-width+1, self.y1+1, self.altitude+1, self.x2+width-1, self.y1+2, self.altitude+2, stairs_n)
				map.fill(self.x1-width+1, self.y2-2, self.altitude+1, self.x2+width-1, self.y2-1, self.altitude+2, stairs_s)

				#bridge
				map.fill(self.x1-width, self.y1+2, self.altitude+1, self.x2+width, self.y2-2, self.altitude+2, wood_plank)

				#beams
				for x, y in [(self.x1-width,self.y1+2), (self.x1+width,self.y1+2), (self.x1-width,self.y2-3), (self.x1+width,self.y2-3)]:
					for z in xrange(self.altitude+2, map.box.miny, -1):
						if get_block(map.level, map.x+x, z, map.y+y) in override_blocks:
							set_block(map.level, wood_beam, map.x+x, z, map.y+y)
						else:
							break

				#barriers
				map.fill(self.x1-width, self.y1+3, self.altitude+2, self.x1-width+1, self.y2-3, self.altitude+3, wood_fence)
				map.fill(self.x2+width-1, self.y1+3, self.altitude+2, self.x2+width, self.y2-3, self.altitude+3, wood_fence)

			else:
				#steps (base)
				map.fill(self.x1+1, self.y1-width+1, self.altitude+1, self.x1+2, self.y2+width-1, self.altitude+2, wood_plank)
				map.fill(self.x2-2, self.y1-width+1, self.altitude+1, self.x2-1, self.y2+width-1, self.altitude+2, wood_plank)

				#steps
				map.fill(self.x1+1, self.y1-width+1, self.altitude+1, self.x1+2, self.y2+width-1, self.altitude+2, stairs_w)
				map.fill(self.x2-2, self.y1-width+1, self.altitude+1, self.x2-1, self.y2+width-1, self.altitude+2, stairs_e)

				#bridge
				map.fill(self.x1+2, self.y1-width, self.altitude+1, self.x2-2, self.y2+width, self.altitude+2, wood_plank)

				#beams
				for x, y in [(self.x1+2,self.y1-width), (self.x1+2,self.y1+width), (self.x2-3,self.y1-width), (self.x2-3,self.y1+width)]:
					for z in xrange(self.altitude+2, map.box.miny, -1):
						if get_block(map.level, map.x+x, z, map.y+y) in override_blocks:
							set_block(map.level, wood_beam, map.x+x, z, map.y+y)
						else:
							break

				#barriers
				map.fill(self.x1+3, self.y1-width, self.altitude+2, self.x2-3, self.y1-width+1, self.altitude+3, wood_fence)
				map.fill(self.x1+3, self.y2+width-1, self.altitude+2, self.x2-3, self.y2+width, self.altitude+3, wood_fence)


class Bridge(Structure):
	def extend_bridge(self):
		if self.fits_inside():
			map = self.map

			if self.direction in 'sn':
				#extend over water
				while self.y1 > 1:
					if (self.center_x, self.y1) in map.occupied_by_impassable:
						self.y1 -= 1
					else:
						break
				while self.y2 < map.h-1:
					if (self.center_x, self.y2-1) in map.occupied_by_impassable:
						self.y2 += 1
					else:
						break

				#extend to avoid cliffs
				while self.y1 > 1:
					if map.grid[self.center_x, self.y1-1]:
						self.y1 -= 1
					else:
						break
				while self.y2 < map.h-1:
					if map.grid[self.center_x, self.y2]:
						self.y2 += 1
					else:
						break

				#extend to match elevation levels at ends
				if map.altitudes[self.center_x, self.y1] < map.altitudes[self.center_x, self.y2-1]:
					while self.y1 > 1:
						if map.altitudes[self.center_x, self.y1] > map.altitudes[self.center_x, self.y2-1]:
							break
						elif map.altitudes[self.center_x, self.y1] == map.altitudes[self.center_x, self.y2-1] and map.grid[self.center_x, self.y1] == 0:
							break
						else:
							self.y1 -= 1
				elif map.altitudes[self.center_x, self.y1] > map.altitudes[self.center_x, self.y2-1]:
					while self.y2 < map.h-1:
						if map.altitudes[self.center_x, self.y2-1] < map.altitudes[self.center_x, self.y2-1]:
							break
						elif map.altitudes[self.center_x, self.y2-1] == map.altitudes[self.center_x, self.y2-1] and map.grid[self.center_x, self.y2-1] == 0:
							break
						else:
							self.y2 += 1

			else:
				#extend over water
				while self.x1 > 1:
					if (self.x1, self.center_y) in map.occupied_by_impassable:
						self.x1 -= 1
					else:
						break
				while self.x2 < map.w-1:
					if (self.x2-1, self.center_y) in map.occupied_by_impassable:
						self.x2 += 1
					else:
						break

				#extend to avoid cliffs
				while self.x1 > 1:
					if map.grid[self.x1-1, self.center_y]:
						self.x1 -= 1
					else:
						break
				while self.x2 < map.w-1:
					if map.grid[self.x2, self.center_y]:
						self.x2 += 1
					else:
						break

				#extend to match elevation levels at ends
				if map.altitudes[self.x1, self.center_y] < map.altitudes[self.x2-1, self.center_y]:
					while self.x1 > 1:
						if map.altitudes[self.x1, self.center_y] > map.altitudes[self.x2-1, self.center_y]:
							break
						elif map.altitudes[self.x1, self.center_y] == map.altitudes[self.x2-1, self.center_y] and map.grid[self.x1, self.center_y] == 0:
							break
						else:
							self.x1 -= 1
				elif map.altitudes[self.x1, self.center_y] > map.altitudes[self.x2-1, self.center_y]:
					while self.x2 < map.w-1:
						if map.altitudes[self.x2-1, self.center_y] < map.altitudes[self.x2-1, self.center_y]:
							break
						elif map.altitudes[self.x2-1, self.center_y] == map.altitudes[self.x2-1, self.center_y] and map.grid[self.x2-1, self.center_y] == 0:
							break
						else:
							self.x2 += 1


	def has_easy_access_to_roads(self):
		map = self.map
		distance = 10

		steps = 0
		if self.direction in 'sn':
			for y in xrange(self.y2, min(map.h, self.y2+distance)):
				if map.grid[self.center_x, y] == 0:
					steps += 1
				else:
					break
			for y in xrange(self.y1, max(0, self.y1-distance), -1):
				if map.grid[self.center_x, y] == 0:
					steps += 1
				else:
					break
		else:
			for x in xrange(self.x2, min(map.w, self.x2+distance)):
				if map.grid[x, self.center_y] == 0:
					steps += 1
				else:
					break
			for x in xrange(self.x1, max(0, self.x1-distance), -1):
				if map.grid[x, self.center_y] == 0:
					steps += 1
				else:
					break

		return steps


	def fits_inside(self):
		return self.x1 > self.entry_distance+1 and self.x2 < self.map.w-self.entry_distance-1 and self.y1 > self.entry_distance+1 and self.y2 < self.map.h-self.entry_distance-1


	def over_water(self):
		return (self.center_x,self.center_y) in self.map.occupied_by_impassable


	def passes_through_mountain(self):
		if self.direction in 'sn':
			for y in xrange(self.y1, self.y2):
				if self.map.altitudes[self.center_x,y] > self.altitude:
					return True
			return False
		else:
			for x in xrange(self.x1, self.x2):
				if self.map.altitudes[x,self.center_y] > self.altitude:
					return True
			return False


	def edge_altitudes_match(self):
		if self.direction in 'ns':
			return self.map.altitudes[self.center_x,self.y1] == self.map.altitudes[self.center_x,self.y2-1]
		else:
			return self.map.altitudes[self.x1,self.center_y] == self.map.altitudes[self.x2-1,self.center_y]


	def acceptable(self):
		outer_x1, outer_y1, outer_x2, outer_y2 = self.outer_x1, self.outer_y1, self.outer_x2, self.outer_y2
		return self.fits_inside() and self.over_water() and not self.collides_structures_all(outer_x1, outer_y1, outer_x2, outer_y2) and self.edge_altitudes_match() and not self.passes_through_mountain()