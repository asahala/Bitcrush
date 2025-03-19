# Bitcrush
Converts images into C64, Amiga and PC retro lookalikes. See /readme/readme.html or my [website for detailed instructions](http://www.mv.helsinki.fi/home/asahala/bitcrush/).

GNU General Public License v3.0

## Screenmodes
* **PC**: SVGA, VGA, MCGA, EGA (hires/normal), CGA (composite, RGBI)
* **Amiga**: HAM8, HAM6, EHB (sliced/normal), OCS (hires/lowres)
* **Commodore 64** 
* **Nintendo Gameboy**

## Requirements
Python 3.4 or newer, [Pillow](https://pypi.org/project/Pillow/) (tested on version 8.1.0).

## Examples
![alt text](http://www.mv.helsinki.fi/home/asahala/bitcrush/ex_raster_large.png)

# Command line examples

Below are some examples how to convert image into various modes. I use varying bit depths `-b`
to adjust the brightness of the image.

## Original image in True color
![alt text](http://www.mv.helsinki.fi/home/asahala/bitcrush/tropic.png)

## EGA
![alt text](http://www.mv.helsinki.fi/home/asahala/bitcrush/tropic-ega.png)

`python main.py -f tropic.png -m EGA --multiplier 2 --rasterize -b 10`

## EGA Hi-res mode (as in PC Lemmings intermission screens)
![alt text](http://www.mv.helsinki.fi/home/asahala/bitcrush/tropic-egahires.png)

`python main.py -f tropic.png -m EGA -r 640 350 -b 14`

## CGA in composite mode
![alt text](http://www.mv.helsinki.fi/home/asahala/bitcrush/tropic-cga.png)

`python main.py -f tropic.png -m CGA -H -S -c 3 --palette 1`

## Super VGA
![alt text](http://www.mv.helsinki.fi/home/asahala/bitcrush/tropic-svga.png)

`python main.py -f tropic.png -m MCGA -r 640 480`

## Commodore 64
![alt text](http://www.mv.helsinki.fi/home/asahala/bitcrush/tropic-c64.png)

`main.py -f tropic.png -m C64  -b 12 --rasterize -H`

## Amiga Extra Half-brite (EHB)
![alt text](http://www.mv.helsinki.fi/home/asahala/bitcrush/tropic-ehb.png)

`python main.py -f tropic.png -m EHB`

## Amiga Hold-and-modify (HAM)
![alt text](http://www.mv.helsinki.fi/home/asahala/bitcrush/tropic-ham.png)

`python main.py -f tropic.png -m HAM -r 320 256`

## Nintendo Gameboy
![alt text](http://www.mv.helsinki.fi/home/asahala/bitcrush/tropic-gameboy.png)

`python main.py -f tropic.png -m Gameboy -S -b 5 --rasterize --multiplier=2`
