#!/usr/bin/env python3
import sys, os, time
import numpy as np
import soundfile as sf
import sounddevice as sd
import argparse
sys.path.append('../robot-mount')
from src import turret

delay = 2
homing_delay = 5
rec_buffer = None

def PlayRecAudio(in_audio, out_path, fs):
    def on_start():

        global rec_buffer
        dur = in_audio.shape[0] / fs

        print (f'Started recording (~{dur:.2f}s).')
        rec_buffer = sd.playrec(in_audio, blocking=False)

    def on_end():
        global rec_buffer

        sd.stop()
        print (f'Done Recording.')

        if out_path is not None:
            sf.write(out_path, rec_buffer, fs)
        print (f'Done Saving to "{out_path}".')

    return on_start, on_end



def AutomateMoving(
        robot,
        extent:int,
        rps:float,
        play_audio:np.ndarray,
        out_path:str,
        fs:int,
        movement_delay:float,
    ):
    '''
    Rotate `extent` degrees at speed `rps` *while* playing out `play_audio` and recording to
    `out_path`, all at sampling frequency `fs`. Movement will occur `movement_delay` seconds
    after playback starts.

    The audio written to `out_path` will have the same duration of `play_audio` regardless of
    movement speed/duration.
    '''
    on_start, on_end = PlayRecAudio(play_audio, out_path=out_path, fs=fs)

    print ('Actually moving (after 1s initial)...')
    robot.Move(
        rps=rps,
        deg=extent,
        delay_ms=1000*movement_delay, # seconds to milliseconds
        on_start=on_start,
        on_end=on_end,
    )
    print (f'Done for {rps} rps.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default='/dev/ttyUSB0', type=str)
    parser.add_argument('-r', '--readfrom', required=True, type=str)
    parser.add_argument('-w', '--writeto', required=True, type=str)

    parser.add_argument('-s', '--speed', default=0.1, type=float)
    parser.add_argument('-e', '--extent', default=360, type=int)
    parser.add_argument('-g', '--gain', default=0, type=float) # in dB
    parser.add_argument('-c', '--channels', default=2, type=int) # recording channels
    parser.add_argument('-md', '--movement-delay', default=0, type=float) # delay (seconds) between starting movement and recording/playback
    args = parser.parse_args()

    # Set up serial communication to robot
    robot = turret.Turret(args.port)

    # Load playback audio signal
    play_audio, fs = sf.read(args.readfrom)
    if play_audio.ndim == 1:
        play_audio = play_audio[:,None]

    # Adjust playback audio signal gain
    assert args.gain <= 0
    scale = 10**(args.gain/20) # dB to scale
    play_audio *= scale
    assert (abs(play_audio).max() < 1), "Dangerously loud!"
    print (f'Probe signal loaded ({fs} Hz).')

    # Set up audio driver settings
    n_sample, n_ch = play_audio.shape
    sd.default.channels = (args.channels, n_ch) # in, out
    sd.default.samplerate = fs # same as playback audio
    sd.default.latency = 'low'

    # Prompt user to choose an audio device
    devices = sd.query_devices()
    print (devices)
    device_idx = int(input('Audio Device Index: '))

    sd.default.device = device_idx
    print ('\nIMPORTANT!: If device settings seem wrong, try `pulseaudio -k` to restart pulse audio, or reboot.')
    print ('Audio Device Set.')

    # Warm up audio device (necessary in some setups)
    PlayRecAudio(play_audio, out_path=None, fs=fs)
    print ('Audio Device Primed.')

    # Set up experiment
    robot.Home(); time.sleep(homing_delay) # wait for rocking to stop
    print ('Robot Homed and Moved to Start Position.')
    
    # Run experiment
    AutomateMoving(
        robot=robot,
        extent=args.extent, 
        rps=args.speed,
        play_audio=play_audio,
        out_path=args.writeto,
        fs=fs,
        movement_delay=args.movement_delay,
    )
    time.sleep(delay)

    print ('Undoing rotation!')
    robot.Move(deg=-args.extent)
    print ('End.')