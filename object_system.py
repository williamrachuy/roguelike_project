
# coding: utf-8

# In[1]:


import random
import math
from pprint import pprint
from collections import Mapping, Set, Sequence 

QUANT_LVL = 1
MAX_FLOAT = 2**32
MIN_FLOAT = -(2**32)
PRI_LOW = 30
PRI_MED = 20
PRI_HIGH = 10

list_object_types	= ['unknown', 'entity', 'item', 'structure']
list_entity_species	= ['unknown', 'human', 'elf', 'dwarf', 'orc', 'troll', 'wraith']

equipment_dict = {
	'head'					: None,
	'face'					: None,
	'neck'					: None,
	'shirt'					: None,
	'coat'					: None,
	'back'					: None,
	'chest_armor'			: None,
	'shoulder_left_armor'	: None,
	'shoulder_right_armor'	: None,
	'arm_upper_left_armor'	: None,
	'arm_upper_right_armor'	: None,
	'arm_lower_left_armor'	: None,
	'arm_lower_right_armor'	: None,
	'wrist_left'			: None,
	'wrist_right'			: None,
	'hand_left'				: None,
	'hand_right'			: None,
	'finger_left_1'			: None,
	'finger_left_2'			: None,
	'finger_left_3'			: None,
	'finger_left_4'			: None,
	'finger_left_5'			: None,
	'finger_right_1'		: None,
	'finger_right_2'		: None,
	'finger_right_3'		: None,
	'finger_right_4'		: None,
	'finger_right_5'		: None,
	'waist'					: None,
	'legs'					: None,
	'leg_upper_left_armor'	: None,
	'leg_upper_right_armor'	: None,
	'leg_lower_left_armor'	: None,
	'leg_lower_right_armor'	: None,
	'ankle_left'			: None,
	'ankle_right'			: None,
	'foot_left'				: None,
	'foot_right'			: None,
	'foot_left_armor'		: None,
	'foot_right_armor'		: None,
	'storage_shoulder'		: None,
	'storage_back'			: None,
	'storage_waist'			: None,
	'storage_leg_left'		: None,
	'storage_leg_right'		: None,
}

entity_stats_dict = {
	'unknown': {
		'strength'		: 0,
		'intelligence'	: 0,
		'agility'		: 0,
		'speed'			: 0,
		'endurance'		: 0,
		'personality'	: 0,
		'luck'			: 0,
		'perception'	: 0,
	},
	'human': {
		'strength'		: 11,
		'intelligence'	: 11,
		'agility'		: 11,
		'speed'			: 11,
		'endurance'		: 11,
		'personality'	: 11,
		'luck'			: 11,
		'perception'	: 11,
	},
	'elf': {
		'strength'		: 12,
		'intelligence'	: 12,
		'agility'		: 15,
		'speed'			: 4,
		'endurance'		: 20,
		'personality'	: 8,
		'luck'			: 5,
		'perception'	: 10,
	}
}

object_priority_dict = {
	'unknown'		: PRI_LOW,
	'human'			: PRI_HIGH,
	'elf'			: PRI_HIGH,
	'dwarf'			: PRI_HIGH + 1,
}

physical_unknown = {
	'mass'		: 0,
	'volume'	: 0,
	'opacity'	: 0,
	'solid'		: False,
	'stationary': False,
}


object_physical_dict = {
	'unknown': {
		'unknown'		: physical_unknown,
	},
	'entity': {
		'unknown'		: physical_unknown,
		'human': {
			'mass'		: 70000,
			'volume'	: 100,
			'opacity'	: 100,
			'solid'		: True,
			'stationary': False,
		},
		'elf': {
			'mass'		: 60000,
			'volume'	: 95,
			'opacity'	: 100,
			'solid'		: True,
			'stationary': False,
		},
	},
	'item': {
		'unknown'		: physical_unknown,
	},
	'structure': {
		'unknown'		: physical_unknown,
		'wall': {
			'mass'		: 200000,
			'volume'	: 1000,
			'opacity'	: 100,
			'solid'		: True,		
			'stationary': True,
		},
		'ground': {
			'mass'		: 1000,
			'volume'	: 100,
			'opacity'	: 0,
			'solid'		: False,
			'stationary': True,		
		},
	}
}

