# make fancy later.  Right now just working out the basic mechanics of things
# look more in 7XNN

# for now keeping this separate
import pygame
import computer

memory = [0] * 4096
registers = [0] * 17 # the 17th register will serve as the I register
stack = [0x200] # starting at 0x200 per reference
ip = 0
dt = 0
st = 0
ipInHex = hex(ip)

screenData = [[0 for y in range(32)] for x in range(64)]

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

# sample program (call subroutine that counts to ten, then return, then halts)
program = [0x00E0, 0x2203, 0x00EE, 0x7001, 0xD005, 0x3005, 0x1000, 0x00EE]

# load instructions into memory
for i in range(0,len(program)):
    memory[0x200+i]=program[i]

# init screen

screen=pygame.display.set_mode([640, 320])
screen.fill([0, 0, 0])

# continue execution until the stack has been emptied
while len(stack)>0:    
    computer.printState(stack, ip, memory, registers)

    # advance clock

    # check for key strokes

    # make sound?

    # compute next instruction
    (stack, ip, memory, registers, screenData) = computer.computeInstruction(stack, ip, memory, registers, screenData)
    f=input()
    computer.drawScreen(screen, screenData)

    
    
    
    
    
    

    
    
    
