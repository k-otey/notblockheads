import this
import pygame, math, queue
import numpy as np
import opensimplex as simplex
from pygame.math import Vector2 
from PIL import Image

print("numpy version: " + np.__version__)

'''
doc:
-WASD movement
-space fly, crouch
-Q change block
-left click place block

# plans:
# grid class
    # infinite terrain
        # chunk terrain system
            3rd chunk and onwards collision broken???
            when hovering, there are still two 99's 
            
            # chunk loading system
                # load chunk based on player position
            #pointers???

            generate terrain for 2nd chunk/
            # fix block 99 of chunk being glitched/
                2nd chunk selection offset 1 block to right/
                
                # because there are 2 block 99's/
                # block 99 is drawn over???/
            # fix block 199 being "nothing"/
    # rendering
        # texture rendering for blocks
    # infinite pathfinding
        # adapt pathfinding for infinite terrain
    # fix player movement between chunks

    
    # position chunk based on chunk number /
    # infinite perlin noise grid /
    # query noise for specific coordinate in infinite perlin noise grid /



    
# camera class
    # FIX CAMERA DRAG
    # smooth draggable camera
    # camera zoom
    
        # adjust hoveredCell with zoom/
        # adjust cell padding with zoom /
        # adjust position of squares /
        # make squares smaller /
# rendering
#   - render with OpenGL for better performance
#   - other optimizations i don't know
# player class
    # player movement
        
        # crouch is disabled temporarily, fix crouching

        # player can climb walls taller than 1 block by pressing right or left movement keys /
        # make player follow pathfinding path /
    # player rendering
        # fix crouched player rendering
        # render player properly
    
    # queue player actions (block breaking, building, moving)
    # limit player building range

    


 done
 terrain editing
 14-7-2025
 player controller; simple crouching
 ??-?-????
 gravity
 grid class
 terrain generation limited with perlin noise
 player controller; climbing
 prevent crash at edge of map
 fix player crouch error
 semi draggable camera
 draggable camera with save pos thing
'''

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0,255,0)
BLUE = (0,0,255)
PURPLE = (255,0,255)
BROWN = (68,56,55)

BEDROCK = (102,90,133)
BLOCK_NAMES = ["air","solid","bedrock"]
COLORS = [WHITE,RED,BEDROCK]

# initialize pygame
pygame.init()
screen_size = (1920, 1080)
  
# create a window
screen = pygame.display.set_mode(screen_size)
screen_rect = screen.get_rect()
pygame.display.set_caption("pygame Test")
  
# clock is used to set a max fps
clock = pygame.time.Clock()

# assets
# asurf = pygame.image.load(os.path.join('data', 'bla.png'))

my_font = pygame.font.SysFont('Comic Sans MS', 30)
def updateText(text):
    return my_font.render(text, False, GREEN)

text_surface = updateText("air")
text_surface2 = updateText("hover: ")
text_surface3 = updateText("playerChunkNumber: ")

smile = pygame.image.load('10x10 smile.png').convert()

# IMAGE = pg.image.load('an_image.png').convert()  # or .convert_alpha()
# Create a rect with the size of the image.
smileRect = smile.get_rect()
smileRect.center = (200, 300)

# create a demo surface, and draw a red line diagonally across it
#surface_size = (25, 45)
test_surface = pygame.Surface([25,45])
test_surface_rect = test_surface.get_rect(center=screen_rect.center)
test_surface.fill(WHITE)

class Camera:
    # to implement, smooth camera drag
    def __init__(self):
        self.position = Vector2(0,0)
        self.zoom = 1
        
        self.goalPosition = Vector2(0,0)
        self.goalZoom = 1

camera = Camera()

