#!/bin/bash


#videos side by side
ffmpeg -i video1.mp4 -i video2.mp4 -filter_complex hstack output.mp4

#audio from first vid
ffmpeg -i video1.mp4 -i video2.mp4 -filter_complex "[0:v][1:v]hstack[v]" -map "[v]" -map 0:a -c:a copy output.mp4

#resize videos to same height
ffmpeg -i video1.mp4 -i video2.mp4 -filter_complex "[0:v]scale=-1:720[v0];[1:v]scale=-1:720[v1];[v0][v1]hstack[v]" -map "[v]" -map 0:a -c:a copy output.mp4

#padding between vids
ffmpeg -i video1.mp4 -i video2.mp4 -filter_complex "[0:v]pad=iw+10:ih[v0];[v0][1:v]hstack[v]" -map "[v]" -map 0:a output.mp4

#shorter duration vid
ffmpeg -i video1.mp4 -i video2.mp4 -filter_complex "[0:v][1:v]hstack=shortest=1[v]" -map "[v]" -map 0:a output.mp4

#mix audio from both
ffmpeg -i video1.mp4 -i video2.mp4 -filter_complex "[0:v][1:v]hstack=shortest=1[v]" -map "[v]" -map 0:a output.mp4

#force same dimensions
ffmpeg -i video1.mp4 -i video2.mp4 -filter_complex "[0:v][1:v]hstack[v];[0:a][1:a]amix[a]" -map "[v]" -map "[a]" output.mp4

#vertical stack
ffmpeg -i video1.mp4 -i video2.mp4 -filter_complex "[0:v]scale=640:480[v0];[1:v]scale=640:480[v1];[v0][v1]hstack[v]" -map "[v]" -map 0:a output.mp4

#3 or more vids sidebyside
ffmpeg -i video1.mp4 -i video2.mp4 -filter_complex vstack output.mp4

# Three videos
ffmpeg -i video1.mp4 -i video2.mp4 -i video3.mp4 -filter_complex "[0:v][1:v][2:v]hstack=inputs=3[v]" -map "[v]" -map 0:a output.mp4

# Four videos (2x2 grid)
ffmpeg -i video1.mp4 -i video2.mp4 -i video3.mp4 -i video4.mp4 -filter_complex "[0:v][1:v]hstack[top];[2:v][3:v]hstack[bottom];[top][bottom]vstack[v]" -map "[v]" -map 0:a output.mp4

