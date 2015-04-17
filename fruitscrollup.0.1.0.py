#####------v0.1.0----------------------------------------------------------#####
#####------Future-Plans----------------------------------------------------#####
#
# Overall future script updates:
#   -config file
#       -more scroll order options
#       -more image scaling options
#       -fancy effects
#           -non-perpendicular scroll, rotations, etc.
#   -cleaner code structure
#
#####------Version-Changes-------------------------------------------------#####
#
# -fixed randomizer
# -added sorting options
#

import wx
import wx.lib.newevent
import time
import random
import os
import os.path
from ConfigParser import SafeConfigParser
random.seed()

parser = SafeConfigParser()
parser.read('scrolling_image.ini')
NeedNewImage, EVT_NEED_NEW_IMAGE = wx.lib.newevent.NewEvent()

class imageWindow(wx.Window):
    def __init__(self, parent, image):
        wx.Window.__init__(self, parent)
        
        self.dc = wx.PaintDC(self)
        self.parent = parent
        self.scrollDir = self.parent.scrollSet
        print self.scrollDir
        self.photo = image.ConvertToBitmap()
        self.H = image.GetHeight()
        self.W = image.GetWidth()
        self.timer = wx.Timer(self, id=2000)
        self.timer2 = wx.Timer(self, id=2001)
        self.x = 0
        self.y = 0
        self.ref = 0
        self.centeringTest = 0
        self.totalJumps = 0
        self.imageJump = parser.getint('ImageSettings', 'imagejump')
        self.jumpTime = parser.getint('ImageSettings', 'jumptime')
        self.totalTime = 0
        self.positions = [(self.x, self.y)]
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_KEY_DOWN, self.onKey)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.Bind(wx.EVT_TIMER, self.newImageCall, self.timer2)
        self.displayData()
        self.imagePos()
#        print "starting timers"
        self.timer.Start(self.jumpTime)
        self.timer2.Start(self.totalTime)
    
    def update(self, evt):
        if self.ref == self.totalJumps:
            self.ref = 0
            self.timer.Stop()
            self.Unbind(wx.EVT_TIMER, self.timer)
            self.dc.Clear()
#            print "image moved"

        else:
            brush = wx.Brush("black")
            self.dc.SetBackground(brush)
            self.dc.Clear()
            self.dc.DrawBitmap(self.photo, self.positions[self.ref][0], 
                               self.positions[self.ref][1])
            self.ref += 1
#            print self.ref
        
    
    def displayData(self):
        location = parser.getint('DisplaySettings', 'wallscreenwidth')
        locationH = parser.getint('DisplaySettings', 'wallscreenheight')

        displayInfo = (wx.Display(1))
        sizeWidth = (displayInfo.GetGeometry().GetWidth())
        sizeHeight = (displayInfo.GetGeometry().GetHeight())
        screenWidth = sizeWidth * location
        screenHeight = sizeHeight * locationH
        
        if self.scrollDir == 'v':
            self.y = screenHeight
            self.centeringTest = screenWidth - self.W
            self.totalJumps = ((screenHeight / self.imageJump) + 
                               (self.H / self.imageJump))
        else:
            self.x = screenWidth
            self.centeringTest = screenHeight - self.H
            self.totalJumps = ((screenWidth / self.imageJump) + 
                               (self.W / self.imageJump))
        
        self.totalTime = (self.jumpTime * self.totalJumps + 2000)
        
    def imagePos(self):
        maxGap = parser.getint('ImageSettings', 'maxgap')
        if self.centeringTest > maxGap:
            if self.scrollDir == 'v':
                print "v centering test"
                self.x = self.centeringTest / 2
            else:
                print "h centering test"
                self.y = self.centeringTest / 2
        
        self.positions = [(self.x, self.y)]
        print "pos initialized"
        
        if self.scrollDir == 'v':
            print "v pos"
            for t in range(self.totalJumps):
                self.y = self.y - self.imageJump
                self.positions.append((self.x, self.y))
        else:
            print "h pos"
            for t in range(self.totalJumps):
                self.x = self.x - self.imageJump
                self.positions.append((self.x, self.y))
            
    def newImageCall(self, evt):
        evt = NeedNewImage()
        self.timer2.Stop()
        self.Unbind(wx.EVT_TIMER, self.timer2)
        wx.PostEvent(self.parent, evt)
