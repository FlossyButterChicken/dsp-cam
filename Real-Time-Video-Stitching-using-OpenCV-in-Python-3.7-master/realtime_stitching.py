# USAGE
# python realtime_stitching.py

# import the necessary packages
from pyimagesearch.basicmotiondetector import BasicMotionDetector
from pyimagesearch.panorama import Stitcher
from imutils.video import VideoStream
import numpy as np
import datetime
import imutils
import time
import cv2

import pyvirtualcam

from skimage import exposure
import matplotlib.pyplot as plt

from color_transfer import color_transfer

# initialize the video streams and allow them to warmup
#print("[INFO] starting cameras...")
# rightStream = VideoStream(src="http://localhost/moto.mp4").start()  #aaka
# leftStream = VideoStream(src="http://localhost/note.mp4").start()  #no aaka
#rightStream = VideoStream(src="https://10.18.83.177:8080/video").start()  #aaka
#leftStream = VideoStream(src="http://192.168.43.131:8080/video").start()  #no aaka
#time.sleep(2.0)

# define a video capture object
rightStream = cv2.VideoCapture(0)
leftStream = cv2.VideoCapture(1)

# initialize the image stitcher, motion detector, and total
# number of frames read
stitcher = Stitcher()
total = 0
concat = 0

with pyvirtualcam.Camera(800, 300, fps=30) as cam:
	print(f'Virtual cam started: {cam.device} ({cam.width}x{cam.height} @ {cam.fps}fps)')


	# loop over frames from the video streams
	while True:
		# grab the frames from their respective video streams
		ret, left = leftStream.read()
		ret1, right = rightStream.read()

		# resize the frames
		left = imutils.resize(left, width=400)
		right = imutils.resize(right, width=400)

		multi = True if right.shape[-1] > 1 else False
		matched_l = exposure.match_histograms(left, right, channel_axis=-1)
		matched_r = exposure.match_histograms(right, left, channel_axis=-1)
		transfer = color_transfer(right, left)

		# stitch the frames together to form the panorama
		# IMPORTANT: you might have to change this line of code
		# depending on how your cameras are oriented; frames
		# should be supplied in left-to-right order
		result = stitcher.stitch([right, left])

		#REMEMBER COMMENT OUT SINCE RESOURCES
		result_left = stitcher.stitch([right, matched_l])
		result_right = stitcher.stitch([matched_r, left])
		stitched_frame = stitcher.stitch([right, transfer])

		result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)

		# no homograpy could be computed
		if result is None:
			print("[INFO] homography could not be computed")
			concat = 1
			break

		# show the output images
		#cv2.imshow("Result", result)
		#cv2.imshow("Left Matched", result_left)
		#cv2.imshow("Right Matched", result_right)
		#cv2.imshow("Transfer Matched", stitched_frame)
		cv2.imshow("Left Frame", left)
		cv2.imshow("Right Frame", right)
		key = cv2.waitKey(1) & 0xFF

		cam.send(cv2.flip(result_rgb, 1))
		cam.sleep_until_next_frame()

		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break

	#switches to concat if homography does not work
	if(not concat): #test with if(not concat)
		cv2.destroyAllWindows()
		print("[INFO] Switching to concatenate.")
		while True:
			ret, left = leftStream.read()
			ret1, right = rightStream.read()
			left = imutils.resize(left, width=400)	
			right = imutils.resize(right, width=400)
			frame_concat = cv2.hconcat([right, left])
			frame_concat_rgb = cv2.cvtColor(frame_concat, cv2.COLOR_BGR2RGB)
			cv2.imshow('frame', frame_concat)
			key = cv2.waitKey(1) & 0xFF

			cam.send(cv2.flip(frame_concat_rgb, 1))
			cam.sleep_until_next_frame()

			if key == ord("q"):
				break

cv2.destroyAllWindows()
leftStream.release()
rightStream.release()


