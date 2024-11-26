from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import sdxf
import os.path

class SolidArc(sdxf.PolyLine):
    def __init__(self,center,radius,thickness,startAngle=0,endAngle=90,RESOLUTION=600,**kwargs):
        points = []
        thickness=min(radius,thickness)
        self.npts = int(abs(endAngle-startAngle)*RESOLUTION/360)
        self.step = 360/RESOLUTION
        for i in range(self.npts):
            points.append([center[0]+(radius+thickness/2)*np.cos(np.radians(startAngle+i*self.step)),
                           center[1]+(radius+thickness/2)*np.sin(np.radians(startAngle+i*self.step)),0])
        points.append([center[0]+(radius+thickness/2)*np.cos(np.radians(endAngle)),
                       center[1]+(radius+thickness/2)*np.sin(np.radians(endAngle)),0])
        for i in range(self.npts):
            points.append([center[0]+(radius-thickness/2)*np.cos(np.radians(endAngle-i*self.step)),
                           center[1]+(radius-thickness/2)*np.sin(np.radians(endAngle-i*self.step)),0])
        points.append([center[0]+(radius-thickness/2)*np.cos(np.radians(startAngle)),
                       center[1]+(radius-thickness/2)*np.sin(np.radians(startAngle)),0])
        points.append([center[0]+(radius+thickness/2)*np.cos(np.radians(startAngle)),
                       center[1]+(radius+thickness/2)*np.sin(np.radians(startAngle)),0])
        
        
            
        super().__init__(points=points,flag=2,**kwargs)

class PDFPrinter:
    def __init__(self):
        plt.figure(figsize=[6, 6])
        #plt.hold(True)

    def save(self, filename):
        plt.axis('equal')
        plt.tick_params(colors='w')
        plt.savefig(os.path.abspath(filename+'.pdf'), bbox_inches = 'tight')

    def draw_arc(self, center, r, angles = [np.pi/6, 5*np.pi/6], **kwargs):
        if r > 0:
            color = 'b'
        else:
            color = 'r'
        angles = np.linspace(angles[0], angles[1])
        plt.plot(center[0] + r * np.cos(angles), center[1] + r * np.sin(angles),
                linewidth=.5,
                 color = color,
                **kwargs)
        plt.plot([center[0],
                  center[0] + r * np.cos(angles[0])],
                 [center[1],
                  center[1] + r * np.sin(angles[0])],
                 linewidth = .01,
                 color = color,
                 marker = '+',
                 markersize = 0.1,
                 **kwargs)

    def draw_line(self, center, length, angle, style='k-', **kwargs):
        plt.plot([center[0] - length/2 * np.cos(angle),
                  center[0] + length/2 * np.cos(angle)],
                 [center[1] - length/2 * np.sin(angle),
                  center[1] + length/2 * np.sin(angle)], style, **kwargs)

    def draw_circle(self, center, r):
        angles = np.linspace(0, 2*np.pi, 100)
        plt.plot(center[0] + r * np.cos(angles),
                 center[1] + r * np.sin(angles), 'k-', linewidth=.5)

    def draw_point(self, center, **kwargs):
        plt.plot(center[0], center[1], **kwargs)

class DXFPrinter:
    def __init__(self,radius=50000,edge=5000,linewidth=8):
        self.linewidth=linewidth
        self.dxf = sdxf.Drawing()
        #add a wafer outline on the frame layer (0)
        self.dxf.append(sdxf.Arc(center=(0,0),radius=radius,startAngle=-65,endAngle=245))
        self.dxf.append(sdxf.Arc(center=(0,0),radius=radius-edge,startAngle=-65,endAngle=245))

    def save(self, filename):
        self.dxf.saveas(filename+'.dxf')

    def draw_arc(self, center, r, angles = [np.pi/6, 5*np.pi/6], **kwargs):
        if r < 0:
            r = -r
            angles = np.array(angles) + np.pi
        startAngle = min(angles) * 180/np.pi
        endAngle = max(angles) * 180/np.pi
        '''
        self.dxf.append(sdxf.Arc(center = center + [0], radius = r,
                                startAngle = startAngle,
                                endAngle = endAngle))
        '''
        self.dxf.append(SolidArc(center = center + [0], radius = r,
                                thickness=self.linewidth,
                                startAngle = startAngle,
                                endAngle = endAngle,
                                layer = "drawinglayer"))

    def draw_line(self, center, length, angle, style='k-', **kwargs):
        self.dxf.append(sdxf.Line(points=
            [[center[0] - length/2 * np.cos(angle),
              center[1] - length/2 * np.sin(angle)],
             [center[0] + length/2 * np.cos(angle),
              center[1] + length/2 * np.sin(angle)]]))