#        print "looking for new image..."
        self.Destroy()

    def onPaint(self, evt):
        dc = wx.PaintDC(self)
        brush = wx.Brush("black")
        dc.SetBackground(brush)
        dc.Clear()
#        print "painting inside..."

    def onKey(self, event):
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
#            print "esc received"
            self.GetParent().Close()
        elif key_code == 78 or 314:
            evt = NeedNewImage()
            self.timer2.Stop()
            self.timer.Stop()
            self.Unbind(wx.EVT_TIMER, self.timer)
            self.Unbind(wx.EVT_TIMER, self.timer2)
            wx.PostEvent(self.parent, evt)
#           print "looking for new image..."
            self.Destroy()
            
        else:
            event.Skip()

class imageScroll(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Scrolling Images", style=wx.NO_BORDER)

#        print parser.get('ImageSettings', 'verticaldirectory')
        self.SetBackgroundColour(wx.BLACK)
        self.sizeHeight = 0
        self.sizeWidth = 0
        self.vertCount = 0
        self.horizCount = 0
        self.fullImageSet = []
#        self.fullScrollSet = []
        self.scrollSet = 'h'
        self.randomList = []
#        self.randomTest = True
        self.imageIndex = 0
#        self.lastIndex = -1
        self.userSel = 0
        self.listLength = 0
        print "init done"
        self.vertDIR = parser.get('ImageSettings', 'verticaldirectory')
        self.horizDIR = parser.get('ImageSettings', 'horizontaldirectory')
        self.vertPermit = parser.getboolean('Features', 'verticalscroll')
        self.horizPermit = parser.getboolean('Features', 'horizontalscroll')
        if self.vertPermit == True and self.horizPermit == True:
            self.listParam = 2
        elif self.vertPermit == True and self.horizPermit == False:
            self.listParam = 1
        else:
            self.listParam = 0
#        print self.listParam
        image = wx.Image("init_image.png")

        self.displayInit()
        
        self.Bind(EVT_NEED_NEW_IMAGE, self.imageHandler)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        
        evt = NeedNewImage()
        wx.PostEvent(self, evt)
    
    def displayInit(self):
        displayInfo = (wx.Display(1))
        location = parser.getint('DisplaySettings', 'wallscreenwidth')
        locationH = parser.getint('DisplaySettings', 'wallscreenheight')

        self.sizeHeight = displayInfo.GetGeometry().GetHeight() * locationH
        self.sizeWidth = displayInfo.GetGeometry().GetWidth() * location
        
#        print self.sizeWidth * location
#        print self.sizeHeight * locationH
#        
        self.SetSize((self.sizeWidth, self.sizeHeight))
#        print self.sizeHeight
#        print self.sizeWidth
    
    def imageList(self):
        print "image list"
        vertList = os.listdir(self.vertDIR)
        horizList = os.listdir(self.horizDIR)
        
        self.vertCount = len([name for name in os.listdir(self.vertDIR) if
                              os.path.isfile(os.path.join(self.vertDIR, name))])
        self.horizCount = len([name for name in os.listdir(self.horizDIR) if
                               os.path.isfile(os.path.join(self.horizDIR, name))])

        self.fullImageSet = [('sample.jpg', 'h')]
#            self.fullScrollSet.append('h')

        if self.vertCount > self.horizCount:
                length = self.vertCount
        else:
                length = self.horizCount
                
        imageSet = [['sample.jpg' for x in range(length)] for x in range(2)]

        for x in range(0, self.vertCount):
            imageSet[0][x] = vertList[x]

        for x in range(0, self.horizCount):
            imageSet[1][x] = horizList[x]

        if self.listParam == 2:
            self.listLength = self.horizCount + self.vertCount
            for x in range(self.listLength - 1):
                self.fullImageSet.append(('sample.jpg', 'h'))
            for x in range(0, self.horizCount):
                self.fullImageSet[x] = (imageSet[1][x], 'h')
#                self.fullImageSet[x][1] = 'h'
#                self.fullScrollSet[x] = 'h'
            for x in range(0, self.vertCount):
#                print x
#                print self.vertCount
#                print imageSet[0][x]
                self.fullImageSet[self.horizCount + x] = (imageSet[0][x], 'v')
#                self.fullImageSet[self.horizCount + x][1] = 'v'
#                print self.fullImageSet
#                self.fullScrollSet[self.horizCount + x] = 'v'

        elif self.listParam == 1:
            self.listLength = self.vertCount
            for x in range(self.listLength - 1):
                self.fullImageSet.append(('sample.jpg', 'h'))
            for x in range(0, self.vertCount):
                self.fullImageSet[x] = (imageSet[0][x], 'v')
#                self.fullImageSet[x][1] = 'v'
#                self.fullScrollSet[x] = 'v'

        else:
            self.listLength = self.horizCount
            for x in range(self.listLength - 1):
                self.fullImageSet.append(('sample.jpg', 'h'))
            for x in range(0, self.horizCount):
                self.fullImageSet[x] = (imageSet[1][x], 'h')
#                self.fullImageSet[x][1] = 'h'
#                self.fullScrollSet[x] = 'h'
        
        print self.fullImageSet, "hello"

    def imageSort(self):
        sortOption = parser.get('Features', 'sortmethod')
        if sortOption == 'ord':
            pass
        elif sortOption == 'rev':
            tempList = self.fullImageSet
            print tempList
            self.fullImageSet = tempList[::-1]
        else:
            random.shuffle(self.fullImageSet)

        print self.fullImageSet, "hello again"

    def imageSelect(self):
        if self.imageIndex == self.listLength or self.imageIndex == 0:
            self.imageIndex = 0
            self.imageList()
            self.imageSort()
            image = self.fullImageSet[self.imageIndex][0]
            self.scrollSet = self.fullImageSet[self.imageIndex][1]
            if self.scrollSet == 'v':
                self.image = wx.Image(self.vertDIR + image)
            elif self.scrollSet == 'h':
                self.image = wx.Image(self.horizDIR + image)
            else:
                print "error in imageSelect"
                self.image = wx.Image("init_image.png")
            self.imageIndex += 1
        else:
            image = self.fullImageSet[self.imageIndex][0]
            self.scrollSet = self.fullImageSet[self.imageIndex][1]
            if self.scrollSet == 'v':
                self.image = wx.Image(self.vertDIR + image)
            elif self.scrollSet == 'h':
                self.image = wx.Image(self.horizDIR + image)
            else:
                print "error in imageSelect"
                self.image = wx.Image("init_image.png")
            self.imageIndex += 1
            
    def imageScale(self):
        W = self.image.GetWidth()
        H = self.image.GetHeight()
        
        if self.scrollSet == 'v':
            if W > (self.sizeWidth):
                W = (self.sizeWidth)
                H = (self.sizeWidth) * H / W
        elif self.scrollSet == 'h':
            if H > (self.sizeHeight):
                W = (self.sizeHeight) * W / H
                H = (self.sizeHeight)

        self.image = self.image.Scale(W, H)

    def onPaint(self, evt):
        dc = wx.PaintDC(self)
        brush = wx.Brush("black")
        dc.SetBackground(brush)
        dc.Clear()
#        print "painting..."

    def imageHandler(self, evt):
        self.imageSelect()
        self.imageScale()
#       Find a better way to do this
        self.SetSize((self.GetSize().width, self.GetSize().height + 1))
        self.SetSize((self.GetSize().width, self.GetSize().height - 1))
        imageWindow(self, self.image)

app = wx.PySimpleApp()
frm = imageScroll()
frm.Show()
app.MainLoop()
