#!/bin/python

import os,sys,random,math
import numpy as np
from functools import reduce
from PIL import Image

### SETUP ###
# Constants
palette = {'bg':(255,255,255),
           'true-black':(0,0,0),
           'black':(10,10,10),
           'true-white':(255,255,255),
           'white':(255,255,255),
           'red':(240,0,0),
           'green':(0,240,0),
           'blue':(0,0,240),
           'cyan':(0,240,240),
           'yellow':(240,240,0),
           'magenta':(240,0,240),
           'dark-green':(0,200,0)}
# Variable defaults
panels       = []
balls        = {}
# Class declarations
class Artist:
    '''
    A profile for a shitty artist.
    '''
    def __init__(self):
        self.border_thick = random.choice(
            (0,
             random.randrange(1,4)))
        self.brush_weight = random.choice(
            ('1px',
             'thin',
             'thick',
             'random'))
        self.colors_style = random.choice(
            ('right',
             'random',
             'colorblind'))
        self.copy_pastes = random.choice(
            ('frequently',
             'occasionally',
             'never'))
        self.ellipse_style = random.choice(
            ('connected',
             'not-overlapping',
             'overlapping',
             'overlapping-overkill'))
        self.eyes_style = random.choice(
            ('elliptical',
             'round'))
        self.geo_knowledge = random.choice(
            ('europe-relevant',
             'europe-irrelevant',
             'asia-relevant'))
        self.hates_muslims = random.choice(
            ('a-lot',))
        self.poland_style = random.choice(
            ('right',
             'wrong',
             'random'))
        self.pupil_style = random.choice(
            ('none',
             'big',
             'small'))
        self.shittiness = random.choice(
            (0.,                      # circletool
             0.5+0.8*random.random(), # good
             0.8+0.4*random.random(), # average
             1.5+random.random()))    # absolutely terrible
        self.into_jpeg     = random.choice((True,False))
        self.idiot = random.choice((True,False))
    def fix_some(self):
        if not self.border_thick == 0 and random.random() < 0.3:
            self.border_thick = 0
        if self.brush_weight not in ('thin','thick') and random.random() < 0.3:
            self.brush_weight = random.choice('thin','thick')
        if not self.colors_style == 'right' and random.random() < 0.3:
            self.colors_style = 'right'
        if not self.copy_pastes == 'never' and random.random() < 0.3:
            self.copy_pastes = 'never'
        if not self.ellipse_style in ('connected','overlapping') and\
                random.random() < 0.3:
            self.ellipse_style = random.choice('connected','overlapping')
        if not self.poland_style == 'right' and random.random() < 0.3:
            self.poland_style = 'right'
        if not self.pupil_style == 'none' and random.random() < 0.3:
            self.pupil_style = 'none'
    def fix_all(self):
        if not self.border_thick == 0:
            self.border_thick = 0
        if self.brush_weight not in ('thin','thick'):
            self.brush_weight = random.choice('thin','thick')
        if not self.colors_style == 'right':
            self.colors_style = 'right'
        if not self.copy_pastes == 'never':
            self.copy_pastes = 'never'
        if not self.ellipse_style in ('connected','overlapping'):
            self.ellipse_style = random.choice('connected','overlapping')
        if not self.poland_style == 'right':
            self.poland_style = 'right'
        if not self.pupil_style == 'none':
            self.pupil_style = 'none'
