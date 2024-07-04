import sys

sys.path.append("/workspaces/waloviz/src")
sys.path.append("/home/runner/work/waloviz/waloviz/src")

import waloviz as wv

wv.extension()

wv.Audio(
    "https://www.mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/Samples/AFsp/M1F1-Alaw-AFsp.wav",
    minimal=True,
)
