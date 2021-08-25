


#######################################################
## Week 4: Statistical Analysis in Python
#distributions
#hypothesis testing

#distribution: set of all possible random variables
#binomial distribution (two possible outcomes)
#discrete distribution (categorical comparison)
#evenly weighted

import pandas as pd
import numpy as np

#run simulation with np.random.binomial(n,p,size)
np.random.binomial(1, 0.5)
np.random.binomial(1000, 0.5)/1000

#if flipped 20 times, what is the propotion of flips that are 15 or more
x = np.random.binomial(20, .5, 10000)
print((x>=15).mean())

#np.random.uniform (0,1)
#np.random.normal(0.75)

#standard deviation
distribution = np.random.normal(0.75, size=1000)
np.sqrt(np.sum((np.mean(distribution)-distribution)**2)/len(distribution))
np.std(distribution)

#kurtosis
import scipy.stats as stats
stats.kurtosis(distribution)

#note that shape of distribution can alter with degrees of freedom
chi_squared_df2 = np.random.chisquare(2, size=10000)
stats.skew(chi_squared_df2)

chi_squared_df5 = np.random.chisquare(5, size=10000)
stats.skew(chi_squared_df5)
#gaussian mixed models are ideal for bimodal distributions, esp when clustering data

#hypothesis testing: a statement we can test
#alternative hypothesis: our idea, eg there is a difference between groups
#null hypothesis: the alternative of our idea, eg there is not a difference between groups
df = pd.read_csv('/Users/wiseer85/Desktop/grades.csv')
len(df) #number of entries 

#create two groups and compare means
early = df[df['assignment1_submission'] <= '2015-12-31']
late = df[df['assignment1_submission'] > '2015-12-31']
early.mean()
late.mean()

#alpha denotes how much chance our models allow (eg 0.01, 0.05, 0.1 for surveys)
#ttests compare independent sample means, but choice of test should depend on distribution
from scipy import stats
stats.ttest_ind?
stats.ttest_ind(early['assignment1_grade'], late['assignment1_grade'])
#remedies for dredging: 
#1) bonferroni correction tightens alpha value based on number of tests running (conservative choice)
#2) hold-out some data for testing to see how generaliable (for maching learning for building predictive models)
#3) pre-registration: outline what you expect to find and why (burden is with theory)



#######################################################
#Course 2: Representation in Python
#######################################################
##the visualization wheel
#abstraction - figuration: boxes and charts or real-world objects
#functionality - decoration: no embellishments or artistic
#density - lightness: studied in depth or on the surface
#multidimensional - unidimensional:  different aspects of a henomena or sinle items
#originality - familiarity: novel methods of visualization or established methods
#novelty - redundancy: explainint each item once or encoding multiple explanations of the same phenomenon
#######################################################
## Week 1: Principals of Visualization
import matplotlib.pyplot as plt

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

fig = Figure()
canvas = FigureCanvasAgg(fig)

ax = fig.add_subplot(111)
ax.plot(3,2,'.')
canvas.print_png('test.png')
%%html
<img src='test.png' />

#######################################################
## Week 2: Basic Charting
#scatter plot
plt.figure()
plt.plot(3,2,'o')
ax = plt.gca()
ax.axis([0,6,0,10]) #min, max, corr y min, corr ymax

ax = plt.gca()
ax.get_children()

import numpy as np
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

#set rotation function
x = plt.gca().xaxis
for item in x.get_ticklabels():
    item.set_rotation(45)
plt.subplots_adjust(bottom=0.25)

#bar plot
plt.figure()
xvals = range(len(linear_data))
plt.bar(xvals, linear_data, width = 0.3)

new_xvals = []
for item in xvals:
    new_xvals.append(item+0.3)
    
plt.bar(new_xvals, quadratic_data, width=0.3, color='red')    

#box plot
from random import randint
linear_err = [randint(0,15) for x in range(len(linear_data))]
plt.bar(xvals, linear_data, width=0.3, yerr=linear_err)
    
#stacked bar graph
plt.figure()
xvals = range(len(linear_data))
plt.bar(xvals, linear_data, width=0.3, color='b')
plt.bar(xvals, quadratic_data, width=0.3, bottom=linear_data, color='r')    
    
