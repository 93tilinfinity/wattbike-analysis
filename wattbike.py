'''
Machine Learning, Cycling & 300W FTP (Part 1)

Script to build Medium article plots.

'''

import preprocess
import plots
import os
import pandas as pd
from datetime import datetime

def build_rawdata(user_id):
    """Create data structure containing session data for given user_id (if downloaded)

    :param user_id: Wattbike unique user id
    :type user_id: str

    """
    path = 'wattbikesessions/'
    files = os.listdir(path+user_id+'/')
    rawdata = []
    for file in files:
        try:
            rawdata.append(pd.read_pickle(path + file))
        except Exception:
            print('Could not load:',file)
            continue
    return preprocess.load_session_data(rawdata)

data = build_rawdata('user_id')

# Figure 2 ##################################################
ftp_test = [d for d in data if d['meta']['session_title'].find('20 Minute Test')==0]
plots.plot_polar(ftp_test[1],True)
plots.plot_polar(ftp_test[-1],True)
plots.plot_polar(ftp_test[-2],True)
plots.plot_polar(ftp_test[0],True)

# Figure 3 ##################################################
plots.time_pwr_bars(data)

# Figure 4 ##################################################
s_year = [[d for d in data if d['meta']['date'].year == y] for y in [2017,2018,2019]]
s17,s18,s19 = s_year
plots.stack_pwr_plots(s19,True)

# Figure 5 ##################################################
plots.stack_pwr_plots(s19,False)

# Figure 6 ##################################################
date0,date1,date2 = datetime(2019,3,25),datetime(2019,5,28),datetime(2019,8,20)

period1 = [d for d in data if (d['meta']['date'] < date1 \
                               and d['meta']['date'] > date0 +datetime.timedelta(days=1))]
period2 = [d for d in data if (d['meta']['date'] < date2 \
                               and d['meta']['date'] > date1 +datetime.timedelta(days=1))]

p1_df = preprocess.build_period_df(period1)
p2_df = preprocess.build_period_df(period2)

plots.period_scatter(p1_df,p2_df)










