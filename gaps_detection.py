import cv2
import numpy as np
from matplotlib import pyplot
from skimage.filters import sobel, threshold_otsu
from skimage.color import rgb2gray


SKIPPED_FRAMES_COUNT = 60
LIMITS = (600, 750)
THRESH_LIMIT = 10
MAX_DEVIATION = 500
GAP_LIMIT = 400 #40


def image_processing(image):
    image = image[:, LIMITS[0]:LIMITS[1]]
    gray_image = rgb2gray(image)
    thresh = threshold_otsu(gray_image)
    binary_mask = gray_image > thresh
    binary_image = binary_mask.astype(int)
    processed_image = sobel(binary_image)
    binary_mask = processed_image == 0
    binary_image = binary_mask.astype(int)
    return gray_image, binary_image


def find_first_column(binary_image):
    start_column = binary_image.shape[1] - 1
    while binary_image[0, start_column] == 1:
        start_column -= 1
        if start_column == 0:
            return binary_image.shape[1] - 1
    return start_column


def find_next_column(binary_image, row, column, current_border):
    old_column = column

    # ищем ноль, ближайший к column, слева
    ok_left = True
    new_column_left = column
    k = 0
    while binary_image[row, new_column_left] == 1:
        k += 1
        new_column_left -= 1
        if (k > MAX_DEVIATION) or (new_column_left < 0):
            ok_left = False
            break

    # ищем ноль, ближайший к column, справа
    ok_right = True
    new_column_right = column
    k = 0
    while binary_image[row, new_column_right] == 1:
        k += 1
        new_column_right += 1
        if (k > MAX_DEVIATION) or (new_column_right >= binary_image.shape[1]):
            ok_right = False
            break

    if not ok_right and not ok_left:
        # pass
        # column = None
        return column
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

    c1 = min(old_column, column)
    c2 = max(old_column, column)
    old = binary_image[row-1, c1:c2+1]
    if np.sum(old)/len(old) > 0.5:
        if len(current_border) > 0:
            mean = np.mean(current_border)
            if abs(mean-column) > abs(mean-old_column):
                column = old_column
    return column


def generate_data(file_name):
    cap = cv2.VideoCapture(file_name)
    counter = 0
    while True:
        try:
            _, image = cap.read()
            # if counter <= SKIPPED_FRAMES_COUNT:
            #     counter += 1
            #     continue

            border = None
            for i in range(2):
                gray_image, binary_image = image_processing(image)
                if border is not None:
                    middle = int(np.mean(border))
                    shift_border = min(middle+10, binary_image.shape[1]-1)
                    binary_image[:, shift_border:] = 1
                start_column = find_first_column(binary_image)
                row = 0
                column = start_column
                border = [column, ]
                while row < binary_image.shape[0]-1:
                    row += 1
                    column = find_next_column(binary_image, row, column, border)
                    if column is not None:
                        border.append(column)
                    else:
                        border.append(border[-1])
                border = np.array(border)

            delta_border = np.diff(border)
            min_a = np.min(delta_border)
            min_index = np.argmin(delta_border)
            next_part = delta_border[min_index + 1: min(min_index + 100, len(delta_border))]
            max_a = np.max(next_part)
            max_index = np.argmax(next_part) + min_index+1
            thresh = max_a - min_a

            if (thresh > THRESH_LIMIT) and (abs(min_a) > THRESH_LIMIT/2) and (max_a > THRESH_LIMIT/2) and (max_index > min_index):
                counter = 0
                gap = max_index - min_index

                if gap < GAP_LIMIT:
                    print(f"gap: {gap}")
                    continue

                    pyplot.subplot(1,4,1)
                    pyplot.plot(delta_border, np.arange(binary_image.shape[0]-1))
                    pyplot.plot([min_a, max_a], [min_index, max_index], "ro")
                    pyplot.gca().invert_yaxis()

                    pyplot.subplot(1,4,2)
                    pyplot.imshow(binary_image)
                    pyplot.plot(border, np.arange(binary_image.shape[0]), color="red")

                    pyplot.subplot(1,4,3)
                    pyplot.imshow(gray_image)

                    pyplot.subplot(1,4,4)
                    pyplot.imshow(rgb2gray(image[-50: -20, 24: 170]))


                    figManager = pyplot.get_current_fig_manager()
                    figManager.window.showMaximized()
                    pyplot.show()
                    pyplot.close()
            else:
                counter += 1
        except ValueError:
            counter += 1
            print("ERROR")
    cap.release()


generate_data("data\\CAM0.avi")