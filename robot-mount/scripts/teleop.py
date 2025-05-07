#!/usr/bin/env python3
import sys
import time
sys.path.append('..')

from src import turret

port = sys.argv[1]
robot = turret.Turret(port)

while (True):
    cmd = input('Input: ')
    if cmd == '':
        break

    if cmd.startswith(turret.CMD_HOME):
        robot.Home()
    elif cmd.startswith(turret.CMD_MOVE):
        args = cmd.split()
        rps = turret.DEFAULT_SPEED if len(args)==2 else float(args[2])
        deg = int(args[1])
        robot.Move(deg, rps=rps, delay_ms=0)
    else:
        print('unk.')
    
print('Done.')