# make fancy later.  Right now just working out the basic mechanics of things
# look more in 7XNN

# for now keeping this separate
import pygame
import computer
import sys

memory = [0] * 4096
registers = [0] * 17 # the 17th register will serve as the I register
stack = [] # starting at 0x200 per reference
ip = 0x200
dt = 0
st = 0
ipInHex = hex(ip)

screenData = [0] * 64 * 32

# default sprites
sprites = [
        0xF0, 0x90, 0x90, 0x90, 0xF0, # 1
        0x20, 0x60, 0x20, 0x20, 0x70, # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
        0x90, 0x90, 0xF0, 0x10, 0x10, # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
        0xF0, 0x10, 0x20, 0x40, 0x40, # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90, # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
        0xF0, 0x80, 0x80, 0x80, 0xF0, # C
        0xE0, 0x90, 0x90, 0x90, 0xE0, # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
        0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]

for i in range(0,len(sprites)):
    memory[i] = sprites[i]

with open(sys.argv[1], mode="rb") as file:
    program=bytearray(file.read())

# load instructions into memory
for i in range(0,len(program)):
    memory[0x200+i]=program[i]

# init screen
pygame.init()
screen=pygame.display.set_mode([64 * 10, 32 * 10], True)
screen.fill([0, 0, 0])

# continue execution until the stack has been emptied
while True:    
    computer.printState(stack, ip, memory, registers)

    # advance clock

    # check for key strokes

    # make sound?
    keypressed = 4
    # compute next instruction
    try:
        (stack, ip, memory, registers, screenData, dt, st) = computer.computeInstruction(stack, ip, memory, registers, screenData, dt, st, keypressed)
    except:
        f=input()
        quit()
    computer.drawScreen(screen, screenData)

    
    
    
    
    
    

    
    
    
