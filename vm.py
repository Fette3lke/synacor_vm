# https://challenge.synacor.com/

import numpy as np
import sys
import time
import exceptions

CMD_KEY = '!'

## OPCODES
HALT = 0   # stop       - execution and terminate the program
SET = 1    # set a b    - set register <a> to value of <b>
PUSH = 2   # push a     - push <a> onto the stack
POP = 3    # pop a      - remove the top element from the stack and write it into <a>; empty stack = error
EQ = 4     # eq a b c   - set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise
GT = 5     # gt a b c   - set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise
JMP = 6    # jmp a      - Jump to <a>
JT = 7     # jt a b     - if <a> is nonzero, jump to <b>
JF = 8     # jf a b     - if <a> is zero, jump to <b>
ADD = 9    # add a b c  - store into <a> the sum of <b> and <c> (modulo 32768)
MULT = 10  # mult a b c - store into <a> the product of <b> and <c> (modulo 32768)
MOD = 11   # mod a b c  - store into <a> the remainder of <b> divided by <c>
AND = 12   # and a b c  - store into <a> the bitwise AND of <b> and <c>
OR = 13    # or a b c   - store into <a> the bitwise OR of <b> and <c>
NOT = 14   # not a b    - store into <a> 15-bit bitwise inverse of <b>
RMEM = 15  # rmem a b   - read memory at address <b> and write it to <a>
WMEM = 16  # wmem a b   - write the value from <b> into memory at address <a>
CALL = 17  # call a     - write the address of the next instruction to the stack and jump to <a>
RET = 18   # ret        - remove the top element from the stack and jump to it; empty stack = halt
OUT = 19   # out a      - write the character represented by asci code <a> to the terminal
IN = 20    # in a       - read a character from the terminal and write its ascii code to <a>; assume continues till
           #              newline
NOOP = 21  # noop       - no operation

NARGS = {
    HALT: 0,
    SET: 2,
    PUSH: 1,
    POP: 1,
    EQ: 3,
    GT: 3,
    JMP: 1,
    JT: 2,
    JF: 2,
    ADD: 3,
    MULT: 3,
    MOD: 3,
    AND: 3,
    OR: 3,
    NOT: 2,
    RMEM: 2,
    WMEM: 2,
    CALL: 1,
    RET: 0,
    OUT: 1,
    IN: 1,
    NOOP: 0
}

