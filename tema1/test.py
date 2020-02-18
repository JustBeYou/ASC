from math import gcd

def find_bad(p):
    for g in range(2, p):
        if gcd(g, p) != 1: continue
        values = [1, g]
        found_one = False

        print ("g = {}".format(g))
        v = g
        for i in range(2, p - 1):
            v *= g
            v %= p
            print (v,  end=' ')
            values.append(v)
            if v == 1:
                found_one = True

        print ()
        if len(set(values)) == p - 1 and found_one == False:
            print ("{} is generator".format(g))
        elif found_one == False:
            print ("baaaad {}".format(g))
            exit()
        else:
            pass

for i in range(3, 1000):
    print ("p:" + str(i))
    find_bad(i)
