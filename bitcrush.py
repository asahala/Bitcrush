#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import math
import os
from optparse import OptionParser
from PIL import Image, ImageEnhance
from palettes import Palettes
Pals = Palettes()

VERSION = "2018-02-07"

"""
Aleksi Sahala 2018 -- Image bitcrusher
Python 3.6.3 (32-bit)

See readme.txt and default() in main.py for documentation

"""

#todo
# - fix resolution issues and define res in true format

""" I/O and general, non screenmode specific global variables """
MULTIPLIER = 2               # image size multiplier
SAVE_TRUE_RESOLUTION = 0     # do not lace/double scanlines when saving
VERBOSE = 1                  # print processing stuff, never use in IDLE
PRESERVE_ASPECT_RATIO = 1
RASTER_SCANLINES = 0         # Use scanline rastering

class Converter(object):

    """ Converter class contains all the tools that are commonly used
    for all screenmodes. Screenmode specific tools are included in
    their corresponding sub-classes """
        
    def __repr__(self):
        """ Print out instance vars as a formatted list. Give
        non screenmode specific vars in parentheses. """
        debug = []
        tab = max([len(k)+2 for k in self.__dict__.keys()])
        debug.append('\n' + self.__class__.__name__ + '()')
        for k, v in self.__dict__.items():
            if isinstance(v, list):
                v = '[list of %s items]' % str(len(v))
            elif isinstance(v, dict):
                v = '[dict of %s keys]' % str(len(v))

            if k not in vars(self.__class__()).keys():
                k = '(%s)' %k
            debug.append('%s%s%s' % (k, ' '*(tab-len(k)+1), str(v)))    
        return '\n'.join(debug) + '\n'

    @staticmethod
    def get_subclasses():
        """ Return a list of available screenmodes. """
        return [x().__class__.__name__ for x in Converter.__subclasses__()]
    
    @property
    def resolution(self):
        return (int(self.image.width),
                int(self.image.height))
    
    @property
    def true_resolution(self):
        """ Resolution with forced aspect ratio """
        return (int(self.width/self.hl),
                int(self.height/self.vl))

    def get_image_object(self):
        return self.image

    def get_image_rawdata(self):
        return self.image.convert('RGB').getdata()

    def print_image_info(self):
        """ Print mode, resolution and color information """
        colors = len(set(self.get_image_rawdata()))
        res = 'x'.join([str(x) for x in list(self.resolution)])
        print('%s - %s - %i colors' % (self.name, res, colors))
    
    def load_image(self, file_name):
        self.image = Image.open(file_name)
        self.original = self.image.copy()

    def save_image(self, file_name):
        if SAVE_TRUE_RESOLUTION:
            img = self.image
        else:
            img = self._resize()
        
        fn = ('_' + file_name)
        path = os.path.join('output', fn)
        img.save(path, 'png')
        print('Image saved as %s' % fn)

    def show_image(self):
        """ Show preview of the image. """
        self._resize().show()

    def adjust(self, b_factor, c_factor):
        """ Adjust brightness/contrast. """
        img = self.image
        i = ImageEnhance.Brightness(img).enhance(b_factor)
        i = ImageEnhance.Contrast(i).enhance(c_factor)
        self.image = i

    def _resize(self):
        """ Resize image for previewing and saving """
        if SAVE_TRUE_RESOLUTION:
            return self.image
        else:
            return self.image.resize((self.image.width * self.hl * MULTIPLIER,
                                      self.image.height * self.vl * MULTIPLIER))
    
    def _show_progress(self, pos, final):
        """ Print progress information for computationally more
        demanding screenmodes """
        print('%i / %i' % (pos, final), end='\r')

    def set_properties(self, **kwargs):            
        """ Set image conversion parameters and stuff. Take parameters
        as kwargs. See readme.txt. """
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)

        """ Set resolution with aspect ratio preserved or discarded. """
        if PRESERVE_ASPECT_RATIO:
            target, source = max([[self.width, self.image.width],
                                  [self.height, self.image.height]])
            correct_res = (int((target/source)*self.image.width/self.hl),
                                int((target/source)*self.image.height/self.vl))
            self.image = self.image.resize(correct_res)
        else:
            self.image = self.image.resize(self.true_resolution)

    def verify_mode(self, image, target_mode):
        """ Verify ´image´ to be in the ´target´ mode: ´P´ = indexed
        or ´RGB´ = RGB. If not, return it in the correct mode. Only
        screenmodes that support more than 256 simultaneous colors
        need to be in RGB, as modern image formats do not support
        indexed palettes larger than 256 colors """
        if target_mode == 'P' and image.mode != target_mode:
            return image.convert('P', None, 0, 1, 256)
        elif target_mode == 'RGB' and image.mode != target_mode:
            return image.convert()
        else:
            return image

    def _chunk(self, width, rawdata):
        """ Split raw image data into chunks (e.g. scanlines) """
        for i in range(0, len(rawdata), width):
            yield rawdata[i:i + width]

    def _bitcrush(self, image, bitdepth):
        """ Bitcrush indexed palette. Image must be in ´P´ mode """
        r = int(math.pow(2**bitdepth,1/3))
        for color in image.getpalette():
            yield int(255 / r * int(color * r / 255))

    def make_image_from_raw(self, rawdata, resolution=None):
        """ Convert raw pixel data in to image. Returns image
        in RGB-format. """
        if resolution is None:
            resolution = self.resolution
            
        canvas = Image.new('RGB', resolution)
        canvas.putdata(rawdata)
        return canvas
    
    def change_bitdepth(self, image, bitdepth):
        """ General palette swapper for non-fixed palette screenmodes.
        Palette is bitcrushed and reapplied to the image. """
        image = self.verify_mode(image, 'P')
        palette = list(self._bitcrush(image, bitdepth))
        image.putpalette(palette)
        return image

    def quantize_to_palette(self, image, palette):
        """ General quantizer for fixed palette screenmodes.
        Palette has to be recreated as an RGB image due to PIL's
        requirements. Quantize image to this palette. """
        tmp = Image.new("RGB", (len(palette), 1))
        tmp.putdata(palette)
        pal = self.verify_mode(tmp, 'P')
        return image.convert('RGB').quantize(len(palette), 2, 0, pal)

    def translate_to_palette(self, image, target_pal):
        """ General source->target palette translator for fixed
        palette screenmodes. Works like change_bitdepth(), but the bit-
        depth doesn't affect the final color space, as the palette
        will be translated to a fixed palette with fixed bit-depth.

        Bit-depth may be increased to brighten up the colors. Normally
        6-12 bit translations produce the best results. """
        verified = self.verify_mode(image, 'P')
        source_pal = self._bitcrush(verified, self.bitdepth)
        palette = Pals.translate_palette(list(source_pal), target_pal)
        verified.putpalette(palette)
        return verified
    
    def rasterize_to_palette(self, im, target_pal):
        """ General rasterizer. """

        def recolor_scanlines(raw_data):
            """ Iterate every scanline from raw image data and
            rasterize mixed colors. Scanline rastering is done
            by disabling the XOR-operation. Vertical raster
            could be produced by using a static ´index´. """
            scanlines = list(self._chunk(im.width, raw_data))
            for i in range(0, len(scanlines)):
                index = i % 2
                j = index
                for pixel in scanlines[i]:
                    if not RASTER_SCANLINES:
                        j = j ^ 1
                    if pixel in self.palette_rasterized.keys():
                       yield self.palette_rasterized[pixel][j]
                    else:
                        yield pixel

        full_palette = target_pal + list(self.palette_rasterized.keys())
        verified = self.translate_to_palette(im, full_palette)
        raw_data = list(verified.convert('RGB').getdata())
        return self.make_image_from_raw(list(recolor_scanlines(raw_data)))

    def process_image(self, image, palette):
        """ Quantize - rasterize - translate selector for the fixed
        palette screenmodes. """
        if self.quantize:
            return self.quantize_to_palette(image, palette)
        elif self.rasterize:
            return self.rasterize_to_palette(image, palette)
        else:
            return self.translate_to_palette(image, palette)

    def process(self):
        """ Print help if process is called from the Converter() """
        subs = Converter.get_subclasses()
        print('Use screenmode specific subcasses: %s.' % ', '.join(subs))

    def validate_kwargs(self, kwarg, value, kwarg_name):
        if kwarg not in value:
            message = '%s must be in [%s].' %\
                      (kwarg_name, ' '.join([str(v) for v in value]))
            raise ValueError(message)
           

