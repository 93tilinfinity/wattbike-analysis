'''
This script is for plotting all aspect of Wattbike files!

Polar plots:
    _plot_single_polar(ax,torque,mean)
    plot_polar(df,mean=False)

Power plots:
    stack_pwr_plots(data, isNorm=True)
    time_pwr_bars(data)
'''

import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap
import seaborn as sns
import matplotlib.pyplot as plt

def _plot_single_polar(ax,torque,mean,label=None):
    if mean:
        linewidth = 2
    else:
        linewidth = 0.5
    radians = np.arange(0, 361) / (180 / np.pi)
    ax.plot(radians, torque, linewidth=linewidth, label = label)
    ax.legend(bbox_to_anchor=(0.4, 0.05), prop={'size': 8})


def plot_polar(df,mean=False):
    full,meta = df['full'],df['meta']
    column_labels = [f'_{i}' for i in range(361)]
    ax = plt.subplot(111,projection='polar')
    if mean:
        torque = full[column_labels].mean()
        label = str(meta['date'].date())
        label += ', FTP:'+str(int((full['power'].mean()*0.95)))+'W'
        label += ', Power SD:'+str(full['power'].std().round(2))+'W'
        _plot_single_polar(ax, torque, mean, label)
    else:
        for row in full[column_labels][::50].values:
            torque = row
            _plot_single_polar(ax, torque, mean)

    ax.set_theta_offset(np.pi / 2)
    xticks_num = 8
    xticks = np.arange(0,2*np.pi,2*np.pi / xticks_num)
    ax.set_xticks(xticks)
    rad_to_deg = lambda i: '{}°'.format(int(i / (2 * np.pi) * 360))
    ax.set_xticklabels([rad_to_deg(i) for i in xticks])
    ax.set_yticklabels([])
    plt.title('The Peanut Plot!',loc='right')
    return ax

def stack_pwr_plots(data, isNorm=True):
    idx = [s['meta']['date'].date() for s in data]
    pwr = [s['power_zone'] for s in data]
    pwr_df = pd.DataFrame(pwr,index = idx)
    pwr_df = pwr_df.sort_index()
    if isNorm:
        pwr_df = pwr_df.div(pwr_df.sum(axis=1), axis=0)
    ax = pwr_df.plot(kind='bar',stacked=True,width=0.9,
                     colormap=ListedColormap(sns.color_palette("YlOrRd", 7)))
    if isNorm:
        ax.set(ylabel="Time (%)")
    else:
        ax.set(ylabel="Time (mins)")
    return ax

def time_pwr_bars(data):
    pwr = [s['power_zone'] for s in data]
    pwr_df = pd.DataFrame(pwr, index=[s['meta']['date'].date() for s in data])
    pwr_df = pwr_df.sort_index()

    pwr_17 = pwr_df[[i.year == 2017 for i in pwr_df.index]]
    pwr_18 = pwr_df[[i.year == 2018 for i in pwr_df.index]]
    pwr_19 = pwr_df[[i.year == 2019 for i in pwr_df.index]]

    pwr_sum = pd.DataFrame({i:[pwr_17[i].sum(),pwr_18[i].sum(),pwr_19[i].sum()] for i in pwr_17.columns})
    pwr_sum.index = [2017,2018,2019]
    pwr_sum = pwr_sum.T

    ax = pwr_sum.plot(kind='bar',color=['lightcoral','lightskyblue','darkkhaki'])
    ax.set_ylabel('Time (mins)')
    ax.grid()
    plt.xticks(rotation=45)
    plt.title('Time Spent in Power Bucket')
    return ax

def period_scatter(period1,period2):
    '''
    Need to clean this up!

    :param period1: period 1 dataframe (preprocess script)
    :param period2: period 2 dataframe (preprocess script)
    :return: plt figure object
    '''
    plt.figure(figsize=(18, 7))

    # Max power
    plt.subplot(231)
    plt.scatter(period1.index, period1['max'], marker='x')
    plt.scatter(period2.index, period2['max'], marker='x')
    plt.ylabel('Max Power (Watts)')
    plt.grid()

    # Avg power
    plt.subplot(232)
    plt.scatter(period1.index, period1['mean'], marker='x')
    plt.scatter(period2.index, period2['mean'], marker='x')
    plt.ylabel('Avg Power (Watts)')
    plt.grid()

    # Length of sessions
    plt.subplot(233)
    plt.scatter(period1.index, period1['time'], marker='x')
    plt.scatter(period2.index, period2['time'], marker='x')
    plt.ylabel('Session Duration (Mins)')
    plt.grid()

    # Avg power * duration = workload
    plt.subplot(234)
    plt.scatter(period1.index, period1['mean'] * period1['time'], marker='x')
    plt.scatter(period2.index, period2['mean'] * period2['time'], marker='x')
    plt.ylabel('Workload (Watts x Mins)')
    plt.grid()

    # Power variance
    # plt.scatter(period1.index,period1['mean']/period1['sd'],marker='x')
    # plt.scatter(period2.index,period2['mean']/period2['sd'],marker='x')
    plt.subplot(235)
    plt.scatter(period1.index, period1['sd'], marker='x')
    plt.scatter(period2.index, period2['sd'], marker='x')
    plt.ylabel('Power S. Deviation (Watts)')
    plt.grid()

    # Cadence Analysis
    plt.subplot(236)
    plt.scatter(period1.index, period1['cadence'], marker='x')
    plt.scatter(period2.index, period2['cadence'], marker='x')
    plt.ylabel('Cadence (RPM)')
    plt.grid()
