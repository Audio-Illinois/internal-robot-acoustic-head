#!/usr/bin/env python3
import sys, os, time
import numpy as np
import soundfile as sf
import sounddevice as sd
import argparse
sys.path.append('./robot-mount')
from src import turret

homing_delay = 3
delay = 1



def PlayRecAudio(in_audio, out_path, fs):
    dur = in_audio.shape[0] / fs
    print (f'Started recording ({dur:.2f}s)')
    rec = sd.playrec(in_audio, blocking=True)

    print (f'Done Recording ({rec.shape}).')
    if out_path is not None:
        sf.write(out_path, rec, fs)
    print (f'Done Saving to "{out_path}".\n')



def AutomateStill(
        robot,
        extent:int,
        increment:int,
        play_audio:np.ndarray,
        out_dir:str,
        fs:int
    ):
    '''
    Rotate `extent` degrees in increments of `increment` degrees. Play `play_audio`
    between each increment while recording to `out_dir` simultaneously. Recordings
    will be labeled with the corresponding angular position. Sampling frequency
    will be `fs` Hz.
    '''
    angles = np.arange(0,extent,increment)

    for i in angles:
        label = f'{i:.2f}deg'
        out_path = f'{out_dir}/{label}.wav'

        PlayRecAudio(play_audio, out_path, fs)
        robot.Move(deg=increment); time.sleep(delay)

    print (f'Done.')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default='/dev/ttyUSB0', type=str)
    parser.add_argument('-r', '--readfrom', required=True, type=str)
    parser.add_argument('-w', '--writeto', required=True, type=str)

    parser.add_argument('-e', '--extent', default=360, type=int)
    parser.add_argument('-i', '--increment', default=0.45, type=float)
    parser.add_argument('-g', '--gain', default=-20, type=float)
    parser.add_argument('-c', '--channels', default=2, type=int)
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

    # Set up directory to save recorded audio to
    os.mkdir(args.writeto)
    print (f'Output directory set to "{args.writeto}"')

    # Set up experiment
    robot.Home(); time.sleep(homing_delay) # wait for rocking to stop
    print ('Robot Homed and Moved to Start Position.')

    # Run experiment
    AutomateStill(
        robot=robot,
        extent=args.extent, 
        increment=args.increment,
        play_audio=play_audio,
        out_dir=args.writeto,
        fs=fs,
    )
    time.sleep(delay)

    print ('Undoing rotation!')
    robot.Move(deg=-args.extent)
    print ('End.')