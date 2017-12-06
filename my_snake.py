import random

import pygame, sys
from pygame.locals import *


# random.seed(a=1)



class Game():
	def __init__(self):
		self.state = 0

class Loader():
	def __init__(self):
		self.background = pygame.image.load('resources/plansza.png')
		self.splash = pygame.image.load('resources/splash.png')
		self.gameover = pygame.image.load('resources/gameover.png')
		self.bar = pygame.image.load('resources/bar1.png'),pygame.image.load('resources/bar2.png'),pygame.image.load('resources/bar3.png'),pygame.image.load('resources/bar4.png')
		self.bodyS = pygame.image.load('resources/bodyS1.png'),pygame.image.load('resources/bodyS2.png')
		self.bodyC = pygame.image.load('resources/bodyC1.png'),pygame.image.load('resources/bodyC2.png')
		self.headOpenS = pygame.image.load('resources/headOpenS.png')
		self.headClosedS = pygame.image.load('resources/headClosedS.png')
		self.headOpenC = pygame.image.load('resources/headOpenC.png')
		self.headClosedC = pygame.image.load('resources/headClosedC.png')
		self.tailS = pygame.image.load('resources/tailS.png')
		self.food = pygame.image.load('resources/x1.png'),pygame.image.load('resources/x2.png'),pygame.image.load('resources/x3.png'),pygame.image.load('resources/x4.png')

class Grid():
	def __init__(self,cell_width,cell_height,grid_width,grid_height,x_offset,y_offset):
		self.cell_width = cell_width
		self.cell_height = cell_height
		self.grid_width = grid_width
		self.grid_height = grid_height
		self.x_offset = x_offset
		self.y_offset = y_offset


		self.generate_new()

	def __iter__(self):
		for cell in self.cells:
			yield cell

	def get_cell_by_coords(self,x,y):
		return self.cells[x + y * self.grid_width]

	def set_cell(self,x,y,value):
		self.cells[x + y * self.grid_width] = value

	def get_cell_pos_by_coords(self,x,y):
		return (self.x_offset+x*self.cell_width,self.y_offset+y*self.cell_height)

	def get_cell_pos_by_idx(self,idx):
		return self.get_cell_pos_by_coords(*self.converse_idx_to_coords(idx))

	def converse_coords_to_idx(self,x,y):
		idx = x + y * self.grid_width
		return idx

	def converse_idx_to_coords(self,idx):
		x = idx % self.grid_width
		y = idx // self.grid_width
		return (x,y)

	def is_border(self,idx):
		x,y, = self.converse_idx_to_coords(idx)
		if x == 0 or x == self.grid_width-1 or y == 0 or y == self.grid_height-1:
			return True
		return False

	def fill_borders(self):
		for idx,_ in enumerate(self):
			if self.is_border(idx):
				self.cells[idx] = 1

	def draw_cells(self,surface):
		for idx,cell in enumerate(self):
			if cell == 1:
				pos_x, pos_y = self.get_cell_pos_by_idx(idx)
				pygame.draw.rect(surface,(255,100,100), (pos_x+1, pos_y+1, self.cell_width-2, self.cell_height-2))


	def randomize_cells(self,density):
		for idx,cell in enumerate(self):
			if random.random()<density:
				if cell == 0:
					self.cells[idx] = 1

	def get_neighbours(self,idx,dist):
		x,y = self.converse_idx_to_coords(idx)
		neighbours=0
		for i in range(dist):
			if x+(i+1) < self.grid_width and self.get_cell_by_coords(x+(i+1),y) == 1:
				neighbours +=1
			if x-(i+1) >= 0 and  self.get_cell_by_coords(x-(i+1),y) == 1:
				neighbours +=1
			if y+(i+1) < self.grid_height and  self.get_cell_by_coords(x,y+(i+1)) == 1:
				neighbours +=1
			if y-(i+1) >= 0 and  self.get_cell_by_coords(x,y-(i+1)) == 1:
				neighbours +=1
		return neighbours

	def expand(self):
		tempCells = []
		for idx,cell in enumerate(self):
			if cell == 0 and not self.is_border(idx):
				if self.get_neighbours(idx,1)>1:
					tempCells.append(1)
				else:
					tempCells.append(0)
			else:
				tempCells.append(cell)
		self.cells = tempCells

	def shrink(self):
		tempCells = []
		for idx,cell in enumerate(self):
			if cell == 1 and not self.is_border(idx):
				if self.get_neighbours(idx,1)<2:
					tempCells.append(0)
				else:
					tempCells.append(1)
			else:
				tempCells.append(cell)
		self.cells = tempCells

	def find_islands(self):
		filled_islands = []
		empty_islands = []
		for idx, cell in enumerate(self):
			filed_islands = self.find_specific_islands(idx,cell,filled_islands,1)
			empty_islands = self.find_specific_islands(idx,cell,empty_islands,0)

		# print('filled = ',len(filled_islands))
		# print('empty = ',len(empty_islands))

		return(filled_islands,empty_islands)

	def find_specific_islands(self,idx,cell,islands,val):
		found = None
		double = None
		if cell == val:
			for island_number,island in enumerate(islands):
				if self.neighbours_in_island(idx,island):
					if found == None:
						found = island_number
						island.append(idx)
					else:
						double = island_number
			if found == None:
				islands.append([idx])
			elif double != None:
				islands[found].extend(islands.pop(double))
		return islands

	def neighbours_in_island(self,idx,island):
		if idx != self.grid_width and idx+1 in island:
			return True
		if idx != 0 and idx-1 in island:
			return True
		if idx//self.grid_width != self.grid_height and idx-self.grid_width in island:
			return True
		if idx//self.grid_width != 0 and idx+self.grid_width in island:
			return True
		return False

	def patch_holes(self,filled_islands,empty_islands):
		for island in filled_islands:
			if len(island) < 5:
				for cell in island:
					self.cells[cell] = 0
		max_len = 0
		max_island_idx = None
		for idx,island in enumerate(empty_islands):
			if len(island) > max_len:
				max_island_idx = idx
				max_len = len(island)

		for idx,island in enumerate(empty_islands):
			if idx != max_island_idx:
				for cell in island:
					self.cells[cell] = 1

	def generate_new(self):
		self.cells = [0]*self.grid_width*self.grid_height
		self.randomize_cells(0.1)
		self.fill_borders()
		for x in range(2):
			self.expand()
		self.patch_holes(*self.find_islands())

