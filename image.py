import cv2 
import matplotlib.pyplot as plt
import numpy as np


img = cv2.imread('pla_1_after.jpg')

# alpha = 1.3 # Contrast control (1.0-3.0)
# beta = 0 # Brightness control (0-100)

# img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

# img = cv2.GaussianBlur(img,(25,25),0)
img = cv2.blur(img,(25,25))

sf = 0.2
w = int(sf*img.shape[1])
h = int(sf*img.shape[0])
img = cv2.resize(img,(w,h))

imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

plt.subplot(1,4,1)
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

plt.subplot(1,4,2)
plt.imshow(cv2.cvtColor(imgGray, cv2.COLOR_BGR2RGB))

# setting threshold of gray image
# _, threshold = cv2.threshold(imgGray, 100, 255, cv2.THRESH_BINARY)

# Otsu's thresholding
#  ret2,threshold = cv2.threshold(imgGray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

threshold = cv2.adaptiveThreshold(imgGray ,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,11,2)

# threshold = cv2.adaptiveThreshold(imgGray ,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
#             cv2.THRESH_BINARY,11,2)

plt.subplot(1,4,3)
plt.imshow(cv2.cvtColor(threshold, cv2.COLOR_BGR2RGB))


# using a findContours() function
contours, _ = cv2.findContours(
    threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

i = 0
maxArea = 0 

print(len(contours))
for contour in contours:
    if (i == 0):
        i = 1
        continue
  
    area = cv2.contourArea(contour)
    if area > maxArea:
        maxArea = area
        maxi = i

     # cv2.approxPloyDP() function to approximate the shape
    approx = cv2.approxPolyDP(
        contour, 0.01 * cv2.arcLength(contour, True), True)
    i+=1
    

print(maxArea)
cv2.drawContours(img, contours, maxi, (0, 255, 0), 3)

# cv2.imshow('Image Contours', img)
# cv2.waitKey()
plt.subplot(1,4,4)
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

plt.show()