# new grid class in development
class GridCell:
    def __init__(self):
        self.grid = None
        self.cellSize = None
        self.gridPosition = None
        self.path = False
        self.elementData = 0
    def render(self, offset):
        renderColor = COLORS[self.elementData]

        if self.path == True:
            renderColor = BROWN

        if self.grid.chunkNumber == 0:
            screenPosition = (
                self.grid.cellPadding*(self.gridPosition[0]) + self.cellSize*(self.gridPosition[0]) + offset[0],
                self.grid.cellPadding*(self.gridPosition[1]) + self.cellSize*(self.gridPosition[1]) + offset[1]
            )
        elif self.grid.chunkNumber > 0:
            screenPosition = (
                self.grid.cellPadding*(self.gridPosition[0]+1) + self.cellSize*(self.gridPosition[0]+1) + offset[0],
                self.grid.cellPadding*(self.gridPosition[1]) + self.cellSize*(self.gridPosition[1]) + offset[1]
            )
        
        #if (not screenPosition[0] >= screen_size[0]+25) and (not screenPosition[1] >= screen_size[1]+25) and (not screenPosition[0] <= 0-25) and (not screenPosition[1] <= 0-25):
        viewPos = Vector2(screenPosition[0],screenPosition[1])/camera.zoom
        gridCellRect = pygame.Rect((viewPos),(self.cellSize/camera.zoom,self.cellSize/camera.zoom))
        pygame.draw.rect(screen,renderColor,gridCellRect)

class GridClass:
    #grid class with cells as cell class
    def __init__(self,gridDimensions,cellSize, chunkNumber):
        self.cellPadding = 5
        self.cells = []
        self.cellSize = cellSize
        self.dimensions = gridDimensions
        self.chunkNumber = chunkNumber
        
        for row in range(gridDimensions[0]):
            currentRow = []
            for column in range(gridDimensions[1]):
                currentGridCell = GridCell()
                currentGridCell.grid = self
                currentGridCell.cellSize = 20
##                if self.chunkNumber > 0:
##                    currentGridCell.gridPosition = (row+(self.chunkNumber*99),column)
##                else:
##                    currentGridCell.gridPosition = (row+(self.chunkNumber*99),column)
                currentGridCell.gridPosition = (row+(self.chunkNumber*99),column)
                
                currentRow.append(currentGridCell)
            self.cells.append(currentRow)
    def getCell(self,coordinate):
        if coordinate[0] >= 0 and coordinate[0] <= grid.dimensions[0]-1 and coordinate[1] >= 0 and coordinate[1] <= grid.dimensions[1]-1:
            return self.cells[coordinate[0]][coordinate[1]]
    def render(self, offset):        
        for row in self.cells:
            for cell in row:
                cell.render(offset)

def gridSelectionUpdate():
    hoveredCoords = (0,0)
    mousePos = mouse.get_pos()
    mouseGridX = math.floor((mousePos[0]-camera.position[0]/camera.zoom)/(grid.cellSize+grid.cellPadding)*camera.zoom)
    mouseGridY = math.floor((mousePos[1]-camera.position[1]/camera.zoom)/(grid.cellSize+grid.cellPadding)*camera.zoom)
    selectionRect = pygame.Rect(
        (mouseGridX*grid.cellSize + (mouseGridX*grid.cellPadding) +camera.position[0])/camera.zoom,
        (mouseGridY*grid.cellSize + (mouseGridY*grid.cellPadding) +camera.position[1])/camera.zoom,
        grid.cellSize/camera.zoom,grid.cellSize/camera.zoom
        )
    pygame.draw.rect(screen, GREEN, selectionRect) # selection rectangle
    
    if isLeftMousePressed:
        if -1 < mouseGridX < len(chunks)*100:
            if mouseGridY < 99*len(chunks):
                selectedCell = getCell((mouseGridX,mouseGridY))

                if selectedCell and selectedCell.elementData != 2 and selected_block_index != 2:
                    selectedCell.elementData = selected_block_index
                else:                    print("bedrock")
    hoveredCoords = (mouseGridX,mouseGridY)
    return hoveredCoords


    
    
# terrain grid size constants
CHUNK_SIZE = (100,100)
CELL_SIZE = 20

chunks = []

