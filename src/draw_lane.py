import cv2
import numpy as np
import matplotlib.pyplot as plt
from lane import l_lane, r_lane # global variables

def draw_lane(img_dst, Minv, offcenter, debug=False):
    '''
    Args:
        - img_dst: is the curvature-corrected, original image stored
          as a np.array
        - Minv: Inverse perspective transform matrix
        - offcenter: float with units in meters specifying the position
          of the vehicle with respect to center
        - debug: Save intermediate plots if True
    Output:
        - img_dst with lane highlighting, detected pixels annotated,
          and annotation text (curvature, offcenter)
    '''

    img_w, img_h = img_dst.shape[1], img_dst.shape[0]  
    img_lane = np.zeros((img_h, img_w, 3), dtype=np.uint8)


    # Define y_pts spanning entire height and corresponding
    # left/right x_pts based on polynomial fit
    y_pts = np.arange(img_h)
    l_x_pts = l_lane.x_of_y_w_avg_coeffs(y_pts)
    r_x_pts = r_lane.x_of_y_w_avg_coeffs(y_pts)
    #l_x_pts = l_lane.x_of_y_w_curr_coeffs(y_pts)
    #r_x_pts = r_lane.x_of_y_w_curr_coeffs(y_pts)
    
  
    # Recast x/y_pts into appropriate form for cv2.fillPoly() and draw on `img_lane`
    l_pts = np.array([np.transpose(np.vstack([l_x_pts, y_pts]))])
    r_pts = np.array([np.flipud(np.transpose(np.vstack([r_x_pts, y_pts])))])
    pts = np.hstack((l_pts, r_pts))
    cv2.fillPoly(img_lane, np.int_([pts]), (0,100, 0))
    if debug: plt.imsave('output/lane_detected_birds_eye.jpg', img_lane, vmin=0, vmax=255)
    

    # Warp perspective and add to original image
    img_lane_t = cv2.warpPerspective(img_lane, Minv, (img_w, img_h))
    if debug: plt.imsave('output/lane_detected_transform.jpg', img_lane_t, vmin=0, vmax=255)
    img_detected = cv2.addWeighted(img_dst, 1, img_lane_t, 1, 0)
    if debug: plt.imsave('output/lane_detected.jpg', img_detected, vmin=0, vmax=255)


    # Add curvature text
    avg_rad_of_curve = (l_lane.rad_of_curve + r_lane.rad_of_curve) / 2
    curvature_text = "Radius of curvature (km): %.2f" % (avg_rad_of_curve/1000)
    cv2.putText(img_detected, curvature_text, (10,35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))


    # Add offcenter text
    if offcenter > 0:
        offcenter_text = 'Right of center (m): %.2f' % offcenter
    else:
        offcenter_text = 'Left of center (m): %.2f' % offcenter
    cv2.putText(img_detected, offcenter_text, (10,75), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))


    # Highlight detected pixels for currently-detected lane
    img_pixels = np.zeros_like(img_dst[:,:,0])
    if l_lane.lost_count == 0:
        img_pixels[l_lane.y_idxs, l_lane.x_idxs] = 255
    if r_lane.lost_count == 0:
        img_pixels[r_lane.y_idxs, r_lane.x_idxs] = 255
    img_pixels = cv2.warpPerspective(img_pixels, Minv, (img_w, img_h))
    nonzero_y, nonzero_x = img_pixels.nonzero()
    img_detected[nonzero_y, nonzero_x, :] = [65,206,250]

    return img_detected
    