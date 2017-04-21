import numpy as np
import pylab as pl
import pandas as pd
import matplotlib.pyplot as plt

def make_barplot(cats, vals, xlab, title, figsize):
    fig, ax = plt.subplots(figsize=figsize)

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


def make_ageplot():
    p_gen_stats_df = pd.read_csv('data/csvs_for_nb/p_gen_stats.csv', index_col=0)
    p_gen_stats_df = p_gen_stats_df.replace(np.nan, 'Not Found')
    p_gen_stats_df['year'] = pd.Series(map(lambda x: int(x.split('/')[-1]), p_gen_stats_df['date']))
    good_p_gen_stats = p_gen_stats_df[~p_gen_stats_df['age'].isin(['Not Found'] + list(range(54, 100)))]
    year = 2016
    sixteen_df = good_p_gen_stats[good_p_gen_stats['year'] == year][~good_p_gen_stats[good_p_gen_stats['year'] == year]['age'].isin(['Not Found'])]
    country_list = ['Spain', 'Belgium', 'Ivory Coast', 'Greece', 'Argentina', 'Uruguay']
    country_ages = list()
    for country in country_list:
        ages = list(sixteen_df[sixteen_df['cob'] == country]['age'][~sixteen_df[sixteen_df['cob'] == country]['cob'].isin(['Not Found'])].values)
        country_ages.append(ages)

    plt.figure(figsize=(12, 6))
    plt.boxplot(country_ages)
    plt.title("Distribution of Age in {} Tournament By Country".format(year))
    plt.xticks(list(range(1,len(country_list)+1)), country_list, rotation=90)
    plt.show()


def plot_club_performances():
    perf = pd.read_csv('data/csvs_for_nb/table.csv')

    fig, ax = plt.subplots(2, 2, figsize=(12, 6))

    for axes, team_name in [((0,0), 'Manchester City'), ((0,1), 'Real Madrid'), ((1,0), 'Porto'), ((1,1), 'Dortmund')]:
        club_perf = list(perf[perf['Club (# of participations)'].str.contains(team_name)].iloc[:,1:25].values[0])
        club_perf = ['R16' if p == 'GS2' else p for p in club_perf] # when there was a second Group Stage, there was no round of 16 (same thing though)
        perf_cats = ['NP', 'GS', 'R16', 'QF', 'SF', 'F', 'C']
        cat_vals = [0, 1, 2, 3, 4, 5, 6]
        club_perf_vals = [cat_vals[perf_cats.index(p)] for p in club_perf]

        N = len(club_perf_vals)

        ind = np.arange(N)  # the x locations for the groups
        width = 0.35       # the width of the bars

        ax[axes].bar(ind, club_perf_vals, width, color='r')
        ax[axes].set_title("{} Performance Over the Years".format(team_name))
        ax[axes].set_yticklabels(perf_cats)
        ax[axes].set_xticklabels(range(1993, 2016))
        ax[axes].grid()


def plot_pass_efficiency():
    p_stats_five_df = pd.read_csv('data/csvs_for_nb/p_stats_2012_on_df.csv', index_col=0)
    p_stats_five_df['filt_pass_pct'] = np.where(p_stats_five_df['minutes'] < 1320, 0, p_stats_five_df['pass_pct'])
    pass_pct = p_stats_five_df.sort_values(by='filt_pass_pct', ascending=False)['filt_pass_pct'][:20]
    make_barplot(pass_pct.index, pass_pct.values, 'Pass Completion Percentage', 'Players With Highest Pass Completion Percentage', (12,6))