def loadChunk(chunkNumber):
    if chunkNumber < 0:
        return
    chunkExists = False
    
    for chunk in chunks:
        if chunk.chunkNumber == chunkNumber:
            chunkExists = True
    if chunkExists == False:
        newGrid = GridClass(CHUNK_SIZE,CELL_SIZE, chunkNumber)
        newGrid = generateTerrain(newGrid)
        newGrid.chunkNumber = chunkNumber
        return newGrid

# manual chunks
grid = GridClass(CHUNK_SIZE,CELL_SIZE, 0)
chunks.append(grid)

grid2 = GridClass(CHUNK_SIZE,CELL_SIZE,1)
chunks.append(grid2)

# terrain generation
FEATURE_SIZE = 18.0


def generateTerrain(grid):
    #noise = noisify.Perlin(grid.dimensions[0], 10).Smoothify(8)
    #img = Image.fromarray(255*noise).convert("L")
    #img.show()
    #print(noise)
    #for some reason the noise around the edges are very linear and weird looking

    simplex.seed(345)
    
    
    for x in range(len(grid.cells)):
        pillar = grid.cells[x]
        for y in range(len(pillar)):
            currentCell = pillar[y]
            currentHeight = (1+simplex.noise2(((currentCell.gridPosition[0]))/FEATURE_SIZE,0/FEATURE_SIZE))/2
            
            if y == grid.dimensions[1]-1:
                currentCell.elementData = 2
            elif y >= currentHeight*grid.dimensions[1]:
                
                currentCell.elementData = 1
            else:
                currentCell.elementData = 0
    return grid

grid = generateTerrain(grid)
grid2 = generateTerrain(grid2)

# never use this shit
def gridNeighbor(coordinate):
    left = None
    right = None
    up = None
    down = None

    if coordinate[0] >= 0 and coordinate[0] <= len(grid.cells[0])+1:
        left = (coordinate[0]-1,coordinate[1])
        right = (coordinate[0]+1,coordinate[1])

    if coordinate[1] >= 0 and coordinate[1] <= len(grid.cells[1])+1: 
        up = (coordinate[0],coordinate[1]-1)
        down = (coordinate[0],coordinate[1]+1)

    return [left,right,up,down]

def gridCellNeighbors(gridCell):
    cellPosition = gridCell.gridPosition
    left = (cellPosition[0]-1,cellPosition[1])
    right = (cellPosition[0]+1,cellPosition[1])
    top = (cellPosition[0],cellPosition[1]-1)
    bottom = (cellPosition[0],cellPosition[1]+1)
    
    neighbors = []
    if left[0] >= 0:
        neighbors.append(grid.getCell(left))
    if right[0] <= grid.dimensions[0]-1:
        neighbors.append(grid.getCell(right))
    if top[1] >= 0:
        neighbors.append(grid.getCell(top))
    if bottom[1] <= grid.dimensions[1]-1:
        neighbors.append(grid.getCell(bottom))
    return neighbors

NULL_CELL = GridCell()
NULL_CELL.elementData = 2

def getCell(coordinate):
    chunkNumber = math.floor((coordinate[0])/100)
    cell = NULL_CELL
    for chunk in chunks:
        if chunk.chunkNumber == chunkNumber:
            if chunk.chunkNumber == 0:
                chunkLocalCoordinate = (coordinate[0]-(chunkNumber*99),coordinate[1])
            elif chunk.chunkNumber > 0:
                chunkLocalCoordinate = (coordinate[0]-(chunkNumber*(100)),coordinate[1])
            cell = chunk.getCell(chunkLocalCoordinate)
            return cell
    return cell
        
