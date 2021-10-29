# make fancy later.  Right now just working out the basic mechanics of things
# look more in 7XNN

# for now keeping this separate
import computer

memory = [0] * 4096
registers = [0] * 16
stack = [0]
ip = 0
ipInHex = hex(ip)

# sample program (call subroutine that counts to ten, then return, then halts)
program = [0x2002, 0x00EE, 0x7001, 0x300A, 0x1000, 0x00EE]

# load instructions into memory
for i in range(0,len(program)):
    memory[i]=program[i]

# continue execution until the stack has been emptied
while len(stack)>0:    
    computer.printState(stack, ip, memory, registers)
    (stack, ip, memory, registers) = computer.computeInstruction(stack, ip, memory, registers)
    ipInHex = hex(ip)
    
    

    
    
    
