import tcod
 
# actual size of the window
SCREEN_WIDTH	= 80
SCREEN_HEIGHT	= 50
 
# size of the map
MAP_WIDTH		= 80
MAP_HEIGHT		= 45
 
# parameters for dungeon generator
ROOM_MAX_SIZE	= 10 
ROOM_MIN_SIZE	=  6
MAX_ROOMS		= 30

FOV_ALGO		=  0
FOV_LIGHT_WALLS	= True
TORCH_RADIUS	= 10
 
LIMIT_FPS		= 20  # 20 frames-per-second maximum

color_dark_wall		= tcod.Color(20, 20, 20) #(0, 0, 100)
color_light_wall	= tcod.Color(80, 80, 80) #(130, 110, 50)
color_dark_ground	= tcod.Color(20, 20, 20) #(50, 50, 150)
color_light_ground	= tcod.Color(100, 100, 100) #(200, 180, 50)

 
class Tile:
	# a tile of the map and its properties
 
	def __init__(self, blocked, block_sight=None):
		self.blocked = blocked
 
		# by default, if a tile is blocked, it also blocks sight
		if block_sight is None:
			block_sight = blocked
		self.block_sight = block_sight
 
 
class Rect:
	# a rectangle on the map. used to characterize a room.
 
	def __init__(self, x, y, w, h):
		self.x1 = x
		self.y1 = y
		self.x2 = x + w
		self.y2 = y + h
 
	def center(self):
		center_x = (self.x1 + self.x2) // 2
		center_y = (self.y1 + self.y2) // 2
		return (center_x, center_y)
 
	def intersect(self, other):
		# returns true if this rectangle intersects with another one
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
				self.y1 <= other.y2 and self.y2 >= other.y1)
 
 
class Object:
	# this is a generic object: the player, a monster, an item, the stairs...
	# it's always represented by a character on screen.
 
	def __init__(self, x, y, char, color):
		self.x = x
		self.y = y
		self.char = char
		self.color = color
 
	def move(self, dx, dy):
		# move by the given amount, if the destination is not blocked
		if not map[self.x + dx][self.y + dy].blocked:
			self.x += dx
			self.y += dy
 
	def draw(self):
			# set the color and then draw the character that represents this
			# object at its position
		if tcod.map_is_in_fov(fov_map, self.x, self.y):
			tcod.console_set_default_foreground(con, self.color)
			tcod.console_put_char(con, self.x, self.y, self.char, tcod.BKGND_NONE)
 
	def clear(self):
		# erase the character that represents this object
		tcod.console_put_char(con, self.x, self.y, ' ', tcod.BKGND_NONE)
 
 
def createRoom(room):
	global map
	# go through the tiles in the rectangle and make them passable
	for x in range(room.x1 + 1, room.x2):
		for y in range(room.y1 + 1, room.y2):
			map[x][y].blocked = False
			map[x][y].block_sight = False
 
 
def createTunnelH(x1, x2, y):
	global map
	# horizontal tunnel. min() and max() are used in case x1>x2
	for x in range(min(x1, x2), max(x1, x2) + 1):
		map[x][y].blocked = False
		map[x][y].block_sight = False
 
 
def createTunnelV(y1, y2, x):
	global map
	# vertical tunnel
	for y in range(min(y1, y2), max(y1, y2) + 1):
		map[x][y].blocked = False
		map[x][y].block_sight = False
 
 
def makeMap():
	global map, player
 
	# fill map with "blocked" tiles
	map = [
		[Tile(True) for y in range(MAP_HEIGHT)]
		for x in range(MAP_WIDTH)
	]
 
	rooms = []
	num_rooms = 0
 
	for r in range(MAX_ROOMS):
		# random width and height
		w = tcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
		h = tcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
		# random position without going out of the boundaries of the map
		x = tcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
		y = tcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)
 
		# "Rect" class makes rectangles easier to work with
		new_room = Rect(x, y, w, h)
 
		# run through the other rooms and see if they intersect with this one
		failed = False
		for other_room in rooms:
			if new_room.intersect(other_room):
				failed = True
				break
 
		if not failed:
			# this means there are no intersections, so this room is valid
			# "paint" it to the map's tiles
			createRoom(new_room)
 
			# center coordinates of new room, will be useful later
			(new_x, new_y) = new_room.center()
 
			if num_rooms == 0:
				# this is the first room, where the player starts at
				player.x = new_x
				player.y = new_y
			else:
				# all rooms after the first:
				# connect it to the previous room with a tunnel
 
				# center coordinates of previous room
				(prev_x, prev_y) = rooms[num_rooms - 1].center()
 
				# draw a coin (random number that is either 0 or 1)
				if tcod.random_get_int(0, 0, 1) == 1:
					# first move horizontally, then vertically
					createTunnelH(prev_x, new_x, prev_y)
					createTunnelV(prev_y, new_y, new_x)
				else:
					# first move vertically, then horizontally
					createTunnelV(prev_y, new_y, prev_x)
					createTunnelH(prev_x, new_x, new_y)
 
			# finally, append the new room to the list
			rooms.append(new_room)
			num_rooms += 1