#horizontal bar graph
plt.figure()
xvals = range(len(linear_data))
plt.barh(xvals, linear_data, width=0.3, color='b')
plt.barh(xvals, quadratic_data, height=0.3, left=linear_data, color='r')    

#example
import matplotlib.pyplot as plt
import numpy as np

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
## Week 3: Charting Fundamentals

%matplotlib notebook
import matplotlib.pyplot as plt
import numpy as np

plt.figure()
plt.subplot(1,2,1)
linear_data=np.array([1,2,3,4,5,6,7,8])
plt.plot(linear_data, '-o')

#multiplots
exponential_data = lindear_data**2
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

fig, ((ax1,ax2,ax3), (ax4, ax5, ax5), (ax7,ax8,ax9)) = plt.subplots(3,3,sharex=Trues,sharey=True)
ax5.plot(linear_data, '-')

for ax in plt.gcf().get_axes():
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_visible(True)

plt.gcf().canvas.draw()

#plot a histogram
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

import matplotlib.gridspec as gridspec
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
import pandas as pd
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
plt,boxplot([df['normal'], df['random'], df['gamma']], whis='range')
ax2 = mpl_il.inset_axes(plt.gca(), width='60%', height='40%', loc=2)
ax2.hist(df['gamma'], bins=100)
ax2.margins(x=0.5)
ax2.yaxis.tick_right()


#######################################################
## Week 4: Applied Visualizations

import panas as pd
import numpy as np
import matplotlib.pyplot as plt

%matplotlib notebook
plt.style.use('seaborn-colorblind')

np.random.seed(123)
df = pd.DataFrame({'A': np.random.randn(365).cumsum(0),
                   'B': np.random.randn(365).cumsum(0)+20,
                   'C': np.random.randn(365).cumsum(0)-20},
    index=pd.date_range('1/1/2017, periods=365))

df.plot();

df.plot('A', 'B', kind = 'scatter');

df.plot('A', 'C', c='B', s=df['B'], colormap = 'viridis');

ax = df.plot.scatter('A', 'C', c='B', s=df['B'], colormap = 'viridis')
ax.set_aspect('equal')

df.plot.box()
df.plot.hist(alpha=0.7);
df.plot.kde(); 
iris = pd.read_csv('iris.csv')
iris.head()
pd.tools.plotting.scatter_matrix(iris);

#parallel coordinate plots
plt.figure()
pd.tools.plotting.parallel_coordinates(iris, 'Name');

#seabornimport seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
%matplotlib notebook

np.random.seed(1234)
v1 = pd.Series(np.random.normal(0,10,1000), name='v1')
v2 = pd.Series(2*v1 + np.random.normal(60,15,1000), name='v2')

plt.figure()
plt.hist(v1,alpha=0.7, bins=np.arange(-50,150,5), label='v1')
plt.hist(v2,alpha=0.7, bins=np.arange(-50,150,5), label='v2')
plt.legend();

plt.figure()
plt.hist([v1, v2], histtype='barstacked', normed=True);
v3 = np.concatenate((v1,v2))
sns.kdeplot(v3);

plt.figure()
sns.distplot(v3, hist_kws={'color': 'Teal'}, kde_kws={'color': 'Navy'});

#joint plots
sns.jointplot(v1, v2, alpha=0.4);
grid = sns.jointplot(v1, v2, alpha=0.4);
grix.ax_joint.set_aspect('equal')
sns.jointplot(v1, v2, kind='hex'); 

sns.set_style('white')
sns.jointplot(v1, v2, kind='kde', space=0);
iris = pd.read_csv('iris.csv')
iris.head()
sns.pairplt(iris, hue='Name', diag_kind='kde');

#violin plot
plt.figure(figsize=(12,8))
plt.subplot(121)
sns.swarmplot('name', 'PetalLength', data=iris);
plt.subplot(122)
sns.violinplot('Name', 'PetalLength', data=iris);


#######################################################
#Course 3: Machine Learning
####################################################### 



#######################################################   
#Course 4: Text Mining
#######################################################



#######################################################   
#Course 5: Social Network Analysis
#######################################################






plt.gca().fill_between[range(len(linear_data)),
       linear_data, quadratic_data, 
       facecolor = 'blue', 
       alpha=0.25]


