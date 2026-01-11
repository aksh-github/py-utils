import cv2
import os

# Input and output video paths
input_video = os.path.join('.', 'src', 'video', 'in', 'RB.mp4')
output_video = os.path.join('.','src', 'video', 'out', 'RB.mp4')
# output_video = './out/RB.mp4'

# Capture the input video
cap = cv2.VideoCapture(input_video)

# Get the video properties
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * 0.5)  # Reduce width by half
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * 0.5)  # Reduce height by half

# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize the frame
    resized_frame = cv2.resize(frame, (width, height))

    # Write the resized frame to the output video
    out.write(resized_frame)

cap.release()
out.release()