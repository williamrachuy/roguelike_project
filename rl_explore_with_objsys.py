# try:
# 	import tcod
# except:
import libtcodpy as tcod

import math, time
import object_system
from object_system import *
import time, random, copy
# import pygame
# from pygame import mixer

font = 'terminal16x16_gs_ro.png'
audio = 'dungeon.mp3'

# actual size of the window
SCREEN_WIDTH	= 80
SCREEN_HEIGHT	= 50

CON_WIDTH		= 80
CON_HEIGHT		= 5

# size of the map
MAP_WIDTH		= SCREEN_WIDTH
MAP_HEIGHT		= SCREEN_HEIGHT - CON_HEIGHT

# parameters for dungeon generator
ROOM_MAX_SIZE	= 10
ROOM_MIN_SIZE	=  6
MAX_ROOMS		= 20

FOV_ALGO		= 0
FOV_LIGHT_WALLS	= True
TORCH_RADIUS	= 20

LIMIT_FPS		= 60  # 20 frames-per-second maximum
TICK_RATE		= 10
BLINK_RATE		= 30
REGEN_RATE		= 5

PRI_LOW			= 20
PRI_MED			= 10
PRI_HIGH		=  0

base_unexplored		= 10
color_unexplored	= tcod.Color(base_unexplored, base_unexplored, base_unexplored)

base_wall = 100
dark_wall = base_wall // 6
color_light_wall	= tcod.Color(base_wall, base_wall, base_wall) #(130, 110, 50)
color_dark_wall		= tcod.Color(dark_wall, dark_wall, dark_wall) #(0, 0, 100)

base_ground = 160
dark_ground = base_ground // 6
color_light_ground	= tcod.Color(base_ground, base_ground, base_ground) #(200, 180, 50)
color_dark_ground	= tcod.Color(dark_ground, dark_ground, dark_ground) #(50, 50, 150)

tcod_color_conversion = {
	'white'		: tcod.white,
	'grey'		: tcod.grey,
	'dark grey'	: tcod.dark_grey,
	'red'		: tcod.red,
	'green'		: tcod.green,
	'blue'		: tcod.blue,
	'yellow'	: tcod.yellow,
	'black'		: tcod.black,
	'orange'	: tcod.orange,
}

class World:
	pass

