#######################################################
#Applied Data Science in Python (University of Michigan)
#######################################################
import pandas as pd
import numpy as np

##Basic Data Processing
#the dataframe data structure: attribute is column, tuple a row and relation a set of tuples that have the same attributes 
purchase_1 = pd.Series({'Name': 'Chris', 'Item': 'Dog food', 'Cost': 22.50})
purchase_2 = pd.Series({'Name': 'Kevyn', 'Item': 'Kitty litter', 'Cost': 2.50})
purchase_3 = pd.Series({'Name': 'Vince', 'Item': 'Bird seed', 'Cost': 5.00})
df = pd.DataFrame([purchase_1, purchase_2, purchase_3], index=['Store 1', 'Store 2', 'Store 3'])
df.head()

##Pandas
#pandas are a form of vectorization 
total=np.sum(n)
print(total)

#calculate number of iterations with np
%%timeit -n 100
summary = np.sum(s)

#compare with basic command
%%timeit -n 100 
summary = 0
for item in s:
    summary += item

#pandas will override what is in your dictionary key list
#to querry by number us iloc, to querry by attribute, use lock attribute
import pandas as pd
sports = {'Basketball': 'USA',
          'Golf': 'Scotland',
          'Sumo': 'Japan',
          'Soccer': 'Germany'}
s=pd.Series(sports)
s.iloc[3]
s.loc['Golf']

#merge a data frame with boolean mask to index data into a new framework
staff_df = pd.DataFrame([{'Name': 'Kelly', 'Role': 'Director'},
                       {'Name': 'Sally', 'Role': 'Liason'},
                       {'Name': 'James', 'Role': 'Grader'}])
staff_df = staff_df.set_index('Name')
student_df = pd.DataFrame([{'Name': 'Mike', 'School': 'Law'},
                       {'Name': 'Sally', 'School': 'Engineering'},
                       {'Name': 'James', 'School': 'Business'}])
student_df = student_df.set_index('Name')
print(staff_df)
print(student_df)

#generate summary tables
staff_df = staff_df.reset_index()
student_df = student_df.reset_index()
pd.merge(staff_df, student_df, how='left', left_on='Name', right_on='Name') #student df
pd.merge(staff_df, student_df, how='right', left_on='Name', right_on='Name') #staff df
pd.merge(staff_df, student_df, how='outer', left_on='Name', right_on='Name') #either df
pd.merge(staff_df, student_df, how='inner', left_index=True, right_index=True) #both df

#pivot tables allows comparison of columns against rows
df = pd.read_csv('/Users/wiseer85/Desktop/cars.csv')
df.pivot_table(values='(kW)', index='YEAR', columns='Make', aggfunc=np.mean)
#print(pd.pivot_table(Bikes, index=['Manufacturer','Bike Type']))

#scales
#ratio scales: units are equally spaced, mathematical operations are valid, eg height or weight
#interval scales: units are equally spaced, but there is no true zero
#ordinal scale: order of units is important, but not spacing, eg letter grades
#nominal scales: categories of data without order, eg sports teams

#recast as ordered categorical data
s = pd.Series(['Low', 'Low', 'High', 'Medium', 'Low', 'High', 'Low'])
s.astype('category', categories=['Low', 'Medium', 'High'], ordered=True)

#method chaining 
#every object returns a reference on that objects, which can be condenced into one line of code
import pandas as pd
df = pd.read_csv('/Users/wiseer85/Desktop/census.csv')

#traditional method
df = df[df['SUMLEV'] == 50]
df.set_index(['STNAME','CTYNAME'], inplace=True)
df.rename(columns={'ESTIMATESBASE2010': 'Estimates Base 2010'})

#pandorable method
(df.where(df['SUMLEV'] == 50)
    .dropna()
    .set_index(['STNAME', "CTYNAME"])
    .rename(columns={'ESTIMATESBASE2010': 'Estimates Base 2010'}))

#group and manipulate df
import numpy as np
def min_max(row):
        data = row[['POPESTIMATE2010',
                    'POPESTIMATE2011',
                    'POPESTIMATE2012',
                    'POPESTIMATE2013',
                    'POPESTIMATE2014',
                    'POPESTIMATE2015']]
        return pd.Series({'min': np.min(data), 'max': np.max(data)})
df.apply(min_max, axis=1) #applies across all rows

#using lambdas 
rows = ['POPESTIMATE2010',
         'POPESTIMATE2011',
         'POPESTIMATE2012',          
         'POPESTIMATE2013',
         'POPESTIMATE2014',
         'POPESTIMATE2015']
df.apply(lambda x: np.max(x[rows]), axis=1)

#group functions (more efficient than loops to group data by a column)
import pandas as pd
import numpy as np
df = pd.read_csv('/Users/wiseer85/Desktop/census.csv')
df = df[df['SUMLEV'] == 50]

#reduce data frame and calculate the average time it takes
%%timeit -n 10 
for group, frame in df.groupby('STNAME'):
    avg = np.average(frame['CENSUS2010POP'])
    print('Counties in state ' + group + ' have an average population of ' + str(avg))

#segment data frame by distributing tasks
df = df. set_index('STNAME')
def fun(item):
    if item[0] < 'M':
        return 0
    if item[0] < 'Q':
        return 1
    return 2

for group, frame in df.groupby(fun):
    print('There are ' + str(len(frame)) + ' records in group ' +
    str(group) + ' for processing.')

#aggregate method by df or series
df = pd.read_csv('/Users/wiseer85/Desktop/census.csv')
df = df[df['SUMLEV'] == 50]

#print average population of counties by state in 2010
df.groupby('STNAME').agg({'CENSUS2010POP': np.average})       

#print average and sum population for 2010 and 2011
(df.set_index('STNAME').groupby(level=0)['POPESTIMATE2010', 'POPESTIMATE2011'].agg({'avg': np.average, 'sum': np.sum}))
