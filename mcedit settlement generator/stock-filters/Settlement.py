import time
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
from numpy import *
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *

from SettlementGenerator import Generator
from SettlementMap import Map, get_block, get_block_tuple, set_block

import keyboard


# lots of spaces to align checkboxes
inputs = [
			(
				("Generation settings", "title"),

				("Seed                          ", 1),
				("Number of structures  ", 10),
				("Number of bridges      ", 3),

				("Branching roads                                               ", True),
				("Generate fences                                              ", True),
				("Start with bridges                                            ", False),

				("Building style              ", ("Depends on location", "Gable roofs only", "Flat roofs only")),
				# ("Building style              ", ("Gable roofs only", "Flat roofs only", "Depends on location")),

				("Farm style                 ", ("Surrounded by fence", "Default village farms")),


				("Modify terrain    ", ("Adjust around settlement", "Don't modify terrain")),
				("Auto Export    ", ("No", "Yes")),
				# ("Modify terrain    ", ("Adjust around settlement", "Adjust entire map", "Don't modify terrain")),
				# ("Modify terrain    ", ("Adjust entire map", "Don't modify terrain")),
				# ("Modify terrain    ", ("Don't modify terrain",)),
			),

			(
				("Structures", "title"),

				("Temples                                                       ", True),
				("Blacksmiths                                                  ", True),
				("Complex Houses                                          ", True),
				("Simple Houses                                             ", True),
				("Town Squares                                              ", True),
				("Farms                                                         ", True),
			)
	]


