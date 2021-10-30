import pygame
import random


def computeInstruction(stack, ip, memory, registers, screenData, dt, st, keypressed):
    opcode = memory[ip] << 8 | memory[ip + 1]
    # take opcode and perform action
    if opcode == 0x00E0:
        clearDisplay(screenData)
        ip+=2
    elif opcode == 0x00EE:
        print("computer was instructed to return")
        stack.pop()
        ip=stack[-1]
    elif opcode >> 12 == 0:
        # Calls machine code routine (RCA 1802 for COSMAC VIP) at address NNN. 
        # Not necessary for most ROMs.
        print(hex(opcode))
        raise NotImplementedError
    elif opcode >> 12 == 1:
        # goto NNN;	Jumps to address NNN.
        ip = (opcode & 0x0FFF) + 0x200
        
    elif opcode >> 12 == 2:
        # *(0xNNN)()	Calls subroutine at NNN.
        # update stack pointer
        stack.append(ip)
        ip = (opcode & 0x0FFF) + 0x200
    elif opcode >> 12 == 3:
        # if (Vx == NN)	Skips the next instruction if VX equals NN.
        #  (Usually the next instruction is a jump to skip a code block);
        var = opcode & 0x00FF
        registerIndex = (opcode & 0x0F00) >> 8
        if (registers[registerIndex] == var):
            ip+=2
        ip+=2
    elif opcode >> 12 == 4:
        # if (Vx != NN)	Skips the next instruction if VX does not equal NN. 
        # (Usually the next instruction is a jump to skip a code block);
        var = opcode & 0x00FF
        registerIndex = (opcode & 0x0F00) >> 8
        if (registers[registerIndex] != var):
            ip+=2
        ip+=2
    elif opcode >> 12 == 5:
        # if (Vx == Vy)	Skips the next instruction if VX equals VY. 
        # (Usually the next instruction is a jump to skip a code block);        
        registerIndexX = (opcode & 0x0F00) >> 8
        registerIndexY = (opcode & 0x00F0) >> 4
        if (registers[registerIndexX] == registers[registerIndexY]):
            ip+=2
        ip+=2
    elif opcode >> 12 == 6:
        # Vx = N	Sets VX to NN.       
        var = opcode & 0x00FF
        registerIndex = (opcode & 0x0F00) >> 8
        registers[registerIndex] = var
        ip+=2
    elif opcode >> 12 == 7:
        # Vx += N	Adds NN to VX. (Carry flag is not changed);      
        var = opcode & 0x00FF
        registerIndex = (opcode & 0x0F00) >> 8
        registers[registerIndex] += var
        registers[registerIndex] &= 0xff

        ip+=2
    elif opcode >> 12 == 8:
        # set of opcodes starting with 8
        registerIndexX = (opcode & 0x0F00) >> 8
        registerIndexY = (opcode & 0x00F0) >> 4
        x = registers[registerIndexX]
        y = registers[registerIndexY]

        cmd = (opcode & 0x000F)
        
        if cmd == 0:
            # Vx = Vy	Sets VX to the value of VY. 
            registers[registerIndexX] = y
        elif cmd == 1:
            # Vx |= Vy	Sets VX to VX or VY. (Bitwise OR operation);
            registers[registerIndexX] = x | y
        elif cmd == 2:
            # Vx &= Vy	Sets VX to VX and VY. (Bitwise AND operation);
            registers[registerIndexX] = x & y
        elif cmd == 3:
            # Vx ^= Vy	Sets VX to VX xor VY.
            registers[registerIndexX] = x ^ y
        elif cmd == 4:
            # Vx += Vy	Adds VY to VX. VF is set to 1 when there's a carry, and to 0 when there is not.            
            registers[registerIndexX]+=y
            if registers[registerIndexX] & 0xF0000 == 1:
                registers[registerIndexX] = 0
                registers[0xF] = 1 
            else:
                registers[0xF] = 0
        elif cmd == 5:
            # Vx -= Vy	VY is subtracted from VX. VF is set to 0 when there's a borrow, and 1 when there is not.
            if y > x:
                registers[0xF] = 0
                registers[registerIndexX]-=y
            else:
                registers[0xF] = 1
                registers[registerIndexX]-=y + 0x100
        elif cmd == 6:
            # Vx >>= 1	Stores the least significant bit of VX in VF and then shifts VX to the right by 1.[b]
            registers[0xF] = x & 0x000F
            registers[registerIndexX] = x >> 1
        elif cmd == 7:
            # Vx = Vy - Vx	Sets VX to VY minus VX. VF is set to 0 when there's a borrow, and 1 when there is not.
            if x > y:
                registers[0xF] = 0
                registers[registerIndexX] = y - x
            else:
                registers[0xF] = 1
                registers[registerIndexX] = (y - x) + 0x100
        elif cmd == 8:
            # Vx <<= 1	Stores the most significant bit of VX in VF and then shifts VX to the left by 1.[b]
            registers[0xF] = (x & 0xF000) >> 12
            registers[registerIndexX] = x << 1
        
        ip+=2
    elif opcode >> 12 == 9:
        # if (Vx != Vy)	Skips the next instruction if VX does not equal VY. (Usually the next instruction is a jump to skip a code block);
        registerIndexX = (opcode & 0x0F00) >> 8
        registerIndexY = (opcode & 0x00F0) >> 4
        if (registers[registerIndexX] != registers[registerIndexY]):
            ip+=2
        ip+=2
    elif opcode >> 12 == 0xA:
        # MEM	I = NNN	Sets I to the address NNN.
        registers[16] = opcode & 0x0FFF
        ip+=2
    elif opcode >> 12 == 0xB:
        # PC = V0 + NNN	Jumps to the address NNN plus V0.
        ip = (opcode & 0x0FFF) + registers[0]
        ip+=2
    elif opcode >> 12 == 0xC:
        # Vx = rand() & NN	Sets VX to the result of a bitwise and operation 
        # on a random number (Typically: 0 to 255) and NN.
        randNum = random.randrange(0,256)
        registerIndexX = (opcode & 0x0F00) >> 8
        nn = opcode & 0x00FF
        registers[registerIndexX] = randNum & nn
        ip+=2
    elif opcode >> 12 == 0xD:
        # draw(Vx, Vy, N)	Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels. Each row of 8 pixels is read as bit-coded 
        # starting from memory location I; I value does not change after the execution of this instruction. As described above, VF is set to 1 if any screen pixels are flipped 
        # from set to unset when the sprite is drawn, and to 0 if that does not happen
        registerIndexX = (opcode & 0x0F00) >> 8
        registerIndexY = (opcode & 0x00F0) >> 4
        height = (opcode & 0x000F)
        registers[0xF] = 0
        
        width = 8
        x = registers[registerIndexX]
        y = registers[registerIndexY]
        i = registers[16]

        for row in range(0,height):
            data = memory[row + i]

            for col in range(0,width):
                if (data & (0x80 >> col)) != 0:
                    pos = (x + row + (col + y) * 64) % 2048

                    if screenData[pos] == 1:
                        registers[0xF] = 1
                    screenData[pos] ^= 1
        ip+=2
    elif opcode >> 12 == 0xE:
        registerIndexX = (opcode & 0x0F00) >> 8
        x = registers[registerIndexX]
        code = opcode & 0x00FF

        if code==0x9E:
            # EX9E	KeyOp	if (key() == Vx)	Skips the next instruction if the key stored in VX is pressed. 
            # (Usually the next instruction is a jump to skip a code block);
            raise NotImplementedError
        elif code==0xA1:
            # EXA1	KeyOp	if (key() != Vx)	Skips the next instruction if the key stored in VX is not pressed. (Usually the next instruction is a jump to skip a code block);
            raise NotImplementedError
        ip+=2
    elif opcode >> 12 == 0xF:
        registerIndexX = (opcode & 0x0F00) >> 8
        x = registers[registerIndexX]
        i = registers[16]
        code = opcode & 0x00FF

        if code==0x07:
            # FX07	Timer	Vx = get_delay()	Sets VX to the value of the delay timer.
            registers[registerIndexX] = dt
        elif code==0x0A:
            # FX0A	KeyOp	Vx = get_key()	A key press is awaited, and then stored in VX. 
            # (Blocking Operation. All instruction halted until next key event);
            raise NotImplementedError
            registers[registerIndexX] = key
        elif code==0x0A:
            # FX15	Timer	delay_timer(Vx)	Sets the delay timer to VX.
            dt = x
        elif code==0x15:
            
            raise NotImplementedError
            if keypressed == x:
                ip+=1
        elif code==0x18:
            # FX18	Sound	sound_timer(Vx)	Sets the sound timer to VX.
            st = x
        elif code==0x1E:
            # FX1E	MEM	I += Vx	Adds VX to I. VF is not affected.[c]
            registers[16]+=x
        elif code==0x29:
            # FX29	MEM	I = sprite_addr[Vx]	Sets I to the location of the sprite for the character in VX. Characters 0-F (in hexadecimal) are represented by a 4x5 font.
            raise NotImplementedError
        elif code==0x33:
            # FX33	BCD	
            # set_BCD(Vx)
            # *(I+0) = BCD(3);
            # *(I+1) = BCD(2);
            # *(I+2) = BCD(1);
            # Stores the binary-coded decimal representation of VX, with the most significant of three digits at the address in I, the middle digit at I plus 1, and the least significant 
            # digit at I plus 2. (In other words, take the decimal representation of VX, place the hundreds digit in memory at location in I, the tens digit at location I+1, and the ones
            #  digit at location I+2.);
            raise NotImplementedError
        elif code==0x55:
            # FX55	MEM	reg_dump(Vx, &I)	Stores V0 to VX (including VX) in memory starting at address I. The offset from I is increased by 1 for each value written, but I itself 
            # is left unmodified.[d]
            raise NotImplementedError
        elif code==0x65:
            # FX65	MEM	reg_load(Vx, &I)	Fills V0 to VX (including VX) with values from memory starting at address I. The offset from I is increased by 1 for each value written, 
            # but I itself is left unmodified.[d]
            raise NotImplementedError
        ip+=2
    
    return(stack, ip, memory, registers, screenData, dt, st)
















