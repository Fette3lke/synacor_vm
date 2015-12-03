# https://challenge.synacor.com/

import numpy as np
import time
import sys

class vm(object):
    register = np.zeros(8, dtype=np.uint16)
    memory = np.zeros(2**16, dtype=np.uint16)
    stack = []
    location = 0
    running = False
    output = ""
    old_output = ""
    test = 0
    debug = False

    def load(self, fname):
        with open(fname, "r") as f:
            self.memory = np.fromfile(f, dtype=np.uint16)
            self.location = 0

    def safeState(self, fname):
        with open(fname, "w") as f:
            np.uint16(self.location).tofile(f)
            np.uint16(len(self.stack)).tofile(f)
            np.array(self.stack, dtype=np.uint16).tofile(f)
            self.register.tofile(f)
            self.memory.tofile(f)

    def loadState(self, fname):
        with open(fname, "r") as f:
            self.location = np.fromfile(f, dtype=np.uint16, count=1)[0]
            nstack        = np.fromfile(f, dtype=np.uint16, count=1)[0]
            self.stack    = list(np.fromfile(f, dtype=np.uint16, count=nstack))
            self.register = np.fromfile(f, dtype=np.uint16, count=8)
            self.memory   = np.fromfile(f, dtype=np.uint16)


    def execute(self):
        i = self.location
        try:
            {
                 0: self.halt,
                 1: self.set,
                 2: self.push,
                 3: self.pop,
                 4: self.eq,
                 5: self.gt,
                 6: self.jmp,
                 7: self.jt,
                 8: self.jf,
                 9: self.add,
                10: self.mult,
                11: self.mod,
                12: self.And,
                13: self.Or,
                14: self.Not,
                15: self.rmem,
                16: self.wmem,
                17: self.call,
                18: self.ret,
                19: self.out,
                20: self.In,
                21: self.noop,
            }[self.memory[i]]()
        except KeyError:
            print "Unknown Opcode: %d" % i
            print self.memory[i]
            self.running = False

    def run(self, location = 0):
        self.running = True
        self.location = location
        while self.running:
            self.execute()
            #print self.location

    def next(self):
        self.location += 1

    def resolve(self, i):
        if i >= 32776:
            raise ValueError("cannot resolve")
        if i >= 32768:
            return self.register[i - 32768]
        return i

    def get(self):
        self.next()
        val = self.resolve(self.memory[self.location])
        return val

    def getRegister(self):
        self.next()
        reg = self.memory[self.location] - 32768
        if reg < 0 or reg > 7:
            print "!", reg
            raise ValueError("illegal register")
        return reg

    def getTriple(self):
        return self.getRegister(), self.get(), self.get()

    def halt(self):
        print "halt encountered at location: ", self.location
        loc = self.location
        print "memory: ", self.memory[loc-32: loc+1]
        self.running = False

    def set(self):
        r = self.getRegister()
        self.register[r] = self.get()
        if (self.debug):
            print "set\t", self.location, r, self.register[r]
        self.next()

    def push(self):
        self.stack.append(self.get())
        if (self.debug):
            print "push\t", self.location, self.stack[-1]
        self.next()

    def pop(self):
        if len(self.stack) < 1:
            raise BufferError("stack underflow")
        r = self.getRegister()
        self.register[r] = self.stack.pop()
        if (self.debug):
            print "pop\t", self.location, r, self.register[r]
        self.next()

    def eq(self):
        r, a, b = self.getTriple()
        if a == b:
            self.register[r] = 1
        else:
            self.register[r] = 0
        if (self.debug):
            print "eq\t", self.location, r, a, b
        self.next()

    def gt(self):
        r, a, b = self.getTriple()
        if a > b:
            self.register[r] = 1
        else:
            self.register[r] = 0
        if (self.debug):
            print "gt\t", self.location, r, a, b
        self.next()

    def jmp(self):
        loc = self.get()
        if (self.debug):
            print "jmp\t", self.location, loc
        self.location = loc

    def jt(self):
        cond = self.get()
        loc = self.get()
        if (self.debug):
            print "jt\t", self.location, cond, loc
        if cond != 0:
            self.location = loc
        else:
            self.next()

    def jf(self):
        cond = self.get()
        loc = self.get()
        if (self.debug):
            print "jf\t", self.location, cond, loc
        if cond == 0:
            self.location = loc
        else:
            self.next()

    def add(self):
        r, a, b = self.getTriple()
        self.register[r] = (a + b) % 32768
        if (self.debug):
            print "add\t", self.location, r, a, b, self.register[r]
        self.next()

    def mult(self):
        r, a, b = self.getTriple()
        d = np.int32(a)
        d = (d * b) % 32768
        self.register[r] = d
        if (self.debug):
            print "mult\t", self.location, r, a, b, self.register[r]
        self.next()

    def mod(self):
        r, a, b = self.getTriple()
        self.register[r] = (a % b)
        if (self.debug):
            print "mod\t", self.location, r, a, b, self.register[r]
        self.next()

    def And(self):
        r, a, b = self.getTriple()
        self.register[r] = (a & b)
        if (self.debug):
            print "and\t", self.location, r, a, b, self.register[r]
        self.next()

    def Or(self):
        r, a, b = self.getTriple()
        self.register[r] = (a | b)
        if (self.debug):
            print "or\t", self.location, r, a, b, self.register[r]
        self.next()

    def Not(self):
        r = self.getRegister()
        a = self.get()
        self.register[r] = a ^ ((1<<15) - 1)
        if (self.debug):
            print "not\t", self.location, r, a, self.register[r]
        self.next()

    def rmem(self):
        r = self.getRegister()
        self.register[r] = self.memory[self.get()]
        if (self.debug):
            print "rmem\t", self.location, r, self.register[r]
        self.next()

    def wmem(self):
        address = self.get()
        val     = self.get()
        self.memory[address] = val
        if (self.debug):
            print "wmem\t", self.location, address, val
        self.next()

    def call(self):
        loc = self.get()
        self.stack.append(self.location + 1)
        if (self.debug):
            print "call\t", self.location, loc
        self.location = loc

    def ret(self):
        if len(self.stack) < 1:
            raise BufferError("empty stack")
        self.location = self.stack.pop()
        if (self.debug):
            print "ret\t", self.location

    def out(self):
        self.output += chr(self.get())
        if (self.debug):
            print "out\t", self.location, self.output[-1]
        if self.output[-1] == "\n":
            if self.output[:1] == "s":
                # self.safeState('memdump')
                print self.location
                print self.register
                print self.stack
            print self.output
            self.output = ""
        self.next()

    def In(self):
        r = self.getRegister()
        if (self.debug):
            print "in\t", self.location, r
        # self.debug = True
        inp = ''
        print "> ",
        while inp != '\n':
            inp = sys.stdin.read(1)
        self.register[r] = ord(inp[0])
        self.next()

    def noop(self):
        if (self.debug):
            print "noop\t", self.location
        self.next()

VM = vm()
VM.debug = True
# VM.load('challenge.bin')
VM.loadState('memdump')
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
