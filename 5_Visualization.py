#######################################################
#Applied Data Science in Python (University of Michigan)
#######################################################
import numpy as np
import pandas as pd
import scipy
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
%matplotlib inline

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
#example 1
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

#seaborn
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
grid.ax_joint.set_aspect('equal')
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


############################################################
#Example 2 from Data Analysis and Interpretation (Wesleyan)
############################################################
data = pd.read_csv('/Users/wiseer85/Desktop/nesarc_pds.csv', low_memory=False)

#Set PANDAS to show all columns in DataFrame
pd.set_option('display.max_columns', None)
#Set PANDAS to show all rows in DataFrame
pd.set_option('display.max_rows', None)

# bug fix for display formats to avoid run time errors
pd.set_option('display.float_format', lambda x:'%f'%x)

#setting variables you will be working with to numeric
data['TAB12MDX'] = pd.to_numeric(data['TAB12MDX'], errors='coerce')
data['CHECK321'] = pd.to_numeric(data['CHECK321'], errors='coerce')
data['S3AQ3B1'] = pd.to_numeric(data['S3AQ3B1'], errors='coerce')
data['S3AQ3C1'] = pd.to_numeric(data['S3AQ3C1'], errors='coerce')
data['S2AQ8A'] = pd.to_numeric(data['S2AQ8A'], errors='coerce')
data['AGE'] = pd.to_numeric(data['AGE'], errors='coerce')

#subset data to young adults age 18 to 25 who have smoked in the past 12 months
sub1=data[(data['AGE']>=18) & (data['AGE']<=25) & (data['CHECK321']==1)]

#make a copy of my new subsetted data
sub2 = sub1.copy()

#SETTING MISSING DATA
# recode missing values to python missing (NaN)
sub2['S3AQ3B1']=sub2['S3AQ3B1'].replace(9, np.nan)
# recode missing values to python missing (NaN)
sub2['S3AQ3C1']=sub2['S3AQ3C1'].replace(99, np.nan)

recode1 = {1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}
sub2['USFREQ']= sub2['S3AQ3B1'].map(recode1)

recode2 = {1: 30, 2: 22, 3: 14, 4: 5, 5: 2.5, 6: 1}
sub2['USFREQMO']= sub2['S3AQ3B1'].map(recode2)

# A secondary variable multiplying the number of days smoked/month and the approx number of cig smoked/day
sub2['NUMCIGMO_EST']=sub2['USFREQMO'] * sub2['S3AQ3C1']

#univariate bar graph for categorical variables
# First hange format from numeric to categorical
sub2["TAB12MDX"] = sub2["TAB12MDX"].astype('category')

seaborn.countplot(x="TAB12MDX", data=sub2)
plt.xlabel('Nicotine Dependence past 12 months')
plt.title('Nicotine Dependence in the Past 12 Months Among Young Adult Smokers in the NESARC Study')

#Univariate histogram for quantitative variable:
seaborn.distplot(sub2["NUMCIGMO_EST"].dropna(), kde=False);
plt.xlabel('Number of Cigarettes per Month')
plt.title('Estimated Number of Cigarettes per Month among Young Adult Smokers in the NESARC Study')

# standard deviation and other descriptive statistics for quantitative variables
print('describe number of cigarettes smoked per month')
desc1 = sub2['NUMCIGMO_EST'].describe()
print(desc1)

c1= sub2.groupby('NUMCIGMO_EST').size()
print(c1)

print('describe nicotine dependence')
desc2 = sub2['TAB12MDX'].describe()
print(desc2)

c1= sub2.groupby('TAB12MDX').size()
print(c1)

print('mode')
mode1 = sub2['TAB12MDX'].mode()
print(mode1)

print('mean')
mean1 = sub2['NUMCIGMO_EST'].mean()
print(mean1)

print('std')
std1 = sub2['NUMCIGMO_EST'].std()
print(std1)

print('min')
min1 = sub2['NUMCIGMO_EST'].min()
print(min1)

print('max')
max1 = sub2['NUMCIGMO_EST'].max()
print(max1)

print('median')
median1 = sub2['NUMCIGMO_EST'].median()
print(median1)

print('mode')
mode1 = sub2['NUMCIGMO_EST'].mode()
print(mode1)

c1= sub2.groupby('TAB12MDX').size()
print(c1)

p1 = sub2.groupby('TAB12MDX').size() * 100 / len(data)
print(p1)

c2 = sub2.groupby('NUMCIGMO_EST').size()
print(c2)

p2 = sub2.groupby('NUMCIGMO_EST').size() * 100 / len(data)
print(p2)

# A secondary variable multiplying the number of days smoked per month and the approx number of cig smoked per day
sub2['PACKSPERMONTH']=sub2['NUMCIGMO_EST'] / 20

c2= sub2.groupby('PACKSPERMONTH').size()
print(c2)

sub2['PACKCATEGORY'] = pd.cut(sub2.PACKSPERMONTH, [0, 5, 10, 20, 30, 147])

# change format from numeric to categorical
sub2['PACKCATEGORY'] = sub2['PACKCATEGORY'].astype('category')

print('describe PACKCATEGORY')
desc3 = sub2['PACKCATEGORY'].describe()
print(desc3)

print('pack category counts')
c7 = sub2['PACKCATEGORY'].value_counts(sort=False, dropna=True)
print(c7)

sub2['TAB12MDX'] = pd.to_numeric(sub2['TAB12MDX'], errors='coerce')

# bivariate bar graph C->Q
seaborn.factorplot(x='PACKCATEGORY', y='TAB12MDX', data=sub2, kind="bar", ci=None)
plt.xlabel('Packs per Month')
plt.ylabel('Proportion Nicotine Dependent')

#creating 3 level smokegroup variable
def SMOKEGRP (row):
   if row['TAB12MDX'] == 1 :
      return 1
   elif row['USFREQMO'] == 30 :
      return 2
   else :
      return 3
         
sub2['SMOKEGRP'] = sub2.apply (lambda row: SMOKEGRP (row),axis=1)

c3= sub2.groupby('SMOKEGRP').size()
print(c3)

#creating daily smoking vairable
def DAILY (row):
   if row['USFREQMO'] == 30 :
      return 1
   elif row['USFREQMO'] != 30 :
      return 0
      
sub2['DAILY'] = sub2.apply (lambda row: DAILY (row),axis=1)
      
c4= sub2.groupby('DAILY').size()
print(c4)

# you can rename categorical variable values for graphing if original values are not informative 
# first change the variable format to categorical if you haven’t already done so
sub2['ETHRACE2A'] = sub2['ETHRACE2A'].astype('category')
# second create a new variable (PACKCAT) that has the new variable value labels
sub2['ETHRACE2A']=sub2['ETHRACE2A'].cat.rename_categories(["White", "Black", "NatAm", "Asian", "Hispanic"])

# bivariate bar graph C->C
seaborn.factorplot(x='ETHRACE2A', y='DAILY', data=sub2, kind="bar", ci=None)
plt.xlabel('Ethnic Group')
plt.ylabel('Proportion Daily Smokers')

#check to see if missing data were set to NaN 
print('counts for S3AQ3C1 with 99 set to NAN and number of missing requested')
c4 = sub2['S3AQ3C1'].value_counts(sort=False, dropna=False)
print(c4)

print('counts for TAB12MDX - past 12 month nicotine dependence')
c5 = sub2['TAB12MDX'].value_counts(sort=False)
print(c5)
