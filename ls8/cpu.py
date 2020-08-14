"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
JMP = 0b01010100
CMP = 0b10100111
LMASK = 0b100
GMASK = 0b010
EMASK = 0b001
JEQ = 0b01010101
JNE = 0b01010110
ST = 0b10000100

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        #self.sp = 7
        self.reg[6] = 0xF4
        self.pc = 0
        self.fl = 0
        self.branchtable = {}

    def load(self):
        """Load a program into memory."""

        address = 0
        with open(sys.argv[1], 'r') as f:
            program = f.readlines()

            for instruction in program:
                inst = instruction.split('#')[0].strip()
                if inst == '':
                    continue
                inst_num = int(inst, 2)
                self.ram[address] = inst_num
                address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op =="CMP":
            reg_a_val = self.reg[reg_a]
            reg_b_val = self.reg[reg_b]
            if reg_a_val < reg_b_val:
                self.fl = LMASK
            elif reg_a_val > reg_b_val:
                self.fl = GMASK
            else:
                self.fl = EMASK

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while True:
            op_code = self.ram_read(self.pc)
            #print(op_code)
            #print(self.pc)
            ir = op_code >> 6
            #print(ir)


            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
        
            if op_code == HLT:
                break
            elif op_code == LDI:
                self.reg[operand_a] = operand_b
                self.pc += 3
            elif op_code == PRN:
                print(self.reg[operand_a])
                self.pc += 2
            elif op_code == ADD:
                self.alu("ADD", operand_a, operand_b)
                self.pc += 3
            elif op_code == MUL:
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3
            elif op_code == PUSH:
                # Decrement the stack pointer
                self.reg[6] -= 1
                # Copy the value in the given register to the address pointed to by SP.
                tmp = self.reg[operand_a]
                self.ram[self.reg[6]] = tmp
                self.pc += 2
            elif op_code == POP:
                # 1. Copy the value from the address pointed to by `SP` to the given register.
                tmp = self.ram[self.reg[6]]
                self.reg[operand_a] = tmp
                # 2. Increment `SP`.
                self.reg[6] += 1
                self.pc += 2
            elif op_code == CALL:
#                 1. The address of the instruction _directly after_ `CALL` is
#                   pushed onto the stack. This allows us to return to where we left off when the subroutine finishes executing.
                # Decrement the stack pointer
                self.reg[6] -= 1
                tmp = self.pc +2
                self.ram[self.reg[6]] = tmp
                self.pc = self.reg[operand_a]
#                 2. The PC is set to the address stored in the given register. We jump to that location in RAM and execute the first instruction in the subroutine. The PC can move forward or backwards from its current location.
            elif op_code == RET:
                # pop return value off the stack
                tmp = self.ram[self.reg[6]]
                # set the pc to the return value
                self.pc = tmp
                # 2. Increment `SP`.
                self.reg[6] += 1
            elif op_code == JMP:
                self.pc = self.reg[operand_a]
            elif op_code == CMP:
                self.alu("CMP", operand_a, operand_b)
                self.pc += 3
            elif op_code == JEQ:
                if self.fl == EMASK:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2
            elif op_code == JNE:
                if self.fl != EMASK:
                # if not (self.fl == EMASK):
                # if self.fl & EMASK == 0
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2
            elif op_code == ST:
                reg_a_val = self.reg[operand_a]
                reg_b_val = self.reg[operand_b]
                self.ram[reg_a_val] = reg_b_val
                self.pc += 3

    def ram_read(self, MAR):
        return self.ram[MAR]

    

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR