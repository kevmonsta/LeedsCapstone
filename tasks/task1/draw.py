#!/usr/bin/env python3
"""
This script reads in the given file, and generates a graph of the words in it
Also contains class Plot, usefull for plotting rectangles
usage: ./draw.py ocroutput.day [pagescan.tif]
"""

import csv
import logging
import sys

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


class Plot:
    """
    Class to manage plotting rectangles
    optionally plots of an image(if provided)
    """

    def __init__(self):
        # make graph
        _, self._ax = plt.subplots(1)

        self._image = None

        # set defaults for plot axis
        # will get overwritten when first thing is added to plot
        self._minx = sys.maxsize
        self._maxx = 0
        self._miny = sys.maxsize
        self._maxy = 0

    def setImage(self, image):
        """
        Sets the image for plot to be overlayed over
        input: str, filepath to image file
        output: none
        """
        logging.info("Adding Image %s to plot", image)
        # FIXME handle case where image exists, but is not a valid image file
        self._image = np.array(Image.open(image), dtype=np.uint8)

    def addRectangle(self, p1, p2, color='r'):
        """
        adds a rectangle to the plot
        input:
            (float, float) [x1, y1]
            (float, float) [x2, y2]
                two opposing corners of the rectangle to plot
            str optional, matplotlib color code to plot draw the rectangle with
                defaults to red
        output: none
        """

        # make sure x1, y1 is the min corner
        x1 = p1[0]
        x2 = p2[0]
        if x1 > x2:
            x1, x2 = x2, x1

        y1 = p1[1]
        y2 = p2[1]
        if y1 > y2:
            y1, y2 = y2, y1

        logging.debug("Adding Rectangle (%d, %d) (%d, %d) to plot", x1, y1, x2,
                      y2)

        # adjust plot axis
        self._minx = min(self._minx, x1)
        self._maxx = max(self._maxx, x2)
        self._miny = min(self._miny, y1)
        self._maxy = max(self._maxy, y2)

        w = x2 - x1
        h = y2 - y1

        r = patches.Rectangle((x1, y1),
                              w,
                              h,
                              linewidth=1,
                              edgecolor=color,
                              facecolor='none')

        self._ax.add_patch(r)

    def show(self):
        """"Shows the plot, blocking"""
        # give ymax first to invert y axis
        plt.axis([
            self._minx - 100, self._maxx + 100, self._maxy + 100,
            self._miny - 100
        ])

        if self._image is not None:
            self._ax.imshow(self._image)

        plt.show()

    def save(self, filepath):
        """
        Save the plot to filepath
        input: str filepath to save the file at
        """
        raise NotImplementedError


def main():
    """
    Graphs the inputed OCR file words
    over an image of the page (if supplied)
    """
    # create graph
    plot = Plot()

    if len(sys.argv) >= 3:
        try:
            plot.setImage(sys.argv[2])
        except FileNotFoundError:
            logging.warning("File %s not found", sys.argv[2])

    # open input file
    if len(sys.argv) < 2:
        logging.error("No OCR data file given")
        print("Usage: {} <OCR .day filepath> [<filepath to page scan>]".format(
            __file__))
        return 1
    try:
        with open(sys.argv[1], newline='') as fh:
            reader = csv.reader(fh, delimiter=',')
            for line in reader:
                text = line[15]

                # ignore empty words
                if text == '':
                    continue

                # get word bounding box in pixels
                x1, x2, y1, y2 = [((int(i) * 400) / 1440) for i in line[1:5]]

                # get color
                # set default to red (shouldn't occur)
                color = "r"
                # check if all caps
                if text.isupper():
                    color = "g"
                # check if all lowercase
                elif text.islower():
                    color = "b"
                # check if only first letter is capatilized
                elif text.istitle():
                    color = "m"
                # check if is a number
                elif text.replace('.', '', 1).isdigit():
                    color = "c"
                else:
                    logging.debug("Not sure what color to draw word '%s'",
                                  text)

                plot.addRectangle([x1, y1], [x2, y2], color)

        plot.show()
    except FileNotFoundError:
        logging.error("OCR data file %s not found", sys.argv[1])
        return 1
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sys.exit(main())
