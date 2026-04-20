#!/bin/bash

INPUT="../input/input.mp4"
OUTPUT="../output/output.gif"

ffmpeg -i "$INPUT" \
-vf "fps=50,scale=800:-1:flags=lanczos" \
-loop 0 "$OUTPUT"