class vm(object):
    register = np.zeros(8, dtype=np.uint16)
    memory = np.zeros(2**16, dtype=np.uint16)
    stack = []
    location = 0
    running = False
    output = ""
    old_output = ""
    test = 0
    delay = 0
    debug = False
    pause = False
    breakchar = ""
    input = ""

    def loadbin(self, fname):
        with open(fname, "r") as f:
            self.memory = np.fromfile(f, dtype=np.uint16)
            self.location = 0

    def save(self, fname):
        with open(fname, "w") as f:
            np.uint16(self.location).tofile(f)
            np.uint16(len(self.stack)).tofile(f)
            np.array(self.stack, dtype=np.uint16).tofile(f)
            self.register.tofile(f)
            self.memory.tofile(f)

    def load(self, fname):
        with open(fname, "r") as f:
            self.location = np.fromfile(f, dtype=np.uint16, count=1)[0]
            nstack        = np.fromfile(f, dtype=np.uint16, count=1)[0]
            self.stack    = list(np.fromfile(f, dtype=np.uint16, count=nstack))
            self.register = np.fromfile(f, dtype=np.uint16, count=8)
            self.memory   = np.fromfile(f, dtype=np.uint16)

    def execute(self):
        i = self.location
        opcode = self.memory[i]
        try:
            {
                HALT: self.halt,
                SET : self.set,
                PUSH: self.push,
                POP : self.pop,
                EQ  : self.eq,
                GT  : self.gt,
                JMP : self.jmp,
                JT  : self.jt,
                JF  : self.jf,
                ADD : self.add,
                MULT: self.mult,
                MOD : self.mod,
                AND : self.And,
                OR  : self.Or,
                NOT : self.Not,
                RMEM: self.rmem,
                WMEM: self.wmem,
                CALL: self.call,
                RET : self.ret,
                OUT : self.out,
                IN  : self.In,
                NOOP: self.noop,
            }[opcode](*self.getargs(NARGS[opcode]))
        except KeyError:
            print "Unknown Opcode: %d at %d" % (opcode, i)
            print self.memory[i-5:i+3]
            self.running = False
            raise

    def run(self, location = 0):
        self.running = True
        self.location = location
        while self.running:
            try:
                self.execute()
                if self.pause:
                    self.pause = False
                    raise KeyboardInterrupt("pause")
                if self.delay:
                    time.sleep(self.delay)
            except KeyboardInterrupt:
                print ""
                cmd = ''
                while cmd != "c":
                    cmd = raw_input(">> ")
                    if cmd and cmd != "c":
                        self.interactive(cmd)
                while self.memory[self.location] not in NARGS and self.location > 0:
                    self.location -= 1
            #print self.location

    def next(self):
        self.location += 1

    def resolve(self, i):
        if i >= 32776:
            raise ValueError("cannot resolve")
        if i >= 32768:
            return self.register[i - 32768]
        if i == 11111:
            self.pause = True
        return i

    def get(self):
        self.next()
        val = (self.memory[self.location])
        return val

    def getRegister(self, i):
        if i >= 32768:
            reg = i - 32768
        else:
            reg = i
        if reg < 0 or reg > 7:
            print "!", reg
            raise ValueError("illegal register")
        return reg

    def getargs(self, n):
        args = []
        for i in range(n):
            args.append(self.get())
        self.next()
        return args

    def getTriple(self, r, a, b):
        return self.getRegister(r), self.resolve(a), self.resolve(b)

    def halt(self):
        print "halt encountered at location: ", self.location
        loc = self.location
        print "memory: ", self.memory[loc-32: loc+1]
        self.running = False

    def set(self, r, a):
        r = self.getRegister(r)
        self.register[r] = self.resolve(a)
        if (self.debug):
            print "set\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), "@%d = %d" % (r, self.register[r])

    def push(self, a):
        self.stack.append(self.resolve(a))
        if (self.debug):
            print "push\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), "%d" % self.stack[-1]

    def pop(self, r):
        if len(self.stack) < 1:
            raise BufferError("stack underflow")
        r = self.getRegister(r)
        self.register[r] = self.stack.pop()
        if (self.debug):
            print "pop\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), "@%d = %d" % (r, self.register[r])

    def eq(self, *args):
        r, a, b = self.getTriple(*args)
        if a == b:
            self.register[r] = 1
        else:
            self.register[r] = 0
        if (self.debug):
            print "eq\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), "@%d: %d == %d ?" %  (r, a, b)

    def gt(self, *args):
        r, a, b = self.getTriple(*args)
        if a > b:
            self.register[r] = 1
        else:
            self.register[r] = 0
        if (self.debug):
            print "gt\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), "@%d: %d > %d ?" %  (r, a, b)

    def jmp(self, a):
        loc = self.resolve(a)
        if (self.debug):
            print "jmp\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), "%d" % loc
        self.location = loc

    def jt(self, a, b):
        cond = self.resolve(a)
        loc = self.resolve(b)
        if (self.debug):
            print "jt\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), "%d ? %d" % (cond, loc)
        if cond != 0:
            self.location = loc

    def jf(self, a, b):
        cond = self.resolve(a)
        loc = self.resolve(b)
        if (self.debug):
            print "jf\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), "%d ? %d" % (cond, loc)
        if cond == 0:
            self.location = loc

    def add(self, *args):
        r, a, b = self.getTriple(*args)
        self.register[r] = (a + b) % 32768
        if (self.debug):
            print "add\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), "@%d: %d + %d = %d" %  (r, a, b, self.register[r])

    def mult(self, *args):
        r, a, b = self.getTriple(*args)
        d = np.int32(a)
        d = (d * b) % 32768
        self.register[r] = d
        if (self.debug):
            print "mult\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), "@%d: %d * %d = %d" %  (r, a, b, self.register[r])

    def mod(self, *args):
        r, a, b = self.getTriple(*args)
        self.register[r] = (a % b)
        if (self.debug):
            print "mod\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), "@%d: %d %% %d = %d" %  (r, a, b, self.register[r])

    def And(self, *args):
        r, a, b = self.getTriple(*args)
        self.register[r] = (a & b)
        if (self.debug):
            print "and\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), "@%d: %d & %d = %d" %  (r, a, b, self.register[r])

    def Or(self, *args):
        r, a, b = self.getTriple(*args)
        self.register[r] = (a | b)
        if (self.debug):
            print "or\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), "@%d: %d | %d = %d" %  (r, a, b, self.register[r])

    def Not(self, r, a):
        r = self.getRegister(r)
        a = self.resolve(a)
        self.register[r] = a ^ ((1<<15) - 1)
        if (self.debug):
            print "not\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), "@%d: ~%d = %d "  % (r, a, self.register[r])

    def rmem(self, r, a):
        r = self.getRegister(r)
        self.register[r] = self.memory[self.resolve(a)]
        if (self.debug):
            print "rmem\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), "@%d: #%d = %d" % (r, a, self.register[r])

    def wmem(self, a, b):
        address = self.resolve(a)
        val     = self.resolve(b)
        self.memory[address] = val
        if (self.debug):
            print "wmem\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), "#%d <- %d" % (address, val)

    def call(self, a):
        loc = self.resolve(a)
        self.stack.append(self.location)
        if (self.debug):
            print "call\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), "%d, %d" % (loc, a)
        self.location = loc

    def ret(self):
        if len(self.stack) < 1:
            raise BufferError("empty stack")
        self.location = self.stack.pop()
        if (self.debug):
            print "ret\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), self.location

    def out(self, a):
        self.output += chr(self.resolve(a))
        if self.breakchar and self.output[-1] == self.breakchar:
            self.pause = True
        if (self.debug):
            print "out\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), self.output[-32:]
        if self.output[-1] == "\n":
            #if self.output[:1] == "s":
                # self.safe('memdump')
            #    print self.location
            #    print self.register
            #    print self.stack
            print self.output,
            self.output = ""

    def In(self, r):
        r = self.getRegister(r)
        if (self.debug):
            print "in\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location]), r
        # self.debug = True
        while len(self.input) < 1:
            self.input = raw_input("> ")
            self.input += "\n"
            if self.input[0] == CMD_KEY:
                self.interactive(self.input[1:-1])
                self.input = ""

        self.register[r] = ord(self.input[0])
        self.input = self.input[1:]

    def noop(self):
        if (self.debug):
            print "noop\t", "{:5} {:5} {:5} {:5} {:5} |".format(self.location-4, *self.memory[self.location-4:self.location])

    def show(self, attr):
        try:
            print getattr(self, attr)
        except (KeyError) as e:
            print "Error: ", e

    def change(self, attr, val):
        setattr(self, attr, eval(val))

    def interactive(self, cmd):
        args = cmd.split()
        for i in range(1, len(args)):
            try:
                n = np.uint16(args[i])
                args[i] = n
            except ValueError:
                pass
        try:
            getattr(self, args[0])(*args[1:])
        except Exception as e:
            print e
            if type(e) == exceptions.KeyboardInterrupt:
                raise

        #self.__dict__[args[0]](*args[1:])


VM = vm()
VM.debug = False
# VM.loadbin('challenge.bin')
VM.load('memdump')
VM.next()

print VM.location
print VM.register
print VM.stack
try:
    VM.run(VM.location)
except ValueError:
    loc = VM.location
    print "memory:   ", VM.memory[loc-1:loc+3]
    print "register: ", VM.register
    raise
