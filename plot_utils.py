import numpy as np
import pylab as pl
import matplotlib.pyplot as plt

def make_barplot(cats, vals, xlab, title):
    fig, ax = plt.subplots()

    y_pos = np.arange(len(cats))

    ax.barh(y_pos, vals, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(cats)
    ax.invert_yaxis()
    ax.set_xlabel(xlab)
    ax.set_title(title)
    ax.grid()

    plt.show()

class Radar(object):

    def __init__(self, fig, titles, labels, rect=None):
        if rect is None:
            rect = [0.05, 0.05, 0.95, 0.95]

        self.n = len(titles)
        self.angles = np.arange(90, 90+360, 360.0/self.n)
        self.axes = [fig.add_axes(rect, projection="polar", label="axes%d" % i)
                         for i in range(self.n)]

        self.ax = self.axes[0]
        self.ax.set_thetagrids(self.angles, labels=titles, fontsize=14)

        for ax in self.axes[1:]:
            ax.patch.set_visible(False)
            ax.grid("off")
            ax.xaxis.set_visible(False)

        for ax, angle, label in zip(self.axes, self.angles, labels):
            ax.set_rgrids(range(1, 6), angle=angle, labels=label)
            ax.spines["polar"].set_visible(False)
            ax.set_ylim(0, 5)

    def plot(self, values, *args, **kw):
        angle = np.deg2rad(np.r_[self.angles, self.angles[0]])
        values = np.r_[values, values[0]]
        self.ax.plot(angle, values, *args, **kw)

def make_radar_plot(attr_titles, val_list, val_cols, val_lab, ax_ticks):
    fig = pl.figure(figsize=(6, 6))

    titles = attr_titles

    labels = [ax_ticks] * len(attr_titles)
    step_size = ax_ticks[1] - ax_ticks[0]

    radar = Radar(fig, titles, labels)
    for i in range(len(val_list)):
        radar.plot(np.array(val_list[i]) / step_size, "-", lw=2, color=val_cols[i], alpha=0.4, label=val_lab[i])
    radar.ax.legend()
