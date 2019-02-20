import colorsys

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm
# from colorspacious import cspace_converter
from collections import OrderedDict
from math import pi
import matplotlib.colors

cmaps = OrderedDict()

cmaps['Miscellaneous'] = [
            'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
            'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
            'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar']
nrows = max(len(cmap_list) for cmap_category, cmap_list in cmaps.items())
gradient = np.linspace(0, 1, 256)
gradient = np.vstack((gradient, gradient))


def plot_color_gradients(cmap_category, cmap_list, nrows):
    fig, axes = plt.subplots(nrows=nrows)
    fig.subplots_adjust(top=0.95, bottom=0.01, left=0.2, right=0.99)
    axes[0].set_title(cmap_category + ' colormaps', fontsize=14)

    for ax, name in zip(axes, cmap_list):
        ax.imshow(gradient, aspect='auto', cmap=plt.get_cmap(name))
        pos = list(ax.get_position().bounds)
        x_text = pos[0] - 0.01
        y_text = pos[1] + pos[3]/2.
        fig.text(x_text, y_text, name, va='center', ha='right', fontsize=10)

    # Turn off *all* ticks & spines, not just the ones with colormaps.
    for ax in axes:
        ax.set_axis_off()


# for cmap_category, cmap_list in cmaps.items():
#     plot_color_gradients(cmap_category, cmap_list, nrows)

xval = np.arange(0, 2*pi, 0.01)
yval = np.ones_like(xval)

# colormap = plt.get_cmap('hsv')
# norm = mpl.colors.Normalize(0.0, 2*np.pi)
#
# ax = plt.subplot(1, 1, 1, polar=True)
# # ax.scatter(xval, yval, c=xval, s=300, cmap=colormap, norm=norm, linewidths=0)
# ax.set_yticks([])
# ax.set_xticks([])

N = len(xval)
HSV_tuples = [(x*1.0/N, 0.5, 0.5) for x in range(N)]
RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))

a = np.arange(5) + 1j*np.arange(6,11)
for i, x in enumerate(xval):
    plt.polar([0, x], [0, 1], marker='o', c=RGB_tuples[i])  # first are angles, second are rs
for x in a:
    x = x / abs(x)
    plt.polar([0, np.angle(x)], [0, 1], marker=10, c=[0,0,0])

x = 0 + -1j
plt.polar([0, np.angle(x)], [0, 1], marker=10, c=[0,0,0])
# plt.yticks([])
# plt.xticks([])
plt.ylabel("Imaginary")
plt.xlabel("Real")
plt.show()

x = np.arange(5)
y = np.exp(x)
print(plt.figure(0))
plt.plot(x, y)

z = np.sin(x)
print(plt.figure(1))
plt.plot(x, z)

w = np.cos(x)
plt.figure(0) # Here's the part I need
print(plt.plot(x, w))
plt.show()