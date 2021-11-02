import pygame
import computer
import sys
import time

# initialize compy
xResolution = 64
yResolution = 32
compy = computer.Chip8(xResolution, yResolution)

# load data into memory
rom = sys.argv[1]
compy.loadInitSpriteData()
compy.loadRom(rom)
halt = False
keypressed = []

gameClock = pygame.time.Clock()

# computation loop
while not halt:
    
    # print pointers, memory, and register info into console for debug
    # as written, leaving this uncommented kills performance
    #compy.printState()

    # check for key changes
    events = pygame.event.get()
    for event in events:        
        if event.type == pygame.KEYDOWN:
            keypressed.append(event.key)
            if event.key == 27:
                halt = True
                print("Goodbye!")
        if event.type == pygame.KEYUP:
            keypressed.remove(event.key)
            #print("Code: %d Unicode: %s" %(keypressed[-1], event.unicode))

    # compute next instruction    
    compy.computeInstruction(keypressed)
    
    # update where shapes should be   
    compy.updateScreen() 

    # leaving this commented out because it doesn't seem to work as I expect it to.
    #gameClock.tick(60)

    # draw the screen
    compy.drawScreen()
    

    
    
    
    
    
    

    
    
    