class Gameboy(Converter):

    """ ================================================================
    NINTENDO GAME BOY
    ====================================================================

    Mimics the four color (2-bit) Nintendo Gameboy. Supports regular
    fixed palette processing methods.
    
    """

    def __init__(self):
        self.platform = 'Game Boy'
        self.name = 'Game Boy'
        self.width = 160
        self.height = 144
        self.bitdepth = 2
        self.quantize = 0
        self.rasterize = 0
        self.hl = 1
        self.vl = 1
        
        """ Raster lookup for Gameboy """
        self.palette_rasterized = Pals.blend_colors(Pals.gameboy)
        
    def process(self):
        self.image = self.process_image(self.image, Pals.gameboy)


class C64(Converter):

    """ ================================================================
    COMMODORE 64
    ====================================================================

    Commodore 64 full color mode. Horizontal lacing should be used in
    order to produce realistic images. Supports regular fixed palette
    processing methods.
    
    """

    def __init__(self):
        self.platform = 'Commodore 64'
        self.name = 'C64 (full color)'
        self.width = 320
        self.height = 200
        self.bitdepth = 6
        self.quantize = 0
        self.rasterize = 0
        self.hl = 2
        self.vl = 1
        
        """ Raster lookup for C64 """
        self.palette_rasterized = Pals.blend_colors(Pals.C64)
        
    def process(self):
        self.image = self.process_image(self.image, Pals.C64)
  