entity_nature_dict = {
	'unknown': {
		'unknown'	: 0,
		'human'		: 0,
		'elf'		: 0,
		'dwarf'		: 0,
		'orc'		: 0,
		'troll'		: 0,
		'wraith'	: 0,
	},
	'human': {
		'unknown'	: 0,
		'human'		: 90,
		'elf'		: 60,
		'dwarf'		: 60,
		'orc'		: -80,
		'troll'		: -60,
		'wraith'	: -100,
	},
	'elf': {
		'unknown'	: 0,
		'human'		: 80,
		'elf'		: 100,
		'dwarf'		: 20,
		'orc'		: -100,
		'troll'		: -50,
		'wraith'	: -100,
	},
}


# In[2]:


def errorMessage(method='unknown method', message="Error message not set"):
	print("Error in {0}: {1}".format(method, message))
	
def dump(obj, obj_name=None, level=0):
	if obj_name is None:
		obj_name = obj.name
	vars_dict = vars(obj)
	for var_str in vars_dict:
		value = vars_dict[var_str]
		print("{}{}.{}={}".format('\t'*level, obj_name, var_str, value))
		if isinstance(value, (Entity, Item, Structure, Spacial, Coord, Physical, Npc, Player, EntityStats,
				EntityProperties, Human, Elf, Dwarf, Orc, Troll, Wraith, EntityUnknown)):
			dump(obj=value, obj_name=var_str, level=level+1)

def isBlocked(x=0, y=0, z=0, map=[], objects=[]):
	# print(x, y)
	if map[int(x)][int(y)].physical.solid:
		return True
	for object in objects:
		if object.physical.solid and object.spacial.position.x == x and object.spacial.position.y == y:
			return True
	return False


# In[3]:


