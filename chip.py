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
frameRate = 60

# computation loop
while not halt:
    
    # print pointers, memory, and register info into console for debug
    #compy.printState()

    # advance clock


    # check for key strokes

    # make sound?
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
    
    
    # refresh display   
    compy.updateScreen() 

    #gameClock.tick(60)

    compy.drawScreen()
    

    
    
    
    
    
    

    
    
    
