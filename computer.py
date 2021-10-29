def computeInstruction(stack, ip, memory, registers):
    opcode = memory[stack[-1] + ip]
    # take opcode and perform action
    if opcode == 0x00E0:
        __clearDisplay()
        ip+=1
    elif opcode == 0x00EE:
        print("computer was instructed to return")
        stack.pop()
        # if there is anything left, set IP to it.  Otherwise, an empty stack indicates halt.
        if len(stack)>0:
            ip=stack[-1]+1
    elif opcode >> 12 == 0:
        # Calls machine code routine (RCA 1802 for COSMAC VIP) at address NNN. 
        # Not necessary for most ROMs.
        raise NotImplementedError
    elif opcode >> 12 == 1:
        # goto NNN;	Jumps to address NNN.
        ip = opcode & 0x0FFF
    elif opcode >> 12 == 2:
        # *(0xNNN)()	Calls subroutine at NNN.
        # update stack pointer
        stack[-1]=ip
        ip = 0
        stack.append(opcode & 0x0FFF)
        print(stack)
    elif opcode >> 12 == 3:
        # if (Vx == NN)	Skips the next instruction if VX equals NN.
        #  (Usually the next instruction is a jump to skip a code block);
        var = opcode & 0x00FF
        registerIndex = (opcode & 0x0F00) >> 8
        if (registers[registerIndex] == var):
            ip+=1
        ip+=1
    elif opcode >> 12 == 4:
        # if (Vx != NN)	Skips the next instruction if VX does not equal NN. 
        # (Usually the next instruction is a jump to skip a code block);
        var = opcode & 0x00FF
        registerIndex = (opcode & 0x0F00) >> 8
        if (registers[registerIndex] != var):
            ip+=1
        ip+=1
    elif opcode >> 12 == 5:
        # if (Vx == Vy)	Skips the next instruction if VX equals VY. 
        # (Usually the next instruction is a jump to skip a code block);        
        registerIndexX = (opcode & 0x0F00) >> 8
        registerIndexY = (opcode & 0x00F0) >> 4
        if (registers[registerIndexX] == registers[registerIndexY]):
            ip+=1
        ip+=1
    elif opcode >> 12 == 6:
        # Vx = N	Sets VX to NN.       
        var = opcode & 0x00FF
        registerIndex = (opcode & 0x0F00) >> 8
        registers[registerIndex] = var
        ip+=1
    elif opcode >> 12 == 7:
        # Vx += N	Adds NN to VX. (Carry flag is not changed);      
        var = opcode & 0x00FF
        registerIndex = (opcode & 0x0F00) >> 8
        registers[registerIndex] += var

        # prevent overflow
        registers[registerIndex] = registers[registerIndex] & 0x00FF
        ip+=1
        
    
    return(stack, ip, memory, registers)



def __clearDisplay():
    print("computer was instructed to clear display")




# 8XY0	Assig	Vx = Vy	Sets VX to the value of VY.
# 8XY1	BitOp	Vx |= Vy	Sets VX to VX or VY. (Bitwise OR operation);
# 8XY2	BitOp	Vx &= Vy	Sets VX to VX and VY. (Bitwise AND operation);
# 8XY3[a]	BitOp	Vx ^= Vy	Sets VX to VX xor VY.
# 8XY4	Math	Vx += Vy	Adds VY to VX. VF is set to 1 when there's a carry, and to 0 when there is not.
# 8XY5	Math	Vx -= Vy	VY is subtracted from VX. VF is set to 0 when there's a borrow, and 1 when there is not.
# 8XY6[a]	BitOp	Vx >>= 1	Stores the least significant bit of VX in VF and then shifts VX to the right by 1.[b]
# 8XY7[a]	Math	Vx = Vy - Vx	Sets VX to VY minus VX. VF is set to 0 when there's a borrow, and 1 when there is not.
# 8XYE[a]	BitOp	Vx <<= 1	Stores the most significant bit of VX in VF and then shifts VX to the left by 1.[b]
# 9XY0	Cond	if (Vx != Vy)	Skips the next instruction if VX does not equal VY. (Usually the next instruction is a jump to skip a code block);
# ANNN	MEM	I = NNN	Sets I to the address NNN.
# BNNN	Flow	PC = V0 + NNN	Jumps to the address NNN plus V0.
# CXNN	Rand	Vx = rand() & NN	Sets VX to the result of a bitwise and operation on a random number (Typically: 0 to 255) and NN.
# DXYN	Disp	draw(Vx, Vy, N)	Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels. Each row of 8 pixels is read as bit-coded starting from memory location I; I value does not change after the execution of this instruction. As described above, VF is set to 1 if any screen pixels are flipped from set to unset when the sprite is drawn, and to 0 if that does not happen
# EX9E	KeyOp	if (key() == Vx)	Skips the next instruction if the key stored in VX is pressed. (Usually the next instruction is a jump to skip a code block);
# EXA1	KeyOp	if (key() != Vx)	Skips the next instruction if the key stored in VX is not pressed. (Usually the next instruction is a jump to skip a code block);
# FX07	Timer	Vx = get_delay()	Sets VX to the value of the delay timer.
# FX0A	KeyOp	Vx = get_key()	A key press is awaited, and then stored in VX. (Blocking Operation. All instruction halted until next key event);
# FX15	Timer	delay_timer(Vx)	Sets the delay timer to VX.
# FX18	Sound	sound_timer(Vx)	Sets the sound timer to VX.
# FX1E	MEM	I += Vx	Adds VX to I. VF is not affected.[c]
# FX29	MEM	I = sprite_addr[Vx]	Sets I to the location of the sprite for the character in VX. Characters 0-F (in hexadecimal) are represented by a 4x5 font.
# FX33	BCD	
# set_BCD(Vx)
# *(I+0) = BCD(3);
# *(I+1) = BCD(2);
# *(I+2) = BCD(1);
# Stores the binary-coded decimal representation of VX, with the most significant of three digits at the address in I, the middle digit at I plus 1, and the least significant digit at I plus 2. (In other words, take the decimal representation of VX, place the hundreds digit in memory at location in I, the tens digit at location I+1, and the ones digit at location I+2.);
# FX55	MEM	reg_dump(Vx, &I)	Stores V0 to VX (including VX) in memory starting at address I. The offset from I is increased by 1 for each value written, but I itself is left unmodified.[d]
# FX65	MEM	reg_load(Vx, &I)	Fills V0 to VX (including VX) with values from memory starting at address I. The offset from I is increased by 1 for each value written, but I itself is left unmodified.[d]



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
    print("stack=%s" % str(stack))
    print("ip=%d" % ip)
    print("next instruction = %s" % hex(memory[stack[-1]+ip]))    
