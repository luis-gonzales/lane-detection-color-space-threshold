import cv2
import sys
import pickle
import numpy as np
import matplotlib.pyplot as plt
from lane import l_lane, r_lane         # global variables
from draw_lane import draw_lane
from moviepy.editor import VideoFileClip
from find_lane_pixels import find_lane_pixels
from lane_thresholding import lane_thresholding

# Unpickle calibration parameters
in_file = open('pickled_cal_params', 'rb')
dict_load = pickle.load(in_file)
in_file.close()
mtx = dict_load['mtx']
dist = dict_load['dist']

# Predefine perspective transform parameters
img_w, img_h = 1280, 720
x_offset = img_w * 0.25                    #      movie 1      movie 2
src = np.float32([ [552,480],              # TL   581,460      552,480   in [x,y]
                   [737,480],              # TR   703,460      737,480
                   [1085,700],             # BR  709
                   [230,700] ])            # BL  709

dst = np.float32([ [x_offset,0],           # TL
                   [img_w-x_offset,0],     # TR
                   [img_w-x_offset,img_h], # BR
                   [x_offset,img_h] ])     # BL in [x,y]

# Compute perspective-transform matrices
M = cv2.getPerspectiveTransform(src, dst)
Minv = cv2.getPerspectiveTransform(dst, src)

debug = True

def lane_detect(img):
    
    img_h, img_w = img.shape[0], img.shape[1]

    # Undistort input image and add minor blurring to de-noise
    img_dst = cv2.undistort(img, mtx, dist, None, mtx)
    if debug: plt.imsave('output/undistorted.jpg', img_dst, vmin=0, vmax=255)
    img_blur = cv2.GaussianBlur(img_dst, (7,7), 0)


    # Apply perspective transform to get bird's-eye view and visualize
    birds_eye = cv2.warpPerspective(img_blur, M, (img_w, img_h), flags=cv2.INTER_LINEAR)

    if debug:
        img_copy = img.copy()
        cv2.line(img_copy, tuple(src[0]), tuple(src[1]), (65,206,250), thickness=5)
        cv2.line(img_copy, tuple(src[1]), tuple(src[2]), (65,206,250), thickness=5)
        cv2.line(img_copy, tuple(src[2]), tuple(src[3]), (65,206,250), thickness=5)
        cv2.line(img_copy, tuple(src[3]), tuple(src[0]), (65,206,250), thickness=5)
        plt.imsave('output/perspective_transform_bounds.jpg', img_copy, vmin=0, vmax=255)
        plt.imsave('output/birds_eye.jpg', birds_eye, vmin=0, vmax=255)


    # Apply thresholding to isolate lane lines
    img_binary = lane_thresholding(birds_eye, debug=debug)


    # Identify individual pixels corresponding to lane lines
    # Global l_lane and r_lane are modified, calcs coeffs if pixels detected
    find_lane_pixels(img_binary, debug=debug)
    if debug:
        birds_eye_color = birds_eye
        birds_eye_color[l_lane.y_idxs,l_lane.x_idxs] = [255,0,0]
        birds_eye_color[r_lane.y_idxs,r_lane.x_idxs] = [0,0,255]
        plt.imsave('output/birds_eye_pixel_annotation.jpg', birds_eye_color, vmin=0, vmax=255)


    # Calculate radius of curvature (l/r_lane attribute set within)
    x_m_per_px = 3.7/620
    y_m_per_px = 30/720
    l_lane.calc_rad_of_curve(x_m_per_px, y_m_per_px, img_h-1)
    r_lane.calc_rad_of_curve(x_m_per_px, y_m_per_px, img_h-1)


    # Calculate distance (in pixel-space and real-world) from center
    l_x = l_lane.x_of_y_w_avg_coeffs(img_h-1)
    r_x = r_lane.x_of_y_w_avg_coeffs(img_h-1)
    offcenter_px = (l_x + r_x)/2 - (img_w-1)/2
    offcenter = offcenter_px * x_m_per_px


    # Draw detected lane atop original image
    return draw_lane(img_dst, Minv, offcenter, debug=debug)


if __name__ == "__main__":
    
    # Parse command line input
    img_path = sys.argv[1]                      # e.g., input/image.jpg
    f_name = img_path.split('/')[1]             # e.g., image.jpg
    ext = img_path.split('.')[1]                # e.g., jpg

    # Process according to `jpg` or `mp4`
    if ext == 'jpg':
        img = cv2.imread(img_path)[:,:,::-1]    # RGB
        lane_detect = lane_detect(img)    
        plt.imsave('output/' + f_name, lane_detect, vmin=0, vmax=255)

    elif ext == 'mp4':
        print('received mp4')
        vid_clip = VideoFileClip(img_path)
        vid_result = vid_clip.fl_image(lane_detect)
        vid_result.write_videofile('output/' + f_name, audio=False, progress_bar=False)

    else:
        print('Unsupported input type received!')
