#######################################################
#Data Analysis and Interpretation (Wesleyen)
#######################################################
import pandas as pd
import numpy as np
import scipy.stats as stats
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf 
import statsmodels.stats.multicomp as multi
%matplotlib inline

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
stats.kurtosis(distribution)

#note that shape of distribution can alter with degrees of freedom
chi_squared_df2 = np.random.chisquare(2, size=10000)
stats.skew(chi_squared_df2)

chi_squared_df5 = np.random.chisquare(5, size=10000)
stats.skew(chi_squared_df5)
#gaussian mixed models are ideal for bimodal distributions, esp when clustering data

#alpha denotes how much chance our models allow (eg 0.01, 0.05, 0.1 for surveys)
#ttests compare independent sample means, but choice of test should depend on distribution
#remedies for dredging: 
#1) bonferroni correction tightens alpha value based on number of tests running (conservative choice)
#2) hold-out some data for testing to see how generaliable (for maching learning for building predictive models)
#3) pre-registration: outline what you expect to find and why (burden is with theory)

#######################################################
##ANOVA example
data = pd.read_csv('/Users/wiseer85/Desktop/nesarc_pds.csv', low_memory=False)

# set variables you will be working with to numeric
data['TAB12MDX'] = pd.to_numeric(data['TAB12MDX'], errors='coerce')
data['CHECK321'] = pd.to_numeric(data['CHECK321'], errors='coerce')
data['S3AQ3B1'] = pd.to_numeric(data['S3AQ3B1'], errors='coerce')
data['S3AQ3C1'] = pd.to_numeric(data['S3AQ3C1'], errors='coerce')
data['AGE'] = pd.to_numeric(data['AGE'], errors='coerce')

#subset data to young adults age 18 to 25 who have smoked in the past 12 months
sub1=data[(data['AGE']>=18) & (data['AGE']<=25) & (data['CHECK321']==1)]

#make a copy of my new subsetted data
sub2 = sub1.copy()

# recode missing values to python missing (NaN)
sub2['S3AQ3B1']=sub2['S3AQ3B1'].replace(9, np.nan)
sub2['S3AQ3C1']=sub2['S3AQ3C1'].replace(99, np.nan)

#recoding values for S3AQ3B1 into a new variable, USFREQMO
recode1 = {1: 30, 2: 22, 3: 14, 4: 6, 5: 2.5, 6: 1}
sub2['USFREQMO']= sub2['S3AQ3B1'].map(recode1)

#Creating a secondary variable multiplying the days smoked/month and the number of cig/per day
#this is a moderating variable or statistical interaction 
sub2['NUMCIGMO_EST']=sub2['USFREQMO'] * sub2['S3AQ3C1']

# using ols function for calculating the F-statistic and associated p value
model1 = smf.ols(formula='NUMCIGMO_EST ~ C(MAJORDEPLIFE)', data=sub2)
results1 = model1.fit()
print(results1.summary())

#store posthoc test results using Tukey for pairs when F statistic is significant
mc1 = multi.MultiComparison(sub2['NUMCIGMO_EST'], sub2['ETHRACE2A'])
res1 = mc1.tukeyhsd()
print(res1.summary())

# contingency table of observed counts
ct1=pd.crosstab(sub2['TAB12MDX'], sub2['USFREQMO'])
print (ct1)

# column percentages
colsum=ct1.sum(axis=0)
colpct=ct1/colsum
print(colpct)

# chi-square
print ('chi-square value, p value, expected counts')
cs1= stats.chi2_contingency(ct1)
print (cs1)

# set variable types 
sub2["USFREQMO"] = sub2["USFREQMO"].astype('category')
# new code for setting variables to numeric:
sub2['TAB12MDX'] = pd.to_numeric(sub2['TAB12MDX'], errors='coerce')

# graph percent with nicotine dependence within each smoking frequency group 
sns.factorplot(x="USFREQMO", y="TAB12MDX", data=sub2, kind="bar", ci=None)
plt.xlabel('Days smoked per month')
plt.ylabel('Proportion Nicotine Dependent')

recode2 = {1: 1, 2.5: 2.5}
sub2['COMP1v2']= sub2['USFREQMO'].map(recode2)

# contingency table of observed counts
ct2=pd.crosstab(sub2['TAB12MDX'], sub2['COMP1v2'])
print(ct2)

# column percentages
colsum=ct2.sum(axis=0)
colpct=ct2/colsum
print(colpct)

print('chi-square value, p value, expected counts')
cs2= stats.chi2_contingency(ct2)
print(cs2)

recode3 = {1: 1, 6: 6}
sub2['COMP1v6']= sub2['USFREQMO'].map(recode3)

# contingency table of observed counts
ct3=pd.crosstab(sub2['TAB12MDX'], sub2['COMP1v6'])
print (ct3)

# column percentages
colsum=ct3.sum(axis=0)
colpct=ct3/colsum
print(colpct)

print('chi-square value, p value, expected counts')
cs3= stats.chi2_contingency(ct3)
print(cs3)

recode4 = {1: 1, 14: 14}
sub2['COMP1v14']= sub2['USFREQMO'].map(recode4)

# contingency table of observed counts
ct4=pd.crosstab(sub2['TAB12MDX'], sub2['COMP1v14'])
print (ct4)

# column percentages
colsum=ct4.sum(axis=0)
colpct=ct4/colsum
print(colpct)

print('chi-square value, p value, expected counts')
cs4= stats.chi2_contingency(ct4)
print(cs4)

recode5 = {1: 1, 22: 22}
sub2['COMP1v22']= sub2['USFREQMO'].map(recode5)

# contingency table of observed counts
ct5=pd.crosstab(sub2['TAB12MDX'], sub2['COMP1v22'])
print (ct5)

# column percentages
colsum=ct5.sum(axis=0)
colpct=ct5/colsum
print(colpct)

print('chi-square value, p value, expected counts')
cs5= stats.chi2_contingency(ct5)
print(cs5)

recode6 = {1: 1, 30: 30}
sub2['COMP1v30']= sub2['USFREQMO'].map(recode6)

# contingency table of observed counts
ct6=pd.crosstab(sub2['TAB12MDX'], sub2['COMP1v30'])
print(ct6)

# column percentages
colsum=ct6.sum(axis=0)
colpct=ct6/colsum
print(colpct)

print('chi-square value, p value, expected counts')
cs6= stats.chi2_contingency(ct6)
print(cs6)

recode7 = {2.5: 2.5, 6: 6}
sub2['COMP2v6']= sub2['USFREQMO'].map(recode7)

# contingency table of observed counts
ct7=pd.crosstab(sub2['TAB12MDX'], sub2['COMP2v6'])
print(ct7)

# column percentages
colsum=ct7.sum(axis=0)
colpct=ct7/colsum
print(colpct)

print('chi-square value, p value, expected counts')
cs7=stats.chi2_contingency(ct7)
print(cs7)
