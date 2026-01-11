from moviepy import VideoFileClip
import os

# Input and output video paths
input_video = os.path.join('.', 'src', 'video', 'in', 'RB.mp4')
output_video = os.path.join('.', 'src', 'video', 'out', 'RB.mp4')

# Load the video clip
clip = VideoFileClip(input_video)

# Resize the video (reduce width and height by half)
resized_clip = clip.resize(0.5)

# Write the result to a file, preserving audio
resized_clip.write_videofile(output_video, audio_codec='aac')

clip.close()
resized_clip.close()