def makeFovMap():
	global fov_map, fov_recompute
	print("generating new fov map")
	fov_map = tcod.map_new(MAP_WIDTH, MAP_HEIGHT)
	fov_recompute = True
	for y in range(MAP_HEIGHT):
		for x in range(MAP_WIDTH):
			tcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)
 
def renderAll():
	global color_dark_wall, color_light_wall
	global color_dark_ground, color_light_ground
	global fov_recompute

	if fov_recompute:
		fov_recompute = False
		tcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)
 
	# go through all tiles, and set their background color
	for y in range(MAP_HEIGHT):
		for x in range(MAP_WIDTH):
			visible = tcod.map_is_in_fov(fov_map, x, y)
			wall = map[x][y].block_sight
			if not visible:
				if wall:
					tcod.console_set_char_background(con, x, y, color_dark_wall, tcod.BKGND_SET)
				else:
					tcod.console_set_char_background(con, x, y, color_dark_ground, tcod.BKGND_SET)
			else:
				if wall:
					tcod.console_set_char_background(con, x, y, color_light_wall, tcod.BKGND_SET)
				else:
					tcod.console_set_char_background(con, x, y, color_light_ground, tcod.BKGND_SET)
 
	# draw all objects in the list
	for object in objects:
		object.draw()
 
	# blit the contents of "con" to the root console
	tcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
 
 
def handleKeys():
	global fov_recompute
	# key = tcod.console_check_for_keypress()  #real-time
	key = tcod.console_wait_for_keypress(True)  # turn-based
 
	if key.vk == tcod.KEY_ENTER and key.lalt:
		# Alt+Enter: toggle fullscreen
		tcod.console_set_fullscreen(not tcod.console_is_fullscreen()) 
	elif key.vk == tcod.KEY_ESCAPE:
		return True  # exit game
	elif key.vk == tcod.KEY_DELETE:
		makeMap()
		makeFovMap()
		fov_recompute = True
 
	# movement keys
	if tcod.console_is_key_pressed(tcod.KEY_UP):
		player.move(0, -1)
		fov_recompute = True
	elif tcod.console_is_key_pressed(tcod.KEY_DOWN):
		player.move(0, 1)
		fov_recompute = True
	elif tcod.console_is_key_pressed(tcod.KEY_LEFT):
		player.move(-1, 0)
		fov_recompute = True
	elif tcod.console_is_key_pressed(tcod.KEY_RIGHT):
		player.move(1, 0)
		fov_recompute = True
 

#############################################
# Initialization & Main Loop
#############################################
 
# tcod.console_set_custom_font('arial10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
tcod.console_set_custom_font('arial10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Adividiardi: The Wanderers', False)
tcod.sys_set_fps(LIMIT_FPS)
con = tcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
 
# create object representing the player
player = Object(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, '@', tcod.white)
 
# create an NPC
npc = Object(SCREEN_WIDTH // 2 - 5, SCREEN_HEIGHT // 2, '@', tcod.yellow)
 
# the list of objects with those two
objects = []
objects.append(player)
 
# generate map (at this point it's not drawn to the screen)
makeMap()

fov_map = None
fov_recompute = True
makeFovMap()

 
while not tcod.console_is_window_closed():
 
	# render the screen
	renderAll()
 
	tcod.console_flush()
 
	# erase all objects at their old locations, before they move
	for object in objects:
		object.clear()
 
	# handle keys and exit game if needed
	exit = handleKeys()
	if exit:
		break