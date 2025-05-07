#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os

'''
Relies on arduino-cli, can be installed at https://arduino.github.io/arduino-cli/0.32/installation/. 
Suggested:
```
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=$ANY_DIR_ON_PATH sh
```
'''

def compile_and_upload(port, ino_path, board_fqbn):
    sketch_dir = os.path.dirname(ino_path)

    print("🔧 Compiling sketch...")
    compile_cmd = [
        "arduino-cli", "compile",
        "--fqbn", board_fqbn,
        sketch_dir
    ]
    result = subprocess.run(compile_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Compilation failed:\n", result.stderr)
        return

    print("✅ Compilation successful.")

    print("⬆️  Uploading to Arduino...")
    upload_cmd = [
        "arduino-cli", "upload",
        "--fqbn", board_fqbn,
        "-p", port,
        sketch_dir
    ]
    result = subprocess.run(upload_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Upload failed:\n", result.stderr)
    else:
        print("✅ Upload successful.")

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='Upload Arduino Code',
        description='Upload any arduino source file (.ino) to a connected Arduino, so we don\'t need to *use* the Arduino IDE (we still need to have it though)',
    )
    parser.add_argument('-P', '--port', default='/dev/ttyUSB0', type=str)
    parser.add_argument('-p', '--path', default='../src/turret_control/turret_control.ino', type=str)
    parser.add_argument('-b', '--board', default='arduino:avr:nano', type=str)
    args = parser.parse_args()

    compile_and_upload(args.port, args.path, args.board)