class Canvas:
    '''
    Stores a drawing surface, with 24-bit color.
    '''
    def __init__(self,height,width,bg_color):
        self.height   = height
        self.width    = width
        self.bg_color = bg_color
        self.pixels = np.tile(
                np.array(bg_color),
                (self.height,self.width))
    def get_pixel(self,x,y):
        '''
        Gets the color of a pixel at point (x,y). This is a tuple of
        three color values, but (-1,-1,-1) corresponds to
        transparency, and (-2,-2,-2) corresponds to nonexistence.
        '''
        if 0 <= x and x < self.width and 0 <= y and y < self.height:
            return (self.pixels[y][3*x],
                    self.pixels[y][3*x+1],
                    self.pixels[y][3*x+2])
        else:
            return (-2,-2,-2) # (-1,-1,-1) would mean transparency
    def get_drawable(self):
        '''
        Returns a version of self.pixels that parses correctly to a
        PIL Image.
        '''
        bg_color = None
        if 0 <= self.bg_color[0] and self.bg_color[0] <= 255 and\
                0 <= self.bg_color[1] and self.bg_color[1] <= 255 and\
                0 <= self.bg_color[2] and self.bg_color[2] <= 255:
            bg_color = self.bg_color
        else:
            bg_color = (255,255,255)
        pixels = []
        for row in self.pixels:
            into_drawable = True
            pixels.append([])
            color = []
            for index,value in enumerate(row):
                into_drawable = into_drawable and value >= 0
                color.append(value)
                if index%3 == 2:
                    if into_drawable:
                        pixels[-1].extend(color)
                    else:
                        pixels[-1].extend(self.bg_color)
                    color = []
        return np.array(pixels)
    def pencil(self,x,y,color):
        if 0 <= x and x < self.width and 0 <= y and y < self.height:
            self.pixels[y][3*x]   = color[0]
            self.pixels[y][3*x+1] = color[1]
            self.pixels[y][3*x+2] = color[2]
    def crop(self):
        '''
        Deletes all rows and columns of pixels from the top, bottom,
        and sides of the canvas that are the same color as bg_color.
        '''
        trim_color = self.bg_color
        top_trim = 0 # amount of lines to trim from the top
        for y in range(self.height):
            is_trim_color = True # whether the line consists only of trim_color
            for x in range(self.width):
                is_trim_color = is_trim_color and\
                        trim_color == self.get_pixel(x,y)
            if not is_trim_color:
                break
            else:
                top_trim += 1
        bottom_trim = 0 # amount of lines to trim from the bottom
        for y in range(self.height-1,-1,-1):
            is_trim_color = True # whether the line consists only of trim_color
            for x in range(self.width):
                is_trim_color = is_trim_color and\
                        trim_color == self.get_pixel(x,y)
            if not is_trim_color:
                break
            else:
                bottom_trim += 1
        left_trim = 0 # amount of lines to trim from the left
        for x in range(self.width):
            is_trim_color = True # whether the line consists only of trim_color
            for y in range(self.height):
                is_trim_color = is_trim_color and\
                        trim_color == self.get_pixel(x,y)
            if not is_trim_color:
                break
            else:
                left_trim += 1
        right_trim = 0 # amount of lines to trim from the right
        for x in range(self.width-1,-1,-1):
            is_trim_color = True # whether the line consists only of trim_color
            for y in range(self.height):
                is_trim_color = is_trim_color and\
                        trim_color == self.get_pixel(x,y)
            if not is_trim_color:
                break
            else:
                right_trim += 1
        self.height -= top_trim+bottom_trim
        self.width  -= left_trim+right_trim
        self.pixels = [row[3*left_trim:len(row)-3*right_trim] for row in
                self.pixels[top_trim:len(self.pixels)-bottom_trim]]
    def merge_down(self,other,disp_x=0,disp_y=0):
        '''
        Merges this canvas with another one, as if this one were
        placed on top of it.
        '''
        final = Canvas(self.height,self.width,self.bg_color)
        for y in range(other.height):
            for x in range(other.width):
                pixel = (-1,-1,-1)
                top_pixel = self.get_pixel(disp_x+x,disp_y+y)
                if top_pixel in ((-2,-2,-2),(-1,-1,-1)):
                    bottom_pixel = other.get_pixel(x,y)
                    if not bottom_pixel in ((-2,-2,-2),(-1,-1,-1)):
                        pixel = bottom_pixel
                else:
                    pixel = top_pixel
                self.pencil(disp_x+x,disp_y+y,pixel)
    def merge_up(self,other,disp_x=0,disp_y=0):
        '''
        Merges this canvas with another one, as if it were placed on
        top of this one.
        '''
        final = Canvas(other.height,other.width,self.bg_color)
        for y in range(other.height):
            for x in range(other.width):
                pixel = (-1,-1,-1)
                top_pixel = other.get_pixel(x,y)
                if top_pixel in ((-2,-2,-2),(-1,-1,-1)):
                    bottom_pixel = self.get_pixel(disp_x+x,disp_y+y)
                    if not bottom_pixel in ((-2,-2,-2),(-1,-1,-1)):
                        pixel = bottom_pixel
                else:
                    pixel = top_pixel
                self.pencil(disp_x+x,disp_y+y,pixel)
    def replace_color(self,to_replace,substitute):
        '''
        Replaces the color to_replace with the color substitute
        everywhere in the canvas.
        '''
        final = Canvas(self.height,self.width,self.bg_color)
        for y in range(self.height):
            for x in range(self.width):
                pixel = self.get_pixel(x,y)
                if pixel == to_replace:
                    self.pencil(x,y,substitute)
                else:
                    self.pencil(x,y,pixel)
    def paint(self,x,y,color,size=1):
        if size == 1:
            self.pencil(x,y,color)
        elif size == 2:
            self.pencil(x,y-1,color)
            self.pencil(x-1,y,color)
            self.paint(x,y,color,1)
            self.pencil(x+1,y,color)
            self.pencil(x,y+1,color)
        elif size == 3:
            self.pencil(x-1,y-1,color)
            self.pencil(x+1,y-1,color)
            self.paint(x,y,color,2)
            self.pencil(x-1,y+1,color)
            self.pencil(x+1,y+1,color)
        elif size == 4:
            self.pencil(x,y-2,color)
            self.pencil(x-2,y,color)
            self.paint(x,y,color,3)
            self.pencil(x+2,y,color)
            self.pencil(x,y+2,color)
        elif size == 5:
            self.pencil(x-1,y-2,color)
            self.pencil(x+1,y-2,color)
            self.pencil(x-2,y-1,color)
            self.pencil(x+2,y-1,color)
            self.paint(x,y,color,4)
            self.pencil(x-2,y+1,color)
            self.pencil(x+2,y+1,color)
            self.pencil(x-1,y+2,color)
            self.pencil(x+1,y+2,color)
        elif size == 6:
            self.pencil(x,y-3,color)
            self.pencil(x-2,y-2,color)
            self.pencil(x+2,y-2,color)
            self.pencil(x-3,y,color)
            self.paint(x,y,color,5)
            self.pencil(x+3,y,color)
            self.pencil(x-2,y+2,color)
            self.pencil(x+2,y+2,color)
            self.pencil(x,y+3,color)
        elif size == 7 or size == 8:
            self.pencil(x-2,y-3,color)
            self.pencil(x-1,y-3,color)
            self.pencil(x+1,y-3,color)
            self.pencil(x+2,y-3,color)
            self.pencil(x-3,y-2,color)
            self.pencil(x+3,y-2,color)
            self.pencil(x-3,y-1,color)
            self.pencil(x+3,y-1,color)
            self.paint(x,y,color,6)
            self.pencil(x-3,y+1,color)
            self.pencil(x+3,y+1,color)
            self.pencil(x-3,y+2,color)
            self.pencil(x+3,y+2,color)
            self.pencil(x-2,y+3,color)
            self.pencil(x-1,y+3,color)
            self.pencil(x+1,y+3,color)
            self.pencil(x+2,y+3,color)
        elif size == 9:
            self.pencil(x-1,y-4,color)
            self.pencil(x,y-4,color)
            self.pencil(x+1,y-4,color)
            self.pencil(x-3,y-3,color)
            self.pencil(x+3,y-3,color)
            self.pencil(x-4,y-1,color)
            self.pencil(x+4,y-1,color)
            self.pencil(x-4,y,color)
            self.paint(x,y,color,8)
            self.pencil(x+4,y,color)
            self.pencil(x-4,y+1,color)
            self.pencil(x+4,y+1,color)
            self.pencil(x-3,y+3,color)
            self.pencil(x+3,y+3,color)
            self.pencil(x-1,y+4,color)
            self.pencil(x,y+4,color)
            self.pencil(x+1,y+4,color)
        elif size == 10:
            self.pencil(x-2,y-4,color)
            self.pencil(x+2,y-4,color)
            self.pencil(x-4,y-2,color)
            self.pencil(x+4,y-2,color)
            self.paint(x,y,color,9)
            self.pencil(x-4,y+2,color)
            self.pencil(x+4,y+2,color)
            self.pencil(x-2,y+4,color)
            self.pencil(x+2,y+4,color)
        elif size < 0:
            self.paint(x,y,color,1)
        elif size > 10:
            self.paint(x,y,color,10)
    def ellipse(self,x,y,vert_len,horz_len=None,color=(0,0,0),rotation=0,
            connected=True,fixed_brush_size=None,shittiness=1.,t_max=6.28319):
        '''
        Draws a wobbly ellipse according to the parameters.
        :param x: x coordinate of center of ellipse
        :type x: int >= 0
        :param y: y coordinate of center of ellipse (origin at top)
        :type y: int >= 0
        :param vert_len: length of axis of ellipse pointing at the
            angle indicated by rotation
        :type vert_len: non-negative float
        :param horz_len: length of axis of ellipse pointing
            perpendicular to the vertical axis
        :type horz_len: non-negative float
        :param color: the color with which to draw the ellipse
        :type color: tuple of integers between 0 and 255
        :param rotation: amount of radians to rotate the ellipse by
        :type rotation: float
        :param connected: whether the ellipse should meet with itself
            at the same slope as when it started getting drawn
        :type connected: bool
        :param fixed_brush_size: brush size to use; if not specified,
            size will be made proportional to ellipse size
        :type fixed_brush_size: int >= 1
        :param shittiness: a measure of how well-drawn the ellipse
            should be; directly proportional to amount of wobbly terms
            added; a shittiness below 1/12 results in a perfect
            ellipse
        :type shittiness: float >= 0
        :param t_max: the value that t should go up to; 2pi is a
            complete ellipse
        :type t_max: float >= 0
        '''
        if horz_len == None:
            horz_len = vert_len
        x_values = [] # each value is a tuple:
        y_values = [] # (phase, frequency, amplitude)
        x_values.append((0,
                         1,
                         horz_len-0.1+shittiness*horz_len*0.2*random.random()))
        y_values.append((-1.570796,
                         1,
                         vert_len-0.1+shittiness*vert_len*0.2*random.random()))
        # Generate the amplitudes for the random deviations:
        min_amount = 8
        max_amount = 12
        x_amount_to_append = random.randrange(min_amount,max_amount)
        y_amount_to_append = random.randrange(min_amount,max_amount)
        freqs = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
        for index in range(x_amount_to_append-1):
            rand_freq = random.choice(freqs)
            x_values.append((
                random.random()*6.28319,
                rand_freq,
                random.choice((-1,1))*\
                        shittiness*\
                        (((vert_len+horz_len)**0.82)*\
                        (0.1*random.random()+0.08)/\
                        (rand_freq**1.45))))
        for index in range(y_amount_to_append-1):
            rand_freq = random.choice(freqs)
            y_values.append((
                random.random()*6.28319,
                rand_freq,
                random.choice((-1,1))*\
                        shittiness*\
                        (((vert_len+horz_len)**0.82)*\
                        (0.1*random.random()+0.08)/\
                        (rand_freq**1.45))))
        if not connected:
            rand_freq = random.choice(freqs)
            x_values.append((
                random.random()*6.28319,
                1./rand_freq,
                random.choice((-1,1))*\
                        shittiness*\
                        (((vert_len+horz_len)**0.82)*\
                        (0.1*random.random()+0.08)/\
                        (rand_freq**1.45))))
            rand_freq = random.choice(freqs)
            y_values.append((
                random.random()*6.28319,
                1./rand_freq,
                random.choice((-1,1))*\
                        shittiness*\
                        (((vert_len+horz_len)**0.82)*\
                        (0.1*random.random()+0.08)/\
                        (rand_freq**1.45))))
        # Determine brush size:
        if fixed_brush_size != None:
            brush_size = fixed_brush_size
        else:
            brush_size = int(math.sqrt(vert_len+horz_len)/3)
        # Draw it:
        increment = 1.5/(len(x_values)+(3*(vert_len+horz_len)-\
                math.sqrt((3*vert_len+horz_len)*\
                (vert_len+3*horz_len)))) # So we don't waste time
        t = 0
        if rotation == 0:
            while t < t_max:
                self.paint(
                    int(x+reduce(
                        lambda a,b:a+b,
                        [amp*math.cos(freq*(t-phase)) for phase,freq,amp in\
                                x_values])),
                    int(y+reduce(
                        lambda a,b:a+b,
                        [amp*math.cos(freq*(t-phase)) for phase,freq,amp in\
                                y_values])),
                        color,
                        brush_size)
                t += increment
        else:
            while t < t_max:
                x_pos = reduce(
                        lambda a,b:a+b,
                        [amp*math.cos(freq*t+phase) for phase,freq,amp in\
                                x_values])
                y_pos = reduce(
                        lambda a,b:a+b,
                        [amp*math.cos(freq*t+phase) for phase,freq,amp in\
                                y_values])
                self.paint(
                        int(x+math.cos(rotation)*x_pos-\
                                math.sin(rotation)*y_pos),
                        int(y+math.sin(rotation)*x_pos+\
                                math.cos(rotation)*y_pos),
                        color,
                        brush_size)
                t += increment
    def flood_fill(self,x,y,color):
        '''
        Exactly like MS Paint bucket fill, down to the inefficiency.
        '''
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        original_color = self.get_pixel(x,y)
        if color == original_color:
            return
        stack = [(x,y)]
        while len(stack) > 0:
            pos = stack.pop()
            if self.get_pixel(*pos) != original_color:
                continue
            self.pencil(*(pos+(color,)))
            stack.append((pos[0],pos[1]-1))
            stack.append((pos[0],pos[1]+1))
            stack.append((pos[0]-1,pos[1]))
            stack.append((pos[0]+1,pos[1]))
    def line(self,x_a,y_a,x_b,y_b,color,exact=False,fixed_brush_size=1,shittiness=1.):
        '''
        Draws a line from point (x_a,y_a) to point (x_b,y_b), which
        must not be the same.
        :param x_a: The x at which the line begins
        :type x_a: float
        :param y_a: The y at which the line begins
        :type y_a: float
        :param x_b: The x at which the line ends
        :type x_b: float
        :param y_b: The y at which the line ends
        :type y_b: float
        :param exact: Whether or not to draw the line at exactly the
            points specified
        :type exact: bool
        :param fixed_brush_size: The brush size with which to draw the
            line.
        :type fixed_brush_size: int >= 1
        :param shittiness: A measure of the shittiness of the line; a
            shittiness less than 1/12 results in a straight line.
        :type shittiness: float >= 0
        '''
        if not exact:
            x_a += shittiness*(16*random.random()-8)
            y_a += shittiness*(16*random.random()-8)
            x_b += shittiness*(16*random.random()-8)
            y_b += shittiness*(16*random.random()-8)
        values = [] # each value is a tuple: (phase, frequency, amplitude,
                    #                         x component, y component)
        min_amount = 8
        max_amount = 12
        x_amount_to_append = random.randrange(min_amount,max_amount)
        y_amount_to_append = random.randrange(min_amount,max_amount)
        wlens = range(5,40)
        for index in range(x_amount_to_append-1):
            rand_wlen = random.choice(wlens)
            values.append((
                random.random()*6.28319,
                rand_wlen,
                random.choice((-1,1))*\
                        0.4*\
                        (fixed_brush_size**0.2)*\
                        shittiness*\
                        (((x_b-x_a)**2.+(y_b-y_a)**2.)**0.22)*\
                        (0.1*random.random()+0.08),
                (x_b-x_a)*(0.9+0.2*random.random()),
                (y_b-y_a)*(0.9+0.2*random.random())))
        t_max = math.sqrt((y_b-y_a)**2.+(x_b-x_a)**2.)
        increment = 1./(2.+len(values))
        t = 0.
        while t < t_max:
            x_distortion = 0
            y_distortion = 0
            for phase,wlen,amp,x_comp,y_comp in values:
                dist = math.sqrt(x_comp**2.+y_comp**2.)
                coef = amp*math.cos((t-phase)/wlen)
                x_distortion += ((y_comp-x_comp)/dist)*coef
                y_distortion += ((x_comp+y_comp)/dist)*coef
            self.paint(
                    int(x_a+(x_b-x_a)*t/t_max+x_distortion),
                    int(y_a+(y_b-y_a)*t/t_max+y_distortion),
                    color,
                    fixed_brush_size)
            t += increment
    def star(self,x,y,size,color,border_thick=0,fixed_brush_size=None,
            shittiness=1.):
        '''
        Draw a star.
        :param x: x position of center of star
        :type x: float
        :param y: y position of center of star
        :type y: float
        :param size: Radius of star
        :type size: float > 0
        :param color: Color to fill the star with
        :type color: tuple of three ints between 0 and 255 inclusive
        :param border_thick: thickness of the border to draw between
            the colors; if it is 0, no border will be drawn
        :type border_thick: int >= 0
        '''
        if not fixed_brush_size:
            fixed_brush_size = 1
        border_color = None
        if border_thick == 0:
            border_color = color
        else:
            border_color = (0,0,0)
        # The constants come from the fifth roots of unity, but
        # inverted with respect to the line y=x
        self.line(
            x,
            y-size,
            x+0.58779*size,
            y+0.80902*size,
            border_color,
            exact=True,
            fixed_brush_size=fixed_brush_size if border_thick == 0 else border_thick,
            shittiness=shittiness)
        self.line(
            x+0.58779*size,
            y+0.80902*size,
            x-0.95106*size,
            y-0.30902*size,
            border_color,
            exact=True,
            fixed_brush_size=fixed_brush_size if border_thick == 0 else border_thick,
            shittiness=shittiness)
        self.line(
            x-0.95106*size,
            y-0.30902*size,
            x+0.95106*size,
            y-0.30902*size,
            border_color,
            exact=True,
            fixed_brush_size=fixed_brush_size if border_thick == 0 else border_thick,
            shittiness=shittiness)
        self.line(
            x+0.95106*size,
            y-0.30902*size,
            x-0.58779*size,
            y+0.80902*size,
            border_color,
            exact=True,
            fixed_brush_size=fixed_brush_size if border_thick == 0 else border_thick,
            shittiness=shittiness)
        self.line(
            x-0.58779*size,
            y+0.80902*size,
            x,
            y-size,
            border_color,
            exact=True,
            fixed_brush_size=fixed_brush_size if border_thick == 0 else border_thick,
            shittiness=shittiness)
        self.flood_fill(x,y,color)
        self.flood_fill(
            x,
            y-int(size/2),
            color)
        self.flood_fill(
            x+int(0.95106*size/2),
            y-int(0.30902*size/2),
            color)
        self.flood_fill(
            x+int(0.58779*size/2),
            y+int(0.80902*size/2),
            color)
        self.flood_fill(
            x-int(0.58779*size/2),
            y+int(0.80902*size/2),
            color)
        self.flood_fill(
            x-int(0.95106*size/2),
            y-int(0.30902*size/2),
            color)

