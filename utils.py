import os
import math
import numpy as np
from numba import jit

from PyQt5.QtGui import QColor


def QColor_HSV(h, s, v, a=255):
    """
    Hue        : > -1 [wraps between 0-360]
    Saturation : 0-255
    Value      : 0-255
    Alpha      : 0-255
    """
    color = QColor()
    color.setHsv(*[int(e) for e in [h, s, v, a]])
    return color


def save(p, fname='image', folder='Images', extension='jpg', quality=100, overwrite=True):
    if not os.path.exists(folder):
        os.mkdir(folder)

    # The image name
    imageFile = f'{folder}/{fname}.{extension}'

    # Do not overwrite the image if it exists already
    if os.path.exists(imageFile):
        assert overwrite, 'File exists and overwrite is set to False!'

    # fileName, format, quality [0 through 100]
    p.saveImage(imageFile, imageFile[-3:], quality)


@jit(nopython=True)
def _calculate_noise(width, height, g00, g10, g01, g11, grid):
    noise = np.zeros((width, height))
    for i in range(width):
        for j in range(height):
            t = grid[i, j]
            d00 = np.dot(g00[i, j], t)
            d10 = np.dot(g10[i, j], np.array([t[0] - 1, t[1]]))
            d01 = np.dot(g01[i, j], np.array([t[0], t[1] - 1]))
            d11 = np.dot(g11[i, j], np.array([t[0] - 1, t[1] - 1]))

            fade_t = t**3 * (t * (t * 6 - 15) + 10)
            u = d00 + fade_t[0] * (d10 - d00)
            v = d01 + fade_t[0] * (d11 - d01)

            noise[i, j] = u + fade_t[1] * (v - u)
    return noise

def Perlin2D(width, height, n_x, n_y, clampHorizontal=False, clampVertical=False):

    msg = 'n_x and n_y must evenly divide into width and height, respectively'
    assert width % n_x == 0 and height % n_y == 0, msg

    angles = 2 * np.pi * np.random.rand(n_x + 1, n_y + 1)
    r = math.sqrt(2)  # The radius of the unit circle
    gradients = np.dstack((r * np.cos(angles), r * np.sin(angles)))

    if clampHorizontal:
        gradients[-1, :] = gradients[0, :]
    if clampVertical:
        gradients[:, -1] = gradients[:, 0]

    delta = (n_x / width, n_y / height)
    x_coords, y_coords = np.meshgrid(np.arange(0, n_x, delta[0]), np.arange(0, n_y, delta[1]), indexing='ij')
    grid = np.stack((x_coords % 1, y_coords % 1), axis=-1)

    px, py = int(width / n_x), int(height / n_y)
    gradients = gradients.repeat(px, 0).repeat(py, 1)
    g00 = gradients[:-px, :-py]
    g10 = gradients[px:, :-py]
    g01 = gradients[:-px, py:]
    g11 = gradients[px:, py:]

    return _calculate_noise(width, height, g00, g10, g01, g11, grid)