class Object:
	def __init__(self, type=None, stationary=False, visible=True, spacial=None,
				physical=None, exists=True, blinking=False, priority=PRI_LOW):
		self.name		= 'object'
		self.color		= 'white'
		self.symbol		= 'O'
		self.visible	= visible
		self.exists		= exists
		self.blinking	= blinking
		self.priority	= priority

		self.setType(type=type, recalc=False)
		self.physical	= physical
		self.spacial	= spacial
		if self.physical is None:
			self.physical	= Physical()
		if self.spacial is None:
			self.spacial	= Spacial()
		self.calcPhysical()
		self.display_symbol = self.getDisplaySymbol()
		self.display_color	= self.getDisplayColor()
		self.explored		= False
		
	def setType(self, type=None, recalc=True):
		if isinstance(type, str):
			if type is 'entity':
				self.type = Entity()
			elif type is 'item':
				self.type = Item()
			elif type is 'structure':
				self.type = Structure()
			else:
				self.type = None
				errorMessage(method=self.setType.__name__, message="Type '{}' not recognized".format(type))
		else:
			self.type = type
		if recalc:
			self.calcPhysical()
		return self.type

	def makeEntity(self, type='npc', species='unknown'):
		self.type = Entity(type=type, species=species)
		self.calcPhysical()
		self.display_symbol = self.getDisplaySymbol()
		self.display_color	= self.getDisplayColor()
		return self.type

	def makeItem(self, species='unknown'):
		self.type = Item(species=species)
		self.calcPhysical()
		self.display_symbol = self.getDisplaySymbol()
		self.display_color	= self.getDisplayColor()
		return self.type

	def makeStructure(self, type='tile', species='unknown'):
		self.type = Structure(type=type, species=species)
		self.calcPhysical()
		self.display_symbol = self.getDisplaySymbol()
		self.display_color	= self.getDisplayColor()
		return self.type
	
	def getMomentum(self):
		mass = self.physical.mass
		velocity = self.spacial.velocity
		x = mass * velocity.x
		y = mass * velocity.y
		z = mass * velocity.z
		return (x, y, z)

	def setPosition(self, x=0, y=0, z=0, delta=False):
		pos = self.spacial.position
		if delta:
			x = pos.x + x
			y = pos.y + y
			z = pos.z + z
		pos.x = x
		pos.y = y
		pos.z = z
		return True

	def move(self, dx=0, dy=0, dz=0, map=[], objects=[]):
		if self.physical.stationary:
			return False
		self.display_symbol = self.getDisplaySymbol().lower()
		pos = self.spacial.position
		if not isBlocked(x=(pos.x + dx), y=(pos.y + dy), z=(pos.z + dz), map=map, objects=objects):
			self.setPosition(x=dx, y=dy, z=dz, delta=True)
			return True
		if not isBlocked(x=(pos.x + dx), y=(pos.y + 0), z=(pos.z + dz), map=map, objects=objects):
			self.setPosition(x=dx, y=0, z=dz, delta=True)
			return True
		if not isBlocked(x=(pos.x + 0), y=(pos.y + dy), z=(pos.z + dz), map=map, objects=objects):
			self.setPosition(x=0, y=dy, z=dz, delta=True)
			return True
		return False

	def face(self, dx=0, dy=0, dz=0):
		self.setDirection(x=dx, y=dy, z=dz)
		return True

	def setDirection(self, x=0, y=0, z=0, delta=False):
		dir = self.spacial.direction
		if delta:
			x = dir.x + x
			y = dir.y + y
			z = dir.z + z
		dir.x = x
		dir.y = y
		dir.z = z
		return True

	def setVelocity(self, delta=False, x=0, y=0, z=0):
		vel = self.spacial.velocity
		if delta:
			x = vel.x + x
			y = vel.y + y
			z = vel.z + z
		vel.x = x
		vel.y = y
		vel.z = z
		return True
	
	def dump(self):
		n = 16
		print("\n{} DUMPING OBJECT {}\n{}\n{}\n".format('='*n, '='*n, self, '=' * (2*n + 16)))
		dump(obj=self, obj_name=self.name)
		print('\n')

	def calcPhysical(self):
		if self.type is None:
			return
		physical_dict = physical_unknown
		if self.type.name in list_object_types:
			if self.type.name is 'entity':
				physical_dict = object_physical_dict[self.type.name][self.type.species.name] #[self.type.species.race.name]
			elif self.type.name is 'item':
				pass
			elif self.type.name is 'structure':
				physical_dict = object_physical_dict[self.type.name][self.type.species.name] #[self.type.species.material.name]
			else:
				print("unknwon object type while calculating physical properties")
		else:
			errorMessage(method=self.calcPhysical.__name__, message="Object type '{}' not recognized".format(object.type))
		self.physical.mass			= physical_dict['mass']
		self.physical.volume		= physical_dict['volume']
		self.physical.opacity		= physical_dict['opacity']
		self.physical.solid			= physical_dict['solid']
		self.physical.stationary	= physical_dict['stationary']
		return self.physical

	def getDisplaySymbol(self):
		if self.type is None:
			return 'U'
		elif self.type.name is 'entity':
			return self.type.getDisplaySymbol()
		elif self.type.name is 'item':
			return 'I'
		elif self.type.name is 'structure':
			return self.type.getDisplaySymbol()
		else:
			return 'U'

	def getDisplayColor(self):
		if self.type is None:
			return 'white'
		elif self.type.name is 'entity':
			return self.type.getDisplayColor()
		elif self.type.name is 'item':
			return 'blue'
		elif self.type.name is 'structure':
			return self.type.getDisplayColor()
		else:
			return 'white'

	def updateObject(self):
		if self.type.name is 'entity':
			if self.type.properties.health == 0:
				self.type.die()
			if self.type.alive:
				self.display_symbol = self.getDisplaySymbol().upper()
				self.display_color = self.getDisplayColor()
				# self.blinking = False
				# if self.type.properties.health < (0.10 * self.type.properties._health):
				# 	self.blinking = True
				self.type.properties.movement = self.type.properties._movement
				if self.type.properties.stamina < (0.20 * self.type.properties._stamina):
					self.type.properties.movement = self.type.properties._movement * 2
			else:
				self.display_symbol = self.getDisplaySymbol().lower()
				self.display_color = 'grey'
				# self.blinking = False
				self.priority = PRI_LOW
				self.physical.solid = False
		elif self.type.name is 'item':
			pass
		elif self.type.name is 'structure':
			self.display_symbol = self.getDisplaySymbol()
			self.display_color = self.getDisplayColor()