def perform(level, box, options):
	start_time = time.time()

	wood_blocks = set([17, 162, 99, 100])
	leaf_blocks = set([18, 161, 106, 99, 100])
	decorative_blocks = set([6, 30, 31, 32, 37, 38, 39, 40, 50, 51, 55, 59, 63, 78, 81, 104, 105, 106, 111, 127, 141, 142, 175, 207])
	impassable_blocks = set([8, 9, 10, 11, 79])

	plank_conversion = {
						(17,0): (5,0),
						(17,1): (5,1),
						(17,2): (5,2),
						(17,3): (5,3),
						(162,0): (5,4),
						(162,1): (5,5),
						(99,0): (5,1), # mushrooms converted into wood
						(100,1): (5,3), # mushrooms converted into wood
					}

	log_conversion = {
						(17,0): (17,0),
						(17,1): (17,1),
						(17,2): (17,2),
						(17,3): (17,3),
						(162,0): (162,0),
						(162,1): (162,1),
						(99,0): (17,1),
						(100,1): (17,3),
					}

	fence_conversion = {
						(17,0): (85,0),
						(17,1): (188,0),
						(17,2): (189,0),
						(17,3): (190,0),
						(162,0): (191,0),
						(162,1): (192,0),
						(99,0): (189,0),
						(100,1): (190,0),
					}

	door_conversion = {
						(17,0): (64,0),
						(17,1): (193,0),
						(17,2): (194,0),
						(17,3): (195,0),
						(162,0): (196,0),
						(162,1): (197,0),
						(99,0): (193,0),
						(100,1): (193,0),
					}

	stairs_conversion = {
						(17,0): (53,0),
						(17,1): (134,0),
						(17,2): (135,0),
						(17,3): (136,0),
						(162,0): (163,0),
						(162,1): (164,0),
						(99,0): (53,0),
						(100,1): (53,0),
					}

	sandstone_conversion = {
								(12,0): (24,0),
								(12,1): (179,0),
								(24,0): (24,2),
								(179,0): (179,0),
							}

	sandstone2_conversion = {
								(12,0): (24,2),
								(12,1): (179,2),
								(24,0): (24,2),
								(179,0): (179,2),
							}

	# the following are only used initially for filling map during generation, then with the exception of roads and plazas mostly ignored during final steps
	materials = {
					'wall': (4,0),
					'floor': (5,0),
					'road': (98,0),
					'plaza': (43,5),
					'farm': (60,0),
				}

	entry_distance = 3
	reserved_space = 4
	road_distance = 1


	branching_roads = options["Branching roads                                               "]
	add_fences = options["Generate fences                                              "]
	bridges_first = options["Start with bridges                                            "]
	seed = options["Seed                          "]
	number_of_bridges = options["Number of bridges      "]
	number_of_structures = options["Number of structures  "]

	roads_can_cross_corners = False

	change_map = (options["Modify terrain    "] == "Adjust around settlement") or (options["Modify terrain    "] == "Adjust entire map")
	splice_map = (options["Modify terrain    "] == "Adjust around settlement")

	# plaza_style = 2
	connect_to_existing_roads = True

	if branching_roads:
		road_connection_points = 5
	else:
		road_connection_points = 1

	if options["Building style              "] == "Gable roofs only":
		roof_setting = 1
	elif options["Building style              "] == "Flat roofs only":
		roof_setting = 2
	else:
		roof_setting = 0

	classic_farms = options["Farm style                 "] == "Default village farms"

	# max_attempts: number of positions considered when placing each structure (higher value = better layouts but slower generation, lower value = opposite)
	max_attempts = 5000


	gen_temples = options["Temples                                                       "]
	gen_blacksmiths = options["Blacksmiths                                                  "]
	gen_complex = options["Complex Houses                                          "]
	gen_simple = options["Simple Houses                                             "]
	gen_squares = options["Town Squares                                              "]
	gen_farms = options["Farms                                                         "]


	print("\nStep 1: generate heightmap")

	# clear_trees = change_map and not splice_map
	clear_trees = False

	# new_box = box

	new_origin = (box.origin[0], 0, box.origin[2])
	new_size = (box._size[0], level.Height-1, box._size[2])
	new_box = BoundingBox(origin=new_origin, size=new_size)

	map = Map(level, new_box, impassable_blocks, wood_blocks, leaf_blocks, decorative_blocks, False, clear_trees, roads_can_cross_corners, change_map, splice_map, roof_setting, start_time)


	print("\nStep 2: generate structures")

	generator = Generator(level, new_box, options, map, materials, seed, start_time)


	sizes_temple_w, sizes_temple_h = [15], [15, 17]
	sizes_complex_w, sizes_complex_h = [15], [15]
	sizes_blacksmith_w, sizes_blacksmith_h = [16], [15]
	sizes_w, sizes_h = [7, 9, 11], [7, 9, 11]
	sizes_plaza_w, sizes_plaza_h = [13], [13]
	sizes_farm_w, sizes_farm_h = [11, 13, 15], [7, 9, 11]

	small_height = 6
	complex_height = 6
	large_height = 7

	sequence = []
	sequence_bridges = []
	current_step = 0

	temple_data = (sizes_temple_w, sizes_temple_h, large_height, entry_distance, reserved_space, road_distance, 'house', 'temple')
	complex_house_data = (sizes_complex_w, sizes_complex_h, complex_height, entry_distance, reserved_space, road_distance, 'house', 'complex house')
	garden_house_data = (sizes_complex_w, sizes_complex_h, complex_height, entry_distance, reserved_space, road_distance, 'house', 'garden house')
	blacksmith_house_data = (sizes_blacksmith_w, sizes_blacksmith_h, complex_height, entry_distance, reserved_space, road_distance, 'house', 'blacksmith house')
	simple_house_data = (sizes_w, sizes_h, small_height, entry_distance, reserved_space, road_distance, 'house', '')
	plaza_data = (sizes_plaza_w, sizes_plaza_h, small_height, entry_distance, reserved_space, road_distance, 'plaza', '')
	farm_data = (sizes_farm_w, sizes_farm_h, small_height, entry_distance, reserved_space, road_distance, 'farm', '')
	bridge_data = ([1], [1], [1], entry_distance, reserved_space, road_distance, 'bridge', '')

	order = []

	if gen_temples:
		order.append(temple_data)
	if gen_squares:
		order.append(plaza_data)
	if gen_complex:
		order.append(complex_house_data)
		order.append(garden_house_data)
	if gen_blacksmiths:
		order.append(blacksmith_house_data)
	if gen_simple:
		order.append(simple_house_data)
		order.append(simple_house_data)
	if gen_farms:
		order.append(farm_data)
		order.append(farm_data)
		order.append(farm_data)

	if len(order) == 0:
		order.append(simple_house_data)


	for i in xrange(number_of_bridges):
		sequence_bridges.append(bridge_data)

	for i in xrange(number_of_structures):
		category = i % len(order)
		sequence.append(order[category])


	if bridges_first:
		generator.add_sequence(sequence_bridges, max_attempts, road_connection_points, connect_to_existing_roads, start_time)
		generator.add_sequence(sequence, max_attempts, road_connection_points, connect_to_existing_roads, start_time)

	else:
		generator.add_sequence(sequence, max_attempts, road_connection_points, connect_to_existing_roads, start_time)
		generator.add_sequence(sequence_bridges, max_attempts, road_connection_points, connect_to_existing_roads, start_time)


	print("\nStep 3: postprocessing")

	# note: at this stage, the level hasn't been modified in any way, but map.altitudes has already been changed to 'intended' heightmap elevation (original heightmap is map.altitudes_original)


	# determine materials

	print("")
	print("Sand occupies %.3f" % (map.sand_percentage) + "% of the area")
	print("Trees occupy %.3f" % (map.tree_percentage) + "% of the area")
	print("")
	for k, v in map.tree_probabilities.items():
		print("  %-20s %f" % (k, v))

	tree_keys = sorted(map.tree_probabilities.keys(), key=lambda k: map.tree_probabilities[k], reverse=True)
	if len(tree_keys) > 0:
		wood_source = tree_keys[0]
	else:
		wood_source = (5,0)


	# everything associated with clearing trees starts here

	print("\nTree keys: %s" % (tree_keys,))

	print("\n  Clearing trees...")

	tree_clearing_start_time = time.time()

	tree_points = []
	for x in xrange(0, map.w):
		for y in xrange(0, map.h):
			if map.trees[x,y] != None:
				tree_points.append((x,y))

	nearest_tree_table = empty((map.w,map.h), object)
	if len(tree_points) > 0:
		for x in xrange(0, map.w):
			for y in xrange(0, map.h):
				nearest_tree_table[x,y] = (x,y)
				if map.leaves[x,y] and map.trees[x,y] == None:
					for d in xrange(1, max(map.w,map.h)):
						points = []

						for i in xrange(0, d+1):
							x1 = x - d + i;
							y1 = y - i;
							if x1 >= 0 and y1 >= 0 and x1 < map.w and y1 < map.h and map.trees[x1,y1] != None:
								points.append((x1,y1))
							x2 = x + d - i;
							y2 = y + i;
							if x2 >= 0 and y2 >= 0 and x2 < map.w and y2 < map.h and map.trees[x2,y2] != None:
								points.append((x2,y2))

						for i in xrange(1, d):
							x1 = x - i;
							y1 = y + d - i;
							if x1 >= 0 and y1 >= 0 and x1 < map.w and y1 < map.h and map.trees[x1,y1] != None:
								points.append((x1,y1))
							x2 = x + d - i;
							y2 = y - i;
							if x2 >= 0 and y2 >= 0 and x2 < map.w and y2 < map.h and map.trees[x2,y2] != None:
								points.append((x2,y2))

						if points:
							ordered_points = sorted(points, key=lambda position: map.get_distance(position[0], position[1], x, y))
							nearest_tree_table[x,y] = ordered_points[0]
							break

	# actually clear trees

	for x in xrange(0, map.w):
		for y in xrange(0, map.h):
			if map.trees[x,y] != None:
				tree_near_settlement = False
				# distance = 8
				distance = 12

				for structure in generator.structures:
					if map.box_collision(structure.x1-distance, structure.y1-distance, structure.x2+distance, structure.y2+distance, x, y, x+1, y+1):
						tree_near_settlement = True
						break

				if not tree_near_settlement:
					for x2 in xrange(max(0,x-distance), min(map.w,x+distance)):
						for y2 in xrange(max(0,y-distance), min(map.h,y+distance)):
							if (x2,y2) in map.occupied_by_any:
								tree_near_settlement = True

						if tree_near_settlement:
							break

				if tree_near_settlement:
					map.clear_tree(x, y, nearest_tree_table, map.altitudes_original)

	print("\nCleared trees in %i s" % (time.time() - tree_clearing_start_time,))


	# clear up a few remaining floating leaves left over from previous step

	print("\n  Double-checking and clearing some remaining leaves...")

	leaf_clearing_start_time = time.time()
	# map.leaf_removal_cleanup()
	map.leaf_removal_cleanup(map.altitudes_original)

	print("\nCleared some remaining leaves in %i s" % (time.time() - leaf_clearing_start_time,))


	# calculate final map elevation by splicing original map with settlement version (if terrain gets modified)

	if (splice_map):
		print("\n  Combining settlement's terrain map with original terrain map...")
		map_slicing_start_time = time.time()

		map.map_settlement_space(generator.structures, materials['road'])
		map.splice_map_altitudes()

		print("\nCombined maps in %i s" % (time.time() - map_slicing_start_time,))


	# apply terrain deformation based on target elevation ('altitudes')

	print("\n  Adjusting terrain based on target elevation...")
	terrain_deform_start_time = time.time()

	map.apply_terrain_deformation()

	print("\nAdjusted terrain in %i s" % (time.time() - terrain_deform_start_time,))


	# generate roads

	map.generate_roads(materials['road'])
	map.expand_roads(materials['road'], set([materials['wall'][0], materials['floor'][0], materials['farm'][0], materials['plaza'][0]]))


	# add fences (if applicable)

	if add_fences:
		print("\n  Adding fences...")
		map.place_fences(copy(map.blocks), set([materials['wall'][0], materials['floor'][0], materials['farm'][0], materials['plaza'][0]]), impassable_blocks, materials, fence_conversion, wood_source)


	# generate final versions of buildings

	print("\n  Generating buildings...")

	for structure in generator.structures:
		structure.generate_details(classic_farms, map.tree_area, map.tree_probabilities, plank_conversion, log_conversion, fence_conversion, stairs_conversion, door_conversion, wood_source)


	# add road ramps (beta)

	map.add_road_ramps(materials['road'], set([materials['wall'][0], materials['floor'][0], materials['farm'][0], materials['plaza'][0]]))


	print("\nDone (total time elapsed: %i s)." % (time.time() - start_time,))

	#keyboard.press_and_release('cmd+z')


