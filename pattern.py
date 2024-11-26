from __future__ import division
import numpy as np
from printer import PDFPrinter, DXFPrinter
import random
import sys
import os.path
import csv
import matplotlib.pyplot as plt

__author__ = "Robin Deits <robin.deits@gmail.com>"

RESOLUTION = 120

class PatternMaker:
    def __init__(self, filename, printers, 
                 image_width_in = 4, 
                 viewing_height_in = 24):
        self.setup_common(filename, printers, image_width_in, viewing_height_in)

    def setup_common(self, filename, printers, image_width_in, viewing_height_in):
        self.filename = filename
        self.reader = csv.reader(open(filename, 'r'))
        self.printers = printers
        self.data = np.array([[float(i) for i in row] for row in self.reader])
        # print self.data
        self.rescale(image_width_in)
        self.viewing_height_in = viewing_height_in

    def rescale(self, image_width_in):
        z_max = np.max(np.abs(self.data[:,2]))
        x_range = (np.max(self.data[:,0]) 
                - np.min(self.data[:,0]) 
                + 2*z_max)
        #rescale
        self.data[:,:3] *= image_width_in / x_range
        #offset
        center=[(np.max(self.data[:,q])+np.min(self.data[:,q]))/2 for q in range(3)]
        self.data[:,:3] -= center

    def print_pattern(self):
        num_points = len(self.data[:,0])
        for i in range(num_points):
            self.plot_point(self.data[i,:])
        for printer in self.printers:
            printer.save(os.path.splitext(self.filename)[0])

    def plot_point(self, point):
        x = point[0]
        y = point[1]
        z = point[2]
        angles = -np.array([point[3], point[4]]) + np.pi / 2
        for printer in self.printers:
            printer.draw_arc([x, y + z], -z,
            # printer.draw_arc([x, y], -z,
                              angles = angles)

    def draw_view(self, angle):
        view_pos = np.array([self.viewing_height_in * np.tan(angle),
                             0,
                             self.viewing_height_in])
        num_points = len(self.data[:,0])
        view_printer = PDFPrinter()
        for i in range(num_points):
            x = self.data[i,0]
            y = self.data[i,1]
            z = self.data[i,2]
            point_angle = np.arctan((view_pos[0] - x)
                                    / (view_pos[2] - z))
            if self.data[i, 3] < point_angle < self.data[i,4]:
                draw_angle = -point_angle + np.pi/2
                view_printer.draw_point([x - z * np.cos(draw_angle),
                         y + z - z * np.sin(draw_angle)], marker = '*',
                         # y - z * np.sin(draw_angle)], marker = '*', 
                                        markersize = 0.1,color = 'k')
        view_printer.save(os.path.splitext(self.filename)[0] 
                          + "_view_" + ("%+3d" %(angle * 180/np.pi)).strip())

    def draw_views(self, angle):
        for printer in self.printers:
            if isinstance(printer, DXFPrinter):
                print("DXFPrinter can't draw perspective views, aborting")
                continue
            self.draw_view(angle)
            self.draw_view(-angle)

def distance(p0, p1):
    return np.sqrt(np.sum(np.power(np.array(p1) - np.array(p0), 2)))