class MCGA(Converter):

    """ ================================================================
    MULTI-COLOR GRAPHICS ARRAY
    ====================================================================

    18-bit MCGA/VGA with 256 colors and dynamic palette.
    
    """

    def __init__(self):
        self.platform = 'PC'
        self.name = 'MCGA/VGA'
        self.width = 320
        self.height = 200
        self.bitdepth = 18
        self.hl = 1
        self.vl = 1

    def process(self):
        self.image = self.change_bitdepth(self.image, self.bitdepth)


class VGA(Converter):

    """ ================================================================
    VIDEO GRAPHICS ARRAY
    ====================================================================

    18-bit VGA with 16 colors and dynamic palette.
    
    """

    def __init__(self):
        self.platform = 'PC'
        self.name = 'VGA'
        self.width = 640
        self.height = 480
        self.bitdepth = 18
        self.quantize = 0
        self.rasterize = 0
        self.hl = 1
        self.vl = 1

    def process(self):
        palette = list(set(Pals.split_rgb(self.image.convert('RGB').quantize(15, 2).getpalette())['dec']))
        self.palette_rasterized = Pals.blend_colors(palette)
        self.image = self.process_image(self.image, palette)


class EGA(Converter):

    """ ================================================================
    ENHANCED GRAPHICS ADAPTER
    ====================================================================

    Mimics two different PC EGA modes and supports regular fixed palette
    processing methods. Due to the heavy saturation of the EGA colors,
    rastering is produced differently from the other fixed palette
    screenmodes (see Palettes module).

    If resolution is set to 640x350, the picture will be converted into
    EGA hi-res mode that utilizes a dynamic 16-color palette from the
    full 6-bit EGA color space (as used in the intermission screens in
    MS-DOS Lemmings). Rastering or dithered quantization are not
    supported in hi-res mode.
    
    """

    def __init__(self):
        self.platform = 'PC'
        self.name = 'EGA'
        self.width = 320
        self.height = 200
        self.bitdepth = 6
        self.quantize = 0
        self.rasterize = 0
        self.hl = 1
        self.vl = 1

        """ Raster lookup for EGA """
        self.palette_rasterized = Pals.blend_colors(Pals.EGA)
        
    def process(self):

        # TODO: hires rasterointi ei toimi
        """ Use different palette for hi-res mode """
        if self.resolution == (640, 350):
            self.name = 'EGA hi-res'
            self.image = self.translate_to_palette(self.process_image(
                self.image, Pals.EGA_hi).quantize(16), Pals.EGA_hi)
        else:
            self.image = self.process_image(self.image, Pals.EGA)