def clearDisplay(screenData):
    # reset all bits to 0 on screen
    for i in range(len(screenData)):
        screenData[i] = 0

def printState(stack, ip, memory, registers):
    print("V0=%s, V1=%s, V2=%s, V3=%s, V4=%s, V5=%s, V6=%s, V7=%s" % (hex(registers[0]),
                                                                            hex(registers[1]),
                                                                            hex(registers[2]),
                                                                            hex(registers[3]),
                                                                            hex(registers[4]),
                                                                            hex(registers[5]),
                                                                            hex(registers[6]),
                                                                            hex(registers[7])))
    print("V8=%s, V9=%s, VA=%s, VB=%s, VC=%s, VD=%s, VE=%s, VF=%s" % (hex(registers[8]),
                                                                            hex(registers[9]),
                                                                            hex(registers[10]),
                                                                            hex(registers[11]),
                                                                            hex(registers[12]),
                                                                            hex(registers[13]),
                                                                            hex(registers[14]),
                                                                            hex(registers[15])))
    print("I=%s" %(hex(registers[16])))    
    print("stack=%s" % str(stack))
    print("ip=%s" % hex(ip))
    opcode = memory[ip] << 8 | memory[ip + 1]
    print("next instruction = %s" % hex(opcode))    

def drawScreen(screen, screenData):
    for i in range(len(screenData)):
        bit = screenData[i]
        color = [0, 200*bit, 0]
        shape = pygame.Rect((i%64)*10, (i/64)*10, 10, 10)
        
        filling = 0
        
        pygame.draw.rect(screen, color, shape)
    pygame.display.flip()


    
    

