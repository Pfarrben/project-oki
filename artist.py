
import math
import random

import numpy as np

from PyQt5.QtGui import QColor, QPen, QBrush
from PyQt5.QtCore import QRectF, QPointF, Qt

import painter
from utils import QColor_HSV, save, Perlin2D


def draw_rectangle(painter, x, y, width, height, angle, color):
    painter.save()
    painter.translate(x, y)
    painter.rotate(angle)
    painter.setBrush(QBrush(color))
    painter.setPen(Qt.NoPen)
    painter.drawRect(QRectF(-width / 2, -height / 2, width, height))
    painter.restore()

def draw_flow_field(width, height, seed=random.randint(0, 100000000)):
    # Set the random seed for repeatability
    np.random.seed(seed)

    # These are color hues
    colors = [1]
    for i, mod in enumerate(colors):
        print('Starting Image %s/%s' % (i + 1, len(colors)))
        picture = painter.Painter(width, height)

        # Allow smooth drawing
        picture.setRenderHint(picture.Antialiasing)

        # Draw the background color
        picture.fillRect(0, 0, width, height, QColor(0, 0, 0))

        # Set the pen color
        picture.setPen(QPen(QColor(150, 150, 225, 5), 2))

        num = 1
        for j in range(num):
            print('Creating Noise... (%s/%s)' % (j + 1, num))
            p_noise = Perlin2D(width, height, 2, 2)
            print('Noise Generated! (%s/%s)' % (j + 1, num))

            MAX_LENGTH = 2 * width
            STEP_SIZE = 0.001 * max(width, height)
            NUM = int(width * height / 1000)
            POINTS = [(random.randint(0, width - 1), random.randint(0, height - 1)) for i in range(NUM)]

            for k, (x_s, y_s) in enumerate(POINTS):
                print(f'{100 * (k + 1) / len(POINTS):.1f}'.rjust(5) + '% Complete', end='\r')

                # The current line length tracking variable
                c_len = 0

                # Actually draw the flow field
                while c_len < MAX_LENGTH:
                    # Set the pen color for this segment
                    sat = 200 * (MAX_LENGTH - c_len) / MAX_LENGTH
                    hue = (mod + 130 * (height - y_s) / height) % 360
                    picture.setPen(QPen(QColor_HSV(hue, sat, 255, 20), 2))

                    # angle between -pi and pi
                    angle = p_noise[int(x_s), int(y_s)] * math.pi

                    # Compute the new point
                    x_f = x_s + STEP_SIZE * math.cos(angle)
                    y_f = y_s + STEP_SIZE * math.sin(angle)

                    # Draw a rectangle
                    if random.random() < 0.01:  # Control the frequency of shape appearance
                        rect_width = random.uniform(5, 15)  # Random rectangle width
                        rect_height = random.uniform(5, 15)  # Random rectangle height
                        rect_angle = math.degrees(angle)  # Use the angle of the flow field
                        rect_color = QColor_HSV(hue, sat, 255, 150)  # Use the color of the flow field lines
                        draw_rectangle(picture, x_s, y_s, rect_width, rect_height, rect_angle, rect_color)

                    # Draw the line
                    picture.drawLine(QPointF(x_s, y_s), QPointF(x_f, y_f))

                    # Update the line length
                    c_len += math.sqrt((x_f - x_s) ** 2 + (y_f - y_s) ** 2)

                    # Break from the loop if the new point is outside our image bounds
                    # or if we've exceeded the line length; otherwise update the point
                    if x_f < 0 or x_f >= width or y_f < 0 or y_f >= height or c_len > MAX_LENGTH:
                        break
                    else:
                        x_s, y_s = x_f, y_f

            save(picture, fname=f'image_{mod}_{num}_{seed}', folder='.', overwrite=True)
