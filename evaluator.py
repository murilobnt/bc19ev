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

# ---------------

# --- DATA REFINEMENT ---

# Select the columns.

refined = data.iloc[:,[1,7,8,9,10,11,12,13]].copy()
refined.columns = ["country","date","retail","grocery","parks","transit","workplaces","residential"]

# Set date as the index of the dataframe.

refined.date = pd.to_datetime(refined.date)
refined.index = refined.date
refined.drop(labels="date",axis=1,inplace=True)

# Select the countries.

countries = ['Greece', 'Sweden', 'Netherlands', 'Germany', 'Italy', 'France', 'Japan', 'United States', 'United Kingdom', 'Spain', 'Brazil', 'India']
refined_countries = refined.loc[~refined["retail"].isnull() & refined.country.isin(countries)]

# ---------------

# --- PLOTTING ---

# Set the dimensions and creating subplots.

size = (16,16)
dpi = 80
fig, ax = plt.subplots(nrows=3, ncols=2, figsize=size)

# Set the items to be displayed in each row/column.

items = [["retail", "grocery"], ["parks", "transit"], ["workplaces", "residential"]]

# Iterate through them.

for i, item_arr in enumerate(items):
  for j, item in enumerate(item_arr):
    # Define the series of data of Brazil, the other countries and the means.

    brazil = refined_countries.groupby(by=[refined_countries.index, "country"]).mean().unstack()[item]["Brazil"].rolling(window=7, min_periods=1).mean()
    other_countries = refined_countries.groupby(by=[refined_countries.index, "country"]).mean().unstack()[item].drop('Brazil', axis=1).rolling(window=7, min_periods=1).mean()
    all_countries_means = refined_countries.groupby(by=[refined_countries.index, "country"]).mean().unstack()[item].rolling(window=7, min_periods=1).mean().mean(axis=1)

    # Transform the index to pydatetime with mdates.

    index_py_dt = mdates.date2num(brazil.index.to_pydatetime())

    # Set the index of other_countries as the pydatetime.

    other_countries.index = mdates.date2num(other_countries.index.to_pydatetime())

    # Plot the other countries curve.

    other_countries.plot(legend=False, color="grey", linewidth=1, alpha=0.5, ax=ax[i][j])

    # Set points and segments for Brazil's line.

    points = np.array([index_py_dt, brazil.values]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Create a line collection for Brazil's line, using the winter cmap
    # (The lower, the darker blue).

    lc = LineCollection(segments, cmap='winter', linewidth=3)
    lc.set_array(brazil.values)

    # Add the line collection to the subplot.

    ax[i][j].add_collection(lc)

    # Format the pydatetime for the index.

    ax[i][j].xaxis.set_major_locator(mdates.MonthLocator())
    monthFmt = mdates.DateFormatter("%b")
    ax[i][j].xaxis.set_major_formatter(monthFmt)

    # Draw the canvas so it's possible to alter the label of the last xtick.

    fig.canvas.draw()

    # Plot the means curve.

    all_countries_means.plot(legend=False, color="red", linewidth=1, alpha=1, ax=ax[i][j])

    # Get the minimum and the last point of Brazil's data.

    min_point_id = brazil.idxmin()
    last_x_id = brazil.tail(1).index[0]

    # Plot the black dashed line in the X and the red dashed line in the Y.

    ax[i][j].plot((min_point_id, last_x_id), (brazil[min_point_id], brazil[min_point_id]), 'k--')
    ax[i][j].plot((last_x_id, last_x_id), (brazil[min_point_id], brazil[last_x_id]), 'r--')

    # Plot the two markers in the minimum and the last point of Brazil's
    # data.

    ax[i][j].plot(last_x_id, brazil[last_x_id], marker="o", color="Black")
    ax[i][j].plot(min_point_id, brazil[min_point_id], marker="o", color="Black")

    # Draw the yaxis grid with 45% opacity.

    ax[i][j].yaxis.grid(True, alpha=0.45)

    # Display the minimum and the last points of Brazil's data.

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

    # Calculate the improvements from the minimum and the last points of
    # Brazil's data.

    improvements_val = brazil[min_point_id] - brazil[last_x_id]
    impr_percent = improvements_val / brazil[min_point_id]

    # Display the improvements.

    ax[i][j].annotate("{0:.0%}".format(impr_percent),
                     (last_x_id, brazil[min_point_id]),
                     textcoords="offset points",
                     xytext=(0,5),
                     ha='right')

    # Set the yticks to right, erasing the xlabel and setting the title
    # of the subplot.

    ax[i][j].yaxis.tick_right()
    ax[i][j].set_xlabel("")
    ax[i][j].set_title(f"For {item}", fontsize=12)

    # For the first subplot, display the legend.

    if i == 0 and j == 0:
      legend_elements = [Line2D([0], [0], color='blue', lw=4, label='Brazil'),
                        Line2D([0], [0], color='gray', lw=2, label='Other countries'),
                        Line2D([0], [0], color='red', lw=2, label='Mean of countries')]
      ax[i][j].legend(handles=legend_elements, loc='upper left')

    # Add the 2020 to the last xtick of the subplot.

    labels = [item.get_text() for item in ax[i][j].get_xticklabels()]
    labels[-1] = labels[-1] + "\n2020"
    ax[i][j].set_xticklabels(labels)

# Set the title of the figure.

fig.suptitle("Overview of Brazil's Mobility Activities During the COVID-19 Outbreak, 2020", fontsize=14)

# Save the figure.

plt.savefig("data/brazil_covid19_evaluation.png", dpi=dpi)#, bbox_inches='tight')

# ---------------
