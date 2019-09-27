'''
This script is for processing the raw json output from Wattbike session data stored in pickles!

Based off 'wblib' - https://github.com/AartGoossens/wblib

'''

import numpy as np
import pandas as pd
import collections
import datetime
from datetime import datetime


def _flatten(df, parent_key='', sep='_'):
    items = []
    for k, v in df.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(_flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def _columns_to_numeric(df):
    for col in df.columns:
        try:
            df.iloc[:,df.columns.get_loc(col)] = pd.to_numeric(df.iloc[:,df.columns.get_loc(col)])
        except ValueError:
            continue
    return df

def _add_torque(df):
    _df = pd.DataFrame()
    new_angles = np.arange(0.0,361.0)
    column_labels = [f'_{i}' for i in range(361)]
    for index,pf in df.polar_force.iteritems():
        if not isinstance(pf,str):
            continue
        forces = [int(i) for i in pf.split(',')]
        forces = np.array(forces + [forces[0]])
        forces = forces / np.mean(forces)
        angle_dx = 360.0 / (len(forces)-1)

        forces_interp = np.interp(
            x=new_angles,
            xp=np.arange(0,360.01,angle_dx),
            fp=forces)
        _df[index] = forces_interp
    _df['angle'] = column_labels
    _df.set_index('angle',inplace=True)
    _df = _df.transpose()
    for angle in column_labels:
        df[angle] = _df[angle]
    df = df.drop(columns='polar_force')
    df = _columns_to_numeric(df)
    return df

def _build_meta(df):
    names = ['session_title','date','user_device','user_id']#,'altitude','latitude','longitude']
    values = [df['title'].values[0], datetime.strptime(df['startDate'].values[0],"%Y-%m-%dT%H:%M:%SZ"),
              df['deviceUserAgent'].values[0], df['userId'].values[0]] #df['altitude'].values[0],
              # df['latitude'].values[0],df['longitude'].values[0]]
    meta = {}
    for i,j in zip(names,values):
        meta[i] = j
    return meta

def _build_power_zones(df, thresholds=[0.5, 0.75, 0.9, 1.05, 1.2], ftp=250):
    cum_data_points = [len(df[z * ftp < df.power]) for z in thresholds]
    data_points = [cum_data_points[i] - cum_data_points[i + 1] for i, t in enumerate(cum_data_points[:-1])]
    data_points.append(cum_data_points[-1])
    data_points_0 = [len(df.index) - cum_data_points[0]]
    data_points_0.extend(data_points)
    pwr = {}
    for i,j in zip(['power_z' + str(i) for i in range(1, len(thresholds) + 2)],[z * df.index[-1] / (len(df.index) * 60) for z in data_points_0]):
        pwr[i] = j
    return pwr

def _build_power(df, thresholds=[100,150,200,250,300]):
    cum_data_points = [len(df[z < df.power]) for z in thresholds]
    data_points = [cum_data_points[i] - cum_data_points[i + 1] for i, t in enumerate(cum_data_points[:-1])]
    data_points.append(cum_data_points[-1])
    data_points_0 = [len(df.index) - cum_data_points[0]]
    data_points_0.extend(data_points)
    n = [0]+thresholds
    names = [str(n[i])+'-'+str(n[i+1])+'W' for i in range(len(n)-1)]
    names.extend([str(thresholds[-1])+'W+'])
    pwr = {}
    for i,j in zip(names,[z * df.index[-1] / (len(df.index) * 60) for z in data_points_0]):
        pwr[i] = j
    return pwr

def _single_session_data(df):
    sess = pd.DataFrame([_flatten(rev) for laps in df['laps'] for rev in laps['data']])
    sess = _columns_to_numeric(sess)
    sess.time = sess.time.cumsum()
    sess.distance = sess.distance.cumsum() / 1000.0
    sess = sess.set_index('time')
    sess = _add_torque(sess)
    pwr = _build_power(sess)
    # pwr = _build_power_zones(sess)
    meta = _build_meta(df)
    return sess, pwr, meta

def load_session_data(raw):
    result = []
    for df in raw:
        full, pwr, meta = _single_session_data(df)
        result.append({'full':full,'power_zone':pwr,'meta':meta})
    return result

def build_period_df(period):
    idx = [s['meta']['date'].date() for s in period]
    p1 = [(s['full']['power'].max(),s['full']['power'].mean(),\
           s['full']['power'].std(),s['full']['power'].index[-1]/60,\
           s['full']['cadence'].mean()) for s in period]
    p1_df = pd.DataFrame(p1,columns = ['max','mean','sd','time','cadence'], index=idx)
    return p1_df.sort_index()