# In[4]:

''' Object Type '''
class Entity:
	def __init__(self, type='npc', alive=True, species='unknown', stats=None):
		self.name		= 'entity'
		self.symbol		= 'E'
		self.color		= 'white'
		self.alive		= alive
		self.storage	= []
		self.equipment	= equipment_dict
		self.setType(type=type)
		self.setSpecies(species=species, recalc=False)  # False?
		species_name	= self.species.name
		species_symbol	= self.species.symbol
		species_color	= self.species.color

		if stats is None:
			stats = species
		self.setEntityStats(stats=stats)
		self.setEntityProperties(name=species_name, symbol=species_symbol, color=species_color)
		self.calcEntityProperties(immediate=True)
		
	def setType(self, type=None):
		if type is 'npc':
			self.type = Npc()
		elif type is 'player':
			self.type = Player()
		else:
			self.type = None
			errorMessage(method=self.setType.__name__, message="Type '{}' not recognized".format(type))        
		return self.type
	
	def setSpecies(self, species=None, recalc=True, immediate=False):
		if   species is 'human':
			self.species = Human()
		elif species is 'elf':
			self.species = Elf()
		elif species is 'dwarf':
			self.species = Dwarf()
		elif species is 'orc':
			self.species = Orc()
		elif species is 'troll':
			self.species = Troll()
		elif species is 'wraith':
			self.species = Wraith()
		else:
			self.species = EntityUnknown()
			errorMessage(method=self.setSpecies.__name__, message="Species '{}' not recognized".format(species))
		if recalc:
			species_name		= self.species.name
			species_symbol		= self.species.symbol
			species_color		= self.species.color
			self.setEntityStats(stats=species_name)
			self.setEntityProperties(name=species_name, symbol=species_symbol, color=species_color)
			self.calcEntityProperties(immediate=immediate)
		return self.species
	
	def setEntityStats(self, stats=None):
		if   stats in list_entity_species:
			self.stats = EntityStats(stats_dict=entity_stats_dict[stats])
		else:
			self.stats = EntityStats(stats_dict=entity_stats_dict['unknown'])
			errorMessage(method=self.setEntityStats.__name__, message="Species '{}' not recognized".format(stats))
		return self.stats

	def setEntityProperties(self, name=None, symbol=None, color=None):
		self.properties = EntityProperties(name=name, symbol=symbol, color=color, nature_dict=entity_nature_dict[name])
		return self.properties

	def calcEntityProperties(self, immediate=False):
		p = self.properties
		s = self.stats
		p._health	= int(round((s.strength + s.endurance) * (1 + s.level / s.level_base)))
		p._essence	= int(round(s.intelligence * (1 + s.level / s.level_base)))
		p._stamina	= int(round((s.strength + s.endurance) * (1 + s.level / s.level_base)))
		p._damage	= int(round((s.strength + s.agility) * (1 + s.level / s.level_base)))
		p._armor	= int(round(s.endurance * (1 + s.level / s.level_base)))
		p._regen	= int(round((30 / (s.agility + s.endurance + s.luck)) * (1 + s.level / s.level_base)))
		p._capacity	= int(round((s.strength + s.endurance) * (1 + s.level / s.level_base)))
		p._sight	= int(round(s.perception * (1 + s.level / s.level_base)))
		p._activity	= int(round(s.agility + s.speed + s.endurance))
		p._movement	= int(round(s.speed / (1 + s.level / (s.level_base + s.level))))
		if immediate:
			p.health	= p._health
			p.essence	= p._essence
			p.stamina	= p._stamina
			p.damage	= p._damage
			p.armor		= p._armor
			p.regen		= p._regen
			p.capacity	= p._capacity
			p.sight		= p._sight
			p.activity	= p._activity
			p.movement	= p._movement

	def calcEntityStats(self):
		#self.stats.level = int(math.log(self.stats.experience + 1, self.stats.level_base))
		self.stats.level = self.calcLevel()

	def calcLevel(self, experience=None):
		if experience is None:
			experience = self.stats.experience
		return int((1 / 200) * experience)

	def calcExperience(self, level=None):
		if level is None:
			level = self.stats.level
		return 200 * level

	def changeProperties(self, type=[], amount=0, delta=False, max=False):
		if 'health' in type:
			health = amount
			if delta:
				health += self.properties.health
			if max:
				health = self.properties._health
			self.properties.health = health
		if 'essence' in type:
			essence = amount
			if delta:
				essence += self.properties.essence
			if max:
				essence = self.properties._essence
			self.properties.essence = essence
		if 'stamina' in type:
			stamina = amount
			if delta:
				stamina += self.properties.stamina
			if max:
				stamina = self.properties._stamina
			self.properties.stamina = stamina

	def changeStats(self, type=[], amount=0, delta=False):
		if 'experience' in type:
			experience = amount
			if delta:
				experience += self.stats.experience
			self.stats.experience = experience
		if 'level' in type:
			level = amount
			if delta:
				level += self.stats.level
			self.stats.level = level

	def heal(self, type=[], amount=0, max=False):
		self.changeProperties(type=type, amount=amount, delta=True, max=max)
		p = self.properties
		if p.health > p._health:
			p.health = p._health
		if p.essence > p._essence:
			p.essence = p._essence
		if p.stamina > p._stamina:
			p.stamina = p._stamina

	def harm(self, type=[], amount=0, max=False):
		self.changeProperties(type=type, amount=-amount, delta=True, max=max)
		p = self.properties
		if p.health < 0:
			p.health = 0
		if p.essence < 0:
			p.essence = 0
		if p.stamina < 0:
			p.stamina = 0

	def modifyExperience(self, amount=0, delta=True):
		s = self.stats
		level_pre = s.level
		self.changeStats(type=['experience'], amount=amount, delta=delta)
		if s.experience < 0:
			s.experience = 0
		self.calcEntityStats()
		level_post = s.level
		if level_post > level_pre:
			self.calcEntityProperties(immediate=True)
			return True
		self.calcEntityProperties(immediate=False)
		return False

	def die(self):
		self.alive = False

	def getDisplaySymbol(self):
		return self.properties.symbol

	def getDisplayColor(self):
		return self.properties.color

	def makePlayer(self):
		self.properties.name	= self.type.name
		self.properties.symbol	= self.type.symbol
		self.properties.color	= self.type.color


