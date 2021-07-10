## Researching how GTA does native audio.

Trying to make GTA native audio a thing... hopefully.

Any help on figuring this out is welcome!

### Working:
- example1: Single audio file under 1 mb using MultitrackSound
- example1-1: Multiple audio files under 1mb using MultitrackSound


### Not working:
- example2: Single audio file over 1mb using MultitrackSound
  * My own audio with default configuration (same as example 1 and 1-1)
  * Audio bank loads indefinitely.
- monkeys
  * An attempt at mimicing `fbi_5_monkeys.awc` implementation.
  * Result was that it did load the audio bank, but no sounds were played. 

### Still to try:
- Single audio file over 1 mb using StreamingSound
- Try wrapping in WrapperSound before exposing.

## Programs

_audiogen = Tool to generate a FiveM resource from an mp3.

_dat54tree = Generate a tree from dat54 nodes.