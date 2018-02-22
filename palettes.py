#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import itertools
import math
import sys
from PIL import Image

"""
Palette definitions and palette modification tools

Aleksi Sahala 2018
Image Bitcrusher / Oldskoolizer
Python 3.6.3 (32-bit)

"""

class Palettes:

    def __init__(self):
        """ New fixed palettes can be defined as below or by extracting
        them from indexed PNG images with extract_palette_from_file().
        See example palettes at http://fornaxvoid.com/colorpalettes/

        All fixed-palette modes will automatically support dithered
        quantization and diagonal rasterization. """

        """ EGA palette in the standard order from black to white. """
        self.EGA = [(0,0,0),     (0,0,170),    (0,170,0),    (0,170,170),
                    (170,0,0),   (170,0,170),  (170,85,0),   (170,170,170),
                    (85,85,85),  (85,85,255),  (85,255,85),  (85,255,255),
                    (255,85,85), (255,85,255), (255,255,85), (255,255,255)]

        """ EGA hi-res mode; a product of 6-bit RGB bands """
        base6 = [0, 85, 170, 255]
        self.EGA_hi = list(itertools.product(*[base6, base6, base6]))

        """ CGA palettes are defined as subsets of EGA.
        See https://en.wikipedia.org/wiki/Color_Graphics_Adapter
        Palette 3 is for 640x200 mode. """
        self.CGA = {0: [self.EGA[i] for i in [0, 11, 13, 15]],
                    1: [self.EGA[i] for i in [0, 10, 12, 14]],
                    2: [self.EGA[i] for i in [0, 11, 12, 15]],
                    3: [self.EGA[i] for i in [0, 15]]}

        """ Lazily defined Old CGA Composite palette in standard order.
        Calculating these is quite complicated and not necessary here,
        see 8088 MPH CGA scripts at https://github.com/reenigne/ """
        self.CGA_comps = {0: [(0,0,0),   (0,154,255),   (0,66,255),    (0,144,255),
                             (170,76,0), (132,250,210), (185,162,173), (150,240,255),
                             (205,31,0), (167,205,255), (220,117,255), (185,195,255), 
                             (255,92,0), (237,255,204), (255,178,166), (255,255,255)],
                          1: [(0,0,0),   (0,118,109),   (0,49,111),    (0,83,65),
                             (122,51,0), (57,190,66),   (130,116,72),  (83,155,14),
                             (235,51,8), (210,196,153), (248,122,155), (217,160,107),
                             (179,68,0), (139,208,74),  (190,133,80),  (152,173,20)],
                          2: [(0,0,0),   (0,154,255),   (229,75,55),   (0,144,255),
                             (170,76,0), (132,250,210), (221,223,221), (150,240,255),
                             (12,34,82), (68,65,63),    (247,108,158), (235,122,116), 
                             (255,92,0), (237,255,204), (221,232,217), (255,255,255)],
                          3: [(0,0,0),   (0,115,0),     (0,63,255),    (0,171,255),
                             (193,0,101),(155,155,155), (230,57,255),  (140,168,255),
                             (85,70,0),  (0,205,0),     (119,119,119), (0,251,124),
                             (255,57,0), (226,202,0),   (255,122,242), (254,254,254)]}

        if self.CGA_comps.keys() != self.CGA.keys():
            print('CGA composite and RGB key mismatch in palettes.py.')
            sys.exit()
        
        """ Composite maps for CGA """
        self.CGA_comp_map = {key: self.make_comp_map(self.CGA[key], key)\
                             for key in self.CGA.keys()}
            
        """ Raster lookups for composite CGA; these could be generated """
        self.CGA_comp_rasters = {key: self.blend_colors(self.CGA_comps[key])\
                                 for key in self.CGA.keys()}
        
        """ C64 in POKE order: https://www.c64-wiki.com/wiki/Color """
        self.C64 = [(0,0,0),       (255,255,255), (136,57,50),   (103,182,189),
                    (139,63,150),  (85,160,73),   (64,49,141),   (191,206,114),
                    (139,84,41),   (87,66,0),     (184,105,98),  (80,80,80),
                    (120,120,120), (148,224,137), (120,105,196), (159,159,159)]

        """ Gameboy in standard order """
        self.gameboy = [(15,56,15), (48,98,48), (139,172,15), (155,188,15)]

        #q = self.extract_palette_from_file('comp1.png')
        #print(q)

    def extract_palette_from_file(self, file_name):
        """ Extract palette from indexed PNG image """
        img = Image.open(file_name)
        if img.mode != 'P':
            raise ValueError('Image must be indexed.')
        else:
            return sorted(list(set(self.split_rgb(img.getpalette())['dec'])))

    def split_rgb(self, palette):
        """ Split PIL's palette format into dec / hex RGB tables:
        {'hex': [rrggbb, ...], 'dec': [(r,g,b), ...] ...}"""
        rgb = {'hex': [], 'dec': []}
        for i in range(0, len(palette), 3):
            hex_vals = ''.join(hex(dec)[2:].zfill(2) for dec in palette[i:i+3])
            rgb['hex'].append(hex_vals)
            rgb['dec'].append(tuple(palette[i:i+3]))
        return rgb

    def get_distance(self, color1, color2):
        """ Return Euclidean distance of two colors """
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        return math.sqrt((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2)

    def translate_palette(self, source, target):
        """ A simple conversion algorithm: cycle through palette
        and calculate penalty for each color pair according to
        their mutual RGB-distance. """
        mod_pal = []
        for rgb in self.split_rgb(source)['dec']:
            penalties = {}
            for t_rgb in target:
                index = target.index(t_rgb)
                penalty = 0
                for s, t in zip(rgb, t_rgb):
                    penalty += abs(s-t)
                penalties[penalty] = index
            color = penalties[min(penalties.keys())]
            mod_pal += target[color]
        return mod_pal

    def blend_colors(self, pal):
        """ Blend fixed palettes to create rasterized tones. ´alpha´
        may be adjusted to balance mixed colors. Palettes with very
        saturated colors (like EGA) should use higher alpha than those
        with low saturation (like C64).  Returns a look-up table
        in format {blend: (color1, color2)}. """
        mixed_palette = {}

        def make_mixture(color1, color2, alpha):
            """ Normalize alpha. """
            if alpha < 0:
                alpha = 0
            elif alpha > 1.0:
                alpha /= alpha

            """ Blend colors together and apply alpha. """
            def alpha_(c1, c2):
                return int(c1 * (1.0 - alpha) + c2 * alpha)
            r1, g1, b1 = color1
            r2, g2, b2 = color2            
            return (alpha_(r1, r2), alpha_(g1, g2), alpha_(b1, b2))

        def mix_general(max_distance):
            """ Produce all possible two-color combinations from the
            palette and map them to their components. Prevent rasters
            with too high contrast. The threshold is defined as
            ´max_distance´. """
            for color1 in pal:
                for color2 in pal:
                    r1, g1, b1 = color1
                    r2, g2, b2 = color2
                    if self.get_distance(color1, color2) < max_distance:
                        blend = make_mixture(color1, color2, 0.5)
                        if color1 != color2 != blend:
                            mixed_palette[blend] = [color1, color2]

        def mix_ega():
            """ More optimized blending for EGA. Mix grayscales
            to colors that produce useful results; produce also
            orange and brown-red. Uses higher alpha (0.7) to compensate
            the extreme saturation of the EGA palette. """
            # Indices point to EGA color values: 0 = black etc.
            ega_grays = [(i, 8) for i in range(1, 7)] +\
                        [(i, 7) for i in range(9, 15)] +\
                        [(i, 0) for i in range(1, 7)] +\
                        [(8, 0), (8, 7), (15, 7)] +\
                        [(12, 14), (4, 6)] +\
                        [(10, 15), (11, 15), (14, 15)]

            for color in ega_grays:
                color1 = pal[color[0]]
                color2 = pal[color[1]]
                blend = make_mixture(color1, color2, 0.7)
                if color1 != color2 != blend:
                    mixed_palette[blend] = [color1, color2]

        if self.EGA == pal: mix_ega() #mix_general(160)
        else: mix_general(80)
        return mixed_palette

    def make_comp_map(self, pal, p_index):
        """ Make composite maps for CGA palettes in format
        {(index1, index2): (r,g,b), ...}, where color indices correspond
        to the two colors that produce the composite tone (r,g,b).
        Palette 3 consists of 16 different patters made from black and
        white. These are defined as binary numbers from 0000 to 1111."""
        def str_to_int(t):
            return tuple([int(i) for i in t])
            
        lookup = {}
        if p_index in [0, 1, 2]:
            i = 0
            for color1 in pal:
                for color2 in pal:           
                    key = (pal.index(color1), pal.index(color2))
                    lookup[key] = self.CGA_comps[p_index][i]
                    i += 1
            return lookup
        else:
            return {str_to_int(bin(i)[2:].zfill(4)):\
                    self.CGA_comps[p_index][i] for i in range(16)}
            