# copied code from https://www.redblobgames.com/pathfinding/a-star
# this is a breadth-first-search implementation
previousPath = []
def pathfind(goalCoordinate):
    goal = grid.getCell(goalCoordinate)
    startCell = getCell((playerX,playerY))
    frontier = queue.Queue()
    frontier.put(startCell)
    came_from = dict() # path A->B is stored as came_from[B] == A
    came_from[startCell] = None
    
    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break
        
        for next in gridCellNeighbors(current):
            nextPos = next.gridPosition
            
            # ensure currentCell is air
            if next.elementData == 0:
                # check if a cell is passable
                passable = False
                posX = nextPos[0]
                posY = nextPos[1]
                if grid.getCell((posX-1,posY)) and grid.getCell((posX-1,posY)).elementData != 0:
                    passable = True

                if grid.getCell((posX-1,posY-1)) and grid.getCell((posX-1,posY-1)).elementData != 0:
                    passable = True

                if grid.getCell((posX-1,posY+1)) and grid.getCell((posX-1,posY+1)).elementData != 0:
                    passable = True

                if grid.getCell((posX+1,posY)) and grid.getCell((posX+1,posY)).elementData != 0:
                    passable = True

                if grid.getCell((posX+1,posY-1)) and grid.getCell((posX+1,posY-1)).elementData != 0:
                    passable = True

                if grid.getCell((posX+1,posY+1)) and grid.getCell((posX+1,posY+1)).elementData != 0:
                    passable = True

                if grid.getCell((posX,posY+1)) and grid.getCell((posX,posY+1)).elementData !=0:
                    passable = True
                
                if (next not in came_from) and passable:
                    frontier.put(next)
                    came_from[next] = current

    current = goal
    path = []

    while current != startCell:
        path.append(current)
        if current not in came_from:
            break
        else:
            current = came_from[current]
    path.append(startCell) # optional
    path.reverse() # optional

    return path

# input?
startRightClickPos = (0,0)
# camera
cameraOffset = (0,0)


# player state
selected_block_index = 0
hoveredCoords = (0,0)
isAutoWalking = False
isCrouching = False
playerRight = True
isGrounded = False
moveVector = (0,0)
playerX = 0
playerY = 0

def getPlayerChunkNumber():
    playerChunkNumber = math.floor(playerX/100)
    return playerChunkNumber

# player functions
# todo: player class, fix player being one pixel larger than grid
def isPlayerColliding():
    isPlayerColliding = False

    if not isCrouching:
        # player is not crouching
        if (playerX)>=len(grid.cells)*len(chunks) or (playerY)>=len(grid.cells[0]) or playerX<0:
            isPlayerColliding = True
        elif getCell((playerX,playerY)).elementData != 0 or getCell((playerX,playerY-1)).elementData != 0:
            isPlayerColliding = True
    else:
        # player is crouching
        if getCell((playerX,playerY)).elementData != 0:
            isPlayerColliding = True
    return isPlayerColliding

def renderPlayer():
    pass

mouse = pygame.mouse
running = True
isLeftMousePressed = False
isRightMousePressed = False

moving = False
moveCounter = 0
moveTime = 1

# spawning player on the surface of terrain
heightCounter = 0
surfaceSolution = None
while not surfaceSolution:
    currentCell = getCell((70,heightCounter))
    if currentCell.elementData != 0:
        surfaceSolution = heightCounter-1
    heightCounter +=1

playerX = 70
playerY = surfaceSolution