class CGA(Converter):

    """ ================================================================
    COLOR GRAPHICS ADAPTER
    ====================================================================

    Mimics CGA in both, RGB and composite modes. Supports all regular
    fixed palette conversion methods.

    CGA palette can be controlled by changing the ´palette´ argument:

        0: black-cyan-purple-white 
        1: black-red-green-yellow  
        2: black-cyan-red-white
        3: black-white

    Intensity bit can be set on and off from ´intensity´:

        0: low intensity
        1: high intensity  (supports composite)

    Supported ´composite´ conversion modes are:

        0: Convert to regular CGA as shown on an RGB monitor
        1: Convert regular CGA image to 16-color composite
        2: Convert any image into RGB rasters that will produce
           16 colors on composite
        3: Convert any image as if it was a CGA shown on a TV with
           composite input

    Mode 1 yields good results only if the input CGA image has vertical
    composite rasters. Composite modes do not support low intensity
    modes yet. Also 256 color composites are not supported.

    Composite images are not fringed/smeared yet.
    """

    def __init__(self):
        self.platform = 'PC'
        self.name = 'CGA'
        self.width = 320
        self.height = 200
        self.bitdepth = 12
        self.quantize = 0
        self.rasterize = 0
        self.composite = 0
        self.intensity = 1
        self.palette = 0
        self.hl = 1
        self.vl = 1

    def process(self):

        self.validate_kwargs(self.palette, [0, 1, 2, 3], 'palette')
        self.validate_kwargs(self.composite, [0, 1, 2, 3], 'composite')
        self.validate_kwargs(self.intensity, [0, 1], 'intensity')

        def set_intensity(palette):
            """ Dim colors if intensity bit is off. I.e. subtract
            8 from color indices that map the CGA palette with
            the 16 color full palette (EGA base colors). See the real
            formula: /wiki/Color_Graphics_Adapter """
            for rgb in palette:
                index = Pals.EGA.index(rgb)
                if self.intensity:
                    yield rgb
                else:
                    yield Pals.EGA[max(0, index-8)]

        def translate_to_composite(img, pal, target_mode, res=None):
            """ Reverse lookup depending if doing rgb->composite
            or composite-rgb """
            if target_mode == 'composite':
                lookup = Pals.CGA_comp_map[self.palette]
            elif target_mode == 'rgb':
                lookup = {v: k for k, v in Pals.CGA_comp_map[self.palette].items()}

            """ Set chunk length according to how many pixels are needed
            to represent a single color. """
            if self.palette == 3:
                chunk_len = 4
            else:
                chunk_len = 2

            """ Iterate and reproduce raw data in chunks of n pixels """
            rawdata = []                
            for x in self._chunk(chunk_len, list(img.convert('RGB').getdata())):
                if target_mode == 'rgb':
                    key = x[0]
                    rawdata.extend([pal[i] for i in lookup[key]])
                elif target_mode == 'composite':
                    if self.palette == 3:
                        key = pal.index(x[0]), pal.index(x[1]),\
                              pal.index(x[2]), pal.index(x[3])
                    else:
                        key = pal.index(x[0]), pal.index(x[1])
                    rawdata.extend([lookup[key]]*chunk_len)
            return self.make_image_from_raw(rawdata, res)

        """ Set palette intensity """
        cga_palette = list(set_intensity(Pals.CGA[self.palette]))

        """ Composite mode selector.It would be more convenient to
        handle 2 and 4 pixels per color modes reparately to avoid
        excess conditional clauses, unnecessary flag combinations and
        forced resolution changes (also in translate_to_composite()). """
        if self.composite == 0 or self.intensity == 0:
            # Regular CGA for both intensities
            self.palette_rasterized = Pals.blend_colors(cga_palette)
            self.image = self.process_image(self.image, cga_palette)

        if self.composite == 1:
            # Composite rasters -> composite. Force horizontal lacing.
            self.palette_rasterized = Pals.blend_colors(cga_palette)
            if self.original.width == 640 and self.palette == 3:
                img = self.verify_mode(self.original, 'P')
                res = (self.original.width, self.original.height)
            else:
                img = self.process_image(self.image, cga_palette)
                res = self.resolution
            self.set_properties(hl=2)
            self.image = translate_to_composite(img, cga_palette, 'composite', res)\
                         .resize(self.resolution)
            
        if self.composite in [2, 3]:
            # Make rasters for composite palette
            cga_comps = Pals.CGA_comps[self.palette]
            self.palette_rasterized = Pals.blend_colors(cga_comps)
        
            # Force hi-res if doing composite rasters for pal 3
            # as it needs 4 pixels per color
            if self.composite == 2 and self.palette == 3:
                self.set_properties(width=640)

            # Convert into 16-color composite     
            img = self.process_image(self.image, cga_comps)

            # If mode 2, translate 16-color -> rasters
            if self.composite == 2:
                self.image = translate_to_composite(img, cga_palette, 'rgb')
            else:
                self.image = img


