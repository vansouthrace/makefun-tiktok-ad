#!/usr/bin/env bash
# Build the make.fun bring-the-humans-03 TikTok ad.
# Scene stills come from build_stills.py (press-pack art + rendered text).
# Voiceover: audio/vo.mp3 (TTS). Music: audio/music.wav (synthesised bed).
# End card + badge come from the press pack (press/), per press/llms.txt recipe.
set -euo pipefail
cd "$(dirname "$0")"

# Scene plan: total 21.0 s; referral card overlays the last 2.5 s (T=18.5).
# s1 3.5 | s2 4.0 | s3 3.5 | s4 3.5 | s5 1.5 | s6 2.5  = 18.5 s of content
mkdir -p scenes
i=0
for spec in "s1 3.5" "s2 4.0" "s3 3.5" "s4 3.5" "s5 1.5" "s6 2.5"; do
  set -- $spec
  frames=$(python3 -c "print(int(float('$2')*30))")
  ffmpeg -y -v error -loop 1 -i "stills/$1.png" \
    -vf "zoompan=z='min(zoom+0.0004,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30" \
    -frames:v "$frames" -c:v libx264 -pix_fmt yuv420p -crf 18 "scenes/$1.mp4"
  i=$((i+1))
done

printf "file 's1.mp4'\nfile 's2.mp4'\nfile 's3.mp4'\nfile 's4.mp4'\nfile 's5.mp4'\nfile 's6.mp4'\n" > scenes/list.txt
ffmpeg -y -v error -f concat -safe 0 -i scenes/list.txt -c copy scenes/joined.mp4

# Audio: voiceover delayed 0.4 s, music bed quiet underneath, 21 s total.
ffmpeg -y -v error -i scenes/joined.mp4 -i audio/vo.mp3 -i audio/music.wav -filter_complex \
  "[1:a]adelay=400|400,aresample=48000[vo];[2:a]volume=0.30,aresample=48000[mus];[vo][mus]amix=inputs=2:duration=first:dropout_transition=0[a]" \
  -map 0:v -map '[a]' -c:v copy -c:a aac -b:a 160k -t 18.5 clip.mp4

# Press recipe: badge from frame 0 until the card, card over the last 2.5 s,
# referral code 05vf2eby typed into the field (JetBrains Mono Bold 62 px, ink).
CLIP=clip.mp4 CODE=05vf2eby FONT=fonts/JetBrainsMono-Bold.ttf
W=1080 H=1920 CARD=press/makefun-card-9x16-transparent.webm LEN=2.5 REST=1.433
CX=210 CY=1232 CW=5 CH=78 MID=1271 SIZE=62 BADGE=press/makefun-badge-9x16.png
HOLD=2.5
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$CLIP")
T=$(awk "BEGIN{print $D+$HOLD-$LEN}")
echo "clip duration $D, card starts at $T"
ffmpeg -y -v error -i "$CLIP" -c:v libvpx-vp9 -i "$CARD" -i "$BADGE" -filter_complex "
[0:v]scale=$W:$H:force_original_aspect_ratio=increase,crop=$W:$H,setsar=1,fps=60,tpad=stop_mode=clone:stop_duration=$HOLD[base];
[base][2:v]overlay=enable='lt(t,$T)',format=yuva420p,split[clip][soft];
[soft]gblur=sigma=28,eq=saturation=0.35,fade=t=in:st=$T:d=0.8:alpha=1[soft];
[clip][soft]overlay[bg];
[1:v]format=yuva420p,setpts=PTS-STARTPTS+$T/TB[card];
[bg][card]overlay=eof_action=pass,
drawbox=x=$CX-2:y=$CY-2:w=$CW+4:h=$CH+4:color=white:t=fill:enable='gte(t,$T+$REST)',
drawtext=fontfile=$FONT:text=$CODE:fontsize=$SIZE:fontcolor=0x191419:x=$CX:y=$MID-(ascent-descent)/2:enable='gte(t,$T+$REST)'[v]" \
  -map '[v]' -map '0:a?' -c:v libx264 -pix_fmt yuv420p -crf 20 -c:a aac -b:a 160k -movflags +faststart ad.mp4

# Phone-friendly copy (same pixels, smaller file) for the TikTok upload.
ffmpeg -y -v error -i ad.mp4 -c:v libx264 -pix_fmt yuv420p -crf 26 -c:a aac -b:a 128k -movflags +faststart ad-tiktok.mp4

echo "=== ad.mp4 ==="; ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,r_frame_rate -of default=nw=1 ad.mp4
echo "=== ad-tiktok.mp4 ==="; ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height -of default=nw=1 ad-tiktok.mp4
ffmpeg -v error -i ad.mp4 -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume" || true
