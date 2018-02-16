#######################################################
#Applied Data Science in Python (University of Michigan)
#######################################################
##Principals of Visualization
##the visualization wheel
#abstraction - figuration: boxes and charts or real-world objects
#functionality - decoration: no embellishments or artistic
#density - lightness: studied in depth or on the surface
#multidimensional - unidimensional:  different aspects of a henomena or sinle items
#originality - familiarity: novel methods of visualization or established methods
#novelty - redundancy: explainint each item once or encoding multiple explanations of the same phenomenon

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec

#scatter plot
plt.figure()
plt.plot(3,2,'o')
ax = plt.gca()
ax.axis([0,6,0,10]) #min, max, corr y min, corr ymax

ax = plt.gca()
ax.get_children()

x = np.array([1,2,3,4,5,6,7,8])
y = x
colors = ['green']*(len(x)-1)
colors.append('red')

plt.figure()
plt.scatter(x[:2],y[:2], s=100, c='red', label='Tall Students')
plt.scatter(x[2:],y[2:], s=100, c='blue', label='Short Students')

plt.xlabel('The number of times the child hit the ball')
plt.ylabel('The grade of the child')
plt.title('Relationship between balls kicked and grade')
plt.legend(loc=4, frameon=False, title='Legend')

#line plot
import numpy as np
linear_data = np.array([1,2,3,4,5,6,7,8])
quadratic_data = linear_data**2

plt.figure()
plt.plot(linear_data, '-o', quadratic_data, '-o')

plt.plot([22,44,55], '--r')

import pandas as pd
plt.figure()
observation_dates = np.arange('2017-01-01', '2017-01-09', dtype='datetime64[D]')
observation_dates=list(map(pd.to_datetime, observation_dates))
plt.plot(observation_dates, linear_data, '-o',
          observation_dates, quadratic_data, '-o')

#bar plot
plt.figure()
xvals = range(len(linear_data))
plt.bar(xvals, linear_data, width = 0.3)

new_xvals = []
for item in xvals:
    new_xvals.append(item+0.3)
    
plt.bar(new_xvals, quadratic_data, width=0.3, color='red')    

#stacked bar graph
plt.figure()
xvals = range(len(linear_data))
plt.barh(xvals, linear_data, width=0.3, color='b')
plt.barh(xvals, quadratic_data, width=0.3, bottom=linear_data, color='r')    
    
#box plot
from random import randint
linear_err = [randint(0,15) for x in range(len(linear_data))]
plt.bar(xvals, linear_data, width=0.3, yerr=linear_err)
    

#######################################################
#example

plt.figure()
languages =['Python', 'SQL', 'Java', 'C++', 'JavaScript']
pos = np.arange(len(languages))
popularity = [56, 39, 34, 34, 29]

# change the bar color to be less bright blue
bars = plt.bar(pos, popularity, align='center', linewidth=0, color='lightslategrey')
# make one bar, the python bar, a contrasting color
bars[0].set_color('#1F77B4')

# soften all labels by turning grey
plt.xticks(pos, languages, alpha=0.8)
# remove the Y label since bars are directly labeled
#plt.ylabel('% Popularity', alpha=0.8)
plt.title('Top 5 Languages for Math & Data \nby % popularity on Stack Overflow', alpha=0.8)

# remove all the ticks (both axes), and tick labels on the Y axis
plt.tick_params(top='off', bottom='off', left='off', right='off', labelleft='off', labelbottom='on')

# remove the frame of the chart
for spine in plt.gca().spines.values():
    spine.set_visible(False)
    
# direct label each bar with Y axis values
for bar in bars:
    plt.gca().text(bar.get_x() + bar.get_width()/2, bar.get_height() - 5, str(int(bar.get_height())) + '%', 
                 ha='center', color='w', fontsize=11)
plt.show()     
  
#######################################################
##Charting Fundamentals

plt.figure()
plt.subplot(1,2,1)
linear_data=np.array([1,2,3,4,5,6,7,8])
plt.plot(linear_data, '-o')

#multiplots
linear_data=np.array([1,2,3,4,5,6,7,8])
exponential_data = linear_data**2
plt.subplot(1,2,2)
plt.plot(linear_data, '-o')

plt.subplot(1,2,1)
plt.plot(linear_data, '-x')

plt.figure()
ax1 = plt.subplot(1,2,1)
plt.plot(linear_data, '-o')
ax2 = plt.subplot(1,2,2, sharey=ax1)
plt.plt(explonential_data, '-x')

#subplots parameters
plt.figure()
plt.subplot(1,2,1) == plt.subplot(121)

fig, ((ax1,ax2,ax3), (ax4, ax5, ax5), (ax7,ax8,ax9)) = plt.subplots(3,3,sharex=True,sharey=True)
ax5.plot(linear_data, '-')

for ax in plt.gcf().get_axes():
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_visible(True)

plt.gcf().canvas.draw()

#plot a histogram
#consider whether 1) the distribution is normal, bimodal or uniformal as well as
#whether 2) distribution is skewed left or right and 3) the spread or variability (e.g. SD)
#the value of the distribution can be captured by the mode, median or mean
fig, ((ax1,ax2), (ax3,ax4)) = plt.subplots(2,2,sharex=True)
axs = [ax1,ax2,ax3,ax4]

for n in range(0,len(axs)):
    sample_size = 10**(n+1)
    sample = np.random.normal(loc=0.0,scale=1.0, size=sample_size)
    axs[n].hist(sample, bins=100)
    axs[n].set_title('n={}'.format(sample_size))

# plot scatter with histogram via indexing operator gridspec
plt.figure()
Y = np.random.normal(loc=0.0, scale=1.0, size=10000)
X = np.random.random(size=10000)
plt.scatter(X,Y)

#subplot with gridspec
plt.figure()
gspec=gridspec.GridSpec(3,3)

top_histogram = plt.subplot(gspec[0,1:]) #row 0, element 1
side_histogram = plt.subplot(gspec[1:,0])
lower_right = plt.subplot(gspec[1:, 2:])

top_histopgram.hist(X, Bins=100)
s = side_histogram.hist(Y, bins=100, orientation='horizontal')

top_histogram.clear()
top_histogram.hist(X, bins=100, normed=True)
side_histogram.clear()
side-histogram.hist(Y, bins=100, orientation='horizontal')
side_histogram.invert_xaxis()

for ax in [top_histogram, lower_right]:
    ax.set_xlim(0,1)
for ax in [side_histogram, lower_right]:
    ax.set_ylim(-5,5)

#box plots
normal_sample = np.random.normal(loc=0.0, scale=1.0, size=10000)
random_sample = np.random.random(size=10000)
gamma_sample = np.random.gamma(2, size=10000)

df = pd.DataFrame({'normal': normal_sample,
                   'random': random_sample,
                   'gamma': gamma_sample})
df.describe

plt.figure()
_ = plt.boxplot(df['normal'], whis='range')

plt.clf()
_ = plt.boxplot([df['normal'], df['random'], df['gamma']], whis='range')

plt.figure()
_ = plt.hist(df['gamma'], bins=100)

#axesgrid
import mpl_toolkits.axes_grid1.inset_locator as mpl_il
plt.figure()
plt.boxplot([df['normal'], df['random'], df['gamma']], whis='range')
ax2 = mpl_il.inset_axes(plt.gca(), width='60%', height='40%', loc=2)
ax2.hist(df['gamma'], bins=100)
ax2.margins(x=0.5)
ax2.yaxis.tick_right()