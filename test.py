import cv2
import numpy as np
from matplotlib import pyplot
from skimage.filters import sobel, threshold_otsu
from skimage.color import rgb2gray


SKIPPED_FRAMES_COUNT = 60
LIMITS = (600, 720)
THRESH_LIMIT = 10
MAX_DEVIATION = 500
GAP_LIMIT = 40


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
    return start_column


def find_next_column(binary_image, row, column):
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
        pass
        # column = None
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

            gray_image, binary_image = image_processing(image)
            start_column = find_first_column(binary_image)

            for i in range(2):
                row = 0
                if i == 0:
                    column = start_column
                else:
                    column = min(start_column, int(np.mean(border)+5))
                border = [column, ]
                while row < binary_image.shape[0]-1:
                    row += 1
                    column = find_next_column(binary_image, row, column)
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
            if (thresh > THRESH_LIMIT) and (max_index > min_index):
                counter = 0
                gap = max_index - min_index

                if gap < GAP_LIMIT:
                    print(f"gap: {gap}")
                    continue

                    pyplot.subplot(1,3,1)
                    pyplot.plot(delta_border, np.arange(binary_image.shape[0]-1))
                    pyplot.plot([min_a, max_a], [min_index, max_index], "ro")
                    pyplot.gca().invert_yaxis()

                    pyplot.subplot(1,3,2)
                    pyplot.imshow(binary_image)
                    pyplot.plot(border, np.arange(binary_image.shape[0]), color="red")

                    pyplot.subplot(1,3,3)
                    pyplot.imshow(gray_image)

                    figManager = pyplot.get_current_fig_manager()
                    figManager.window.showMaximized()
                    pyplot.show()
                    pyplot.close()
            else:
                counter += 1
        except:
            counter += 1
            print("ERROR")

    cap.release()

generate_data("data\\CAM0.avi")