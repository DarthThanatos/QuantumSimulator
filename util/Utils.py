from math import sqrt

import functools
from win32api import GetSystemMetrics

import wx
from functools import reduce


def AddToolButtonBmpIS(frame, toolbar, path, hint, triggermeth, toggleBmp ='', type=wx.BITMAP_TYPE_PNG):
    if toggleBmp:
        return AddToggleToolButtonBmpObject(frame, toolbar, wx.Image(path, type).ConvertToBitmap(), hint[:85], triggermeth)
    else:
        return AddToolButtonBmpObject(frame, toolbar, wx.Image(path, type).ConvertToBitmap(), hint[:85], triggermeth)

def AddToggleToolButtonBmpObject(frame, toolbar, thebitmap, hint, triggermeth):
    nId = wx.NewId()
    toolbar.AddTool(nId, thebitmap, thebitmap, shortHelpString = hint, isToggle = True)
    frame.Bind(wx.EVT_TOOL, triggermeth, id=nId)
    return nId

def AddToolButtonBmpObject(frame, toolbar, thebitmap, hint, triggermeth,
      theToggleBitmap=wx.NullBitmap):
    nId = wx.NewId()
    toolbar.AddTool(bitmap=thebitmap, toolId =nId,
              label = "", shortHelp=hint)
    frame.Bind(wx.EVT_TOOL, triggermeth, id=nId)
    return nId


def appendMenuItem(menu, wId, label, code=(), bmp='', help=''):
    # XXX Add kind=wx.ITEM_NORMALwhen 2.3.3 is minimum.
    text = label + (code and ' \t'+code[2] or '')
    menuItem = wx.MenuItem(menu, wId, text, help)
    if bmp and bmp != '-':
        menuItem.SetBitmap(wx.Image(bmp).ConvertToBitmap())
    menu.Append(menuItem)

def newScaledImg(image_path, size):
    image = wx.Image(name = image_path) # e.g. "..\\Images\\Circuit\\ket_0.png"
    return image.Scale(*size)

def newScaledImgBitmap(image_path, size):
    # return wx.StaticBitmap(view, wx.ID_ANY, wx.BitmapFromImage(newScaledImg(image_path, size)), size = size)
    return wx.Bitmap(newScaledImg(image_path, size))

def euclDist(p1, p2):
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def newIconButton(parent, size, icon_path, on_click, color=wx.WHITE):
    btn = wx.Button(parent, size=size)
    btn.SetBackgroundColour(color)
    btn.Bind(wx.EVT_BUTTON, on_click)
    btn.SetBitmap(newScaledImgBitmap(icon_path, size))
    return btn

def flatten_list(listOfLists, fun = lambda x: x):
    return reduce(list.__add__, map(fun, listOfLists))

def update_dict(a, b):
    dest = dict(a)
    dest.update(b)
    return dest

def flatten_dicts(list_of_dicts):
    return dict(functools.reduce(lambda acc, d: update_dict(acc, d), list_of_dicts, {}))

def get_screen_w_h():
    return GetSystemMetrics(0), GetSystemMetrics(1)

def get_screen_middle_point():
    w,h = get_screen_w_h()
    return w/2, h/2