def make_eye(size,fixed_brush_size=None,pupil=None,pupil_style=None,
        shittiness=1.,style='elliptical'):
    '''
    Returns a Canvas of an eye.
    :param size: Roughly half the height of the eye
    :type size: float > 0
    :param fixed_brush_size: Brush size to use; if not specified,
        brush size will be made proportional to the parameter size
    :type fixed_brush_size: int >= 1
    :param pupil: Where to put the pupil; None makes no pupil
    :type pupil: None, or str in ('left','center','right')
    :param pupil_style: How the pupil should be drawn
    :type pupil_style: str in ('elliptical','round')
    :param shittiness: A measure of how well-drawn the eye should be;
        a shittiness of 0 gives geometric perfection
    :type shittiness: float >= 0
    :param style: How the eye should be drawn
    :type style: str in ('elliptical','round')
    '''
    final = Canvas(size*4,size*4,(-1,-1,-1))
    if style == 'elliptical':
        final.ellipse(
                size*2,
                size*2,
                size,
                size*0.7,
                fixed_brush_size=fixed_brush_size,
                shittiness=shittiness)
    elif style == 'round':
        final.ellipse(
                size*2,
                size*2,
                size*0.8,
                fixed_brush_size=fixed_brush_size,
                shittiness=shittiness)
    final.flood_fill(size*2,size*2,(255,255,255))
    if pupil:
        if not pupil_style:
            pupil_style = style
        offset = None
        if pupil == 'left':
            offset = -size//2.5
        elif pupil == 'center':
            offset = 0
        elif pupil == 'right':
            offset = size//2.5
        if pupil_style == 'elliptical':
            final.ellipse(
                    int(size*2+0.7*offset),
                    size*2,
                    size//1.6,
                    (size*0.7)//2,
                    fixed_brush_size=1,
                    shittiness=shittiness)
            final.flood_fill(
                    int(size*2+0.7*offset),
                    size*2,
                    (0,0,0))
        elif pupil_style == 'round':
            final.ellipse(
                    int(size*2+offset),
                    size*2,
                    size//2,
                    fixed_brush_size=1,
                    shittiness=shittiness)
            final.flood_fill(
                    int(size*2+offset),
                    size*2,
                    (0,0,0))
    final.crop()
    return final
