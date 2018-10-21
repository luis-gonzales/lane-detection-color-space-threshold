import cv2
import numpy as np
import matplotlib.pyplot as plt
from lane import l_lane, r_lane # global variables


def find_from_prev(binary_transform):
  
  # Grab activated pixels
  nonzero = binary_transform.nonzero()
  nonzeroy = np.array(nonzero[0])
  nonzerox = np.array(nonzero[1])
  margin = 30
  
  l_lane_idxs = (nonzerox > l_lane.x_of_y_w_avg_coeffs(nonzeroy) - margin) & (nonzerox < l_lane.x_of_y_w_avg_coeffs(nonzeroy) + margin)
  r_lane_idxs = (nonzerox > r_lane.x_of_y_w_avg_coeffs(nonzeroy) - margin) & (nonzerox < r_lane.x_of_y_w_avg_coeffs(nonzeroy) + margin)

  # Extract left and right line pixel positions
  leftx = nonzerox[l_lane_idxs]
  lefty = nonzeroy[l_lane_idxs] 
  rightx = nonzerox[r_lane_idxs]
  righty = nonzeroy[r_lane_idxs]

  # Define minimum number of pixels to consider a find
  thresh = 1800
  
  # Set pixels for left lane lane found or increment lost_count counter
  if (leftx.shape[0] > thresh):
    l_lane.lost_count = 0
    l_lane.set_pixel_idxs(nonzerox[l_lane_idxs], nonzeroy[l_lane_idxs])
    l_lane.calc_curr_coeffs()
  else:
    if l_lane.lost_count > 10:
      l_lane.set_prev_detect(False)
    l_lane.lost_count += 1

  if (rightx.shape[0] > thresh):
    r_lane.lost_count = 0
    r_lane.set_pixel_idxs(nonzerox[r_lane_idxs], nonzeroy[r_lane_idxs])
    r_lane.calc_curr_coeffs()
  else:
    if r_lane.lost_count > 10:
      r_lane.set_prev_detect(False)
    r_lane.lost_count += 1


def find_new(binary_warped):
  
  # Perform column-wise count of the bottom half of the image
  histogram = np.sum(binary_warped[binary_warped.shape[0]//2:,:], axis=0)

  # Create an output image to draw on and visualize the result
  out_img = np.dstack((binary_warped, binary_warped, binary_warped))
  
  # Find the peak of the left and right halves of the histogram
  midpoint = np.int(histogram.shape[0]//2)
  leftx_base = np.argmax(histogram[:midpoint])
  rightx_base = np.argmax(histogram[midpoint:]) + midpoint

  # Sliding window parameters
  nwindows = 9    # number of sliding windows
  margin = 100    # width of window
  minpix = 50     # Min number of pixels found to recenter window

  # Set height of windows based on nwindows above and image shape
  window_height = np.int(binary_warped.shape[0]//nwindows)
  
  # Identify the x and y positions of all nonzero pixels in the image
  nonzero = binary_warped.nonzero()
  nonzeroy = np.array(nonzero[0])
  nonzerox = np.array(nonzero[1])

  # Current positions to be updated later for each window in nwindows
  leftx_current = leftx_base
  rightx_current = rightx_base

  # Create empty lists to receive left and right lane pixel indices
  left_lane_inds = []
  right_lane_inds = []

  # Step through the windows one by one
  for window in range(nwindows):#range(nwindows):
    
    # Identify window boundaries in x and y (and right and left)
    win_y_low = binary_warped.shape[0] - (window+1)*window_height
    win_y_high = binary_warped.shape[0] - window*window_height
    
    # Find the four below boundaries of the window
    win_xleft_low = leftx_current - margin
    win_xleft_high = leftx_current + margin
    win_xright_low = rightx_current - margin
    win_xright_high = rightx_current + margin 
        
    # Draw the windows on the visualization image
    cv2.rectangle(out_img,(win_xleft_low,win_y_low),
                  (win_xleft_high,win_y_high),(0,255,0), 2) 
    cv2.rectangle(out_img,(win_xright_low,win_y_low),
                  (win_xright_high,win_y_high),(0,255,0), 2) 
        
    ### Identify the nonzero pixels in x and y within the window
    good_y = np.logical_and( (nonzeroy < win_y_high), (nonzeroy >= win_y_low) )
    good_left_x = np.logical_and( (nonzerox < win_xleft_high), (nonzerox >= win_xleft_low) )
    good_left =  np.logical_and( good_left_x, good_y )
    good_left_inds = np.where(good_left)[0]
    good_right_x = np.logical_and( (nonzerox < win_xright_high), (nonzerox >= win_xright_low) )
    good_right = np.logical_and( good_right_x, good_y )
    good_right_inds = np.where(good_right)[0]
        
    # Append these indices to the lists
    left_lane_inds.append(good_left_inds)
    right_lane_inds.append(good_right_inds)
        
    # If greater than minpix pixels, recenter next window
    if good_right_inds.shape[0] > minpix:
      rightx_current = np.uint32(np.mean( nonzerox[good_right_inds] ))
    if good_left_inds.shape[0] > minpix:
      leftx_current = np.uint32(np.mean( nonzerox[good_left_inds] ))
  
  # Concatenate the arrays of indices (previously was a list of lists of pixels)
  left_lane_inds = np.concatenate(left_lane_inds)
  right_lane_inds = np.concatenate(right_lane_inds)

  # Extract left and right line pixel positions
  leftx = nonzerox[left_lane_inds]
  lefty = nonzeroy[left_lane_inds] 
  rightx = nonzerox[right_lane_inds]
  righty = nonzeroy[right_lane_inds]

  # Modify l_lane attributes if any left pixels found
  if leftx.shape[0] > 0:      # number of x and y pts expected to be equal
    l_lane.set_prev_detect(True)
    l_lane.set_pixel_idxs(leftx, lefty)
    l_lane.calc_curr_coeffs()

  if rightx.shape[0] > 0:
    r_lane.set_prev_detect(True)
    r_lane.set_pixel_idxs(rightx, righty)
    r_lane.calc_curr_coeffs()

  return out_img


def find_lane_pixels(binary_transform, debug=False):

    # Send to proper function based on whether previous frame had a lane
    if l_lane.prev_detect & r_lane.prev_detect:
        find_from_prev(binary_transform)
    
    else:
        out_img = find_new(binary_transform)
        if debug: plt.imsave('output/sliding_windows_search.jpg', out_img, vmin=0, vmax=255)
