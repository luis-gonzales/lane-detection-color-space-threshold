import cv2
import sys
import pickle
import numpy as np
from glob import glob

'''
Usage: `python src/calibration.py <dir> <n_col> <n_row>`
       <dir>: directory of checkerboard images
       <n_col>: number of checkerboard intersections along column dimension
       <n_row>: number of checkerboard intersections along row dimension
'''

# Parse command-line inputs
img_path = sys.argv[1] 
n_col = int(sys.argv[2])
n_row = int(sys.argv[3])

# Setup fixed objp of [ [0,0,0], [1,0,0], ... ]
objp = np.zeros((n_col*n_row, 3), np.float32) # float needed for cv2.calibrateCamera
objp[:, 0:2] = np.mgrid[0:n_col, 0:n_row].T.reshape(-1,2)

obj_pts = []
img_pts = []

# Step through all jpgs in `img_path`
for fname in glob(img_path + '*.jpg'):

  # Read in each image and find chessboard corners
  img = cv2.imread(fname)
  img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  ret, corners = cv2.findChessboardCorners(img_gray, (n_col,n_row), None)

  # Append if checkerboard found
  if ret:
    img_pts.append(corners)
    obj_pts.append(objp)

# Compute calibration parameters
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_pts, img_pts,
                                                   img_gray.shape[::-1],
                                                   None, None)

# Save calibration parameters to pickle file
pickled_dict = {'ret': ret, 'mtx': mtx, 'dist': dist, 'rvecs': rvecs, 'tvecs': tvecs}
out_file = open('pickled_cal_params','wb')
pickle.dump(pickled_dict, out_file)
out_file.close()
