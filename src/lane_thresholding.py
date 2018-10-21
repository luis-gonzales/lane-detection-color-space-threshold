import cv2
import numpy as np
import matplotlib.pyplot as plt


def adjust_gamma(image, gamma=1.0):
  # build a lookup table mapping the pixel values [0, 255] to
  # their adjusted gamma values
  invGamma = 1.0 / gamma
  table = np.array([((i / 255.0) ** invGamma) * 255
    for i in np.arange(0, 256)]).astype("uint8")
 
  # apply gamma correction using the lookup table
  return cv2.LUT(image, table)


def rescale(channel):
  return np.uint8( (np.float32(channel) - np.min(channel)) * 255 / (np.max(channel) - np.min(channel)) )


def lane_thresholding(img_dst, debug=False):

  # Calculate mean brightness and create gamma-corrected image
  img_yuv = cv2.cvtColor(img_dst, cv2.COLOR_RGB2YUV)
  y_mean = np.mean(img_yuv[:,:,0])
  img_gamma = adjust_gamma(img_dst, gamma=(-0.0079)*y_mean + 1.8605)
  if debug: plt.imsave('output/gamma_correction.jpg', img_gamma, vmin=0, vmax=255)


  # Transform into HSV, YUV, and Lab color spaces for thresholding and force to [0,255]
  r = rescale(img_gamma[:,:,0])
  
  img_hsv = cv2.cvtColor(img_gamma, cv2.COLOR_RGB2HSV)
  v_hsv = rescale(img_hsv[:,:,2])

  img_yuv = cv2.cvtColor(img_gamma, cv2.COLOR_RGB2YUV)
  y_yuv = rescale(img_yuv[:,:,0])
  u_yuv = rescale(img_yuv[:,:,1])
  v_yuv = rescale(img_yuv[:,:,2])

  img_lab = cv2.cvtColor(img_gamma, cv2.COLOR_RGB2Lab)
  b_lab = rescale(img_lab[:,:,2])


  # Output grayscale representations for each channel
  if debug:
    plt.imsave('output/channel_R_RGB.jpg', r, cmap='gray', vmin=0, vmax=255)
    plt.imsave('output/channel_Y_YUV.jpg', y_yuv, cmap='gray', vmin=0, vmax=255)
    plt.imsave('output/channel_U_YUV.jpg', u_yuv, cmap='gray', vmin=0, vmax=255)
    plt.imsave('output/channel_V_YUV.jpg', v_yuv, cmap='gray', vmin=0, vmax=255)
    plt.imsave('output/channel_V_HSV.jpg', v_hsv, cmap='gray', vmin=0, vmax=255)
    plt.imsave('output/channel_B_LAB.jpg', b_lab, cmap='gray', vmin=0, vmax=255)


  # Apply thresholding
  r_min, r_max = 215, 255
  r_mask = (r >= r_min) & (r <= r_max)
  
  y_yuv_min, y_yuv_max = 200, 255
  y_yuv_mask = (y_yuv >= y_yuv_min) & (y_yuv <= y_yuv_max)
  
  u_yuv_min, u_yuv_max = 0, 110
  u_yuv_mask = (u_yuv >= u_yuv_min) & (u_yuv <= u_yuv_max)

  v_yuv_min, v_yuv_max = 135, 255
  v_yuv_mask = (v_yuv >= v_yuv_min) & (v_yuv <= v_yuv_max)

  v_hsv_min, v_hsv_max = 210, 255
  v_hsv_mask = (v_hsv >= v_hsv_min) & (v_hsv <= v_hsv_max)

  b_lab_min, b_lab_max = 105, 255
  b_lab_mask = (b_lab >= b_lab_min) & (b_lab <= b_lab_max)


  # Visualize individual masks
  if debug:
    r_viz = np.zeros_like(img_dst[:,:,0])
    r_viz[r_mask] = 255
    plt.imsave('output/mask_r.jpg', r_viz, cmap='gray', vmin=0, vmax=255)

    y_yuv_viz = np.zeros_like(img_dst[:,:,0])
    y_yuv_viz[y_yuv_mask] = 255
    plt.imsave('output/mask_y_yuv.jpg', y_yuv_viz, cmap='gray', vmin=0, vmax=255)

    u_yuv_viz = np.zeros_like(img_dst[:,:,0])
    u_yuv_viz[u_yuv_mask] = 255
    plt.imsave('output/mask_u_yuv.jpg', u_yuv_viz, cmap='gray', vmin=0, vmax=255)

    v_yuv_viz = np.zeros_like(img_dst[:,:,0])
    v_yuv_viz[v_yuv_mask] = 255
    plt.imsave('output/mask_v_yuv.jpg', v_yuv_viz, cmap='gray', vmin=0, vmax=255)

    v_hsv_viz = np.zeros_like(img_dst[:,:,0])
    v_hsv_viz[v_hsv_mask] = 255
    plt.imsave('output/mask_v_hsv.jpg', v_hsv_viz, cmap='gray', vmin=0, vmax=255)

    b_lab_viz = np.zeros_like(img_dst[:,:,0])
    b_lab_viz[b_lab_mask] = 255
    plt.imsave('output/mask_b_lab.jpg', b_lab_viz, cmap='gray', vmin=0, vmax=255) 
  

  # Combine masks and use to create output image
  final_mask = r_mask | y_yuv_mask | u_yuv_mask | v_yuv_mask | b_lab_mask | v_hsv_mask
  img_binary = np.zeros_like(img_dst[:,:,0])
  img_binary[final_mask] = 255
  if debug: plt.imsave('output/binary_image.jpg', img_binary, cmap='gray', vmin=0, vmax=255)
  
  return img_binary