def make_ball(size,colors,style,border_thick=0,eyes_style=None,eyebrows=False,
        facing='right',fixed_brush_size=None,pupil=None,pupil_style=None,
        shittiness=1.):
    '''
    Returns a Canvas of a ball.
    :param size: Roughly the radius of the ball.
    :type size: float > 0
    :param colors: the list of colors that the flag should use
    :type color: tuple of tuples of three ints between 0 and 255
        inclusive
    :param style: The style of the flag of the ball:
        'bicolor_horz': two colors, horizontally
        'bicolor_vert': two colors, vertically
        'tricolor_horz': three colors, horizontally
        'tricolor_vert': three colors, vertically
        'cross-ortho': centered orthogonal cross (e.g. England)
        'cross-diag': centered diagonal cross (e.g. Scotland)
        'circle': solid circle in the middle
        'star': solid star in the middle
        'china': China's flag pattern
        'muslim': crescent and star in the middle
    :param border_thick: thickness of the border to draw between the
        colors; if it is 0, no border will be drawn
    :type border_thick: int >= 0
    :param connected: whether the outline of the ball should meet with
        itself at the same slope as when it started getting drawn
    :type connected: bool
    :param eyebrows: Whether or not the ball has eyebrows
    :type eyebrows: bool
    :param eyes_style: How to draw the eyes
    :type eyes_style: str in ('elliptical','round')
    :param facing: Which way the ball is facing
    :type facing: str in ('left','center','right')
    :param fixed_brush_size: brush size to use; if not specified,
        brush size will be made proportional to the parameter size
    :type fixed_brush_size: int >= 1
    :param pupil: Whether or not the ball has pupils
    :type pupil: None, or str in ('left','center','right')
    :param shittiness: A measure of how well-drawn the ball is; a
        shittiness of 0 gives a geometrically perfect ball
    '''

    def frac(val,a,b):
        return (a*val)//b

    final = Canvas(int(size*4),int(size*4),(-3,-3,-3))
    final.ellipse(
            size*2,
            size*2,
            size,
            size,
            color=(0,0,0),
            fixed_brush_size=fixed_brush_size,
            shittiness=shittiness)
    final.flood_fill(size*2,size*2,(-1,-1,-1))
    final.crop()
    pattern = Canvas(final.height,final.width,(-1,-1,-1))
    width   = pattern.width
    height  = pattern.height
    if style == 'bicolor_horz':
        border_color = None
        if border_thick == 0:
            border_color = colors[0]
        else:
            border_color = (0,0,0)
        pattern.line(
                -10,
                frac(height,1,2),
                width+10,
                frac(height,1,2),
                border_color,
                fixed_brush_size=1 if border_thick == 0 else border_thick,
                shittiness=shittiness)
        pattern.flood_fill(frac(width,1,2),frac(height,1,4),colors[0])
        pattern.flood_fill(frac(width,1,2),frac(height,3,4),colors[1])
    elif style == 'bicolor_vert':
        border_color = None
        if border_thick == 0:
            border_color = colors[0]
        else:
            border_color = (0,0,0)
        pattern.line(
                frac(width,1,2),
                -10,
                frac(width,1,2),
                height+10,
                border_color,
                fixed_brush_size=1 if border_thick == 0 else border_thick,
                shittiness=shittiness)
        pattern.flood_fill(frac(width,1,4),frac(height,1,2),colors[0])
        pattern.flood_fill(frac(width,3,4),frac(height,1,2),colors[1])
    elif style == 'tricolor_horz':
        border_color = None
        if border_thick == 0:
            border_color = colors[0]
        else:
            border_color = (0,0,0)
        pattern.line(
                -10,
                frac(height,1,3),
                width+10,
                frac(height,1,3),
                border_color,
                fixed_brush_size=1 if border_thick == 0 else border_thick,
                shittiness=shittiness)
        border_color = None
        if border_thick == 0:
            border_color = colors[1]
        else:
            border_color = (0,0,0)
        pattern.line(
                -10,
                frac(height,2,3),
                width+10,
                frac(height,2,3),
                border_color,
                fixed_brush_size=1 if border_thick == 0 else border_thick,
                shittiness=shittiness)
        pattern.flood_fill(frac(width,1,2),frac(height,1,6),colors[0])
        pattern.flood_fill(frac(width,1,2),frac(height,1,2),colors[1])
        pattern.flood_fill(frac(width,1,2),frac(height,5,6),colors[2])
    elif style == 'tricolor_vert':
        border_color = None
        if border_thick == 0:
            border_color = colors[0]
        else:
            border_color = (0,0,0)
        pattern.line(
                frac(width,1,3),
                -10,
                frac(width,1,3),
                height+10,
                border_color,
                fixed_brush_size=1 if border_thick == 0 else border_thick,
                shittiness=shittiness)
        color = None
        if border_thick == 0:
            border_color = colors[1]
        else:
            color = (0,0,0)
        pattern.line(
                frac(width,2,3),
                -10,
                frac(width,2,3),
                height+10,
                border_color,
                fixed_brush_size=1 if border_thick == 0 else border_thick,
                shittiness=shittiness)
        pattern.flood_fill(frac(width,1,6),frac(height,1,2),colors[0])
        pattern.flood_fill(frac(width,1,2),frac(height,1,2),colors[1])
        pattern.flood_fill(frac(width,5,6),frac(height,1,2),colors[2])
    elif style == 'cross_ortho':
        border_color = None
        if border_thick == 0:
            border_color = colors[1]
        else:
            border_color = (0,0,0)
        pattern.flood_fill(frac(width,1,2),frac(height,1,2),colors[0])
        pattern.line(
            frac(width,3,7),
            -20,
            frac(width,3,7),
            height+20,
            border_color,
            fixed_brush_size=1 if border_thick == 0 else border_thick,
            shittiness=shittiness)
        pattern.line(
            frac(width,4,7),
            -20,
            frac(width,4,7),
            height+20,
            border_color,
            fixed_brush_size=1 if border_thick == 0 else border_thick,
            shittiness=shittiness)
        pattern.flood_fill(frac(width,1,2),frac(height,1,2),colors[1])
        pattern.line(
            -20,
            frac(height,3,7),
            width+20,
            frac(height,3,7),
            border_color,
            fixed_brush_size=1 if border_thick == 0 else border_thick,
            shittiness=shittiness)
        pattern.line(
            -20,
            frac(height,4,7),
            pattern.width+20,
            frac(height,4,7),
            border_color,
            fixed_brush_size=1 if border_thick == 0 else border_thick,
            shittiness=shittiness)
        pattern.flood_fill(frac(width,1,14),frac(height,1,2),colors[1])
        pattern.flood_fill(frac(width,13,14),frac(height,1,2),colors[1])
    elif style == 'cross_diag':
        border_color = None
        if border_thick == 0:
            border_color = colors[1]
        else:
            border_color = (0,0,0)
        pattern.line(
            0.,
            -frac(height,1,7),
            frac(width,8,7),
            height,
            border_color,
            fixed_brush_size=1 if border_thick == 0 else border_thick,
            shittiness=shittiness)
        pattern.line(
            -frac(width,1,7),
            0.,
            width,
            frac(height,8,7),
            border_color,
            fixed_brush_size=1 if border_thick == 0 else border_thick,
            shittiness=shittiness)
        pattern.flood_fill(frac(width,1,2),frac(height,1,2),colors[1])
        pattern.line(
            -frac(width,1,7),
            height,
            width,
            -frac(height,1,7),
            border_color,
            fixed_brush_size=1 if border_thick == 0 else border_thick,
            shittiness=shittiness)
        pattern.line(
            0.,
            frac(height,8,7),
            frac(width,8,7),
            0.,
            border_color,
            fixed_brush_size=1 if border_thick == 0 else border_thick,
            shittiness=shittiness)
        pattern.flood_fill(frac(width,1,14),frac(height,13,14),colors[1])
        pattern.flood_fill(frac(width,13,14),frac(height,1,14),colors[1])
        pattern.flood_fill(frac(width,1,2),frac(height,1,14),colors[0])
        pattern.flood_fill(frac(width,13,14),frac(height,1,2),colors[0])
        pattern.flood_fill(frac(width,1,2),frac(height,13,14),colors[0])
        pattern.flood_fill(frac(width,1,14),frac(height,1,2),colors[0])
    elif style == 'circle':
        border_color = None
        if border_thick == 0:
            border_color = colors[1]
        else:
            border_color = (0,0,0)
        pattern.flood_fill(frac(width,1,2),frac(height,1,2),colors[0])
        pattern.ellipse(
            frac(width,1,2),
            frac(height,1,2),
            frac(width,1,5),
            color=border_color,
            fixed_brush_size=1 if border_thick == 0 else border_thick,
            shittiness=shittiness)
        pattern.flood_fill(frac(width,1,2),frac(height,1,2),colors[1])
    elif style == 'star':
        border_color = None
        if border_thick == 0:
            border_color = colors[1]
        else:
            border_color = (0,0,0)
        pattern.flood_fill(frac(width,1,2),frac(height,1,2),colors[0])
        pattern.star(
            frac(width,1,2),
            frac(height,1,2),
            frac(width,1,5),
            colors[1],
            border_thick=border_thick,
            shittiness=shittiness)
    elif style == 'china':
        pattern.flood_fill(frac(width,1,2),frac(height,1,2),colors[0])
        pattern.star(
            frac(width,1,4),
            frac(height,3,10),
            height/8,
            colors[1],
            border_thick=border_thick,
            shittiness=shittiness)
        pattern.star(
            frac(width,2,5),
            frac(height,1,8),
            height/22,
            colors[1],
            border_thick=border_thick,
            shittiness=shittiness)
        pattern.star(
            frac(width,4,9),
            frac(height,5,24),
            height/22,
            colors[1],
            border_thick=border_thick,
            shittiness=shittiness)
        pattern.star(
            frac(width,4,9),
            frac(height,7,24),
            height/22,
            colors[1],
            border_thick=border_thick,
            shittiness=shittiness)
        pattern.star(
            frac(width,2,5),
            frac(height,3,8),
            height/22,
            colors[1],
            border_thick=border_thick,
            shittiness=shittiness)
    elif style == 'muslim':
        pattern.flood_fill(frac(width,1,2),frac(height,1,2),colors[0])
        # Draw the crescent
        pattern.ellipse(
            frac(width,3,7),
            frac(height,1,2),
            frac(height,1,5),
            color=colors[1],
            shittiness=shittiness)
        pattern.flood_fill(frac(width,3,7),frac(height,1,2),colors[1])
        pattern.ellipse(
            frac(width,4,7),
            frac(height,1,2),
            frac(height,1,5),
            frac(height,1,6),
            color=colors[0],
            shittiness=shittiness)
        pattern.flood_fill(frac(width,4,7),frac(height,1,2),colors[0])
        # Draw the star
        pattern.star(
            frac(width,2,3),
            frac(height,1,2),
            height/8,
            colors[1],
            border_thick=border_thick,
            shittiness=shittiness)
    elif style == 'nazi':
        border_color = None
        if border_thick == 0:
            border_color = colors[1]
        else:
            border_color = (0,0,0)
        pattern.flood_fill(frac(width,1,2),frac(height,1,2),colors[0])
        # Draw the circle in the center
        pattern.ellipse(
            frac(width,1,2),
            frac(height,1,2),
            frac(width,1,5),
            color=border_color,
            fixed_brush_size=1 if border_thick == 0 else border_thick,
            shittiness=shittiness)
        pattern.flood_fill(frac(width,1,2),frac(height,1,2),colors[1])
        # Draw the swastika
        pattern.line(
            frac(width,1,2)-frac(width,1,10),
            frac(height,1,2)-frac(height,1,10),
            frac(width,1,2)+frac(width,1,10),
            frac(height,1,2)+frac(height,1,10),
            colors[2],
            exact=True,
            fixed_brush_size=(5,border_thick)[3<border_thick], # max
            shittiness=shittiness)
        pattern.line(
            frac(width,1,2)+frac(width,1,10),
            frac(height,1,2)-frac(height,1,10),
            frac(width,1,2)-frac(width,1,10),
            frac(height,1,2)+frac(height,1,10),
            colors[2],
            exact=True,
            fixed_brush_size=(5,border_thick)[3<border_thick], # max
            shittiness=shittiness)
        pattern.line(
            frac(width,1,2)-frac(width,1,10),
            frac(height,1,2)-frac(height,1,10),
            frac(width,1,2),
            frac(height,1,2)-frac(height,1,5),
            colors[2],
            exact=True,
            fixed_brush_size=(5,border_thick)[3<border_thick], # max
            shittiness=shittiness)
        pattern.line(
            frac(width,1,2)+frac(width,1,10),
            frac(height,1,2)-frac(height,1,10),
            frac(width,1,2)+frac(width,1,5),
            frac(height,1,2),
            colors[2],
            exact=True,
            fixed_brush_size=(5,border_thick)[3<border_thick], # max
            shittiness=shittiness)
        pattern.line(
            frac(width,1,2)+frac(width,1,10),
            frac(height,1,2)+frac(height,1,10),
            frac(width,1,2),
            frac(height,1,2)+frac(height,1,5),
            colors[2],
            exact=True,
            fixed_brush_size=(5,border_thick)[3<border_thick], # max
            shittiness=shittiness)
        pattern.line(
            frac(width,1,2)-frac(width,1,10),
            frac(height,1,2)+frac(height,1,10),
            frac(width,1,2)-frac(width,1,5),
            frac(height,1,2),
            colors[2],
            exact=True,
            fixed_brush_size=(5,border_thick)[3<border_thick], # max
            shittiness=shittiness)
    final.merge_down(pattern)
    final.replace_color((-3,-3,-3),(-1,-1,-1))
    if facing == 'left':
        final.merge_up(
                make_eye(
                    frac(height,2,17),
                    pupil=pupil,
                    pupil_style=pupil_style,
                    shittiness=shittiness,
                    style=eyes_style),
                frac(width,1,10),
                frac(height,2,7))
        final.merge_up(
                make_eye(
                    frac(height,1,9),
                    pupil=pupil,
                    pupil_style=pupil_style,
                    shittiness=shittiness,
                    style=eyes_style),
                frac(width,3,10),
                frac(height,1,3))
    elif facing == 'center':
        final.merge_up(
                make_eye(
                    frac(height,1,9),
                    pupil=pupil,
                    pupil_style=pupil_style,
                    shittiness=shittiness,
                    style=eyes_style),
                frac(width,3,9),
                frac(height,2,7))
        final.merge_up(
                make_eye(
                    frac(height,1,9),
                    pupil=pupil,
                    pupil_style=pupil_style,
                    shittiness=shittiness,
                    style=eyes_style),
                frac(width,5,9),
                frac(height,2,7))
    elif facing == 'right':
        final.merge_up(
                make_eye(
                    frac(height,1,9),
                    pupil=pupil,
                    pupil_style=pupil_style,
                    shittiness=shittiness,
                    style=eyes_style),
                frac(width,4,5),
                frac(height,2,7))
        final.merge_up(
                make_eye(
                    frac(height,2,17),
                    pupil=pupil,
                    pupil_style=pupil_style,
                    shittiness=shittiness,
                    style=eyes_style),
                frac(width,3,5),
                frac(height,1,3))
    return final

