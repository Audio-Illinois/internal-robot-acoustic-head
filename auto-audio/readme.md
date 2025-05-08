# Automated Experiments with the Robot Dummy Head

Presuming you have both the dummy head in [`../head-shell/`](../head-shell/) and robot turntable in [`../robot-mount/`](../robot-mount/) set up an assembled properly, with teleop working for the latter, then you can run some basic automated experments using the scripts in this folder.

## 1. Setup

Connect the host PC to:
1. The robot PCB, via USB serial
2. Any audio interface

Ensure that the audio interface can be identified via Python. Note that the `sounddevice` library uses `PortAudio` to this end.

```python
import sounddevice as sd
sd.query_devices()
```

> 💡 A common issue is your device being listed, but with 0 input or output channels. Check that no other application is using the audio interface, or on Ubuntu, run `pulseaudio -k` to reset system audio.

Check robot responsiveness by following the guide in [`../robot-mount/`](../robot-mount/). Keep an eye out for egregious latency between submitting a command and the robot performing that action, or for mismatch between the commanded motion extent and the observed movement.

> 💡 On an Ubuntu machine, you likely should set `PORT=/dev/ttyUSB0`. On Windows, try `PORT=COM4`.

## 2. Automatic HRTF or Directivity recordings

Run
```bash
python3 ./auto_still.py -p $PORT -r $path_to_wav_to_play -w $path_to_save_recordings_to
```
to have the dummy head rotated in a full 360 degrees, in increments of 45 degrees. At each position, audio at `$path_to_wav_to_play` is played from the mouth loudspeaker (or whichever loudspeakers are connected to the audio interface). At the same time, audio is recorded from both ears (or whichever mics are connected to the audio interface) to `$path_to_save_recordings_to`. Before recording, the dummy head will self-home.

To measure an HRTF, instead of the mouth loudspeaker, a studio monitor in the far-field could be used as the audio output.
```bash
python3 ./auto_still.py -p $PORT -r $path_to_wav_to_play -w $path_to_save_recordings_to -i 15
```

To mesaure directivity of the dummy head, record from a single microphone in the far-field.
```bash
python3 ./auto_still.py -p $PORT -r $path_to_wav_to_play -w $path_to_save_recordings_to -i 15 -c 1
```


For convenience, we provide a [clip of a reading of the Rainbow Passage](https://www.voxforge.org/home/audacity/the-rainbow-passage) at `./audio/rp-01.wav`. 

## 3. Recording a moving sound source

Run
```bash
python3 ./auto_move.py -p $PORT -r $path_to_wav_to_play -w $path_to_save_recordings_to
```
to have the dummy head rotate _while_ audio is played and recorded. Before recording, the dummy head will self-home.


> 💡 A possible issue is latency in the recorded audio. This can be remedied with a loopback audio channel and subsequent sample-wise synchronization in post-processing.

> 💡 The above scripts were tested on an host PC with Ubuntu 20.04 LTS, ALSA audio, and Python 3.8.10, connected to a [Behringer U-Phoria UMC202HD](https://www.behringer.com/product.html?modelCode=0805-AAR) audio interface.

> 💡 Due to the choice of a weak-as-possible stepper motor, any tangles in the dummy head cables will **not** cause the dummy head to fall, or the cables to be damaged.
