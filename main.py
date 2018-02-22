#!/usr/bin/python
# -*- coding: utf-8 -*-

#from bitcrush import Converter
import time
import bitcrush
from argparse import ArgumentParser

# Available screenmodes
MODES = bitcrush.Converter().get_subclasses()

def get_args():
    ap = ArgumentParser()
    ap.add_argument('-f', '--filename')
    ap.add_argument('-m', '--screenmode', type=str, choices=MODES)
    ap.add_argument('-b', '--bitdepth', type=int, default=None)
    ap.add_argument('-r', '--resolution', type=int, nargs=2, default=(None,None))
    ap.add_argument('-a', '--adjust', type=float, nargs=2, default=(1.0, 1.0))
    ap.add_argument('-V', '--vertical-lacing', action='store_true', default=False)
    ap.add_argument('-H', '--horizontal-lacing', action='store_true', default=False)
    ap.add_argument('-x', '--multiplier', type=int, default=1)
    ap.add_argument('-t', '--save-true-resolution', action='store_true', default=False)
    ap.add_argument('-P', '--preserve-aspect-ratio', action='store_true', default=False)
    ap.add_argument('-v', '--verbose', action='store_true', default=False)
    ap.add_argument('-R', '--rasterize', action='store_true', default=None)
    ap.add_argument('--rasterize-scanlines', action='store_true', default=False)    
    ap.add_argument('-d', '--dither', action='store_true', default=None)
    ap.add_argument('-p', '--palette', type=int, choices=[0, 1, 2, 3], default=None)
    ap.add_argument('-c', '--composite', type=int, choices=[0, 1, 2, 3], default=None)
    ap.add_argument('-l', '--low-intensity', action='store_false', default=None)
    ap.add_argument('-s', '--slices', type=int, default=None)
    ap.add_argument('--fast-ham', action='store_false', default=None)
    ap.add_argument('--no-fringing', action='store_false', default=None)
    ap.add_argument('--ordered-transitions', action='store_false', default=None)
    ap.add_argument('-S', '--show-preview', action='store_true', default=False)
    ap.add_argument('-n', '--no-save', action='store_true', default=False)
    ap.add_argument('--debug', action='store_true', default=False)
    args = ap.parse_args()
    return args

def default():
    """ Default mode for playing with different settings; see
    readme.txt for more info on setting variables.
    See kwargs for set_properties() from commandline processing. """
    filename = 'maisema2.png'
    pic = bitcrush.CGA()                         # select mode
    pic.load_image(filename)                     # load input picture
    pic.set_properties(bitdepth=12, rasterize=1) # define settings
    pic.process()                                # convert image
    pic.show_image()                             # show image
    pic.save_image(filename)                     # save image

def commandline_process(fname, args):
    """ Process file(s) from the command line. Input may be given
    as a image file or as a text file containing a list of files. """

    hl = None
    vl = None

    if args.vertical_lacing:
        vl = 2
    if args.horizontal_lacing:
        hl = 2
    
    """ Set global variables """
    bitcrush.MULTIPLIER = args.multiplier
    bitcrush.VERBOSE = args.verbose
    bitcrush.SAVE_TRUE_RESOLUTION = args.save_true_resolution
    bitcrush.PRESERVE_ASPECT_RATIO = args.preserve_aspect_ratio
    bitcrush.RASTER_SCANLINES = args.rasterize_scanlines

    if args.rasterize_scanlines:
        args.rasterize = True

    """ Set conversion variables"""
    screenmode = getattr(bitcrush, args.screenmode)
    img = screenmode()
    img.load_image(fname)
    img.set_properties(bitdepth=args.bitdepth,
                       width=args.resolution[0],
                       height=args.resolution[1],
                       hl=hl,
                       vl=vl,
                       quantize=args.dither,
                       rasterize=args.rasterize,
                       palette=args.palette,
                       composite=args.composite,
                       intensity=args.low_intensity,
                       slices=args.slices,
                       algorithm=args.fast_ham,
                       fringe=args.no_fringing,
                       transitions=args.ordered_transitions)
    img.adjust(args.adjust[0], args.adjust[1])
    if args.debug: print(img)
        
    img.process()
    img.print_image_info()

    if args.show_preview:
        img.show_image()
    if not args.no_save:
        img.save_image(fname)


def main():
    #start_time = time.time()
    args = get_args()
    """ Enter default mode if commandline is not used """
    if args.filename is None:
        default()
    else:
        fname = args.filename
        if fname.endswith('.txt'):
            with open(fname, encoding='utf-8') as filelist:
                files = filelist.read().splitlines()
            for fname in files:
                if fname:
                    commandline_process(fname, args)
        else:
            commandline_process(fname, args)
    #elapsed_time = time.time() - start_time
    #print(elapsed_time)

if __name__ == "__main__":
    main()