class OCS(Converter):

    """ ================================================================
    ORIGINAL CHIPSET (DENISE) Standard graphics
    ====================================================================

    Mimics standard graphics on the Amiga Original Chipset.
    Mode uses a dynamic palette from the 12-bit color space. In lowres
    the mode can handle 32 simultaneous colors. In hires mode the maximum
    palette size is 16.

    Although the palette is dynamic, OCS supports fixed palette conversion
    methods (dithered quantization and rastering).

    Lowres modes have width of 320. Hires is used automatically if image
    width exceeds 640 (unless horizontal lacing is used). Scanlines can
    be doubled by using vertical lacing.
    
    """

    def __init__(self):
        self.platform = 'Commodore Amiga'
        self.name = 'OCS lowres'
        self.width = 320
        self.height = 200
        self.bitdepth = 12
        self.rasterize = 0
        self.quantize = 0
        self.hl = 1
        self.vl = 1
 
    def process(self):
        """ Set color limitation for hires mode """
        if self.width > 320:
            colors = 16
            self.name = 'OCS hires'
        else:
            colors = 32
        lowbit = self.change_bitdepth(self.image, self.bitdepth)\
                                    .quantize(colors-1, 0)

        """ Post-processing: apply rastering etc. """
        palette = list(set(Pals.split_rgb(lowbit.getpalette())['dec']))
        if self.rasterize:
            self.palette_rasterized = Pals.blend_colors(list(set(palette)))
        self.image = self.process_image(self.image, palette)
            
        