class Console:
	def __init__(self):
		tcod.console_set_custom_font('data/fonts/{}'.format(font), tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_ASCII_INROW)
		tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Adividiardi: The Wanderers', False)
		tcod.sys_set_fps(LIMIT_FPS)
		self.con = tcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
		tcod.mouse_show_cursor(False)

	def draw(self, object=None, visibility=False, color=None):
			# set the color and then draw the character that represents this
			# object at its position
		if color is None:
			color = tcod_color_conversion[object.display_color]
		if visibility:
			tcod.console_set_default_foreground(self.con, color)
			tcod.console_put_char(self.con, object.spacial.position.x, object.spacial.position.y, object.display_symbol, tcod.BKGND_NONE)			
		elif tcod.map_is_in_fov(fov_map, object.spacial.position.x, object.spacial.position.y):
			tcod.console_set_default_foreground(self.con, color)
			tcod.console_put_char(self.con, object.spacial.position.x, object.spacial.position.y, object.display_symbol, tcod.BKGND_NONE)			
		# else:
		# 	tcod.console_set_default_foreground(con, tcod.Color(20, 20, 20))
		# 	tcod.console_put_char(con, self.x, self.y, self.char, tcod.BKGND_NONE)

	def clear(self, object):
		# erase the character that represents this object
		tcod.console_put_char(self.con, object.spacial.position.x, object.spacial.position.y, ' ', tcod.BKGND_NONE)

	def renderMessage(self, message="no message", x=0, y=0, color=tcod.white, transparent=True):
		if not transparent:
			self.renderErase()
		tcod.console_set_default_foreground(self.con, color)
		for i in range(SCREEN_WIDTH):
			tcod.console_put_char(self.con, i, y, ' ', tcod.BKGND_NONE)
		for i in range(len(message)):
			tcod.console_put_char(self.con, x + i, y, message[i], tcod.BKGND_NONE)
		tcod.console_blit(self.con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

	def renderErase(self, h=SCREEN_HEIGHT, w=SCREEN_WIDTH, x=0, y=0):
		for _y in range(y, y + h):
			for _x in range(x, x + w):
				tcod.console_set_char_background(self.con, _x, _y, tcod.black, tcod.BKGND_SET)
				tcod.console_put_char(self.con, _x, _y, ' ', tcod.BKGND_NONE)
		tcod.console_blit(self.con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

	def renderAll(self, visibility=False):
		global color_dark_wall, color_light_wall
		global color_dark_ground, color_light_ground
		global fov_recompute, map, map_explored

		n = 1
		if (tick_counter % n == 0) and show_fps:
			message = "{:.2f} ticks/second".format(n/getTickPeriod())
			self.renderMessage(message=message)

		if not visibility:
			if fov_recompute:
				fov_recompute = False
				tcod.map_compute_fov(fov_map, player.spacial.position.x, player.spacial.position.y, fov_range + fov_flicker, FOV_LIGHT_WALLS, FOV_ALGO)

		# go through all tiles, and set their background color
		for y in range(MAP_HEIGHT):
			for x in range(MAP_WIDTH):

				if not visibility:
					visible = tcod.map_is_in_fov(fov_map, x, y)
				wall = (map[x][y].physical.opacity > 50)

				if visibility:
					if wall:
						tcod.console_set_char_background(self.con, x, y, color_light_wall, tcod.BKGND_SET)
					else:
						tcod.console_set_char_background(self.con, x, y, color_light_ground, tcod.BKGND_SET)
				elif not visible:
					if map[x][y].explored:
						if wall:
							tcod.console_set_char_background(self.con, x, y, color_dark_wall, tcod.BKGND_SET)
						else:
							tcod.console_set_char_background(self.con, x, y, color_dark_ground, tcod.BKGND_SET)
					else:
						if wall:
							tcod.console_set_char_background(self.con, x, y, color_unexplored, tcod.BKGND_SET)
						else:
							tcod.console_set_char_background(self.con, x, y, color_unexplored, tcod.BKGND_SET)
				else:
					if not map[x][y].explored and not wall:
						map_explored += 1
					map[x][y].explored = True
					radius = math.sqrt((x - player.spacial.position.x)**2 + (y - player.spacial.position.y)**2)
					variance = 0
					if random.randint(0, 100) < 100:
						variance = random.randint(0, 2)
					if wall:
						base = base_wall
						dark = dark_wall
						# color = tcod.Color(round(dr * (1.0 + (variance * 0.1))), round(dg * (1.0 + (variance * 0.08))), round(db * (1.0 + (variance * 0..04))))
						# tcod.console_set_char_background(self.con, x, y, color, tcod.BKGND_SET)
					else:
						base = base_ground
						dark = dark_ground
					dr = dg = db = dark + ((base - dark) * (1.0 - (radius / (fov_range + fov_flicker))**0.4))
					color = tcod.Color(round(dr + variance), round(dg + variance), round(db + variance))
					tcod.console_set_char_background(self.con, x, y, color, tcod.BKGND_SET)

					if (x, y) == ((player.spacial.position.x + player.spacial.direction.x), (player.spacial.position.y + player.spacial.direction.y)):
						color = color + tcod.dark_grey
						tcod.console_set_char_background(self.con, x, y, color, tcod.BKGND_SET)


					# if wall:
					# 	tcod.console_set_char_background(self.con, x, y, color_light_wall, tcod.BKGND_SET)
					# else:
					# 	if not map[x][y].explored:
					# 		map_explored += 1
					# 	map[x][y].explored = True
					# 	tcod.console_set_char_background(self.con, x, y, color_light_ground, tcod.BKGND_SET)


		x_offset = 7
		bar_length = (SCREEN_WIDTH // 4) - x_offset
		xb = x_offset + bar_length

		for x in range(x_offset, xb):
			color = tcod.grey
			if x < int((player.type.properties.health / player.type.properties._health) * bar_length) + x_offset:
				color = tcod.red
				if player.type.properties.health == player.type.properties._health:
					color = tcod.light_red
				elif (player.type.properties.health < (0.10 * player.type.properties._health)) and (tick_counter % BLINK_RATE < BLINK_RATE // 2):
					color = tcod.dark_red
			tcod.console_set_char_background(self.con, x, SCREEN_HEIGHT - 5, color, tcod.BKGND_SET)

		for x in range(x_offset, xb):
			color = tcod.grey
			if x < int((player.type.properties.stamina / player.type.properties._stamina) * bar_length) + x_offset:
				color = tcod.yellow
				if player.type.properties.stamina == player.type.properties._stamina:
					color = tcod.light_yellow
				elif (player.type.properties.stamina < (0.10 * player.type.properties._stamina)) and (tick_counter % BLINK_RATE < BLINK_RATE // 2):
					color = tcod.dark_yellow
			tcod.console_set_char_background(self.con, x, SCREEN_HEIGHT - 4, color, tcod.BKGND_SET)

		for x in range(x_offset, xb):
			color = tcod.grey
			if x < int((player.type.properties.essence / player.type.properties._essence) * bar_length) + x_offset:
				color = tcod.blue
				if player.type.properties.essence == player.type.properties._essence:
					color = tcod.light_blue
				elif (player.type.properties.essence < (0.10 * player.type.properties._essence)) and (tick_counter % BLINK_RATE < BLINK_RATE // 2):
					color = tcod.dark_blue
			tcod.console_set_char_background(self.con, x, SCREEN_HEIGHT - 3, color, tcod.BKGND_SET)

		for x in range(x_offset, xb):
			color = tcod.grey
			# if x < int((player.type.stats.experience / (player.type.stats.level_base**(player.type.stats.level + 1))) * bar_length) + x_offset:
			xp_current	= player.type.stats.experience - player.type.calcExperience()
			xp_needed	= player.type.calcExperience(level=player.type.stats.level+1) - player.type.calcExperience()
			if x < int((xp_current / xp_needed) * bar_length) + x_offset:
				color = tcod.green
			tcod.console_set_char_background(self.con, x, SCREEN_HEIGHT - 2, color, tcod.BKGND_SET)

		text_color = tcod.white
		pad = len(str(player.type.properties._health)) - len(str(player.type.properties.health))
		message = "{}{}/{}".format(' '*pad, player.type.properties.health, player.type.properties._health)
		msg_offset = x_offset - len(message)
		self.renderMessage(message=message, color=text_color, x=msg_offset, y=SCREEN_HEIGHT-5)
		pad = len(str(player.type.properties._stamina)) - len(str(player.type.properties.stamina))
		message = "{}{}/{}".format(' '*pad, player.type.properties.stamina, player.type.properties._stamina)
		msg_offset = x_offset - len(message)
		self.renderMessage(message=message, color=text_color, x=msg_offset, y=SCREEN_HEIGHT-4)
		pad = len(str(player.type.properties._essence)) - len(str(player.type.properties.essence))
		message = "{}{}/{}".format(' '*pad, player.type.properties.essence, player.type.properties._essence)
		msg_offset = x_offset - len(message)
		self.renderMessage(message=message, color=text_color, x=msg_offset, y=SCREEN_HEIGHT-3)
		pad = 0
		message = "LVL {}".format(player.type.stats.level)
		msg_offset = x_offset - len(message)
		self.renderMessage(message=message, color=text_color, x=msg_offset, y=SCREEN_HEIGHT-2)


		self.renderErase(h=1, w=SCREEN_WIDTH, x=0, y=SCREEN_HEIGHT-1)
		message = "{} of {} tiles explored".format(map_explored, map_explorable)
		if map_explored == map_explorable:
			message = "You explored the entire map!"
		self.renderMessage(message=message, x=0, y=SCREEN_HEIGHT-1, transparent=True)     

		# draw all objects in the list
		for object in objects:
			overlap = False
			radius = math.sqrt((object.spacial.position.x - player.spacial.position.x)**2 + (object.spacial.position.y - player.spacial.position.y)**2)
			color = tcod_color_conversion[object.display_color] / (1 + radius)
			for other in objects:				
				if (object.spacial.position.x == other.spacial.position.x) and (object.spacial.position.y == other.spacial.position.y) and (object is not other):
					# print("overlap for {0}({1}) and {2}({3})".format(object.name, object.priority, other.name, other.priority))
					overlap = True
					if object.priority <= other.priority:
						self.draw(object=object, visibility=visibility, color=color)
			if not overlap:
				self.draw(object=object, visibility=visibility, color=color)
			if object.blinking:
				if tick_counter % BLINK_RATE < BLINK_RATE // 2:
					self.clear(object=object)
		# blit the contents of "con" to the root console
		tcod.console_blit(self.con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)


class Tile:
	# a tile of the map and its properties

	def __init__(self, blocked, block_sight=None):
		self.blocked = blocked

		# by default, if a tile is blocked, it also blocks sight
		if block_sight is None:
			block_sight = blocked
		self.block_sight = block_sight
		self.explored = False


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

	def __init__(self, name, blocks, x, y, char, color, priority=0, blinking=False, speed=1, alive=True, health=100, stamina=100,
			damage=10, fov=10, avoid=True, stationary=True, activity=100, friends=[], friendly_fire=True, essence=0):
		self.name = name
		self.blocks = blocks
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.priority = priority
		self.blinking = blinking
		self.speed = speed
		self.alive = alive
		self.health = health
		self.damage = damage
		self.fov = fov
		self.avoid = avoid
		self.stationary = stationary
		self._char = char
		self._health = health
		self.activity = activity
		self.friends = friends
		self.friendly_fire = friendly_fire
		self.stamina = stamina
		self._stamina = stamina
		self._color = color
		self.essence = essence
		self._essence = essence
		self._speed = speed

	def move(self, dx, dy):
		# move by the given amount, if the destination is not blocked
		if self.stationary:
			return False
		self.char = self._char.lower()
		if not isBlocked(x=(self.x + dx), y=(self.y + dy)) and (0 <= self.x + dx < MAP_WIDTH) and (0 <= self.y + dy < MAP_HEIGHT):
			self.x += dx
			self.y += dy
			return True
		return False

	def dig(self, dx, dy):
		self.char = '%'
		return dig(object=self, x=(self.x + dx), y=(self.y + dy))

	def attack(self, dx, dy):
		self.char = '%'
		return attack(attacker=self, x=(self.x + dx), y=(self.y + dy))

	def harm(self, type=[], amount=0):
		if 'health' in type:
			self.health -= amount
			if self.health < 0:
				self.health = 0
		if 'essence' in type:
			self.essence -= amount
			if self.essence < 0:
				self.essence = 0
		if 'stamina' in type:
			self.stamina -= amount
			if self.stamina < 0:
				self.stamina = 0

	def heal(self, type=[], amount=0):
		if 'health' in type:
			self.health += amount
			if self.health > 100:
				self.health = 100
		if 'essence' in type:
			self.essence += amount
			if self.essence > 100:
				self.essence = 100
		if 'stamina' in type:
			self.stamina += amount
			if self.stamina > 100:
				self.stamina = 100

	def die(self):
		self.blinking = False
		self.alive = False
		self.blocks = False
		self.char = self._char.lower()
		self.color = tcod.grey
		self.priority = PRI_LOW

	def updateStatus(self):
		if self.health == 0:
			self.die()
		elif self.health < self._health // 5:
			self.blinking = True
			self.color = tcod.light_red
		else:
			self.speed = self._speed
			self.blinking = False
			self.color = self._color
		if (self.stamina < self._stamina // 10) or (self.health < self._health // 10):
			self.speed = self._speed * 3

	def draw(self, visibility=False, color=None):
			# set the color and then draw the character that represents this
			# object at its position
		if color is None:
			color = self.color
		if visibility:
			tcod.console_set_default_foreground(con, color)
			tcod.console_put_char(con, self.x, self.y, self.char, tcod.BKGND_NONE)			
		elif tcod.map_is_in_fov(fov_map, self.x, self.y):
			tcod.console_set_default_foreground(con, color)
			tcod.console_put_char(con, self.x, self.y, self.char, tcod.BKGND_NONE)
		# else:
		# 	tcod.console_set_default_foreground(con, tcod.Color(20, 20, 20))
		# 	tcod.console_put_char(con, self.x, self.y, self.char, tcod.BKGND_NONE)

	def clear(self):
		# erase the character that represents this object
		tcod.console_put_char(con, self.x, self.y, ' ', tcod.BKGND_NONE)


def createRoom(room):
	global map
	# go through the tiles in the rectangle and make them passable
	for x in range(room.x1 + 1, room.x2):
		for y in range(room.y1 + 1, room.y2):
			object = map[x][y]
			object.type.species = Ground()
			object.calcPhysical()
			object.updateObject()


def createTunnelH(x1, x2, y, w=1):
	global map
	# horizontal tunnel. min() and max() are used in case x1>x2
	for x in range(min(x1, x2), max(x1, x2) + 1):
		for _w in range(w):
			object = map[x][y + _w]
			object.type.species = Ground()
			object.calcPhysical()
			object.updateObject()


def createTunnelV(y1, y2, x, w=1):
	global map
	# vertical tunnel
	for y in range(min(y1, y2), max(y1, y2) + 1):
		for _w in range(w):
			object = map[x + _w][y]
			object.type.species = Ground()
			object.calcPhysical()
			object.updateObject()

def getExplorableTiles():
	global map
	explorable = 0
	for x in range(MAP_WIDTH):
		for y in range(MAP_HEIGHT):
			if not map[x][y].physical.solid:
				explorable += 1
	return explorable

def makeMap():
	global map, player, map_explorable, map_explored

	# fill map with "blocked" tiles
	map_explored = 0
	map = [
		[createTile(species='wall', x=x, y=y, z=0) for y in range(MAP_HEIGHT)]
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

		failed = False
		if not failed:
			# this means there are no intersections, so this room is valid
			# "paint" it to the map's tiles
			createRoom(new_room)

			# center coordinates of new room, will be useful later
			(new_x, new_y) = new_room.center()

			if num_rooms == 0:
				# this is the first room, where the player starts at
				player.spacial.position.x = new_x
				player.spacial.position.y = new_y
			else:
				# all rooms after the first:
				# connect it to the previous room with a tunnel

				# center coordinates of previous room
				(prev_x, prev_y) = rooms[num_rooms - 1].center()

				# draw a coin (random number that is either 0 or 1)
				if tcod.random_get_int(0, 0, 3) < 2:
					if tcod.random_get_int(0, 0, 1) == 1:
						# first move horizontally, then vertically
						createTunnelH(x1=prev_x, x2=new_x, y=prev_y, w=tcod.random_get_int(0, 1, 4))
						createTunnelV(y1=prev_y, y2=new_y, x=new_x, w=tcod.random_get_int(0, 1, 4))
					else:
						# first move vertically, then horizontally
						createTunnelH(x1=prev_x, x2=new_x, y=new_y, w=tcod.random_get_int(0, 1, 4))
						createTunnelV(y1=prev_y, y2=new_y, x=prev_x, w=tcod.random_get_int(0, 1, 4))

			# if spawn_monsters:
			# 	placeObjects(new_room)
			# finally, append the new room to the list
			num_rooms += 1
			rooms.append(new_room)
			# if show_room_no:
			# 	room_no = Object(name='room{}'.format(chr(65 + num_rooms - 1)), blocks=False,
			# 				x=new_x, y=new_y, char=chr(65 + num_rooms - 1),
			# 				color=tcod.grey, priority=99)
			# 	objects.insert(0,room_no)

			# renderAll(visibility=True)
			tcod.console_flush()
			for object in objects:
				console.clear(object=object)

	map_explorable = getExplorableTiles()
	# [[print(map[x][y].physical.solid) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

def makeFovMap():
	global fov_map, fov_recompute
	fov_map = tcod.map_new(MAP_WIDTH, MAP_HEIGHT)
	fov_recompute = True
	for y in range(MAP_HEIGHT):
		for x in range(MAP_WIDTH):
			physical = map[x][y].physical
			tcod.map_set_properties(fov_map, x, y, not (physical.opacity > 20), not physical.solid)

def handleKeys():
	global fov_recompute, objects, visibility_override, player, move, fov_range, show_fps
	player.updateObject()
	key = tcod.console_check_for_keypress(tcod.KEY_RELEASED)  #real-time
	# key = tcod.console_wait_for_keypress(True)  # turn-based

	if key.vk == tcod.KEY_ENTER and key.lalt:
		# Alt+Enter: toggle fullscreen
		tcod.console_set_fullscreen(not tcod.console_is_fullscreen()) 
	elif key.vk == tcod.KEY_ESCAPE:
		return 'exit'  # exit game
	elif key.vk == tcod.KEY_DELETE:
		# mixer.music.stop()
		objects = []
		xp = player.type.stats.experience
		player = copy.deepcopy(player_base)
		player.type.stats.experience = xp
		player.type.calcEntityStats()
		objects.append(player)
		makeMap()
		fov_recompute = True
		makeFovMap()
		# time.sleep(1)
		# message = "You wake up..."
		# console.renderMessage(message=message, x=(SCREEN_WIDTH//2)-(len(message)//2), y=SCREEN_HEIGHT//2, transparent=False)
		# tcod.console_flush()
		# time.sleep(2)
		# console.renderErase()
		# tcod.console_flush()
		# mixer.music.play(-1)
	elif key.vk == tcod.KEY_1:
		visibility_override = not visibility_override
	elif key.vk == tcod.KEY_2:
		player.blinking = not player.blinking
	elif key.vk == tcod.KEY_3:
		show_fps = not show_fps
		console.renderMessage(message=' '*SCREEN_WIDTH)
	elif key.c == ord('p'):
		return 'pause'
	elif key.c == ord('h'):
		player.type.harm(type=['health', 'essence', 'stamina'], amount=1)
		player.type.modifyExperience(amount=-10, delta=True)
		player.updateObject()
	elif key.c == ord('n'):
		if fov_range > 1:
			fov_range -= 1
			fov_recompute = True
	elif key.c == ord('m'):
		fov_range += 1
		fov_recompute = True

	mov_mult = 2
	if tcod.console_is_key_pressed(tcod.KEY_SHIFT):
		mov_mult = 1

	look = False
	if tcod.console_is_key_pressed(tcod.KEY_CONTROL):
		look = True

	if tick_counter % (player.type.properties.movement * mov_mult) == 0:
		move = True
		player.display_symbol = player.getDisplaySymbol()
	elif not move:
		player.display_symbol = player.getDisplaySymbol().lower()


	if game_state == 'playing':
		# movement keys
		(dx, dy) = (0, 0)
		keypress = False
		if tcod.console_is_key_pressed(tcod.KEY_UP):
			(dx, dy) = (dx + 0, dy - 1)
			keypress = True
		if tcod.console_is_key_pressed(tcod.KEY_DOWN):
			(dx, dy) = (dx + 0, dy + 1)
			keypress = True
		if tcod.console_is_key_pressed(tcod.KEY_LEFT):
			(dx, dy) = (dx - 1, dy + 0)
			keypress = True
		if tcod.console_is_key_pressed(tcod.KEY_RIGHT):
			(dx, dy) = (dx + 1, dy + 0)
			keypress = True
		if tcod.console_is_key_pressed(tcod.KEY_SPACE):
			if tick_player % int(round(player.type.properties.regen)) == 0: # originally tick_player
				player.type.heal(type=['health', 'essence', 'stamina'], amount=1)
				player.type.modifyExperience(amount=10, delta=True)
				# player.updateObject()
			return 'action'

		if move and keypress and (tick_counter % (player.type.properties.movement * mov_mult) == 0):
			# print("{0} at {1} {2}".format(player.name, player.x, player.y))
			# print("Tick #{}".format(tick_counter))
			move = False
			# player.char = 'o'
			player.face(dx=dx, dy=dy, dz=0)
			if look:
				return 'action'
			if player.move(dx=dx, dy=dy, dz=0, map=map, objects=objects) == True:
				# print("\tmoves to {0} {1}".format(player.x, player.y))
				fov_recompute = True
				if mov_mult == 2:
					player.type.heal(type=['stamina'], amount=1)
				else:
					if player.type.properties.stamina != 0:
						player.type.harm(type=['stamina'], amount=1)
					else:
						player.type.harm(type=['health'], amount=1)
				if player.type.properties.stamina == player.type.properties._stamina:
					player.type.heal(type=['health'], amount=1)
			'''
			elif player.dig(dx, dy) == True:
				# print("\tdigs")
				pass
			elif player.attack(dx, dy):
				# print("\tattacks {0} {1}".format(player.x + dx, player.y + dy))
				# print("\tattack (dx, dy) {0} {1}".format(dx, dy))
				pass
				# print("\tattacks")
			else:
				pass
				# print("\tnothing to do")
			'''
			return 'action'
		elif keypress and (tick_counter % (player.type.properties._movement * mov_mult) == 0): # originally tick_player and properties.movement
			player.face(dx=dx, dy=dy, dz=0)
			if mov_mult == 2:
				player.type.heal(type=['stamina'], amount=1)
			return 'fatigued'
		return 'no action'


MAX_ROOM_MONSTERS = 3
def placeObjects(room):
	num_monsters = tcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)

	for i in range(num_monsters):
		x = tcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
		y = tcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

		if not isBlocked(x, y):
			# chances:
			#	35%: spider
			#	20%: goblin
			#	10%: troll
			#	 5%: wraith
			damage_variance = tcod.random_get_int(0, -5, 5)
			health_variance = tcod.random_get_int(0, -5, 5)
			choice = tcod.random_get_int(0, 0, 100)
			if choice >= (5 + 10 + 20):
				monster = Object(
						name='spider', blocks=True,
						x=x, y=y, char='S', color=tcod.light_red,
						priority=4, blinking=False,
						speed=2,  alive=True,
						health=10+health_variance, damage=15+damage_variance, fov=4, avoid=True,
						stationary=False, activity=90,
						friends=['spider'], friendly_fire=False,
						essence=0)
			elif choice >= (5 + 10):
				monster = Object(
						name='goblin', blocks=True,
						x=x, y=y, char='G', color=tcod.green,
						priority=3, blinking=False,
						speed=2, alive=True,
						health=30+health_variance, damage=33+damage_variance, fov=10, avoid=False,
						stationary=False, activity=33,
						friends=['goblin', 'troll'], friendly_fire=False,
						essence=0)
			elif choice >= 5:
				monster = Object(
						name='troll', blocks=True,
						x=x, y=y, char='T', color=tcod.yellow,
						priority=2, blinking=False,
						speed=20, alive=True,
						health=80+health_variance, damage=50+damage_variance, fov=5, avoid=False,
						stationary=False, activity=10,
						friends=['goblin', 'troll'], friendly_fire=False,
						essence=0)
			elif choice >= 0:
				monster = Object(
						name='wraith', blocks=True,
						x=x, y=y, char='W', color=tcod.lighter_blue,
						priority=1, blinking=False,
						speed=2, alive=True,
						health=1, damage=100, fov=1, avoid=False,
						stationary=False, activity=50,						
						friends=['wraith'], friendly_fire=False,
						essence=50)
			objects.append(monster)

# def isBlocked(x=0, y=0, z=0):
# 	if map[x][y].physical.solid:
# 		return True
# 	for object in objects:
# 		if object.physical.solid and object.spacial.position.x == x and object.spacial.position.y == y:
# 			return True
# 	return False

def dig(object, x, y):
	global map, map_explorable
	if object.stamina < 5:
		return False
	if (0 < x < MAP_WIDTH-1) and (0 < y < MAP_HEIGHT-1) and (map[x][y].blocked):
		object.harm(type=['stamina'], amount=5)
		map[x][y].blocked = False
		map[x][y].block_sight = False
		map_explorable = getExplorableTiles()
		makeFovMap()
		object.updateStatus()
		return True
	return False

def attack(attacker, x, y):
	global map
	for object in objects:
		if (object.name in attacker.friends) and (attacker.friendly_fire == False):
			return False
		if (object.x == x) and (object.y == y):
			if attacker.stamina == 0:
				attacker.harm(type=['health'], amount=5)
			else:
				attacker.harm(type=['stamina'], amount=5)
			object.harm(type=['health'], amount=attacker.damage)
			# if object.name in ['spider']:
				# mixer.Channel(1).play(hurt_spider)
			# elif object.name in ['troll']:
				# mixer.Channel(1).play(hurt_troll)
			object.updateStatus()
			return True
	return False

def takeTurn(object, tick):
	return
	global fov_recompute
	# print("{0} at {1} {2}".format(object.name, object.x, object.y))
	object.updateStatus()
	if tick % object.speed == 0:
		object.display_symbol = object.object_display_symbol.upper()
	else:
		# print("\tmust wait")
		return 'no action'

	if game_state == 'playing':
		(dx, dy) = (0, 0)



		avoidance = 1
		if object.avoid or (object.health <= object._health // 33):
			avoidance = -1
		if player.health < object.damage:
			avoidance = 1
		move = False

		tcod.map_compute_fov(fov_map, object.x, object.y, object.fov, FOV_LIGHT_WALLS, FOV_ALGO)
		visible = tcod.map_is_in_fov(fov_map, player.x, player.y)
		fov_recompute = True
		if visible: # (abs(object.x - player.x) <= object.fov) and (abs(object.y - player.y) <= object.fov):
			if object.x > player.x:
				dx = -1 * avoidance
			elif object.x < player.x:
				dx = 1 * avoidance
			if object.y > player.y:
				dy = -1 * avoidance
			elif object.y < player.y:
				dy = 1 * avoidance
			# print("\tlooks at {0} {1}".format(object.x + dx, object.y + dy))
			move = True

		if move is False and (tcod.random_get_int(0, 0, 100) < object.activity):
			dx += random.choice([-1, 0, 1])
			if dx == 0:
				dy += random.choice([-1, 1])
			else:
				dy += random.choice([-1, 0, 1])
			move = True

		# print("\tabout to make an action")
		if move is True:
			# object.char = object.char.lower()
			if object.move(dx, dy):
				# print("\tmoves to {0} {1}".format(object.x, object.y))
				object.heal(type=['stamina'], amount=1)
				if object.stamina == object._stamina:
					object.heal(type=['health'], amount=1)
				return 'action'
				# print("\t{} moves".format(object.name))
			# 	fov_recompute = True
			# elif object.dig(dx, dy):
			# 	print("\t{} digs".format(object.name))
			elif (dx != 0) or (dy != 0):
				# print("\tattacks {0} {1}".format(object.x + dx, object.y + dy))
				# print("\tattack (dx, dy) {0} {1}".format(dx, dy))
				object.attack(dx, dy)
				return 'action'
			# else:
				# print("\tdoes nothing")
		return 'no action'

def updateTickCounter():
	global tick_counter
	tick_counter += 1

def updateTickPlayer():
	global tick_player
	tick_player += 1

def updateFovFlicker():
	global fov_flicker, fov_recompute
	if not (random.randint(0, 100) < 25):
		return
	min = -fov_flicker
	max = round(fov_flicker**0.5)
	fov_flicker += random.randint(min, max)
	if fov_flicker < 1:
		fov_flicker = 1
	fov_recompute = True
	# print('|'*(fov_range + fov_flicker))

def getTickPeriod():
	global time_tick_pre
	time_tick_now = time.time()
	retval = time_tick_now - time_tick_pre
	time_tick_pre = time_tick_now
	return retval

def spawnMonsters():
	global objects
	npc_list = ['human', 'elf']
	npc_species = random.choice(npc_list)

	while True:
		(x, y) = (random.randint(1, MAP_WIDTH-1), random.randint(1,MAP_HEIGHT-1))
		if not map[x][y].physical.solid:
			break

	npc = createNpc(species=npc_species, x=x, y=y, z=0)
	objects.append(npc)
	print("a {} was created at {} {}".format(npc.type.species.name, npc.spacial.position.x, npc.spacial.position.y))
	npc.dump()

# def createProjectile(source=None, dx=0, dy=0):
# 	projectile = Object(
# 			name='projectile', blocks=False,
# 			x=source.x, y=source.y,
# 			char='~', color=tcod.white,
# 			priority=99)

#############################################
# Initialization & Main Loop
#############################################

# tcod.console_set_custom_font('arial10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
console = Console()
# tcod.console_set_fullscreen(True)

# mixer.init()
# mixer.init()
# music = mixer.music.load('data/audio/{}'.format(audio))
# hurt_spider = mixer.Sound('data/audio/{}'.format('ouch.wav'))
# hurt_troll = mixer.Sound('data/audio/{}'.format('cough.wav'))

# create object representing the player
player_base = createPlayer(species='human', display_symbol='O', level=0)
player_base.type.stats.speed = 4
player = copy.deepcopy(player_base)

# create an NPC
# npc = Object(SCREEN_WIDTH // 2 - 5, SCREEN_HEIGHT // 2, '@', tcod.yellow)

# the list of objects with those two
objects = []
objects.append(player)

# generate map (at this point it's not drawn to the screen)
game_state = 'playing'
player_action = None
map_explorable = 0
map_explored = 0
fov_map = None
fov_recompute = True
fov_range = player.type.properties.sight
fov_flicker = 0
visibility_override = False
spawn_monsters = True
toggle_blinking = False
show_room_no = False
tick_counter = 0
tick_player = 0
move = False
show_fps = False

time_tick_pre = time.time()

makeMap()
makeFovMap()

if spawn_monsters:
	spawnMonsters()

'''
message = "You wake up..."
console.renderMessage(message=message, x=(SCREEN_WIDTH//2)-(len(message)//2), y=SCREEN_HEIGHT//2, transparent=False)
tcod.console_flush()
time.sleep(2)
console.renderErase()
tcod.console_flush()
# mixer.music.play(-1)
time.sleep(1)
'''

while not tcod.console_is_window_closed():
	map_explored_old = map_explored
	# render the screen
	console.renderAll(visibility=visibility_override)
	tcod.console_flush()

	if map_explored > map_explored_old:
		player.type.modifyExperience(amount=10, delta=True)

	if player.type.properties.health <= 0:
		message = "Y O U   D I E D . . ."
		console.renderMessage(message=message, x=(SCREEN_WIDTH//2)-(len(message)//2), y=SCREEN_HEIGHT//2, transparent=False)
		tcod.console_flush()
		# mixer.music.stop()
		time.sleep(2)
		tcod.console_wait_for_keypress(False)
		console.renderErase()
		tcod.console_flush()
		objects = []
		player = copy.deepcopy(player_base)
		objects.append(player)
		fov_map = None
		fov_recompute = True
		# tick_player = 0
		# tick_counter = 0
		makeMap()
		makeFovMap()

		message = "You wake up..."
		console.renderMessage(message=message, x=(SCREEN_WIDTH//2)-(len(message)//2), y=SCREEN_HEIGHT//2, transparent=False)
		tcod.console_flush()
		time.sleep(2)
		console.renderErase()
		tcod.console_flush()
		# mixer.music.play(-1)
		time.sleep(1)


	updateTickCounter()
	updateFovFlicker()

	# erase all objects at their old locations, before they move
	for object in objects:
		console.clear(object=object)
		# if object is not player:
		# 	object.char = object.char.upper()

	# handle keys and exit game if needed
	player_action = handleKeys()
	if player_action == 'exit':
		break
	elif player_action == 'pause':
		while handleKeys() is not 'pause':
			pass
	elif player_action in ['action', 'fatigued']:
		updateTickPlayer()

	# let monsters make their turn
	if (game_state is 'playing') and (player_action in ['action', 'fatigued']):
		for object in objects:
			if object.type.name is 'entity':
				if (object.type.type.name is not 'player') and object.type.alive:
					object.display_symbol = object.display_symbol.upper()
					takeTurn(object=object, tick=tick_player)