#######################
# MAIN LOOP MAIN LOOP #
#######################
while running:
    mousePos = Vector2(mouse.get_pos())
    currentPosition = (playerX,playerY)
    playerChunkNumber = getPlayerChunkNumber()
    playerChunk = None

    # find playerChunk
    for chunk in chunks:
        if chunk.chunkNumber == playerChunkNumber:
            playerChunk = chunk
            break

        loadChunk(playerChunkNumber)
        loadChunk(playerChunkNumber-1)
        newChunk = loadChunk(playerChunkNumber+1)
        if newChunk:
            chunks.append(newChunk)
            for chunk in chunks:
                if chunk.chunkNumber == 1:
                    pass

    isClimbing = False
    isGrounded = False

    playerCurrentChunkX = playerX-(playerChunkNumber*99)
    blockBelow = getCell((playerX,playerY+1))
    if blockBelow and blockBelow.elementData != 0: # filled block ID is 1
        isGrounded = True
    
    if not playerX == 0 and getCell((playerX-1,playerY)).elementData != 0:
        isClimbing = True
    elif not playerX == 0 and getCell((playerX-1,playerY-1)).elementData != 0:
        isClimbing = True
        
    if not playerX == (grid.dimensions[0]*len(chunks))-1 and getCell((playerX+1,playerY)).elementData != 0:
        isClimbing = True
    elif not playerX == (grid.dimensions[0]*len(chunks))-1 and getCell((playerX+1,playerY-1)).elementData != 0:
        isClimbing = True

    if isCrouching:
        isClimbing = False
    
    if not isGrounded and not isClimbing and not isAutoWalking:
        playerY+=1

    
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_q:
                selected_block_index +=1
                if selected_block_index == 2:
                    selected_block_index = 0
                elif selected_block_index >= len(COLORS):
                    selected_block_index=0
            if event.key == pygame.K_a:
                moveVector=(moveVector[0]-1,moveVector[1])
            if event.key == pygame.K_d:
                moveVector=(moveVector[0]+1,moveVector[1])
            if event.key == pygame.K_w:
                moveVector = (moveVector[0],moveVector[1]-1)
            if event.key == pygame.K_s:
                moveVector = (moveVector[0],moveVector[1]+1)
            if event.key == pygame.K_SPACE:
                isAutoWalking = True
                # crouch is disabled as of now
                #isCrouching = not isCrouching
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_q:
                pass
            if event.key == pygame.K_a:
                moveVector=(moveVector[0]+1,moveVector[1])
            if event.key == pygame.K_d:
                moveVector=(moveVector[0]-1,moveVector[1])
            if event.key == pygame.K_w:
                moveVector = (moveVector[0],moveVector[1]+1)
            if event.key == pygame.K_s:
                moveVector = (moveVector[0],moveVector[1]-1)
            if event.key == pygame.K_SPACE:
                isAutoWalking = False
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                isLeftMousePressed = False
            elif event.button == 3: # right click
                isRightMousePressed = False
                camera.goalPosition+=(mousePos-startRightClickPos)*camera.zoom
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                isLeftMousePressed = True
            if event.button == 2:
                pass
##                hoveredCell = grid.getCell(hoveredCoords)
##                if hoveredCell and hoveredCell.elementData == 0:
##                    for cell in previousPath:
##                        cell.path = False
##                    path = pathfind(hoveredCoords)
##                    for cell in path:
##                        cell.path = True
##                    previousPath = path
            if event.button == 3: # right click
                isRightMousePressed = True
                startRightClickPos = mousePos
        if event.type == pygame.MOUSEWHEEL:
            # event.x, event.y
            camera.goalZoom+=-event.y/10
            camera.goalZoom = np.clip(camera.goalZoom,0.5,5)

    # camera smoothing smooth camera
    camera.position+=(camera.goalPosition-camera.position)*0.2
    camera.zoom+=(camera.goalZoom-camera.zoom)*0.2
    
    # hold key movement
    moveCounter+=1
    if moveVector[0]!=0 or moveVector[1]!=0:
        moving = True
    else:
        moving = False

    # move step condition
    if moving and moveCounter >= moveTime:
        # move step execution
        playerX+=moveVector[0]
        playerY+=moveVector[1]
        if isPlayerColliding():
            # most beautiful piece of code yet
            upBlock = getCell((playerX,playerY-1))
            upUpBlock = getCell((playerX,playerY-2))
            nextBlock = getCell((playerX,playerY))
            if upBlock and upUpBlock and nextBlock and nextBlock.elementData != 0  and upBlock.elementData == 0 and upUpBlock.elementData == 0 and nextBlock.elementData != 0:
                # move player upwards
                playerY-=1
            elif moveVector[0]!=0:
                nextFeetBlock = getCell((playerX,playerY))
                nextHeadBlock = getCell((playerX,playerY-1))
                nextRoofBlock = getCell((playerX,playerY-2))

                # checking existence of all these blocks
                if nextFeetBlock and nextHeadBlock and nextRoofBlock:
                    #checking if block is solid or not
                    if nextFeetBlock.elementData!=0 and nextHeadBlock.elementData!=0:
                        playerY-=1

                    playerX-=moveVector[0]
                playerY-=moveVector[1]
            else:
                playerX = currentPosition[0]
                playerY = currentPosition[1]
   
        moveCounter = 0
    if not moving:
        moveCounter = 0
    
    #clear the screen
    screen.fill(BLACK)

    # pathfinding execution
    hoveredCell = getCell(hoveredCoords)
