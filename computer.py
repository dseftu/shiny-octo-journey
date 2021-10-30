import pygame
import random

class Chip8():

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

        self.initScreen()

    def computeInstruction(self, keypressed):
        # moved this into it's own thing to make the method more focused
        (opcode, registerIndexX, registerIndexY, vx, vy, nnn, nn, opcodeType, lsb, i, v0) = self.decodeOpcodeData()

        # take opcode and perform action
        if opcode == 0x00E0:
            self.clearDisplay()

        elif opcode == 0x00EE:
            self.ip=self.stack.pop()

        elif opcodeType == 0:
            # 0NNN
            # Calls machine code routine (RCA 1802 for COSMAC VIP) at address NNN. 
            # Not necessary for most ROMs.
            raise NotImplementedError

        elif opcodeType == 1:
            # 1NNN        
            # goto NNN;	Jumps to address NNN.
            self.ip = nnn - 2 # decrement by 2 to account for increment at end
            
        elif opcodeType == 2:
            # 2NNN
            # *(0xNNN)()	Calls subroutine at NNN.
            # update stack pointer
            self.stack.append(self.ip)
            self.ip = nnn - 2 # decrement by 2 to account for increment at end

        elif opcodeType == 3:
            # 3XNN
            # if (Vx == NN)	Skips the next instruction if VX equals NN.
            #  (Usually the next instruction is a jump to skip a code block);
            if (vx == nn):
                self.ip+=2

        elif opcodeType == 4:
            # 4XNN
            # if (Vx != NN)	Skips the next instruction if VX does not equal NN. 
            # (Usually the next instruction is a jump to skip a code block);
            if (vx != nn):
                self.ip+=2

        elif opcodeType == 5:
            # 5XY0
            # if (Vx == Vy)	Skips the next instruction if VX equals VY. 
            # (Usually the next instruction is a jump to skip a code block);        
            if (vx == vy):
                self.ip+=2

        elif opcodeType == 6:
            # 6XNN
            # Vx = N	Sets VX to NN.       
            self.registers[registerIndexX] = nn

        elif opcodeType == 7:
            # 7XNN
            # Vx += N	Adds NN to VX. (Carry flag is not changed);      
            self.registers[registerIndexX] += nn
            self.registers[registerIndexX] &= 0xff

        elif opcodeType == 8:
            # set of opcodes starting with 8
            if lsb == 0:
                # 8XY0
                # Vx = Vy	Sets VX to the value of VY. 
                self.registers[registerIndexX] = vy
            elif lsb == 1:
                # 8XY1
                # Vx |= Vy	Sets VX to VX or VY. (Bitwise OR operation);
                self.registers[registerIndexX] = vx | vy
            elif lsb == 2:
                # 8XY2
                # Vx &= Vy	Sets VX to VX and VY. (Bitwise AND operation);
                self.registers[registerIndexX] = vx & vy
            elif lsb == 3:
                # 8XY3
                # Vx ^= Vy	Sets VX to VX xor VY.
                self.registers[registerIndexX] = vx ^ vy
            elif lsb == 4:
                
                # 8XY4
                # Vx += Vy	Adds VY to VX. VF is set to 1 when there's a carry, and to 0 when there is not.            
                self.registers[registerIndexX]+=vy

                if self.registers[registerIndexX] & 0xF00 == 1:
                    self.registers[0xF] = 1 
                else:
                    self.registers[0xF] = 0

                self.registers[registerIndexX] &= 0xff
            elif lsb == 5:
                # 8XY5
                # Vx -= Vy	VY is subtracted from VX. VF is set to 0 when there's a borrow, and 1 when 
                # there is not.
                if vy > vx:
                    self.registers[0xF] = 0                    
                else:
                    self.registers[0xF] = 1
                self.registers[registerIndexX]-=vy
                self.registers[registerIndexX] &= 0xFF

            elif lsb == 6:
                # 8XY6
                # Vx >>= 1	Stores the least significant bit of VX in VF and then shifts VX to the right by 1.[b]
                self.registers[0xF] = vx & 0x000F
                self.registers[registerIndexX] = vx >> 1
            elif lsb == 7:
                # 8XY7
                # Vx = Vy - Vx	Sets VX to VY minus VX. VF is set to 0 when there's a borrow, and 1 when there is not.
                if vx > vy:
                    self.registers[0xF] = 0
                    self.registers[registerIndexX] = vy - vx
                else:
                    self.registers[0xF] = 1
                    self.registers[registerIndexX] = (vy - vx) + 0x100
                raise NotImplementedError
            elif lsb == 0xE:
                # 8XYE
                # Vx <<= 1	Stores the most significant bit of VX in VF and then shifts VX to the left by 1.[b]
                self.registers[0xF] = (vx & 0xF000) >> 12
                self.registers[registerIndexX] = vx << 1
            
        elif opcodeType == 9:
            # 9XY0
            # if (Vx != Vy)	Skips the next instruction if VX does not equal VY. (Usually the next instruction is a jump to skip a code block);
            if (vx != vy):
                self.ip+=2

        elif opcodeType == 0xA:
            # ANNN
            # MEM	I = NNN	Sets I to the address NNN.
            self.registers[16] = nnn

        elif opcodeType == 0xB:
            # BNNN
            # PC = V0 + NNN	Jumps to the address NNN plus V0.
            self.ip = nnn + v0

        elif opcodeType == 0xC:
            # CVNN
            # Vx = rand() & NN	Sets VX to the result of a bitwise and operation 
            # on a random number (Typically: 0 to 255) and NN.
            randNum = random.randrange(0,256)
            nn = opcode & 0x00FF
            self.registers[registerIndexX] = randNum & nn

        elif opcodeType == 0xD:
            # DXYN
            # draw(Vx, Vy, N)	Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels. Each row of 8 pixels is read as bit-coded 
            # starting from memory location I; I value does not change after the execution of this instruction. As described above, VF is set to 1 if any screen pixels are flipped 
            # from set to unset when the sprite is drawn, and to 0 if that does not happen
            height = lsb
            self.registers[0xF] = 0        
            width = 8
            xStart = vx
            yStart = vy

            for yOffset in range(0,height):
                spriteLine = self.memory[yOffset + i]

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
                        

        elif opcodeType == 0xE:
            if nn==0x9E:
                # EX9E	KeyOp	if (key() == Vx)	Skips the next instruction if the key stored in VX is pressed. 
                # (Usually the next instruction is a jump to skip a code block);
                raise NotImplementedError
            elif nn==0xA1:
                # EXA1	KeyOp	if (key() != Vx)	Skips the next instruction if the key stored in VX is not pressed. (Usually the next instruction is a jump to skip a code block);
                raise NotImplementedError

        elif opcodeType == 0xF:
            if nn==0x07:
                # FX07	Timer	Vx = get_delay()	Sets VX to the value of the delay timer.
                self.registers[registerIndexX] = self.dt

            elif nn==0x0A:
                # FX0A	KeyOp	Vx = get_key()	A key press is awaited, and then stored in VX. 
                # (Blocking Operation. All instruction halted until next key event);
                raise NotImplementedError
                registers[registerIndexX] = key

            elif nn==0x15:
                # FX15	Timer	delay_timer(Vx)	Sets the delay timer to VX.
                dt = vx

            elif nn==0x18:
                # FX18	Sound	sound_timer(Vx)	Sets the sound timer to VX.
                st = vx

            elif nn==0x1E:
                # FX1E	MEM	I += Vx	Adds VX to I. VF is not affected.[c]
                self.registers[16]+=vx

            elif nn==0x29:
                # FX29	MEM	I = sprite_addr[Vx]	Sets I to the location of the sprite for the character in 
                # VX. Characters 0-F (in hexadecimal) are represented by a 4x5 font.
                self.registers[16] = 5*vx

            elif nn==0x33:
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
                onesPlace = vx % 10
                vx-=onesPlace
                tensPlace = (vx % 100)
                vx-= tensPlace
                tensPlace //= 10
                hundredsPlace = (vx % 1000) // 100

                self.memory[i] = hundredsPlace
                self.memory[i+1] = tensPlace
                self.memory[i+2] = onesPlace


            elif nn==0x55:
                # FX55	MEM	reg_dump(Vx, &I)	Stores V0 to VX (including VX) in memory starting at 
                # address I. The offset from I is increased by 1 for each value written, but I itself 
                # is left unmodified.[d]
                for j in range(0,registerIndexX+1):
                    self.memory[i+j] = self.registers[j]

            elif nn==0x65:
                # FX65	MEM	reg_load(Vx, &I)	Fills V0 to VX (including VX) with values from memory 
                # starting at address I. The offset from I is increased by 1 for each value written, 
                # but I itself is left unmodified.[d]
                for j in range(0,registerIndexX+1):
                    self.registers[j] = self.memory[i+j]

        self.ip+=2

    def decodeOpcodeData(self):
        opcode = self.memory[self.ip] << 8 | self.memory[self.ip + 1]       
        registerIndexX = (opcode & 0x0F00) >> 8
        registerIndexY = (opcode & 0x00F0) >> 4
        vx = self.registers[registerIndexX]
        vy = self.registers[registerIndexY]
        nnn = (opcode & 0x0FFF)
        nn = opcode & 0x00FF
        opcodeType = opcode >> 12
        lsb = (opcode & 0x000F)
        i = self.registers[16]
        v0 = self.registers[0]

        return (opcode,
                registerIndexX, 
                registerIndexY, 
                vx, 
                vy, 
                nnn, 
                nn, 
                opcodeType, 
                lsb, 
                i, 
                v0)

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

    def drawScreen(self):
        for i in range(len(self.screenData)):
            bit = self.screenData[i]
            color = [0, 200*bit, 0]
            shape = pygame.Rect((i%64)*10, (i/64)*10, 10, 10)
            pygame.draw.rect(self.screen, color, shape)
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