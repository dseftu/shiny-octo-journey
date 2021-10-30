import pygame
import computer
import sys

# initialize compy
xResolution = 64
yResolution = 32
compy = computer.Chip8(xResolution, yResolution)

# load data into memory
rom = sys.argv[1]
compy.loadInitSpriteData()
compy.loadRom(rom)

# computation loop
while True:
    # print pointers, memory, and register info into console for debug
    compy.printState()

    # advance clock

    # check for key strokes

    # make sound?
    keypressed = 4

    # compute next instruction
    try:
        compy.computeInstruction(keypressed)
    except Exception as e:
        print(e)
        f=input()
        quit()

    # refresh display    
    compy.drawScreen()

    
    
    
    
    
    

    
    
    
