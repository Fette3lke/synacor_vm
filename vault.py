from random import randint
grid = [
    ['*', '8', '-', '1'],
    ['4', '*', '11', '*'],
    ['+', '4', '-', '18'],
    ['22', '-', '9', '*']
    ]

def findpath():
    it = 0
    while True:
        y = 3
        x = 0

        w = 22
        l = 0
        path = "22"
        op   = ""

        while l < 12:
            while True: # choose next step
                i = randint(0, 4)
                if i == 0:
                    if x == 2 and y == 0:
                        if w != 31:
                            continue
                    if x < 3:
                        x += 1
                        break
                if i == 1:
                    if x == 1 and y == 3:
                        continue
                    if x > 0:
                        x -= 1
                        break
                if i == 2:
                    if x == 0 and y == 2:
                        continue
                    if y < 3:
                        y += 1
                        break
                if i == 3:
                    if x == 3 and y == 1:
                        if w != 30:
                            continue
                    if y > 0:
                        y -= 1
                        break

            l += 1
            path += grid[y][x]
            op   += grid[y][x]
            if len(op) > 1:
                w = eval(str(w)+op)
                w = w % 32768
                op = ""
            if w == 30 and x == 3 and y == 0:
                print l, w, path
                return
        if (it % 10000) == 0:
            print l, w, path
        it += 1

findpath()