##    if hoveredCell and hoveredCell.elementData == 0:
##        for cell in previousPath:
##            cell.path = False
##        path = pathfind(hoveredCoords)
##        for cell in path:
##            cell.path = True
##        previousPath = path
##
##        if isAutoWalking:
##            # auto walk according to pathfinding path
##            if 1+1 <= len(path):
##                nextCell = path[1]
##
##                playerX = nextCell.gridPosition[0]
##                playerY = nextCell.gridPosition[1]
    
    #///////////
    # RENDERING
    #///////////
    for chunk in chunks:
        chunk.render(camera.position)
##    grid.render(camera.position)
##    grid2.render(camera.position)
    hoveredCoords = gridSelectionUpdate()
    
    # drawing player
    if not isCrouching:
        # player is not crouching
        pygame.draw.rect(
            screen,
            BLUE,
            pygame.Rect(
                ((playerX*(grid.cellSize+grid.cellPadding)) + camera.position[0])/camera.zoom, ((playerY*(grid.cellSize+grid.cellPadding))-(grid.cellSize+grid.cellPadding) + camera.position[1])/camera.zoom,
                (1*(grid.cellSize+grid.cellPadding)-4)/camera.zoom, (2*(grid.cellSize+grid.cellPadding)-4)/camera.zoom)
            )
        headPosition = (
            playerX*(grid.cellSize+grid.cellPadding)+(grid.cellSize+grid.cellPadding)/2+(playerRight*(grid.cellSize+grid.cellPadding)/4),
            playerY*(grid.cellSize+grid.cellPadding)+(grid.cellSize+grid.cellPadding)/2)
        pygame.draw.circle(screen, RED, np.add(headPosition,camera.position), 3)
    else:
        # player is crouching
        pygame.draw.rect(screen, BLUE, pygame.Rect((playerX*(grid.cellSize+grid.cellPadding)),(playerY*(grid.cellSize+grid.cellPadding)),1*(grid.cellSize+grid.cellPadding)-4+(grid.cellSize+grid.cellPadding),1*(grid.cellSize+grid.cellPadding)-4))
        headPosition = (playerX*(grid.cellSize+grid.cellPadding)+(grid.cellSize+grid.cellPadding)/2+(playerRight*(grid.cellSize+grid.cellPadding)),playerY*(grid.cellSize+grid.cellPadding)+(grid.cellSize+grid.cellPadding)/2)
        pygame.draw.circle(screen, RED, np.add(headPosition,camera.position), 3)

    
    # draw to the screen
    screen.blit(smile, smileRect)

    # drawing the debug console menu
    consoleRect = pygame.Rect(1920-400,0,400,200)
    pygame.draw.rect(screen, BLACK, consoleRect) # background
    pygame.draw.rect(screen, GREEN, consoleRect,5) # outline

    text_surface = updateText(BLOCK_NAMES[selected_block_index] + ' ' + str(math.floor(clock.get_fps())) + ' ' + str((playerX,playerY)))
    screen.blit(text_surface, (1920-400+7,0))
    
    if hoveredCell:
        text_surface2 = updateText('hov: ' + 'blockID' + str(hoveredCell.elementData) + ' ' + str(hoveredCell.gridPosition))
    else:
        text_surface2 = updateText('nothing')
    
    screen.blit(text_surface2, (1920-400+7,30))
    text_surface3 = updateText("playerChunkNumber: " + str(playerChunkNumber))
    screen.blit(text_surface3, (1920-400+7,60))
    
    
    # flip() updates the screen to make our changes visible
    pygame.display.flip()
    
    # how many updates per second
    clock.tick(60)
  
pygame.quit()
