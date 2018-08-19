#!/usr/bin/env python
"""view.py: Creates and manages viewing parameters and transformation matrix. Python 2.7."""

import numpy as np
import copy
import math

__author__ = "Raj Kane"
__version__ = "Spring 2018"

class View:
    def __init__(self):
        self.vrp = None
        self.vpn = None
        self.vup = None
        self.u = None
        self.extent = []
        self.screen = []
        self.offset = []

        self.reset()

    def reset(self):
        #default values
        self.vrp = np.matrix([0.5, 0.5, 1])
        self.vpn = np.matrix([0, 0, -1])
        self.vup = np.matrix([0, 1, 0])
        self.u = np.matrix([-1, 0, 0])
        self.extent = [1., 1., 1.]
        self.screen = [400., 400.]
        self.offset = [20., 20.]

    def build(self):
        vtm = np.identity(4, float)
        #translate vrp to origin
        t1 = np.matrix([[1,0,0,-self.vrp[0, 0]],
                        [0, 1, 0, -self.vrp[0, 1]],
                        [0, 0, 1, -self.vrp[0, 2]],
                        [0, 0, 0, 1]])
        vtm = t1 * vtm

        #calculate the view reference axes
        tu = np.cross(self.vup, self.vpn)
        tu = self.normalize(tu)
        tvup = np.cross(self.vpn, tu)
        tvup = self.normalize(tvup)
        tvpn = self.vpn
        tvpn = self.normalize(tvpn)

        self.u = np.copy(tu)
        self.vup = np.copy(tvup)
        self.vpn = np.copy(tvpn)

        #align the axes
        r1 = np.matrix([[tu[0, 0], tu[0, 1], tu[0, 2], 0.0],
                        [tvup[0, 0], tvup[0, 1], tvup[0, 2], 0.0],
                        [tvpn[0, 0], tvpn[0, 1], tvpn[0, 2], 0.0],
                        [0.0, 0.0, 0.0, 1.0]])
        vtm = r1 * vtm
        t2 = np.matrix([[1.0, 0.0, 0.0, 0.5 * self.extent[0]],
                        [0.0, 1.0, 0.0, 0.5 * self.extent[1]],
                        [0.0, 0.0, 1.0, 0.0],
                        [0.0, 0.0, 0.0, 1.0]])
        vtm = t2 * vtm

        s1 = np.matrix([[-self.screen[0] / self.extent[0], 0.0, 0.0, 0.0],
                        [0.0, -self.screen[1] / self.extent[1], 0.0, 0.0],
                        [0.0, 0.0, 1.0 / self.extent[2], 0.0],
                        [0.0, 0.0, 0.0, 1.0]])
        vtm = s1 * vtm

        t3 = np.matrix([[1.0, 0.0, 0.0, self.screen[0] + self.offset[0]],
                        [0.0, 1.0, 0.0, self.screen[1] + self.offset[1]],
                        [0.0, 0.0, 1.0, 0.0],
                        [0.0, 0.0, 0.0, 1.0]])
        vtm = t3 * vtm
        return vtm

    def rotateVRC(self, thetaVUP, thetaU):
        #translate the center of rotation (middle of extent volume)
        v = self.vrp + self.vpn * self.extent[2] * 0.5
        t1 = np.matrix([[1.0, 0.0, 0.0, -v[0, 0]],
                        [0.0, 1.0, 0.0, -v[0, 1]],
                        [0.0, 0.0, 1.0, -v[0, 2]],
                        [0.0, 0.0, 0.0, 1.0]])
        #axis alignment matrix
        Rxyz = np.matrix([[self.u[0, 0], self.u[0, 1], self.u[0, 2], 0.0],
                        [self.vup[0, 0], self.vup[0, 1], self.vup[0, 2], 0.0],
                        [self.vpn[0, 0], self.vpn[0, 1], self.vpn[0, 2], 0.0],
                        [0.0, 0.0, 0.0, 1.0]])
        #rotation matrix about y axis by vup angle
        r1 = np.matrix([[math.cos(thetaVUP), 0.0, math.sin(thetaVUP), 0.0],
                        [0.0, 1.0, 0.0, 0.0],
                        [-math.sin(thetaVUP), 0.0, math.cos(thetaVUP), 0.0],
                        [0.0, 0.0, 1.0, 0.0]])
        #rotation matrix about x axis by u angle
        r2 = np.matrix([[1.0, 0.0, 0.0, 0.0],
                        [0.0, math.cos(thetaU), -math.sin(thetaU), 0.0],
                        [0.0, math.sin(thetaU), math.cos(thetaU), 0.0],
                        [0.0, 0.0, 0.0, 1.0]])
        #translation opposite to t1
        t2 = np.matrix([[1.0, 0.0, 0.0, v[0, 0]],
                        [0.0, 1.0, 0.0, v[0, 1]],
                        [0.0, 0.0, 1.0, v[0, 2]],
                        [0.0, 0.0, 0.0, 1.0]])

        tvrc = np.matrix([[self.vrp[0, 0], self.vrp[0, 1], self.vrp[0, 2], 1.0],
                        [self.u[0, 0], self.u[0, 1], self.u[0, 2], 0.0],
                        [self.vup[0, 0], self.vup[0, 1], self.vup[0, 2], 0.0],
                        [self.vpn[0, 0], self.vpn[0, 1], self.vpn[0, 2], 0.0]])
        tvrc = (t2 * Rxyz.T * r2 * r1 * Rxyz * t1 * tvrc.T).T

        self.vrp = np.copy(tvrc[0, :3])
        self.u = np.copy(tvrc[1, :3])
        self.vup = np.copy(tvrc[2, :3])
        self.vpn = np.copy(tvrc[3, :3])

        #normalize
        self.vrp = self.normalize(self.vrp)
        self.u = self.normalize(self.u)
        self.vup = self.normalize(self.vup)
        self.vpn = self.normalize(self.vpn)


    def normalize(self, vector):
        #normalize view axes tu, tvup, tvpn
        length = np.linalg.norm(vector)
        if length == 0:
            return vector
        else:
            unit_vector = vector / length
            return unit_vector

    def clone(self):
        View_clone = View()
        View_clone.vrp = np.copy(self.vrp)
        View_clone.vpn = np.copy(self.vpn)
        View_clone.vup = np.copy(self.vup)
        View_clone.u = np.copy(self.u)
        View_clone.extent = copy.copy(self.extent)
        View_clone.screen = copy.copy(self.screen)
        View_clone.offset = copy.copy(self.offset)
        return View_clone

def main():
    v = View()
    v.build()

if __name__=="__main__":
    main()
