import os
import wx
 
class DummyBulb(wx.App):
    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)
        self.frame = wx.Frame(None, title='Photo Control')
 
        self.panel = wx.Panel(self.frame)
        
        self.PhotoMaxSize = 240
        self.photoOnPath="on.png"
        self.photoOffPath="off.png"
        self.path=self.photoOffPath		
        self.createWidgets()
        self.frame.Show()
 
    def createWidgets(self):
        instructions = 'Dummy bulb'
        img = wx.EmptyImage(250,250)
        self.imageCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY, 
                                         wx.BitmapFromImage(img))
 
        instructLbl = wx.StaticText(self.panel, label=instructions)
        
        browseBtn = wx.Button(self.panel, label='Switch')
        browseBtn.Bind(wx.EVT_BUTTON, self.click)
 
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
 
        self.mainSizer.Add(wx.StaticLine(self.panel, wx.ID_ANY),
                           0, wx.ALL|wx.EXPAND, 5)
        self.mainSizer.Add(instructLbl, 0, wx.ALL, 5)
        self.mainSizer.Add(self.imageCtrl, 0, wx.ALL, 5)
        
        self.sizer.Add(browseBtn, 0, wx.ALL, 5)        
        self.mainSizer.Add(self.sizer, 0, wx.ALL, 5)
 
        self.panel.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self.frame)
        self.panel.Layout()
        
        self.onView()
    
    def onView(self):
        filepath = self.path
        img = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * H / W
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * W / H
        img = img.Scale(NewW,NewH)
 
        self.imageCtrl.SetBitmap(wx.BitmapFromImage(img))
        self.panel.Refresh()

    def click(self, event):
               
        if self.path == self.photoOnPath:
            self.path=self.photoOffPath
        else:self.path=self.photoOnPath
        self.onView()
 
 
if __name__ == '__main__':
    app = DummyBulb()
    app.MainLoop()