class Borders():
	def __init__(self,grid):
		self.generate(grid)

	def generate(self,grid):
		self.grid = grid
		self.borders = []

		for idx,cell in enumerate(grid.cells):
			if cell ==0:
				if self.grid.cells[idx+1] == 1:
					x,y = self.grid.get_cell_pos_by_idx(idx)
					x+= self.grid.cell_width -3
					y-= 3
					self.borders.append(Border((x,y),0,random.randrange(4)))	
				if self.grid.cells[idx-1] == 1:
					x,y = self.grid.get_cell_pos_by_idx(idx)
					x-= 3
					y-= 3
					self.borders.append(Border((x,y),0,random.randrange(4)))	
				if self.grid.cells[idx+self.grid.grid_width] == 1:
					x,y = self.grid.get_cell_pos_by_idx(idx)
					x-= 2
					y+= self.grid.cell_height -3
					self.borders.append(Border((x,y),90,random.randrange(4)))	
				if self.grid.cells[idx-self.grid.grid_width] == 1:
					x,y = self.grid.get_cell_pos_by_idx(idx)
					x-= 2
					y-= 3
					self.borders.append(Border((x,y),90,random.randrange(4)))	

	def draw(self,surface):
		for border in self.borders:
			border.draw(surface)

class Border():
	def __init__(self,position,rotation,idx):
		self.position = position
		self.rotation = rotation
		self.idx = idx

	def draw(self,surface):
		surface.blit(pygame.transform.rotate(loader.bar[self.idx],self.rotation),self.position)

