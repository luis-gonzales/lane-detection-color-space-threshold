import numpy as np
from collections import deque


class Lane():
  
  def __init__(self):
    
    # Boolean signifying whether a lane was detected in the previous frame
    self.prev_detect = False

    # x, y indices of detected pixels corresponding to a lane
    self.x_idxs = None
    self.y_idxs = None

    # Polynomial coefficients for the most recent fit
    self.curr_coeffs = None  
      
    # Radius of curvature in meters
    self.rad_of_curve = None 

    # Queue of most recent coefficients
    self.container = deque([], 15)

    # Number of frames for which a lane has not been detected (ideally remains 0)
    self.lost_count = 0    
      
    # Polynomial coefficients averaged over the last n iterations
    self.best_fit = None


  def set_prev_detect(self, bool_):
    self.prev_detect = bool_


  def set_pixel_idxs(self, x_idxs, y_idxs):
    self.x_idxs = x_idxs
    self.y_idxs = y_idxs


  def calc_curr_coeffs(self):
    self.curr_coeffs = np.polyfit(self.y_idxs, self.x_idxs, 2)
    self.container.appendleft(self.curr_coeffs)
    self.best_fit = np.mean(self.container, 0)


  def calc_rad_of_curve(self, x_m_per_px, y_m_per_px, y_eval):
    A = x_m_per_px * self.best_fit[0] / (y_m_per_px**2)
    B = x_m_per_px * self.best_fit[1] / y_m_per_px
    self.rad_of_curve = ((1 + (2*A*y_eval*y_m_per_px+B)**2)**1.5) / np.abs(2*A)


  def x_of_y_w_curr_coeffs(self, y):
    return self.curr_coeffs[0]*y**2 + self.curr_coeffs[1]*y + self.curr_coeffs[2]


  def x_of_y_w_avg_coeffs(self, y):
    return self.best_fit[0]*y**2 + self.best_fit[1]*y + self.best_fit[2]


  def set_curr_coeff(self, new_coeff, idx):
    self.curr_coeffs[idx] = new_coeff


# Global variables for left and right lanes
l_lane = Lane()
r_lane = Lane()
