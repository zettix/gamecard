#!/usr/bin/python
# vim:sm:ai:et:syntax=python:ts=2:
# Copyright 2018 Sean Brennan
# Licensed under the Apache License, Version 2.0

import os
import sys
import subprocess
import cgi
import glob
import pilcard
import time

DEBUG = 0
webform = cgi.FieldStorage() # instantiate only once!
class T:
  NUM = 1
  IMAGE = 2
  TEXT = 3 
  FONT = 4
  BOOL = 5
  AREA = 6
  FLOAT = 7

class WebParams:
  def __init__(self):
   # truetype fonts in say, /usr/lib/cgi-bin/ or wherever they can be loaded.
   #  Be aware of default fonts below.
   #[
   #  ("RIKY2vamp.ttf", "Scary, Caligraphic"),
   #  ("DejaVuSans-Bold.ttf", "Basic sans bold normal"),
   #  ("AbductionII.ttf", "wide. hi tech"),
   #  ("CelesteNormal.ttf", "whispy cursive."),
   #  ("CelticNormal.ttf",  "calligraphic wide"),
   #]
   self.webparamsdict = {
     "card": {
      "Card 1 Red background": ["Card R background", T.NUM, 200],
      "Card 2 Green background": ["Card G background", T.NUM, 64],
      "Card 3 Blue background": ["Card B background", T.NUM, 64],
      "Card 4 resolution": ["Card X resolution", T.NUM, 2500],   # 250 * 3
      "Card 5 resolution": ["Card Y resolution", T.NUM, 3500],   # 350 * 3
      #"Card 6 aspect ratio": ["Card aspect ratio", T.NUM],
      #"Card 7 border image": ["Card border image", T.IMAGE],
      "Card 8 border thickness": ["Card border thickness", T.NUM, 10],
     },
     "title": {
      "Title 1 X Red background": ["Title R background", T.NUM, 188],  # 188
      "Title 2 X Green background": ["Title G background", T.NUM, 89], # 89
      "Title 3 X Blue background": ["Title B background", T.NUM, 1],  # 1
      "Title 4 Text": ["Title Text", T.TEXT, "Organized rats."],
      "Title 5 font": ["Title font", T.FONT, "RIKY2vamp.ttf"],
      "Title 6 font size": ["Title font size", T.NUM, 360],             # 60
      "Title 7 space handling": ["Space to newline?", T.BOOL, 1],   # true
      "Title 8 boarder size": ["Title boarder size", T.NUM, 10],       # 50
      #"Title 9 boarder image": ["Title boarder image", T.IMAGE],
      "Title 0 present": ["Title present", T.BOOL, 1],               # true
      "Title 99 y offset": ["Title y offset", T.FLOAT, 0.05],              # 
     },
     "body": {
      "Body 1 X Red background": ["Body R background", T.NUM, 188],
      "Body 2 X Green background": ["Body G background", T.NUM, 89],
      "Body 3 X Blue background": ["Body B background", T.NUM, 1],
      "Body 4 Text": ["Body Text", T.AREA, """A single rat stood in the center of this room, glaring at the party as they entered.  It tapped it's little paw upon the floor in a most menacing way, then two more rats appeared.  They too tapped their little paws and four more rats appeared.  In a few seconds they were surrounded by hungry, organized rats."""],
      "Body 5 font": ["Body font", T.FONT, "RIKY2vamp.ttf"],
      "Body 6 font size": ["Body font size", T.NUM, 120],
      #"Body 7 space handling": ["Body space handling", T.NUM],
      "Body 8 boarder size": ["Body boarder size", T.NUM, 10],
      #"Body 9 boarder image": ["Body boarder image", T.IMAGE],
      "Body 0 present": ["Body present", T.BOOL, 1],
      "Body 99 y offset": ["Body y offset", T.FLOAT, 0.5],
     },
     "footer": {
      "Footer 1 X Red background": ["Footer R background", T.NUM, 188],
      "Footer 2 X Green background": ["Footer G background", T.NUM, 89],
      "Footer 3 X Blue background": ["Footer B background", T.NUM, 1],
      "Footer 4 Text": ["Footer Text", T.AREA, "0 2/0 3"],
      "Footer 5 font": ["Footer font", T.FONT, "RIKY2vamp.ttf"],
      "Footer 6 font size": ["Footer font size", T.NUM, 132],
      #"Footer 7 space handling": ["Footer space handling", T.NUM],
      "Footer 8 boarder size": ["Footer boarder size", T.NUM, 10],
      #"Footer 9 boarder image": ["Footer boarder image", T.IMAGE],
      "Footer 0 present": ["Footer present", T.BOOL, 1],
      "Footer 99 y offset": ["Footer y offset", T.FLOAT, 0.9],
     },
     #"image": {
     # "Image 1 boarder size": ["Image boarder size", T.NUM],
     # "Image 2 boarder image": ["Image boarder image", T.IMAGE],
     # "Image 3 image": ["Image image", T.IMAGE],
     # "Image 4 present": ["Image present", T.BOOL],
     # "Image 5 y offset": ["Image y offset", T.FLOAT],
     #}
    }
   self.fonts = self.LoadFonts()
   
  def LoadFonts(self):
    result = []
    # a line of the font file is
    # path, desc
    # so a comma cannot be in the font path.
    fontfile = '/usr/lib/cgi-bin/cardfonts.txt'
    with open(fontfile, 'r') as fd:
      lines = [x.strip() for x in fd.readlines() if x]
      for l in lines:
        stuff = l.split(',')
        fontname = stuff[0]
        fontdesc = ''
        if len(stuff) > 1:
          fontdesc = ','.join(stuff[1:])
        result.append((fontname, fontdesc))
    return result


  # Load params from a form submission.
  def LoadParams(self, paramob):
    k = self.webparamsdict.keys()
    k.sort()
    for ak in k:
      k2 = self.webparamsdict[ak].keys()
      k2.sort()
      for ak2 in k2:
        keyname = self.webparamsdict[ak][ak2][0]  # string
        keytype = self.webparamsdict[ak][ak2][1]  # T type
        keydefault = self.webparamsdict[ak][ak2][2]  # default
        if (T.NUM == keytype) or (T.BOOL == keytype):
          webvalue = paramob.getfirst(keyname, keydefault)
          self.webparamsdict[ak][ak2].append(int(webvalue))
        if (T.TEXT == keytype) or (T.FONT == keytype) or (T.AREA == keytype):
          webvalue = paramob.getfirst(keyname, keydefault)
          self.webparamsdict[ak][ak2].append(str(webvalue))
        if T.FLOAT == keytype:
          webvalue = paramob.getfirst(keyname, keydefault)
          self.webparamsdict[ak][ak2].append(float(webvalue))
        if T.IMAGE == keytype:
          webvalue = paramob.getfirst(keyname, keydefault)
          self.webparamsdict[ak][ak2].append(str(webvalue))

  # Return text of input form for card.
  def DisplayParams(self):
    result = []
    result.append('<table><tr><td>')
    result.append('<form method="POST" action="/cgi-bin/cardweb.py">')
    result.append("<table>")
    k = self.webparamsdict.keys()
    k.sort()
    for ak in k:
      result.append("<tr>")
      result.append("<td>")
      result.append(ak)
      result.append("</td>")
      result.append("<td>")
      result.append("<table>")
      k2 = self.webparamsdict[ak].keys()
      k2.sort()
      for ak2 in k2:
        result.append("<tr>")
        result.append("<td>")
        keyname = self.webparamsdict[ak][ak2][0]  # string
        result.append(keyname)
        result.append("</td>")
        result.append("<td>")
        keytype = self.webparamsdict[ak][ak2][1]  # T type
        preval = ''
        if len(self.webparamsdict[ak][ak2]) > 2:
          preval = self.webparamsdict[ak][ak2][2]
        if len(self.webparamsdict[ak][ak2]) > 3:
          preval = self.webparamsdict[ak][ak2][3]
        if T.NUM == keytype:
          result.append('<input type="text" value="%s" name="%s">' % (preval, keyname))
        if T.FLOAT == keytype:
          result.append('<input type="text" value="%s" name="%s">' % (preval, keyname))
        if T.TEXT == keytype:
          result.append('<input type="text" value="%s" name="%s">' % (preval, keyname))
        if T.AREA == keytype:
          result.append('<textarea rows="10" cols="30" name="%s">%s</textarea>' % (keyname,preval.strip()))
        if T.IMAGE == keytype:
          result.append('<input  type="file"  name="%s">' % keyname)
        if T.BOOL == keytype:
          result.append('Yes?')
          yc = "checked"
          nc = ""
          if preval != 1:
            nc = "checked"
            yc = ""
          result.append('<input  type="radio" value="1"  name="%s" %s>' % (keyname, yc))
          result.append('<input  type="radio" value="-1" name="%s" %s>' % (keyname, nc))
        if T.FONT == keytype:
          result.append('<select name="%s">' % keyname)
          for fontuple in self.fonts: 
            fname = fontuple[0]
            fdesc = fontuple[1]
            selected = ''
            if preval == fname:
              selected = "selected"
            result.append('<option  value="%s" %s>%s</option>' % (fname, selected,fname))
          result.append('</select>')
        result.append("</td>")
      result.append("</table>")
      result.append("</td>")
      result.append("</tr>")
    result.append("</table>")
    result.append('<input type="submit">')
    result.append("</form>")
    result.append('</td><td><img width=800 src="/cards/%s">' % self.outbase)
    result.append('</td></tr></table>')
    return '\n'.join(result)


  def Run(self):
    pc = pilcard.GenCard(self.webparamsdict)
    outproto = time.ctime(time.time()).replace(' ','_').replace(':','-')
    self.outbase = "%s.png" % outproto
    outname = '/var/www/html/html/cards/%s' % self.outbase
    pc.save(outname)
    self.renderpath = outname

  def EmitHtml(self):
    print "Content-Type: text/html"
    print
    print """\
<!DOCTYPE html>
<head>
  <title>Game Card Designer</title>
  <meta charset="utf-8">
  <link rel="stylesheet" type="text/css" href="/cardstyle.css">
</head>
<body>
<h1>Card Designer</h1>
"""
    self.LoadParams(webform)
    self.Run()
    print self.DisplayParams()
    print """</body></html>"""


def test():
  wb = WebParams()
  wb.EmitHtml()

if __name__ == '__main__':
  test() 
