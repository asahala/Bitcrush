# Bitcrush
Converts images into C64, Amiga and PC retro lookalikes. See /readme/readme.html for detailed information.

==================================================================================
ALL COMMANDLINE PARAMETERS =======================================================
==================================================================================

The order of the parameters is free. Most parameters have abbreviated aliases.

python main.py [parameters]

  -h, --help                             
  -f, --filename [FILENAME]                     (mandatory)
  -m, --screenmode [SCREENMODE]                 (mandatory)
  -b, --bitdepth [BITDEPTH]             
  -r, --resolution [WIDTH] [HEIGHT]
  -a, --adjust [BRIGHTNESS] [CONTRAST]
  -V, --vertical-lacing
  -H, --horizontal-lacing
  -x, --multiplier [MULTIPLIER]
  -t, --save-true-resolution
  -P, --preserve-aspect-ratio
  -v, --verbose
  -R, --rasterize
  --rasterize-scanlines
  -d, --dither
  -p, --palette [PALETTE NUMBER]
  -c, --composite [COMPOSITE MODE]
  -l, --low-intensity
  -s, --slices [NUMBER OF SLICES]
  --fast-ham
  --no-fringing
  --ordered-transitions
  -S, --show-preview
  -n, --no-save
  --debug


==================================================================================
DETAILED DESCRIPTION OF THE COMMAND LINE PARAMETERS ==============================
==================================================================================

Only MANDATORY parameter must be defined. If a parmeter is left undefined,
the image will be processed with hard-coded default settings for the 
screenmode

General settings:

 --debug
    OPTIONAL: Print instance variables.

 --multiplier [int]   -x [int]
    OPTIONAL: Image dimensions are multiplied.

 --no-save   -n
    OPTIONAL: Do not save image.

 --preserve-aspect-ratio   -P
    OPTIONAL: Preseve image's aspect ratio. The image will only be scaled
    to the wanted width or height.

 --save-true-resolution   -t
    OPTIONAL: Laced or doubled images will not be stretched when saved.

 --show-preview  -S
    OPTIONAL: Preview image after processing. Should not be used when batch
    processing files.

 --verbose   -v
    OPTIONAL: Print additional processing information for computationally
    more time consuming screenmodes like sliced EHB and HAM.


Image processing parameters:

  --filename [arg]   -f [arg]
     MANDATORY: Argument may be an image file or a text file containing
     a list of images one per each line.

  --screenmode [arg]   -m [arg]
     MANDATORY: Define screenmode, e.g. -m C64 for the Commodore 64. Available
     modes are C64, Gameboy, CGA, EGA, MCGA, VGA, OCS, EHB and HAM.

  --adjust [float] [float]   -a [float] [float]
     OPTIONAL: Adjusts image brightness and contrast. For example, -a 1.5 1.8
     increases brightness by 50% and contrast by 80%. 

  --bitdepth [int]   -b [int]
     OPTIONAL: Define color bit-depth. Must be an integer higher than 1.
     Non-fixed/dynamic palette modes should use their default bit-depth.
     For fixed palette modes, bit-depth is used to control the translation
     algorithm and it will NOT affect the final color space! All fixed
     palettes have hard-coded bit-depth. Recommended bit-depth for fixed
     palette modes are 6, 8, 10 or 12. Lower values push the color space
     towards white resulting into darker and more simplistic coloring.
     High bit-depts provide more vivid colors and detail.

  --resolution [int] [int]  -r [int] [int]
     OPTIONAL: Define target resolution. E.g. to produce MCGA images use
     VGA with -r 320 200.

  --vertical-lacing   -V
     OPTIONAL: Use vertical lacing, i.e. scanline doubling.

  --horizontal-lacing   -H
     OPTIONAL: Use horizontal lacing, i.e. stretch the pixels horizontally.

  --rasterize    -R                              (fixed and dynamic palettes)
     OPTIONAL: Use diagonal rastering on fixed and some dynamic palette modes.
     Incompatible with dithering.

  --rasterize-scanlines                          (fixed and dynamic palettes)
     OPTIONAL: Use scanline rastering on fixed and some dynamic palette modes.
     Incompatible with dithering.

  --dither    -d                                 (fixed and dynamic palettes)
     OPTIONAL: Dither image to a fixed palette. Incompatible with rasterization.

  --palette [int]  -P [int]                   (CGA only)
    OPTIONAL: If CGA is selected, define which palette to use. Option is given
    as an integer from 0 to 2. See general screenmode description for more info.
  
  --low-intensity  -l                        (CGA only)  
     OPTIONAL: Use low-intensity palette for CGA. Incompatible with --composite.

  --composite [int]  -c [int]                    (CGA only)
     OPTIONAL: Mimic different CGA outputs on different monitors. See
     available modes from the general screenmode description. 

  --slices [int]    -s [int]                     (EHB only)
     OPTIONAL: Define the number of slices for Amiga EHB mode.

  --no-fringing                              (HAM only)
     OPTIONAL: Disable Amiga HAM fringing effect.

  --fast-ham                                     (HAM only)
     OPTIONAL: Use fast comparison when producing HAM fringes. About
     50% faster to compute.

  --ordered-transitions                      (HAM only)
     OPTIONAL: Force fringing algorithm to modify pixels in R->G->B order.
     
==================================================================================
EXAMPLE USAGE ====================================================================
==================================================================================

python main.py -f test.png -b 12 -r 320 200 -H -m EGA --rasterize -S 

Produces an EGA image from (-f) test.png in horizontally laced (-H) 320x200 
resolution (-r) with rasterized (--rasterize) colors and 12-bit recoloring (-b). 
Image will be previewed (-S).

