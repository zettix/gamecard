#!/usr/bin/python2
# vim:sm:ai:et:syntax=python:ts=2:

import sys
import math
import Image
import ImageFont, ImageDraw

class NameBox(object):
  def __init__(self,
       fontscale=10,
       font='',
       yoff=0,
       bg=(0, 0, 0),
       text='',
       xborder=10,
       yborder=10,
       shandler=0):

    self.namestring = text
    if shandler > 0:
      self.namestring = '\n'.join(text.split(' '))
    self.shandler = shandler
    fontfile = font
    self.font = ImageFont.truetype(fontfile, fontscale)
    self.bias = 1.00
    self.xborder = xborder
    self.yborder = yborder
    self.foreground_color = (0, 0, 0)
    self.background_color = bg


  def fontbox(self):
    "Draw self.string in an image buffer with boarders. Return image handle"
    #im = Image.new("RGB", (600, 200))
    doggies = self.namestring.split("\n");
    f_width = 0
    f_height = 0
    for dog in doggies:
      t_w, t_h = self.font.getsize(dog)
      if f_width < t_w:
        f_width = t_w
      f_height += t_h
      
    # f_width, f_height = self.name_width_height()
    height = int(f_height * self.bias)
    width =  f_width + self.xborder * 2
    height += self.yborder * 2
    newline_count = 0
    #for c in self.namestring:
    #  if c == "\n":
    #    newline_count += 1
    #height += int(f_height * self.bias) * newline_count
    im = Image.new("RGB", (width, height), self.background_color)
    draw = ImageDraw.Draw(im)
    #draw.text((10, 25), "world", font=font)
    draw.text((self.xborder, self.yborder + int(height * (self.bias - 1.0))),
               self.namestring, font=self.font, fill=self.foreground_color)
    return im

  def name_width_height(self):
    return self.font.getsize(self.namestring)


class Frame(object):
  def __init__(self, x_thick=29, y_thick=30):
    self.x_size = 300
    self.y_size = 200
    self.x_thick = x_thick
    self.y_thick = y_thick
    self.mask_background = 0
    self.foreground_color = (0, 0, 0)
    self.background_color = (0, 0, 0)
    self.f_type = 'edge'

  def LoadBackgroundImage(self):
    #self.back_im = Image.open('wood_640x480.jpg')
    self.back_im = Image.open('wood-bw.png')

  def ColorFunc(self, x, max_x):
    """f(x, max_x) -> (0, 256) using sin/triangular/sin^4 interpolation"""
    interp = float(x) / max_x
    f1 = 1.0
    if self.f_type == 'sin':
      f1 = math.sin(math.pi * interp)
    elif self.f_type == 'tri':
      if interp > 0.5:
        f1 = (1.0 - interp) * 2.0
      else:
        f1 = interp * 2.0
    elif self.f_type == 'edge':
      f1 = math.sin(math.pi * interp)
      f1 = f1 ** 4
    if f1 > 1.0:
      f1 = 1.0
    linecolor = int(f1 * 256)
    return linecolor

  def DrawFrame(self):
    mask = Image.new("L", (self.x_size, self.y_size), self.mask_background)
    frame_output = Image.new("RGB", (self.x_size, self.y_size), self.background_color)
    mask_draw = ImageDraw.Draw(mask)
    slope = float(self.y_thick) / self.x_thick
    for x in range(self.x_thick):
      # Auto Bevel using (x, x)
      linecolor = self.ColorFunc(x, self.x_thick)
      clist = [ (x, x * slope), (x, self.y_size - x * slope)]
      mask_draw.line(clist, fill=linecolor)
      clist = [ (self.x_size - x, x * slope), (self.x_size - x, self.y_size - x * slope)]
      mask_draw.line(clist, fill=linecolor)
    for y in range(self.y_thick):
      linecolor = self.ColorFunc(y, self.y_thick)
      clist = [ (y / slope, y), (self.x_size - y / slope, y)]
      mask_draw.line(clist, fill=linecolor)
      clist = [ (y / slope, self.y_size - y), (self.x_size - y / slope, self.y_size - y)]
      mask_draw.line(clist, fill=linecolor)
    # FIXME(Sean): repeat instead of crop
    #mask_input_im = self.back_im.crop((0, 0, self.x_size, self.y_size))
    mask_input_im = Image.new("RGB", (self.x_size, self.y_size), self.background_color)
    mask_input_im.paste(self.back_im.resize((self.x_size,self.y_size)), (0,0))
    im_out = Image.composite(mask_input_im, frame_output, mask)

    #return mask
    return im_out

class NameFrame(object):
  def __init__(self,
       fontscale=10,
       font='',
       yoff=0,
       bg=(0, 0, 0),
       text='',
       xborder=10,
       yborder=10,
       shandler=0):
    self.namebox = NameBox(
       fontscale=fontscale,
       font=font,
       yoff=yoff,
       bg=bg,
       text=text,
       xborder=xborder,
       yborder=yborder,
       shandler=shandler)

  def render(self):
    "Compose string image, background image, and frame.  Return image handle"
    name_image = self.namebox.fontbox()
    nx, ny = name_image.size
    self.frame = Frame(x_thick=self.namebox.xborder, y_thick=self.namebox.yborder)
    self.frame.LoadBackgroundImage()
    self.frame.x_size = nx + 2 * self.frame.x_thick
    self.frame.y_size = ny + 2 * self.frame.y_thick
    frame_image = self.frame.DrawFrame()
    frame_image.paste(name_image, (self.frame.x_thick, self.frame.y_thick))
    return frame_image
