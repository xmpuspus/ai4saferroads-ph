#!/usr/bin/env bash
# Encode the hero gif from a record_demo.mjs take.
#
# Usage: bash build/encode_demo.sh <take.webm> <TRIM_S> <MARK_FLIP> <MARK_END>
# The three numbers come from the recorder's stdout. The take runs ~20% slow under
# swiftshader, so timing is normalized against the designed length before encoding.
# Two palette segments split at the Safe flip: one global palette crushes the teal
# finale to grey because the satellite frames dominate it.
set -euo pipefail

WEBM=$1; TRIM_S=$2; FLIP=$3; END=$4
DESIGNED=66.55                       # sum of the recorder's subtitle beats
FACTOR=$(python3 -c "print(($END-$TRIM_S)/$DESIGNED)")
SPLIT=$(python3 -c "print(($FLIP-$TRIM_S)/$FACTOR)")
W=576; FPS=7; LOSSY=65               # 640/8fps broke the 15 MB LinkedIn cap at this length
TMP=$(mktemp -d)

ffmpeg -loglevel error -i "$WEBM" -ss "$TRIM_S" -to "$END" \
  -vf "setpts=(PTS-STARTPTS)/$FACTOR" -an -c:v libx264 -crf 20 -pix_fmt yuv420p \
  -y docs/demo.mp4

for seg in A B; do
  if [ $seg = A ]; then RANGE=(-t "$SPLIT"); else RANGE=(-ss "$SPLIT"); fi
  ffmpeg -loglevel error "${RANGE[@]}" -i docs/demo.mp4 \
    -vf "fps=$FPS,scale=$W:-2:flags=lanczos,palettegen=max_colors=160" -y "$TMP/pal$seg.png"
  ffmpeg -loglevel error "${RANGE[@]}" -i docs/demo.mp4 -i "$TMP/pal$seg.png" \
    -lavfi "fps=$FPS,scale=$W:-2:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5" \
    -y "$TMP/seg$seg.gif"
done

gifsicle "$TMP/segA.gif" "$TMP/segB.gif" -O3 --lossy=$LOSSY -o docs/demo.gif
rm -rf "$TMP"
ls -la docs/demo.gif docs/demo.mp4
echo "Frame-extract and READ the beats before committing: ffmpeg -ss <t> -i docs/demo.gif -frames:v 1 /tmp/beat.png"