class Snake():
	def __init__(self,grid):
		length = 0
		direction = None
		interval = 0
		last_action = 0
		self.spawn(grid)


	def spawn(self,grid):
		self.grid = grid
		self.head_cell = self.find_place_for_head()
		self.direction = self.randomize_direction()
		self.previous_direction = self.direction
		length = 3
		self.segment_cells = self.set_segments(length)
		self.interval = 500
		self.last_action = pygame.time.get_ticks()

	def find_place_for_head(self):
		cell = None
		while cell == None:
			candidate = random.randrange(len(self.grid.cells))
			if self.grid.cells[candidate] == 0 and self.grid.get_neighbours(candidate,5) == 0:
				cell = candidate
		return cell

	def randomize_direction(self):
		directionections = ['right','left','up','down']
		return directionections[random.randrange(4)]

	def move_idx(self,direction):
		if direction == 'right':
			return 1
		elif direction == 'left':
			return -1
		elif direction == 'up':
			return -1* self.grid.grid_width
		elif direction == 'down':
			return self.grid.grid_width

	def set_segments(self,length):
		segment_cells = []
		for i in range(length):
			segment_cells.append(self.head_cell - (length-i-1)*self.move_idx(self.direction))
		return segment_cells

	def move(self):
		self.segment_cells.append(self.segment_cells[len(self.segment_cells)-1] + self.move_idx(self.direction))
		self.previous_direction = self.direction
		
		if food.try_to_eat(self.segment_cells[len(self.segment_cells)-1]) == True:
			self.interval = self.interval*0.95
		else:
			self.segment_cells.pop(0)

		if self.grid.cells[self.segment_cells[len(self.segment_cells)-1]] == 1 or len(self.segment_cells) != len(set(self.segment_cells)):
			wait = max(250,self.interval)
			pygame.time.wait(int(wait))
			game.state = 2

	def update(self):
		if game.state ==1 and self.last_action + self.interval < pygame.time.get_ticks():
			self.last_action = pygame.time.get_ticks()
			self.move()


	def draw(self,surface):
		for idx,segment in enumerate(self.segment_cells):
			if idx == len(self.segment_cells)-1:
				self.draw_head(surface,idx,segment)
			elif idx == 0:
				self.draw_tail(surface,idx,segment)
			else:
				self.draw_body(surface,idx,segment)

	def draw_head(self,surface,idx,segment):
		x,y = self.grid.get_cell_pos_by_idx(segment)
		rotation = 0
		x_flip = False
		y_flip = False
		if self.check_food_on_spot(segment):
			img_S = loader.headOpenS
			img_C = loader.headOpenC
		else:
			img_S = loader.headClosedS
			img_C = loader.headClosedC
		img = img_S
		if self.check_touching_segment_orientation(idx,idx-1) == 'up':
			rotation = 0
			if self.direction == 'right':
				img = img_C
			if self.direction == 'left':
				img = img_C
				x_flip = True
		if self.check_touching_segment_orientation(idx,idx-1) == 'down':
			rotation = 180
			if self.direction == 'right':
				img = img_C
				x_flip = True
			if self.direction == 'left':
				img = img_C
		if self.check_touching_segment_orientation(idx,idx-1) == 'right':
			rotation = 270
			if self.direction == 'up':
				img = img_C
				x_flip = True
			if self.direction == 'down':
				img = img_C
		if self.check_touching_segment_orientation(idx,idx-1) == 'left':
			rotation = 90
			if self.direction == 'up':
				img = img_C
			if self.direction == 'down':
				img = img_C
				x_flip = True
		surface.blit(pygame.transform.rotate(pygame.transform.flip(img,x_flip,y_flip),rotation),self.grid.get_cell_pos_by_idx(segment))

	def draw_body(self,surface,idx,segment):
		x,y = self.grid.get_cell_pos_by_idx(segment)
		img = loader.bodyS[(segment//3)%2]
		if self.check_touching_segment_orientation(idx,idx+1) == 'up':
			rotation = 90
			if self.check_touching_segment_orientation(idx,idx-1) == 'right':
				img = loader.bodyC[(segment//3)%2]
			if self.check_touching_segment_orientation(idx,idx-1) == 'left':
				rotation = 180
				img = loader.bodyC[(segment//3)%2]
		if self.check_touching_segment_orientation(idx,idx+1) == 'down':
			rotation = 90
			if self.check_touching_segment_orientation(idx,idx-1) == 'right':
				rotation = 0
				img = loader.bodyC[(segment//3)%2]
			if self.check_touching_segment_orientation(idx,idx-1) == 'left':
				rotation = 270
				img = loader.bodyC[(segment//3)%2]
		if self.check_touching_segment_orientation(idx,idx+1) == 'right':
			rotation = 0
			if self.check_touching_segment_orientation(idx,idx-1) == 'up':
				rotation = 90
				img = loader.bodyC[(segment//3)%2]
			if self.check_touching_segment_orientation(idx,idx-1) == 'down':
				rotation = 0
				img = loader.bodyC[(segment//3)%2]
		if self.check_touching_segment_orientation(idx,idx+1) == 'left':
			rotation = 0
			if self.check_touching_segment_orientation(idx,idx-1) == 'up':
				rotation = 180
				img = loader.bodyC[(segment//3)%2]
			if self.check_touching_segment_orientation(idx,idx-1) == 'down':
				rotation = 270
				img = loader.bodyC[(segment//3)%2]

		surface.blit(pygame.transform.rotate(img,rotation),self.grid.get_cell_pos_by_idx(segment))

	def draw_tail(self,surface,idx,segment):
		x,y = self.grid.get_cell_pos_by_idx(segment)
		if self.check_touching_segment_orientation(idx,idx+1) == 'up':
			rotation = 0
		if self.check_touching_segment_orientation(idx,idx+1) == 'down':
			rotation = 180
		if self.check_touching_segment_orientation(idx,idx+1) == 'right':
			rotation = 270
		if self.check_touching_segment_orientation(idx,idx+1) == 'left':
			rotation = 90

		surface.blit(pygame.transform.rotate(loader.tailS,rotation),self.grid.get_cell_pos_by_idx(segment))

	def check_touching_segment_orientation(self,idx,other_idx):
		difference = self.segment_cells[idx] - self.segment_cells[other_idx]
		if difference == 1:
			return 'left'
		if difference == -1:
			return 'right'
		if difference == self.grid.grid_width:
			return 'up'
		if difference == -self.grid.grid_width:
			return 'down'

	def check_food_on_spot(self,segment):
		if self.direction == 'up' and food.cell == segment-self.grid.grid_width:
			return True
		if self.direction == 'down' and food.cell == segment+self.grid.grid_width:
			return True
		if self.direction == 'right' and food.cell == segment+1:
			return True
		if self.direction == 'left' and food.cell == segment-1:
			return True

class Food():
	def __init__(self,grid,snake):

		self.reset(grid,snake)

	def reset(self,grid,snake):
		self.grid = grid
		self.snake = snake
		self.cell = self.spawn()

	def spawn(self):
		self.idx = random.randrange(4)
		while 1:
			candidate = random.randrange(len(self.grid.cells))
			if self.grid.cells[candidate] == 0 and self.grid.get_neighbours(candidate,1) == 0 and candidate not in self.snake.segment_cells:
				return candidate

	def try_to_eat(self,snake_head):
		if snake_head == self.cell:
			self.cell = self.spawn()
			return True
		return False

	def draw(self,surface):
		surface.blit(loader.food[self.idx],self.grid.get_cell_pos_by_idx(self.cell))

def update_stuff():
	snake.update()

def reset():
	grid.generate_new()
	borders.generate(grid)
	snake.spawn(grid)
	food.reset(grid,snake)

def process_events(event):
	if event.type == KEYDOWN:
		if game.state==0:
			game.state = 1
			snake.last_action = pygame.time.get_ticks()
		elif game.state==1:
			if event.key == K_r:
				reset()
			elif event.key == K_RIGHT:
				if snake.previous_direction != 'left':
					snake.direction = 'right'
			elif event.key == K_LEFT:
				if snake.previous_direction != 'right':
					snake.direction = 'left'
			elif event.key == K_UP:
				if snake.previous_direction != 'down':
					snake.direction = 'up'
			elif event.key == K_DOWN:
				if snake.previous_direction != 'up':
					snake.direction = 'down'

		elif game.state==2:
			game.state = 1
			reset()

def draw_stuff(surface):
	surface.blit(loader.background,(0,0))

	if game.state==0:
		surface.blit(loader.splash,(0,0))

	elif game.state==1:
		# grid.draw_cells(surface)
		borders.draw(surface)
		snake.draw(surface)
		food.draw(surface)

	elif game.state==2:
		surface.blit(loader.gameover,(0,0))
	else:
		pass

	pygame.display.flip()

def run_game():
	
	pygame.init()
	pygame.mixer.quit()
	FPS = 30
	fpsClock = pygame.time.Clock()

	DISPLAYSURF = pygame.display.set_mode((640,480))

	

	pygame.display.set_caption('Wąż w zeszycie')
	while True:
		for event in pygame.event.get():
			#print('event: {}'.format(event))
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			process_events(event)
		update_stuff()
		draw_stuff(DISPLAYSURF)

	fpsClock.tick(FPS)

loader = Loader()
game = Game()
grid = Grid(13.9,13.9,40,28,40,56)
borders = Borders(grid)
snake = Snake(grid)
food = Food(grid,snake)

if __name__ == '__main__':
	run_game()