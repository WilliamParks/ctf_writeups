bad_char = ">"

flag = [bad_char for _ in range(58)] #Empty
flag[57] = "}"
flag[0] = "O"
flag[1] = "O"
flag[2] = "O"

# llle(8,11,17,22,26,30,34,39,44,51)be(0,1,2)rle(20,32,37,54)be(27)re(31,55)re(25,38,50)zzzbe(4,6,15,16,19,36)rle(13,41)re(42,49)zbe(24)re(9)zzbe(7,33)rlle(23,28)re(48)zbe(14,21,35,53)re(43,45)zbe(12,40,46,52)rle(47)be(5)re(10,18,29)re(3)zzzz
variable_ones = "(20,32,37,54)be(27)re(31,55)re(25,38,50)zzzbe(4,6,15,16,19,36)rle(13,41)re(42,49)zbe(24)re(9)zzbe(7,33)rlle(23,28)re(48)zbe(14,21,35,53)re(43,45)zbe(12,40,46,52)rle(47)be(5)re(10,18,29)"
for i in "brelz(":
    variable_ones = variable_ones.replace(i,"")
groups = variable_ones.split(")")
print(groups)
w = []
for g in groups:
    if g == "":
        continue
    w += [g.split(",")]

sols = []
def build_from_dict(d):
    assert(len(d) < 35)
    flag = [bad_char for _ in range(57)]  # Empty
    for key, value in d.items():
        for i in value:
            flag[int(i)] = key
    global sols
    sols += ["".join(flag)]

def build_solution(base_solution, min_index, rest_candidates):
    if len(rest_candidates) == 0:
        build_from_dict(base_solution)
    else:
        candidate = rest_candidates[0]
        rest = rest_candidates[1:]
        for i in range(min_index, 26 - len(rest_candidates)+1):
            temp_val = chr(0x61 + i)
            base_solution[temp_val] = candidate
            build_solution(base_solution, i+1, rest)

def main():
    base_map = {" ":[8,11,17,22,26,30,34,39,44,51], "O":[0,1,2], "{":[3], "}":[56]}
    build_solution(base_map, 0, w)
    global sols
    with open("solutions.txt","w") as f:
         for s in sols:
             f.write(s + "\n")

if __name__ == '__main__':
    main()

    #"OOO{even my three year old boy can read this stupid trace}"