class EHB(Converter):

    """ ================================================================
    EXTRA HALFBRITE (OCS DENISE)
    ====================================================================

    Mimics the Amiga Extra Halfbrite mode that uses a dynamic 32 color
    palette chosen from the 12-bit color space. In addition to the
    chosen 32 colors EHB produces a half-brite version of this palette
    (literally a palette with half the brightness), which yields a
    palette of 64 colors in total.

    EHB images can be sliced to increase the number of available colors.
    Results vary greatly on the source image. The number of ´slices´
    cannot exceed the number of scanlines.

    Non-sliced EHB mode supports ´quantize´ and ´rasterize´. For sliced
    images calculating rasterized palettes is quite slow and thus
    disabled. 
    
    """   

    def __init__(self):
        self.platform = 'Commodore Amiga'
        self.name = 'EHB'
        self.width = 320
        self.height = 200
        self.bitdepth = 12
        self.rasterize = 0
        self.quantize = 0
        self.hl = 1
        self.vl = 1
        self.slices = 1
        
    def process(self):
        """ Mimic (a rather unoptimized) EHB by calculating a
        palette and its half-brite counterpart. Translate a
        12-bit 256 color version of the image into a concatenation
        of these palettes. """

        def recolor(im):
            """ Recolor EHB slices and make halfbrites """
            ver_slice = self.verify_mode(im, 'P')
            source_pal = list(self._bitcrush(ver_slice, self.bitdepth))
            brite = ver_slice.quantize(31, 0).getpalette()[0:3*32]
            halfbrite = [int(c / 2) for c in brite]
            ehb = Pals.split_rgb(brite+halfbrite)['dec']
            pal = Pals.translate_palette(source_pal, ehb)
            if self.rasterize and self.slices == 1:
                self.palette_rasterized = Pals.blend_colors(ehb)
                ver_slice = self.process_image(ver_slice, ehb)
            else:
                ver_slice.putpalette(pal)
            return ver_slice

        canvas = Image.new("RGB", self.resolution)
        verified = self.verify_mode(self.image, 'RGB')
        slice_height = int(verified.height / self.slices)

        if self.slices > self.image.height:
            self.slices = self.image.height
        if self.slices > 1 and VERBOSE:
            print('Slicing...')

        """ Slice image and reconstruct it """
        i, j = 0, 0
        while i <= self.image.height:
            if VERBOSE:
                self._show_progress(i, self.image.height)
            if j == self.slices:
                remainder = self.image.height % self.slices
            else:
                remainder = 0
            """ Define crop area as a 4-tuple (x0, y0, x1, y1) """
            crop_area = (0, i, self.image.width, slice_height+i+remainder)
            part = recolor(verified.crop(crop_area))
            """ Add slice to RGB canvas """
            canvas.paste(part.convert('RGB'), (0, i))
            i += slice_height
            j += 1

        self.image = canvas

    
