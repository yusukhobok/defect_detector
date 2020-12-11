import numpy
import scipy
import matplotlib
from matplotlib import image
from matplotlib import pyplot
from skimage.filters import sobel, threshold_otsu


file_name = "data\\picture.jpg"
image = image.imread(file_name)

from skimage.color import rgb2gray
grayImage = rgb2gray(image)

thresh = threshold_otsu(grayImage)
binary_mask = grayImage > thresh
binary_image = binary_mask.astype(int)

pyplot.imshow(binary_image)
pyplot.show()