#!/bin/bash
# Builds the Instagram Reels version of one episode: audio → video → IG export + cover.
set -e
n=$1
cd "$(dirname "$0")"
case " 2 3 10 11 15 18 19 20 21 22 23 26 27 " in *" $n "*) python3 bot_audio.py $n >/dev/null ;; *) python3 ig_audio.py $n >/dev/null ;; esac
node render.mjs episode${n}_ig.html >/dev/null
ffmpeg -nostdin -loglevel error -y -i build/episode${n}_ig_silent.mp4 -i build/episode${n}_ig.wav \
  -c:v libx264 -profile:v high -level 4.1 -pix_fmt yuv420p -preset slow -crf 18 -maxrate 10M -bufsize 20M -r 30 -g 30 -keyint_min 30 -sc_threshold 0 \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.8:level=false" -ar 48000 -ac 2 -c:a aac -b:a 256k -shortest -movflags +faststart \
  instagram/ADUZ_${n}-qism_reels.mp4
node render.mjs episode${n}_ig.html --stills=0.14 >/dev/null
cp build/episode${n}_ig/still_0.14.jpg instagram/ADUZ_${n}-qism_cover.jpg
echo "done $n"