class HAM(Converter):

    """ ================================================================
    HOLD-AND-MODIFY
    ====================================================================

    Mimics the Amiga Hold-and-modify mode that is able to show the whole
    12-bit color space (4096 colors) simultaneously by using a palette
    of 16 colors.

    HAM uses an unusual technique, where the left pixel can be partially
    copied in case its color is closer to the wanted shade than any
    available color in the palette. One RGB value of the left pixel can
    be modified to correspond the wanted color, but the remaining two
    must be held. This means, that HAM is able to change from any color
    to another by using three or less intermediary pixels. These
    intermediary artifacts are known as fringes.

    For example, if HAM wants to produce purple from black, the color
    transition would need one blue intermediary pixel:

        (0,0,0) -> (255,0,0) -> (255,0,255) 

    Tip: The frining may be observed clearly by setting ´base_palette´
    manually to black and white [(0,0,0), (255,255,255)]. Base palette
    will be optimized to the image only if it is an empty list [].

    As the bitplanes are not emulated here, the fringes are produced
    artifically. Due to the computational cost of the pixel operations,
    fringing can be turned off by setting ´fringe´ to 0.

    Supported modes are changed by adjusting the bit-depth:

        OCS HAM6 (12-bit). Uses a base palette of 16 colors. Fringing is
        quite fast to calculate especially in lowres modes (width 320)

        AGA HAM8 (18-bit). Uses a base palette of 256 colors. Fringing
        is slow but tolerable in lowres modes, but it should not be used
        on higher resolutions. Fringed and non-fringed HAM8 images are
        practically impossible to distinguish from each other by eye.

    Fringing ´algorithm´ may be changed (default 1):

        0: Fast comparison. Does not look at the base palette if the
           left pixel looks close enough (algorithm is bugged)
        1: Accurate comparison. Better result but 30-50 % slower.

    Pixel ´transitions´ can be controlled as well (default 1):

        0: Ordered. The colors are modified in R->G->B order.
        1: Optimal. The colors are modified in the optimal order
           starting from the most different one.
        
    """

    def __init__(self):
        self.platform = 'Commodore Amiga'
        self.name = 'HAM6'
        self.width = 320
        self.height = 200
        self.bitdepth = 12
        self.hl = 1
        self.vl = 1
        self.fringe = 1
        self.algorithm = 1
        self.transitions = 1
        self.base_palette = [] # Set to override optimized base palette

    def process(self):
        """ HAM processing is rather complicated in comparison to the
        other screenmodes. It first involves truncating the color space
        into >256 color palette (which is not supported by modern
        systems). The truncated image is then fringed. """
        lowbit_bands = self._extract_bands(self.image)
        canvas = Image.merge('RGB', tuple(lowbit_bands))
        
        if self.fringe:
            if VERBOSE:
                print('Calculating fringes...')
            self.image = self._generate_fringing(canvas.getdata(), self.image)
        else:
            self.image = canvas

    def _extract_bands(self, img):
        """ Split image into RGB bands and bitcrush them. This reduces
        the maximum color amount to 4096 for 12-bit HAM and 262144 for
        18-bit HAM. """
        bands = img.convert('RGB').split()
        for band in bands:
            band = band.quantize(256, 0, 0, 0)
            band = self.change_bitdepth(band, self.bitdepth)
            yield band.convert('L')

    def _generate_fringing(self, data, img):
        self.BBB = 0
        """ Fringing algorithm:
        1: quantize ´img´ to create an optimal base palette of n colors
        2: for each pixel in image raw ´data´
               if Δ(pixel, left pixel) ≤ Δ(pixel, base palette) or
               left pixel does not exist
                  return closest color from base palette
               else for each RGB value in pixel and left pixel
                  if pixel RGB value ≠ left RGB value
                     return that RGB value from pixel (modify) and
                     return two other RGB values from left (hold) """

        if self.bitdepth == 18:
            self.name = 'HAM8'
            breakpoint = 12
            colors = 256
            print('Warning: calculating 18-bit fringes may take a while...')
        else:
            breakpoint = 4
            colors = 16
               
        if not self.base_palette:
            self.base_palette = list(set(Pals.split_rgb(
                            self.verify_mode(img, 'P')\
                            .quantize(colors, 0)\
                            .getpalette())['dec']))

        def compare(cp, lp, bp, pos):
            """ Compare RGB values and calculate penalties to
            the base palette and the left pixel. ´cp´ = current
            pixel, ´lp´ = left pixel, ´bp´ = base palette,
            ´pos´ = pixel position in the raw data """

            penalties = {}
            r1, g1, b1 = cp
            r3, g3, b3 = lp
            diff_table = [abs(r1-r3), abs(g1-g3), abs(b1-b3)]
            left_penalty = sum(diff_table)
                           
            for rgb in bp:
                r2, g2, b2 = rgb
                penalty = abs(r1-r2) + abs(g1-g2) + abs(b1-b2)
                penalties[penalty] = rgb
                if not self.algorithm and penalty > left_penalty * breakpoint\
                   or not self.algorithm and left_penalty < 50:
                    break

            """ Hold and modify if closer to the left pixel,
            else return color from the palette; disallow
            holding if on the left border """
            if left_penalty <= min(penalties.keys())\
               and pos not in range(0, len(data), img.width):
                mod_r, mod_g, mod_b = lp # Held values
                if self.transitions:
                    max_diff = max(diff_table)
                    if diff_table.index(max_diff) == 0:
                        mod_r = r1 # Modify red
                    elif diff_table.index(max_diff) == 1:
                        mod_g = g1 # Modify green
                    elif diff_table.index(max_diff) == 2:
                        mod_b = b1 # Modify blue
                    return (mod_r, mod_g, mod_b)
                else:
                    if r1 != r3:
                        mod_r = r1 # Modify red
                    elif g1 != g3:
                        mod_g = g1 # Modify green
                    elif b1 != b3:
                        mod_b = b1 # Modify blue
                    return (mod_r, mod_g, mod_b)
            else:
                return penalties[min(penalties.keys())]

        def iterate_pixels(data):
            """ Initialize left pixel and cycle through raw
            image data to compare each pixel against the base
            palette and preceding (left) pixel """
            left_pixel = (0,0,0)
            for pos in range(0, len(data)):
                if pos in range(0, len(data), img.width) and VERBOSE:
                    self._show_progress(pos, len(data))
                current_pixel = data[pos]
                new_pixel = compare(current_pixel, left_pixel,
                                    self.base_palette, pos)
                left_pixel = new_pixel
                yield new_pixel

        canvas = self.make_image_from_raw(list(iterate_pixels(data)))
        return canvas
