import functools
import os
import re
import sys
from functools import reduce
from math import sqrt
from win32api import GetSystemMetrics
import matplotlib.patches
import matplotlib.lines
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import matplotlib.pyplot as plt

import numpy as np
import wx

from view.constants import *


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


def makeSelfIconButton(btn, size, icon_path, color=wx.WHITE):
    btn.SetBackgroundColour(color)
    btn.SetBitmap(newScaledImgBitmap(icon_path, size))


def newStandardButton(parent, size, label, on_click):
    btn = wx.Button(parent, size=size, label=label)
    btn.Bind(wx.EVT_BUTTON, on_click)
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

def to_bin_str(value, nqubits):
    return bin(value)[2:].zfill(nqubits)

def print_register_state(psi, nqubits):
    for existing_state in psi.data.tocoo().row:
        binS = to_bin_str(existing_state, nqubits)
        amplitude = psi.data[existing_state, 0]
        probability = np.abs(amplitude) ** 2
        print("|{}> |{}>: prob: {} ampl: {}".format(existing_state, binS, probability, amplitude))
    print("="*20)

def new_big_font_label(parent, label_txt):
    label = wx.StaticText(parent, label=label_txt, style=wx.ALIGN_CENTRE)
    font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.NORMAL)
    label.SetFont(font)
    return label

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def get_workspace_path():
    cwd = os.getcwd()
    C_root, subdir, _, _ = re.findall(r'(C:\\)((\w+\\)+)(\w+)', cwd)[0]
    workspacePath = C_root + subdir + "workspace"
    return workspacePath

def mouse_to_grid_coordinates(m_x, m_y):
    i = int(m_y / GATE_SIZE)
    j = int((m_x - GRID_OFFSET * GATE_SIZE) / (GATE_SIZE + GATE_H_SPACE))
    return i, j

def is_iterable(arg):
    try:
        iter(arg)
        return True
    except TypeError:
        return False


def new_titled_view(parent, title, view):
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(wx.StaticText(parent, label=title))
    sizer.AddSpacer(10)
    sizer.Add(view)
    return sizer


class ImgPanel(wx.Panel):

    def __init__(self, parent, img_path, size):
        wx.Panel.__init__(self, parent, size=size)
        self.__bmp = newScaledImgBitmap(img_path, size)
        self.__size = size
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour(wx.WHITE)
        self.Bind(wx.EVT_PAINT, self.__on_paint)

    def __on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        dc.DrawBitmap(self.__bmp, 0, 0)


class CenteredTextLatexPanel(wx.Panel):

    def __init__(self, parent, figure_number, figure_size, fontsize=23):
        wx.Panel.__init__(self, parent)
        self.__fig = plt.figure(figure_number, figsize=figure_size)
        self.__fig_number = figure_number
        self.__font_size=fontsize
        FigureCanvas(self, -1, self.__fig)
        plt.clf()
        plt.axis("off")
        self.__t = self._draw()

    def _draw(self):
        text = self._prepare_text()
        t = plt.text(0, 0, text, fontsize=self.__font_size)
        self._center_text(t)
        return t

    def _get_text_coordinates(self, text):
        r = self.__fig.canvas.get_renderer()
        bb = text.get_window_extent(renderer=r)
        inv = self.__fig.axes[0].transData.inverted()
        x0, y0 = inv.transform((bb.x0, bb.y0))
        x1, y1 = inv.transform((bb.x1, bb.y1))
        return x0, y0, x1-x0, y1-y0

    def _draw_rect_to_text(self, text):
        fig = self.__fig
        x0, y0, width, height = self._get_text_coordinates(text)
        rect = matplotlib.patches.Rectangle((x0, y0), width, height, linewidth=1, edgecolor='r', facecolor='none')
        fig.axes[0].add_patch(rect)

    def _draw_line(self, fig):
        l = matplotlib.lines.Line2D([0, 1], [.5, .5])
        fig.axes[0].add_line(l)

    def _center_text(self, t):
        _, _, width, height = self._get_text_coordinates(t)
        new_x = .5 - width * .5
        new_y = .5 - height * .25
        t.set_position((new_x, new_y))

    def _prepare_text(self):
        raise Exception("No prepared text to display")

    def _redraw(self):
        plt.figure(self.__fig_number)
        self.__t.remove()
        self.__t = self._draw()
        self.__fig.canvas.draw()


class MatrixPanel(CenteredTextLatexPanel):
    def __init__(self, parent, matrix, fig_numer, symbol="H", figsize=(5., .75), fontsize=23):
        self.__matrix = matrix
        self.__symbol = symbol
        CenteredTextLatexPanel.__init__(self, parent, fig_numer, figsize, fontsize)

    def _prepare_text(self):
        matrix = self.__matrix
        text = r'$' + self.__symbol + ' = \left[' \
               r' \stackrel{' + '{:.2f}'.format(matrix[0][0]) + '}{' + '{:.2f}'.format(matrix[0][1]) + r'}' \
               r'\,\,\,' \
               r' \stackrel{' + '{:.2f}'.format(matrix[1][0]) + '}{' + '{:.2f}'.format(matrix[1][1]) + r'}' \
               r'\right]$'
        return text

    def change_matrix_value(self, matrix):
        self.__matrix = matrix
        self._redraw()


class InspectorMatrixPanel(CenteredTextLatexPanel):
    def __init__(self, parent, symbol, fig_numer, str_latex_matrix="", fig_size=(3., 1.)):
        self.__str_latex_matrix = str_latex_matrix
        self.__symbol = symbol
        CenteredTextLatexPanel.__init__(self, parent, fig_numer, fig_size, fontsize=17)

    def _prepare_text(self):
        text = r'$' + self.__symbol + r' = ' + self.__str_latex_matrix + '$'
        return text