### MAKE AND SAVE COMIC ###
if os.path.isfile('comic.png'):
    os.remove('comic.png')
panel_amount = random.randrange(1,10)+random.randrange(3)+random.randrange(2)
artist = Artist()
potential_characters = ['france','germany','italy','sweden','denmark','russia',
                        'nazi-germany']
if artist.geo_knowledge in ('europe-irrelevant','asia-relevant'):
    potential_characters.extend(
        ['austria','romania','hungary','poland','belgium','finland'])
if artist.geo_knowledge in ('asia-relevant'):
    potential_characters.extend(
        ['china','japan','turkey','indonesia','pakistan','vietnam','yemen'])
    # pretend Yemen is Egypt
# I could also do Bangladesh and Palau, but nobody knows about those
characters = []
for index in range(random.randrange(2,7)):
    if random.random() < 0.6 or 'sweden' in characters:
        selected = random.randrange(len(potential_characters))
        characters.append(potential_characters[selected])
        del potential_characters[selected]
    else:
        characters.append('sweden')
for panel_count in range(panel_amount):
    panel_characters = []
    for char_count in range(random.randrange(2,5)):
        selected = random.randrange(len(characters))
        panel_characters.append(characters[selected])
        del characters[selected]
    characters.extend(panel_characters)
    # oh shit i forgot i was in the middle of something, sorry guys this is
    # going to look a lot lamer than i anticipated
    panel = Canvas(600,900,palette['white'])
    character = panel_characters[0]
    country_colors = \
    {'france':(palette['blue'],palette['white'],palette['red']),
     'germany':(palette['black'],palette['red'],palette['yellow']),
     'italy':(palette['green'],palette['white'],palette['red']),
     'sweden':(palette['blue'],palette['yellow'],palette['blue']),
     'denmark':(palette['red'],palette['white'],palette['red']),
     'russia':(palette['white'],palette['blue'],palette['red']),
     'nazi-germany':(palette['red'],palette['white'],palette['black']),
     'austria':(palette['red'],palette['white'],palette['red']),
     'romania':(palette['blue'],palette['yellow'],palette['red']),
     'hungary':(palette['red'],palette['white'],palette['green']),
     'poland':(palette['red'],palette['white'],palette['red']),
     'belgium':(palette['black'],palette['yellow'],palette['red']),
     'finland':(palette['white'],palette['blue'],palette['white']),
     'china':(palette['red'],palette['yellow'],palette['red']),
     'japan':(palette['white'],palette['red'],palette['white']),
     'turkey':(palette['red'],palette['white'],palette['red']),
     'indonesia':(palette['red'],palette['white'],palette['red']),
     'pakistan':(palette['green'],palette['white'],palette['green']),
     'vietnam':(palette['red'],palette['yellow'],palette['red']),
     'yemen':(palette['red'],palette['white'],palette['black'])}
    country_shapes = \
    {'france':'tricolor_vert',
     'germany':'tricolor_horz',
     'italy':'tricolor_vert',
     'sweden':'cross_ortho',
     'denmark':'cross_ortho',
     'russia':'tricolor_horz',
     'nazi-germany':'nazi',
     'austria':'tricolor_horz',
     'romania':'tricolor_vert',
     'hungary':'tricolor_horz',
     'poland':'bicolor_horz',
     'belgium':'tricolor_vert',
     'finland':'cross_ortho',
     'china':'china',
     'japan':'circle',
     'turkey':'muslim',
     'indonesia':'bicolor_horz',
     'pakistan':'muslim',
     'vietnam':'star',
     'yemen':'tricolor_horz'}
    color = country_colors[character]
    shape = country_shapes[character]
    if character == 'poland' and artist.poland_style in ('wrong','random'):
        if artist.poland_style == 'wrong' or random.random() > 0.5:
            color = (palette['white'],palette['red'],palette['white'])
    if artist.idiot:
        color = list(color)
        random.shuffle(color)
    if character == 'sweden' and random.random() > 0.8:
        shape = random.choice(('nazi','muslim'))
    panel.merge_up(
        make_ball(
            100,
            color,
            shape,
            border_thick=artist.border_thick,
            eyes_style=artist.eyes_style,
            facing=random.choice(('left','center','right')),
            pupil=(None if artist.pupil_style == 'none' else 'center'),
            shittiness=artist.shittiness),
        disp_x=350,
        disp_y=200)
    # Save the panel:
    if os.path.isfile('comic.png'):
        # Why do I even care about memory usage? I have sixteen gigs of ram
        comic_png = Image.open('comic.png')
        panel_png = Image.fromarray(
                np.uint8(
                    np.reshape(
                        panel.get_drawable(),
                        (panel.height,panel.width,3))))
        final_width,final_height = comic_png.size
        final_height += panel_png.size[1]
        final_png = Image.new('RGB',(final_width,final_height))
        final_png.paste(comic_png,(0,0))
        final_png.paste(panel_png,(0,comic_png.size[1]))
        final_png.save('comic.png')
    else:
        panel_png = Image.fromarray(
                np.uint8(
                    np.reshape(
                        panel.get_drawable(),
                        (panel.height,panel.width,3)))).save('comic.png')