def exportSchematicc(self, schematic):
        filename = mcplatform.askSaveSchematic(
            directories.schematicsDir, self.level.displayName, ({"Minecraft Schematics": ["schematic"], "Minecraft Structure NBT": ["nbt"]},[]))

        def save_as_nbt(schem, filename):
            structure = StructureNBT.fromSchematic(schem)
            if 'Version' in self.level.root_tag['Data']:
                structure._version = self.level.root_tag['Data']['Version'].get('Id', pymclevel.TAG_Int(1)).value
            structure.save(filename)

        if filename:
            if filename.endswith(".schematic"):
                schematic.saveToFile(filename)
            elif filename.endswith(".nbt"):
                if (schematic.Height, schematic.Length, schematic.Width) >= (50, 50, 50):
                    result = ask("You're trying to export a large selection as a Structure NBT file, this is not recommended " +
                                 "and may cause MCEdit to hang and/or crash. We recommend you export this selection as a Schematic instead.",
                                 responses=['Export as Structure anyway', 'Export as Schematic', 'Cancel Export'], wrap_width=80)
                    if result == 'Export as Structure anyway':
                        save_as_nbt(schematic, filename)
                    elif result == 'Export as Schematic':
                        schematic.saveToFile(filename.replace('.nbt', '.schematic'))
                    elif result == 'Cancel Export':
                        return
                save_as_nbt(schematic, filename)