''' Object Type '''			
class Item:
	def __init__(self):
		self.name	= 'item'
		self.symbol	= 'I'
		self.color	= 'white'
	

''' Object Type '''
class Structure:
	def __init__(self, type=None, species=None):
		self.name	= 'structure'
		self.symbol	= 'S'
		self.color	= 'white'

		self.type		= None
		self.species	= None
		self.setType(type=type)
		self.setSpecies(species=species)

	def setType(self, type=None):
		if type is 'tile':
			self.type = Tile()
		elif type is 'symbol':
			self.type = Symbol()
		else:
			self.type = None
			errorMessage(method=self.setType.__name__, message="Type '{}' not recognized".format(type))
		return self.type

	def setSpecies(self, species=None):
		if species is 'wall':
			self.species = Wall()
		elif species is 'ground':
			self.species = Ground()
		else:
			self.species = None
			errorMessage(method=self.setSpecies.__name__, message="Species '{}' not recognized".format(species))
		return self.species

	def getDisplaySymbol(self):
		symbol = '?'
		if self.type.name is 'tile':
			symbol = ' '
		elif self.type.name is 'symbol':
			symbol = self.species.display_symbol
		else:
			errorMessage(method=self.getDisplaySymbol.__name__, message="Type '{}' not recognized".format(self.type))
		return symbol

	def getDisplayColor(self):
		color = 'white'
		return self.species.display_color

