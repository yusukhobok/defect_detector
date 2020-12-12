import sys
import cv2



import numpy as np
import scipy
import matplotlib
from matplotlib import image
from matplotlib import pyplot
from skimage.filters import sobel, threshold_otsu

from time import time



cap = cv2.VideoCapture("data\\CAM0.avi")

k = 0
while True:
    try:
        t1 = time()
        ret, image = cap.read()

        if k <= 60:
            k += 1
            continue

        from skimage.color import rgb2gray
        grayImage = rgb2gray(image)

        thresh = threshold_otsu(grayImage)
        binary_mask = grayImage > thresh
        binary_image = binary_mask.astype(int)

        processed_image = sobel(binary_image)
        processed_image = processed_image[:, 600:720]
        binary_mask = processed_image == 0
        binary_image = binary_mask.astype(int)



        np.set_printoptions(threshold=sys.maxsize)
        start_column = binary_image.shape[1]-1
        while binary_image[0, start_column] == 1:
            start_column -= 1

        row = 0
        column = start_column
        border = [column, ]
        while row < binary_image.shape[0]-1:
            row += 1

            #ищем ноль, ближайший к column слева
            ok_left = True
            new_column_left = column
            while binary_image[row, new_column_left] == 1:
                new_column_left -= 1
                if new_column_left < 0:
                    ok_left = False
                    break

            #ищем ноль, ближайший к column справа
            ok_right = True
            new_column_right = column
            while binary_image[row, new_column_right] == 1:
                new_column_right += 1
                if new_column_right >= binary_image.shape[1]:
                    ok_right = False
                    break

            if not ok_right and not ok_left:
                break
            elif ok_left and not ok_right:
                column = new_column_left
            elif ok_right and not ok_left:
                column = new_column_right
            else:
                delta_left = column - new_column_left
                delta_right = new_column_right - column
                if delta_left < delta_right:
                    column = new_column_left
                else:
                    column = new_column_right

            border.append(column)
        border = np.array(border)


        t2 = time()
        # print(t2-t1)


        delta_border = np.diff(border)
        min_a = np.min(delta_border)
        max_a = np.max(delta_border)
        thresh = max_a - min_a

        min_index = np.argmin(delta_border)
        max_index = np.argmax(delta_border)

        if (thresh > 10) and (max_index > min_index):
            print(k)
            k = 0
            gap = max_index - min_index
            print(f"gap {gap}")

            if gap > 40:
                pyplot.subplot(1,3,1)
                pyplot.plot(delta_border, np.arange(binary_image.shape[0]-1))
                pyplot.gca().invert_yaxis()

                pyplot.subplot(1,3,2)
                pyplot.imshow(binary_image)
                pyplot.plot(border, np.arange(binary_image.shape[0]), color="k")

                pyplot.subplot(1,3,3)
                pyplot.imshow(grayImage)
                pyplot.show()
                pyplot.close()
        else:
            k += 1
    except:
        k += 1
        print("ERROR")

# 60


# [-50:-20, 24:170]
cap.release()