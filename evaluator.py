# File: evaluator.py
# Author: Murilo Bento
#
# MIT License
#
# Copyright (c) 2020 Murilo Bento
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# --- IMPORTS ---

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import pandas_profiling

from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
import matplotlib.dates as mdates

# ---------------

# --- DATA ACQUISITION ---

input = "https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv"

data = pd.read_csv(input)
pandas_profiling.ProfileReport(data)

# ---------------

# --- DATA REFINEMENT ---

refined = data.iloc[:,[1,7,8,9,10,11,12,13]].copy()
refined.columns = ["country","date","retail","grocery","parks","transit","workplaces","residential"]

refined.date = pd.to_datetime(refined.date)
refined.index = refined.date
refined.drop(labels="date",axis=1,inplace=True)

countries = ['Greece', 'Sweden', 'Netherlands', 'Germany', 'Italy', 'France', 'Japan', 'United States', 'United Kingdom', 'Spain', 'Brazil', 'India']
refined_countries = refined.loc[~refined["retail"].isnull() & refined.country.isin(countries)]

# ---------------

# --- PLOTTING ---

size = (16,16)
dpi = 80
fig, ax = plt.subplots(nrows=3, ncols=2, figsize=size)

items = [["retail", "grocery"], ["parks", "transit"], ["workplaces", "residential"]]

for i, item_arr in enumerate(items):
  for j, item in enumerate(item_arr):
    brazil = refined_countries.groupby(by=[refined_countries.index, "country"]).mean().unstack()[item]["Brazil"].rolling(window=7, min_periods=1).mean()
    other_countries = refined_countries.groupby(by=[refined_countries.index, "country"]).mean().unstack()[item].drop('Brazil', axis=1).rolling(window=7, min_periods=1).mean() #.plot(legend=False, color="grey", linewidth=1, alpha=0.4, ax=ax)
    all_countries_means = refined_countries.groupby(by=[refined_countries.index, "country"]).mean().unstack()[item].rolling(window=7, min_periods=1).mean().mean(axis=1)

    index_py_dt = mdates.date2num(brazil.index.to_pydatetime())
    other_countries.index = mdates.date2num(other_countries.index.to_pydatetime())

    other_countries.plot(legend=False, color="grey", linewidth=1, alpha=0.5, ax=ax[i][j])

    points = np.array([index_py_dt, brazil.values]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    lc = LineCollection(segments, cmap='winter', linewidth=3)
    lc.set_array(brazil.values)
    ax[i][j].add_collection(lc)

    ax[i][j].xaxis.set_major_locator(mdates.MonthLocator())
    monthFmt = mdates.DateFormatter("%b")
    ax[i][j].xaxis.set_major_formatter(monthFmt)

    all_countries_means.plot(legend=False, color="red", linewidth=1, alpha=1, ax=ax[i][j])

    min_point_id = brazil.idxmin()
    last_x_id = brazil.tail(1).index[0]

    ax[i][j].plot((min_point_id, last_x_id), (brazil[min_point_id], brazil[min_point_id]), 'k--')
    ax[i][j].plot((last_x_id, last_x_id), (brazil[min_point_id], brazil[last_x_id]), 'r--')

    ax[i][j].plot(last_x_id, brazil[last_x_id], marker="o", color="Black")
    ax[i][j].plot(min_point_id, brazil[min_point_id], marker="o", color="Black")

    ax[i][j].annotate(int(brazil[min_point_id]),
                     (min_point_id, brazil[min_point_id]),
                     textcoords="offset points",
                     xytext=(0,-15),
                     ha='right')

    ax[i][j].annotate(int(brazil[last_x_id]),
                     (last_x_id, brazil[last_x_id]),
                     textcoords="offset points",
                     xytext=(0,10),
                     ha='right')

    improvements_val = brazil[min_point_id] - brazil[last_x_id]
    impr_percent = improvements_val / brazil[min_point_id]

    ax[i][j].annotate("{0:.0%}".format(impr_percent),
                     (last_x_id, brazil[min_point_id]),
                     textcoords="offset points",
                     xytext=(0,5),
                     ha='right')

    ax[i][j].yaxis.tick_right()
    ax[i][j].set_xlabel("")
    ax[i][j].set_title(f"For {item}", fontsize=12)

    if i == 0 and j == 0:
      legend_elements = [Line2D([0], [0], color='blue', lw=4, label='Brazil'),
                        Line2D([0], [0], color='gray', lw=2, label='Other countries'),
                        Line2D([0], [0], color='red', lw=2, label='Mean of countries')]
      ax[i][j].legend(handles=legend_elements, loc='upper left')

fig.suptitle("Evaluation of the Social Distancing in Brazil during COVID-19 outbreak, 2020", fontsize=14)
plt.savefig("data/brazil_covid19_evaluation.png", dpi=dpi)

# ---------------