class Tile:
	def __init__(self):
		self.name	= 'tile'
		self.symbol = 'T'
		self.color	= 'white'

	def getDisplaySymbol(self):
		return ' '

class Symbol:
	def __init__(self):
		self.name	= 'symbol'
		self.symbol	= 'S'
		self.color	= 'white'

class Wall:
	def __init__(self):
		self.name	= 'wall'
		self.symbol = 'W'
		self.color	= 'white'

		self.display_symbol	= '#'
		self.display_color	= 'grey'

class Ground:
	def __init__(self):
		self.name	= 'ground'
		self.symbol = 'G'
		self.color	= 'white'

		self.display_symbol	= '.'
		self.display_color	= 'dark grey'


# In[10]:


''' Entity Type '''
class Npc:
	def __init__(self):
		self.name	= 'npc'
		self.symbol	= 'N'
		self.color	= 'white'
	

''' Entity Type '''
class Player:
	def __init__(self):
		self.name	= 'player'
		self.symbol	= 'P'
		self.color	= 'yellow'
		

''' Entity Object '''
class EntityStats:
	def __init__(self, stats_dict=entity_stats_dict['unknown'], experience=0, level=0, level_base=4, unspent=0):
		self.strength		= stats_dict['strength']
		self.intelligence	= stats_dict['intelligence']
		self.agility		= stats_dict['agility']
		self.speed			= stats_dict['speed']
		self.endurance		= stats_dict['endurance']
		self.personality	= stats_dict['personality']
		self.luck			= stats_dict['luck']
		self.perception		= stats_dict['perception']

		self.experience		= experience
		self.level			= level
		self.level_base		= level_base

		self.unspent		= unspent

''' Entity Object '''
class EntityProperties:
	def __init__(self, name='unknown', symbol='U', color='white', health=0, essence=0, stamina=0, damage=0, armor=0, regen=0,
			capacity=0, sight=0, activity=0, movement=0, nature_dict=entity_nature_dict['unknown']):
		self.name	= name
		self.symbol	= symbol
		self.color	= color

		self.health = self._health		= health
		self.essence = self._essence	= essence
		self.stamina = self._stamina	= stamina
		self.damage = self._damage		= damage
		self.armor = self._armor		= armor
		self.regen = self._regen		= regen
		self.capacity = self._capacity	= capacity
		self.sight = self._sight		= sight
		self.activity = self._activity	= activity
		self.movement = self._movement	= movement

		self.nature						= nature_dict

		
class Human:
	def __init__(self):
		self.name	= 'human'
		self.symbol	= 'H'
		self.color	= 'orange'
		
class Elf:
	def __init__(self):
		self.name	= 'elf'
		self.symbol	= 'E'
		self.color	= 'yellow'
		
class Dwarf:
	def __init__(self):
		self.name	= 'dwarf'
		self.symbol	= 'D'
		self.color	= 'white'
		
class Orc:
	def __init__(self):
		self.name	= 'orc'
		self.symbol	= 'O'
		self.color	= 'white'
		
class Troll:
	def __init__(self):
		self.name	= 'troll'
		self.symbol	= 'T'
		self.color	= 'white'
	
class Wraith:
	def __init__(self):
		self.name	= 'wraith'
		self.symbol	= 'W'
		self.color	= 'white'

