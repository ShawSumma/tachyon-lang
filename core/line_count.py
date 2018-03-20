import os
lins = 0
for i in os.listdir():
    if i[0] not in '_.' and i != 'line_count.py':
        lins += len(list(filter(lambda x: x.strip() != '' and x.strip()[0] != '#',open(i).read().split('\n'))))
print(lins)
