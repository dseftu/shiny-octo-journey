import pygame
import random

class Chip8():

    keys = {
        0x0:49,
        0x1:50,
        0x2:51,
        0x3:113,
        0x4:119,
        0x5:101,
        0x6:97,
        0x7:115,
        0x8:100,
        0x9:122,
        0xa:99,
        0xb:120,
        0xc:113,
        0xd:102,
        0xe:118,
        0xf:52
    }

    def __init__(self, xResolution, yResolution):
        self.xResolution = xResolution
        self.yResolution = yResolution
        self.memory = [0] * 4096
        self.registers = [0] * 17 # the 17th register will serve as the I register
        self.stack = [] # starting at 0x200 per reference
        self.offset = 0x200
        self.ip = self.offset
        self.dt = 0
        self.st = 0
        self.screenData = [0] * xResolution * yResolution
        self.deltaScreenData = []
        
        # lookups for opcode methods
        self.opcodeLookup = {
            0x0: self.opcode_0XXX,
            0x1: self.opcode_1XXX,
            0x2: self.opcode_2XXX,
            0x3: self.opcode_3XXX,
            0x4: self.opcode_4XXX,
            0x5: self.opcode_5XXX,
            0x6: self.opcode_6XXX,
            0x7: self.opcode_7XXX,
            0x8: self.opcode_8XXX,
            0x9: self.opcode_9XXX,
            0xA: self.opcode_AXXX,
            0xB: self.opcode_BXXX,
            0xC: self.opcode_CXXX,
            0xD: self.opcode_DXXX,
            0xE: self.opcode_EXXX,
            0xF: self.opcode_FXXX,
            }

        self.opcodeLSBLookup = {
            0x0: self.opcode_XXX0,
            0x1: self.opcode_XXX1,
            0x2: self.opcode_XXX2,
            0x3: self.opcode_XXX3,
            0x4: self.opcode_XXX4,
            0x5: self.opcode_XXX5,
            0x6: self.opcode_XXX6,
            0x7: self.opcode_XXX7,
            0xE: self.opcode_XXXE,
        }
        
        self.opcodeNNLookup = {
            0x07: self.opcode_XX07,
            0x0A: self.opcode_XX0A,
            0x15: self.opcode_XX15,
            0x18: self.opcode_XX18,
            0x1E: self.opcode_XX1E,
            0x29: self.opcode_XX29,
            0x33: self.opcode_XX33,
            0x55: self.opcode_XX55,
            0x65: self.opcode_XX65,
        }

        self.initScreen()

    def computeInstruction(self, keypressed):
        # one less thing to pass around.  Need to look into doing this with the rest of the thingies I'm passing around.
        self.keypressed = keypressed

        # moved this into it's own thing to make the method more focused
        self.decodeOpcodeData()
        
        # take opcode and perform action
        self.opcodeLookup[self.opcodeType]()

        self.ip+=2

    def decodeOpcodeData(self):
        self.opcode = self.memory[self.ip] << 8 | self.memory[self.ip + 1]       
        self.registerIndexX = (self.opcode & 0x0F00) >> 8
        self.registerIndexY = (self.opcode & 0x00F0) >> 4
        self.vx = self.registers[self.registerIndexX]
        self.vy = self.registers[self.registerIndexY]
        self.nnn = (self.opcode & 0x0FFF)
        self.nn = self.opcode & 0x00FF
        self.opcodeType = self.opcode >> 12
        self.lsb = (self.opcode & 0x000F)
        self.i = self.registers[16]
        self.v0 = self.registers[0]

    def opcode_0XXX(self):
        if self.opcode == 0x00E0:
            self.clearDisplay()

        elif self.opcode == 0x00EE:
            self.ip=self.stack.pop()

        elif self.opcodeType == 0:
            # 0NNN
            # Calls machine code routine (RCA 1802 for COSMAC VIP) at address NNN. 
            # Not necessary for most ROMs.

            # NotImplementedError until I find a rom that uses it
            raise NotImplementedError

    def opcode_1XXX(self):
        # 1NNN        
        # goto NNN;	Jumps to address NNN.
        self.ip = self.nnn - 2 # decrement by 2 to account for increment at end

    def opcode_2XXX(self):
        # 2NNN
        # *(0xNNN)()	Calls subroutine at NNN.
        # update stack pointer
        self.stack.append(self.ip)
        self.ip = self.nnn - 2 # decrement by 2 to account for increment at end

    def opcode_3XXX(self):
        # 3XNN
        # if (Vx == NN)	Skips the next instruction if VX equals NN.
        #  (Usually the next instruction is a jump to skip a code block);
        if (self.vx == self.nn):
            self.ip+=2

    def opcode_4XXX(self):
        # 4XNN
        # if (Vx != NN)	Skips the next instruction if VX does not equal NN. 
        # (Usually the next instruction is a jump to skip a code block);
        if (self.vx != self.nn):
            self.ip+=2

    def opcode_5XXX(self):
        # 5XY0
        # if (Vx == Vy)	Skips the next instruction if VX equals VY. 
        # (Usually the next instruction is a jump to skip a code block);        
        if (self.vx == self.vy):
            self.ip+=2

    def opcode_6XXX(self):
        # 6XNN
        # Vx = N	Sets VX to NN.       
        self.registers[self.registerIndexX] = self.nn

    def opcode_7XXX(self):
        # 7XNN
        # Vx += N	Adds NN to VX. (Carry flag is not changed);      
        self.registers[self.registerIndexX] += self.nn
        self.registers[self.registerIndexX] &= 0xff

    def opcode_8XXX(self):
        # set of opcodes starting with 8
        # take opcode and perform action 
        self.opcodeLSBLookup[self.lsb]()

    def opcode_XXX0(self):
        # 8XY0
        # Vx = Vy	Sets VX to the value of VY. 
        self.registers[self.registerIndexX] = self.vy

    def opcode_XXX1(self):
        # 8XY1
        # Vx |= Vy	Sets VX to VX or VY. (Bitwise OR operation);
        self.registers[self.registerIndexX] = self.vx | self.vy

    def opcode_XXX2(self):
        # 8XY2
        # Vx &= Vy	Sets VX to VX and VY. (Bitwise AND operation);
        self.registers[self.registerIndexX] = self.vx & self.vy

    def opcode_XXX3(self):
        # 8XY3
        # Vx ^= Vy	Sets VX to VX xor VY.
        self.registers[self.registerIndexX] = self.vx ^ self.vy

    def opcode_XXX4(self):
            
        # 8XY4
        # Vx += Vy	Adds VY to VX. VF is set to 1 when there's a carry, and to 0 when there is not.            
        self.registers[self.registerIndexX]+=self.vy

        if self.registers[self.registerIndexX] & 0xF00 == 1:
            self.registers[0xF] = 1 
        else:
            self.registers[0xF] = 0

        self.registers[self.registerIndexX] &= 0xff

    def opcode_XXX5(self):
        # 8XY5
        # Vx -= Vy	VY is subtracted from VX. VF is set to 0 when there's a borrow, and 1 when 
        # there is not.
        if self.vy > self.vx:
            self.registers[0xF] = 0                    
        else:
            self.registers[0xF] = 1
        self.registers[self.registerIndexX]-=self.vy
        self.registers[self.registerIndexX] &= 0xFF

    def opcode_XXX6(self):
        # 8XY6
        # Vx >>= 1	Stores the least significant bit of VX in VF and then shifts VX to the right by 1.[b]
        self.registers[0xF] = self.vx & 0x000F
        self.registers[self.registerIndexX] = self.vx >> 1

    def opcode_XXX7(self):
        # 8XY7
        # Vx = Vy - Vx	Sets VX to VY minus VX. VF is set to 0 when there's a borrow, and 1 when there is not.
        if self.vx > self.vy:
            self.registers[0xF] = 0
            self.registers[self.registerIndexX] = self.vy - self.vx
        else:
            self.registers[0xF] = 1
            self.registers[self.registerIndexX] = (self.vy - self.vx) + 0x100
        
        # do not trust this as written, NotImplementedError until I find a rom that uses it
        raise NotImplementedError

    def opcode_XXXE(self):
        # 8XYE
        # Vx <<= 1	Stores the most significant bit of VX in VF and then shifts VX to the left by 1.[b]
        self.registers[0xF] = (self.vx & 0xF000) >> 12
        self.registers[self.registerIndexX] = self.vx << 1    

    def opcode_9XXX(self):
        # 9XY0
        # if (Vx != Vy)	Skips the next instruction if VX does not equal VY. (Usually the next instruction is a jump to skip a code block);
        if (self.vx != self.vy):
            self.ip+=2

    def opcode_AXXX(self):
        # ANNN
        # MEM	I = NNN	Sets I to the address NNN.
        self.registers[16] = self.nnn

    def opcode_BXXX(self):
        # BNNN
        # PC = V0 + NNN	Jumps to the address NNN plus V0.
        self.ip = self.nnn + self.v0

    def opcode_CXXX(self):
        # CVNN
        # Vx = rand() & NN	Sets VX to the result of a bitwise and operation 
        # on a random number (Typically: 0 to 255) and NN.
        randNum = random.randrange(0,256)
        self.registers[self.registerIndexX] = randNum & self.nn

    def opcode_DXXX(self):
        # DXYN
        # draw(Vx, Vy, N)	Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels. Each row of 8 pixels is read as bit-coded 
        # starting from memory location I; I value does not change after the execution of this instruction. As described above, VF is set to 1 if any screen pixels are flipped 
        # from set to unset when the sprite is drawn, and to 0 if that does not happen
        height = self.lsb
        self.registers[0xF] = 0        
        width = 8
        xStart = self.vx
        yStart = self.vy

        for yOffset in range(0,height):
            spriteLine = self.memory[yOffset + self.i]

            for xOffset in range(0,width):
                # this nabs the current pixel of interest in the sprite line
                thisPixel = (spriteLine & (0x80 >> xOffset)) >> (7-xOffset)

                # determine the current state of the pixel
                currentPixelStatePosition = (xStart + xOffset + (yStart + yOffset) * 64) % 2048
                currentPixelState = self.screenData[currentPixelStatePosition]

                # determine the new state by xor the new pixel coming in and the current state
                newPixelState = thisPixel ^ currentPixelState
                self.screenData[currentPixelStatePosition] = newPixelState

                # if newPixelState is 0 and thisPixel is 1, that means we turned it off
                if (newPixelState == 0 and thisPixel == 1):
                    self.registers[0xF] = 1
                if (newPixelState != currentPixelState):
                    # keep track of pixel changes
                    self.deltaScreenData.append(currentPixelStatePosition)

    def opcode_EXXX(self):
        if self.nn==0x9E:
            # EX9E	KeyOp	if (key() == Vx)	Skips the next instruction if the key stored in VX is 
            # pressed. 
            # (Usually the next instruction is a jump to skip a code block);
            if self.keys[self.vx] in self.keypressed:
                self.ip+=2
            
        elif self.nn==0xA1:
            # EXA1	KeyOp	if (key() != Vx)	Skips the next instruction if the key stored in VX is
            # pressed. (Usually the next instruction is a jump to skip a code block);
            if self.keys[self.vx] not in self.keypressed:
                self.ip+=2

    def opcode_FXXX(self):
        # opcode FXXX begets more lookup
        self.opcodeNNLookup[self.nn]()

    def opcode_XX07(self):
        # FX07	Timer	Vx = get_delay()	Sets VX to the value of the delay timer.
        self.registers[self.registerIndexX] = self.dt

    def opcode_XX0A(self):
        # FX0A	KeyOp	Vx = get_key()	A key press is awaited, and then stored in VX. 
        # (Blocking Operation. All instruction halted until next key event);
        
        # do not trust this as written, NotImplementedError until I find a rom that uses it
        raise NotImplementedError
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                keypressed.append(event.key)
                if event.key == 27:
                    halt = True

    def opcode_XX15(self):
        # FX15	Timer	delay_timer(Vx)	Sets the delay timer to VX.
        self.dt = self.vx

    def opcode_XX18(self):
        # FX18	Sound	sound_timer(Vx)	Sets the sound timer to VX.
        self.st = self.vx

    def opcode_XX1E(self):
        # FX1E	MEM	I += Vx	Adds VX to I. VF is not affected.[c]
        self.registers[16]+=self.vx

    def opcode_XX29(self):
        # FX29	MEM	I = sprite_addr[Vx]	Sets I to the location of the sprite for the character in 
        # VX. Characters 0-F (in hexadecimal) are represented by a 4x5 font.
        self.registers[16] = 5 * self.vx

    def opcode_XX33(self):
        # FX33	BCD	
        # set_BCD(Vx)
        # *(I+0) = BCD(3);
        # *(I+1) = BCD(2);
        # *(I+2) = BCD(1);
        # Stores the binary-coded decimal representation of VX, with the most significant of three 
        # digits at the address in I, the middle digit at I plus 1, and the least significant 
        # digit at I plus 2. (In other words, take the decimal representation of VX, place the 
        # hundreds digit in memory at location in I, the tens digit at location I+1, and the ones                
        #  digit at location I+2.);
        onesPlace = self.vx % 10
        self.vx-=onesPlace
        tensPlace = (self.vx % 100)
        self.vx-= tensPlace
        tensPlace //= 10
        hundredsPlace = (self.vx % 1000) // 100

        self.memory[self.i] = hundredsPlace
        self.memory[self.i+1] = tensPlace
        self.memory[self.i+2] = onesPlace


    def opcode_XX55(self):
        # FX55	MEM	reg_dump(Vx, &I)	Stores V0 to VX (including VX) in memory starting at 
        # address I. The offset from I is increased by 1 for each value written, but I itself 
        # is left unmodified.[d]
        for j in range(0,self.registerIndexX+1):
            self.memory[self.i+j] = self.registers[j]

    def opcode_XX65(self):
        # FX65	MEM	reg_load(Vx, &I)	Fills V0 to VX (including VX) with values from memory 
        # starting at address I. The offset from I is increased by 1 for each value written, 
        # but I itself is left unmodified.[d]
        for j in range(0,self.registerIndexX+1):
            self.registers[j] = self.memory[self.i+j]

    def clearDisplay(self):
        # reset all bits to 0 on screen
        for i in range(len(self.screenData)):
            self.screenData[i] = 0

    def printState(self):
        print("V0=%s, V1=%s, V2=%s, V3=%s, V4=%s, V5=%s, V6=%s, V7=%s" % (hex(self.registers[0]),
                                                                                hex(self.registers[1]),
                                                                                hex(self.registers[2]),
                                                                                hex(self.registers[3]),
                                                                                hex(self.registers[4]),
                                                                                hex(self.registers[5]),
                                                                                hex(self.registers[6]),
                                                                                hex(self.registers[7])))
        print("V8=%s, V9=%s, VA=%s, VB=%s, VC=%s, VD=%s, VE=%s, VF=%s" % (hex(self.registers[8]),
                                                                                hex(self.registers[9]),
                                                                                hex(self.registers[10]),
                                                                                hex(self.registers[11]),
                                                                                hex(self.registers[12]),
                                                                                hex(self.registers[13]),
                                                                                hex(self.registers[14]),
                                                                                hex(self.registers[15])))
        print("I=%s" %(hex(self.registers[16])))    
        print("stack=%s" % str(self.stack))
        print("ip=%s" % hex(self.ip))
        opcode = self.memory[self.ip] << 8 | self.memory[self.ip + 1]
        print("next instruction = %s" % hex(opcode))    

    def updateScreen(self):
        # only update screendata if shadow copy has delta
        while len(self.deltaScreenData) > 0:
            i = self.deltaScreenData.pop()
            bit = self.screenData[i]
            color = [0, 200*bit, 0]
            shape = pygame.Rect((i%64)*10, (i/64)*10, 10, 10)
            pygame.draw.rect(self.screen, color, shape)

    def drawScreen(self):    
        pygame.display.flip()

    def loadInitSpriteData(self):
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
            self.memory[i] = sprites[i]

    def loadRom(self, rom):
        with open(rom, mode="rb") as file:
            romdata=bytearray(file.read())

        # load instructions into memory
        for i in range(0,len(romdata)):
            self.memory[self.offset+i]=romdata[i]

    def initScreen(self):
        pygame.init()
        self.screen=pygame.display.set_mode([self.xResolution * 10, self.yResolution * 10], True)
        self.screen.fill([0, 0, 0])