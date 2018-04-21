#!/usr/bin/python2
# vim:sm:ai:et:syntax=python:ts=2:
# Copyright 2018 Sean Brennan
# Licensed under the Apache License, Version 2.0

import sys
import math
import Image
import ImageFont, ImageDraw
import pilfont

"""Card has:
/---------\
|  name   |
|         |
|  art    |
|         |
| color   |
| text    |
|         |
| list    |
\---------/
"""

class CardInit(object):
  def __init__(self, paramsdict):
    """Old:
      namestring='', art='tmp_art.png', color_text='', item_list=None, fontscale=60, bg=None):
    """
    self.namestring = paramsdict["title"]["Title 4 Text"][3]
    self.color_text = paramsdict["body"]["Body 4 Text"][3]
    self.item_list = paramsdict["footer"]["Footer 4 Text"][3]

    self.name_fontscale = int(paramsdict["title"]["Title 6 font size"][3])
    self.color_fontscale = int(paramsdict["body"]["Body 6 font size"][3])
    self.item_fontscale = int(paramsdict["footer"]["Footer 6 font size"][3])

    self.name_font = paramsdict["title"]["Title 5 font"][3]
    self.color_font = paramsdict["body"]["Body 5 font"][3]
    self.item_font = paramsdict["footer"]["Footer 5 font"][3]

    self.yes_namestring = int(paramsdict["title"]["Title 0 present"][3])
    self.yes_color_text = int(paramsdict["body"]["Body 0 present"][3])
    self.yes_item_list = int(paramsdict["footer"]["Footer 0 present"][3])

    self.name_y_offset = float(paramsdict["title"]["Title 99 y offset"][3])
    self.color_y_offset = float(paramsdict["body"]["Body 99 y offset"][3])
    self.item_y_offset = float(paramsdict["footer"]["Footer 99 y offset"][3])

    #self.art = paramsdict[""]["Image 3 image"]

    self.width = int(paramsdict["card"]["Card 4 resolution"][3])
    self.height =  int(paramsdict["card"]["Card 5 resolution"][3])
    self.center = int(self.width / 2)
    cred = int(paramsdict["card"]["Card 1 Red background"][3])
    cgreen = int(paramsdict["card"]["Card 2 Green background"][3])
    cblue = int(paramsdict["card"]["Card 3 Blue background"][3])
    self.background_color = (cred, cgreen, cblue)
    self.cthick = int(paramsdict["card"]["Card 8 border thickness"][3])

     
    if self.yes_namestring:
      self.xborder = int(paramsdict["title"]["Title 8 boarder size"][3])
      self.yborder = int(paramsdict["title"]["Title 8 boarder size"][3])
      red = int(paramsdict["title"]["Title 1 X Red background"][3])
      green = int(paramsdict["title"]["Title 2 X Green background"][3])
      blue = int(paramsdict["title"]["Title 3 X Blue background"][3])
      self.name_background = (red, green, blue)
      self.name_shandler = int(paramsdict["title"]["Title 7 space handling"][3])

  def fontbox(self):
    "Draw self.string in an image buffer with boarders. Return image handle"
    #im = Image.new("RGB", (600, 200))
    im = Image.new("RGB", (self.width, self.height), self.background_color)
    return im

class GenCard(object):
  def __init__(self, paramsdict):
    self.paramsdict = paramsdict
    self.namebox = CardInit(paramsdict)

  def save(self, path):
    im = self.render()
    im.save(path, 'PNG')


  def boxy(self, l, sz=30):
    idx = 0
    maxl = len(l)
    res = []
    nexy = l.find(' ', sz)
    while (nexy != -1):
      res.append(l[idx:nexy])
      idx = nexy + 1
      nexy = l.find(' ', sz + idx)
    res.append(l[idx:])
    return '\n'.join(res)


  def render(self):
    "Compose string image, background image, and frame.  Return image handle"
    # card
    nx, ny = self.namebox.width, self.namebox.height
    self.frame = pilfont.Frame(x_thick=self.namebox.cthick, y_thick=self.namebox.cthick)
    self.frame.LoadBackgroundImage()
    self.frame.x_size = nx  # + 2 * self.frame.x_thick
    self.frame.y_size = ny  # + 2 * self.frame.y_thick
    frame_image = self.frame.DrawFrame()
    newx = nx - self.frame.x_thick * 2
    newy = ny - self.frame.y_thick * 2
    im = Image.new("RGB", (newx, newy), self.namebox.background_color)
    frame_image.paste(im, (self.frame.x_thick, self.frame.y_thick))

    # name
    if self.namebox.yes_namestring > 0:
      nn = pilfont.NameFrame(
         fontscale=self.namebox.name_fontscale,
         font=self.namebox.name_font,
         bg=self.namebox.name_background,
         text=self.namebox.namestring,
         xborder=int(self.paramsdict["title"]["Title 8 boarder size"][3]),
         yborder=int(self.paramsdict["title"]["Title 8 boarder size"][3]),
         shandler=self.namebox.name_shandler)
      yoff = self.namebox.name_y_offset
      im = nn.render()
      nn_x, nn_y = im.size
      frame_image.paste(im, (int(self.namebox.center - nn_x / 2), int(yoff * self.namebox.height))) 


    # color text
    if self.namebox.yes_color_text > 0:
      bbg = (int(self.paramsdict["body"]["Body 1 X Red background"][3]),
             int(self.paramsdict["body"]["Body 2 X Green background"][3]),
             int(self.paramsdict["body"]["Body 3 X Blue background"][3]))
      nn = pilfont.NameFrame(
         fontscale=self.namebox.color_fontscale,
         font=self.namebox.color_font,
         bg=bbg,
         text=self.boxy(self.paramsdict["body"]["Body 4 Text"][3]),
         xborder=int(self.paramsdict["body"]["Body 8 boarder size"][3]),
         yborder=int(self.paramsdict["body"]["Body 8 boarder size"][3]),
         shandler=0)
      yoff = self.namebox.color_y_offset
      im = nn.render()
      nn_x, nn_y = im.size
      frame_image.paste(im, (int(self.namebox.center - nn_x / 2), int(yoff * self.namebox.height))) 

    # list
    if self.namebox.yes_item_list > 0:
      bbg = (int(self.paramsdict["footer"]["Footer 1 X Red background"][3]),
             int(self.paramsdict["footer"]["Footer 2 X Green background"][3]),
             int(self.paramsdict["footer"]["Footer 3 X Blue background"][3]))
      nn = pilfont.NameFrame(
         fontscale=self.namebox.item_fontscale,
         font=self.namebox.item_font,
         bg=bbg,
         text=self.paramsdict["footer"]["Footer 4 Text"][3],
         xborder=int(self.paramsdict["footer"]["Footer 8 boarder size"][3]),
         yborder=int(self.paramsdict["footer"]["Footer 8 boarder size"][3]),
         shandler=0)
      im = nn.render()
      nn_x, nn_y = im.size
      yoff = self.namebox.item_y_offset
      frame_image.paste(im, (int(self.namebox.center - nn_x / 2), int(yoff * self.namebox.height))) 

    return frame_image
