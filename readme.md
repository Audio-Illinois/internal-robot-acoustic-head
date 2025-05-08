# Robotic Dummy Heads for Acoustic Data Collection

This repository contains open-source resources for building and using **robot dummy heads**, developed to collect high-quality data for the study of audio and acoustic processing algorithms. These heads are designed to mimic human acoustic properties while being mountable on robotic platforms, supporting realistic audio data capture even in environments with source motion.

<div style="text-align:center">
<img alt="Banner image showing 3D printed heads assembled in a row and disassembled in a suitcase. University/sponsor affilidations are shown at the bottom" src="./imgs/banner.png" width=80%>
</div>

## Overview
In tasks like sound localization, speech enhancement, or multi-microphone array processing, capturing realistic human-like audio is critical. Our dummy heads are designed to:

- Accurately model human head-related transfer functions (HRTFs)
- Provide interchangeable components for various research needs
- Integrate naturally with robotic platforms (e.g. our quiet turntable)

Our quiet turntable is designed to:
- Be inaudible in the far-field (>1.0 m), enabling recordings with source motion that are not possible with conventional, noisy robots
- Accurately repeat prior movements, enabling the use of objective performance metrics

Overall, these tools enable robust, reproducible audio data collection under controlled and in-the-wild conditions.

## Repository Structure

The project is modular, with each core component in its own subdirectory:

```
robot-dummy-head/
├── head-shell/ # 3D models and manufacturing specs for the head structure
├── robot-mount/ # The quiet turntable robot: 3D models, electronics, and code
└── auto-audio/ # Scripts for automated spatially-stationary and dynamic recordings with the head+robot
```

Further, detailed information can be found in each directory. `auto-audio` presumes that `head-shell` and `robot-mount` have been viewed and the instructions within followed, yielding the fully-assembled robotic head.

## Getting Started

Each subdirectory contains a README with build instructions, parts lists, and diagrams. To get started quickly:

1. Clone this repo
2. Review the [`head-shell`](./head-shell) and [`ear-assemblies`](./ear-assemblies) for 3D printing and assembly
3. Follow [`robot-mount`](./robot-mount) to attach the head to your robot
4. Use [`audio-calibration`](./audio-calibration) to validate audio performance

## Applications

- Binaural spatial audio
- Objective evaluation of audio and acoustic processing algorithms
- Dataset collection for speech source separation and enhancement
- Dataset collection for sound source localization

## Citation

If you use this resource in your research, please cite the following. Various acousitic measurements validating the acoustic realism of the dummy head or quietness and repeatability of the robot are provided in the paper as well.

```
@misc{lu2025,
      title={Accelerating Audio Research with Robotic Dummy Heads}, 
      author={Austin Lu and Kanad Sarkar and Yongjie Zhuang and Leo Lin and Ryan M Corey and Andrew C Singer},
      year={2025},
      eprint={2505.04548},
      archivePrefix={arXiv},
      primaryClass={eess.AS},
      url={https://arxiv.org/abs/2505.04548}, 
}
```