class EntityUnknown:
	def __init__(self):
		self.name	= 'unknown'
		self.symbol	= 'U'
		self.color	= 'white'
	


# In[6]:


class Coord:
	def __init__(self, x=0, y=0, z=0):
		self.x = x
		self.y = y
		self.z = z

		
class Spacial:
	def __init__(self, position=Coord(0, 0, 0), direction=Coord(0, 0, 0), velocity=Coord(0, 0, 0)):
		
		self.position = position
		self.direction = direction
		self.velocity = velocity
	
	def randomize(self, position=None, direction=None, velocity=None, all=None):
		if all is not None:
			position = direction = velocity = all
		
		if position is not None:
			self.position.x		= random.uniform(position[0], position[1])
			self.position.y		= random.uniform(position[0], position[1])
			self.position.z		= random.uniform(position[0], position[1])
		if direction is not None:
			self.direction.x	= random.uniform(direction[0], direction[1])
			self.direction.y	= random.uniform(direction[0], direction[1])
			self.direction.z	= random.uniform(direction[0], direction[1])
		if velocity is not None:
			self.velocity.x		= random.uniform(velocity[0], velocity[1])
			self.velocity.y		= random.uniform(velocity[0], velocity[1])
			self.velocity.z		= random.uniform(velocity[0], velocity[1])
			
	def getPosition(self):
		x = self.position.x
		y = self.position.y
		z = self.position.z
		return (x, y, z)
			
	def getDirection(self):
		x = self.direction.x
		y = self.direction.y
		z = self.direction.z
		return (x, y, z)
			
	def getVelocity(self):
		x = self.velocity.x
		y = self.velocity.y
		z = self.velocity.z
		return (x, y, z)

		
class Physical:
	def __init__(self, mass=0, volume=0, opacity=0, solid=False, stationary=False):
		
		self.mass		= mass
		self.volume		= volume
		self.opacity	= opacity
		self.solid		= solid
		self.stationary	= stationary
		
	def randomize(self, mass=None, volume=None, opacity=False, solid=False, all=None):
		if all is not None:
			mass = volume = all
			opacity = solid = True            
		if mass is not None:
			self.mass = random.uniform(mass[0], mass[1])
		if volume is not None:
			self.volume = random.uniform(volume[0], volume[1])
		if opacity is True:
			self.opacity = random.choice([True, False])
		if solid is True:
			self.solid = random.choice([True, False])


def createNpc(species, x=0, y=0, z=0):
	object = Object()
	object.makeEntity(species=species)
	object.setPosition(delta=False, x=x, y=y, z=z)
	return object

def createPlayer(species, display_symbol='@', level=0, x=0, y=0, z=0):
	object = Object()
	object.makeEntity(type='player', species=species)
	object.type.makePlayer()
	object.priority = 0
	object.type.properties.symbol = display_symbol
	level_xp = object.type.calcExperience(level=level)
	object.type.modifyExperience(amount=level_xp, delta=False)
	object.setPosition(delta=False, x=x, y=y, z=z)
	object.updateObject()
	return object

def createTile(species, x=0, y=0, z=0):
	object = Object()
	object.makeStructure(type='tile', species=species)
	object.setPosition(delta=False, x=x, y=y, z=z)
	return object

def createSymbol(species, x=0, y=0, z=0):
	object = Object()
	object.makeStructure(type='symbol', species=species)
	object.setPosition(delta=False, x=x, y=y, z=z)
	return object

if __name__ == '__main__':
	print('running script')

	print("Creating human player...")
	player = createPlayer(species='human', x=10, y=20, z=30)
	player.dump()

	print('\n'*4)

	print("Creating ground tile...")
	tile = createTile(species='ground', x=20, y=30, z=40)
	tile.dump()

	print('\n'*4)

	print("Creating wall symbol...")
	tile = createSymbol(species='wall', x=30, y=40, z=50)
	tile.dump()