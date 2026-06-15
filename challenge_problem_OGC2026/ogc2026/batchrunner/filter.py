import sys
inst = ''
for l in sys.stdin:
    l = l.rstrip()
    if 'Instance' in l:
        inst = l
    if any(x in l for x in ['[ICG]', 'window=', 'Repair done', 'Phase 1 done', 'Z1=']):
        if inst:
            print(inst)
            inst = ''
        print(l)
