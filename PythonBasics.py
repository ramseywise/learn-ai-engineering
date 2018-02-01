#######################################################
# Python for Informatics (University of Michigan)
####################################################### 
##Intro to Python that covers basic operations, variables, expressions, 
##conditional statements and functions; it also covers loops, strings, 
##lists, tuples, dictionaries as well as retreiving and parsing data
#######################################################
#Chapter 2: Variables and Expressions  
var=2
print(var+2)

string = "Hello world!"
print(string)

inp = "75"
fahr = float(inp) 
cel=(fahr-32.0)*5.0/9.0
print(cel)

####################################################### 
#Chapter 3: Conditional Statements
x=5
if x%2==0:
    print("x is even")
else:
    print("x is odd")

try:
    x = int("seven")
except ValueError:
    print ("Oops!  That was no valid number.  Try again...")

#Exercise 3.1 Calculate pay with overtime
gpay=475
hours=45
rate=10
if hours>40:
    newrate=1.5*rate 
newpay=rate*40+newrate*5

####################################################### 
#Chapter 4: Functions
#random function can retrieve a random number within a range
import random
for i in range(10):
    x = random.random() 
print(x)

random.randint(5,100)

t=[1,2,3] 
random.choice(t)

#math function allow basic math operations
import math
decibels=10*math.log10(100)
print(decibels)

radians=45/360*2*math.pi
math.sin(radians)
math.sqrt(2)/2       
x = math.cos(radians)
golden = (math.sqrt(5) + 1) / 2
print(golden)
         
#define new functions
def print_lyrics():
        print("I sleep all night, ")
        print("and I work all day.")
print_lyrics()

def print_twice():
    print_lyrics()
    print_lyrics()
print_twice()

#define function that is already available in Python
def min(values):
    smallest = None
    for value in values:
        if smallest is None or itervar < smallest: 
            smallest = value
    return smallest
    
####################################################### 
#Chapter 5: Iteration (or loops)
#iteration updates a variable so that the new value depends on the old 
n=5 
while n>0:
    print(n)
    n=n-1
print("Blastoff!")

friends = ['Joseph', 'Glenn', 'Sally'] 
for friend in friends:
    print("Happy New Year:", friend) 

#Calculate count in sequence
count = 0
for itervar in [3, 41, 12, 9, 74, 15]:
    count = count + 1 
print("Count: ", count)

#Calculate sum with total
total=0
for itervar in [3, 41, 12, 9, 74, 15]:
    total = total + itervar 
print("Total: ", total)

#Identify the largest number in a sequence
largest = None
print("Before:", largest)
for itervar in [3, 41, 12, 9, 74, 15]:
    if largest is None or itervar > largest : 
        largest = itervar
    print("Loop:", itervar, largest)
print("Largest:", largest)

####################################################### 
#Chapter 6: Strings
#strings help identify characters in a sequence
fruit = 'banana' 
for char in fruit:
    print(char)

#use len function to identify last item in sequence
length=len(fruit)
last=fruit[length-1]
print(last)

#specify item from left or right with the first character as [0]    
fruit[:3]
fruit[3:]
fruit[:]

#Use a loop to count items in sequence
count = 0
for letter in fruit:
    if letter == 'a': 
        count = count + 1
print(count)

#change to uppercase
"a" in fruit
"seed" in fruit
FRUIT=fruit.upper()
print(FRUIT)

#use find to find characters in a string
fruit.find("na")

#strip spaces from text between quotations
line=" Here we go! "
line.strip()

#write conditional statements about text
line = 'Please have a nice day' 
line.startswith('Please')
line.startswith('p')
#change to lower case and try again
line.lower().startswith("p")

#use \n to return output lines
nextline = 'X\nY' 
print(nextline)

#format operator constructs strings and replaces parts stored in variables
camels=42
"%d"%camels
"I saw %d camels."%camels
'In %d years I have spotted %g %s.' % (3, 0.1, 'camels') 


#######################################################
#Chapter 7: Using Data Files
#use open for large files rather than reading in a file with input()
data_long = open("/Users/wiseer85/Desktop/mbox.txt")
count = 0
for line in data_long:
    count = count + 1 
print('Line Count:', count)

#save short files
with open("/Users/wiseer85/Desktop/mbox-short.txt", 'r') as infile:
    #NOTE: r is standard, rU is universal, rB is binary code, rT is text
    data = infile.read()
print(data)
len(data)

#import files from internet using requests
import requests
url = "http://www.py4inf.com/code/mbox-short.txt"
res = requests.get(url)
text = res.text
len(text)
print(text)

#strip specific words from text file by line
fhand = open("/Users/wiseer85/Desktop/mbox-short.txt",'r')
count=0
for line in fhand:
    if line.startswith("Subject:"): 
        count=count+1
print("There were",count,"subject lines")
    
#same thing using find words in text 
data = open("/Users/wiseer85/Desktop/mbox-short.txt",'r')
for line in data:
    line=line.rstrip()
    if line.find("@uct.ac.za")==-1: 
        continue

#read in and write out a file 
fhand = open("/Users/wiseer85/Desktop/mbox.txt",'r')
whand = open("/Users/wiseer85/Desktop/mailaddress.txt",'w')
for line in fhand:
    if line.startswith('From:') and line.endswith('umich.edu\n'):
        whand.write(line[6:])
fhand.close()
whand.close()


####################################################### 
#Chapter 8: Lists
#unlike strings, lists are mutable because you can change the order or reassign items to a list
numbers=[17, "five"]
print(numbers)

numbers[1]=5
print(numbers)

#can also sort lists
numbers.sort()
print(numbers)

#other functions with lists
print(max(numbers))
print(min(numbers))
print(sum(numbers))

#like strings, lists can also be concatenated
a=[1,2,3]
b=[4,5,6]
c=a+b
print(c)

#lists can also be sliced to show only specific items in the list
#second parameter is "up to but not including" (remember starts at [0])
c[1:3]

#to delete items in a list
del c[1]
print(c)

#if you know the element you want to remove (but not the index), you can use remove:
t = ['a', 'b', 'c', 'd', 'e', 'f'] 
t.remove('b')
print(t)

#to remove more than one element, you can use del with a slice index
del t[1:5]
print(t)

#we can build a list with append
stuff=list()
stuff.append("book")
stuff.append("movie")
print(stuff)

#or use conditional statements to identify if a variable in a list
"book" in stuff
"ipod" in stuff

#len can give number of characters in a string or number of elements in a list
greet="Hello Bob"
print(len(greet))
print(len(numbers))

#range retuns the range of lists
print(range(len(numbers)))

#split breaks a sequence into parts to create a list of strings
#items based by spaces but considers multiple spaces one split
#you can also split by defining parameter by semicolon, comma or dash etc.
s ='spam-spam-spam' 
delimiter = '-'
s.split(delimiter) 

#parsing lines 
#open files
fhand = open("/Users/wiseer85/Desktop/mbox.txt",'r') 

#strip lines from a text with r.strip
for line in fhand:
    line = line.rstrip()
    if not line.startswith('From'): continue 
    words = line.split()
print(words)

#double split between username and host
email=words[1]
pieces=email.split("@")
print(pieces[1])

####################################################### 
#Chapter 9: Dictionaries
#Whereas list is a linear collection of ordered values, a dictionary is an 
#assortment of unordered labeled values, similar to a database
#Becuase dictionaries are not ordered, they require labels (or key for values)
purse = dict()
purse['money'] = 12
purse['candy'] = 3
purse['tissues'] = 75
print(purse)

#check if key is in dictionary
print("money" in purse)

#use dictionaries to count items
counts = dict()
names = ['csev','owen','csev','zqian','cwen']
for name in names:
  if name not in counts:
    counts[name]= 1
  else:
    counts[name] = counts[name] + 1
print(counts) 

#equivalent to the GET function
for name in names:
    counts[name]=counts.get(name,0)
print(counts)

#use split to split items in a sequence
text="the clown ran after the car and the car ran into the tent and the tent fell down on the clown and the car"
print(text)

words=text.split()
print(words)

#find most frequent word by splitting lines into words
counts=dict()
for word in words:
    counts[word]=counts.get(word,0)+1
bigcount = None
bigword = None
for word,count in counts.items():
    if bigcount is None or count > bigcount: 
        bigword = word
        bigcount = count 
print(bigword, bigcount)

#retrieve text from internet with requests 
import requests
import string
url = "http://www.py4inf.com/code/romeo.txt"
res = requests.get(url)
text = res.text
len(text)
print(text)

####################################################### 
#Chapter 10: Tuples
#like lists, tubles is a sequence of values that are immutable
#but they are more efficient when creating a temporary list that won't be changed
t=tuple("lupins")
print(t)

#create a tuple and print left hand side of the assignment (parentheses optional)
(x,y)=(4,12)
print(x)

#you can't modify a tuple, but you can replace it with another by identifying order in tuple
t=("L",) + t[1:]
print(t)

#sorting tuples
c = {'a': 10, 'c': 22, 'b': 1, 'f': 22}
sorted(c)

#print key-value pairs by key
for k in sorted(c):
    print(k, c[k])

#create temporary list to sort by values instead of key and reverse sort
tmp=list()
for k,v in c.items():
    tmp.append((v,k))
tmp.sort(reverse=True)
print(tmp)

#shorthand for list comprehension in ascending order
print(sorted([(v,k) for k,v in c.items()]))

#######################################################
#Chapter 11: Regular Expressions
#many of these can be used in other programming languages as well to match and parse strings
# ^ Matches the beginning of a line $ Matches the end of the line
# . Matches any character
# * Repeats a character zero or more times
# \s Matches whitespace
# \S Matches any non­whitespace character
# *? Repeats a character zero or more times (non­greedy) + Repeats a character one or more times
# +? Repeats a character one or more times(non­greedy) [aeiou] Matchesasinglecharacterinthelistedset [^XYZ] Matches a single character not in the listed set [a­z0­9] Thesetofcharacterscanincludearange
# ( Indicates where string extraction is to start
# ) Indicates where string extraction is to end

#re.search is find()
import re
fhand = open("/Users/wiseer85/Desktop/mbox.txt",'r') 
for line in fhand:
    line = line.rstrip()
    if not line.startswith('From'): continue 
    words = line.split()
print(words)

#re.findall finds and retrieves a list
hand = open("/Users/wiseer85/Desktop/mbox-short.txt") 
for line in hand:
    line = line.rstrip()
    x = re.findall('\S+@\S+', line) 
    if len(x) > 0 :
        print(x)
  
#lambda (useful for simple data cleaning tasks)
my_function = lambda a, b, c: a + b
my_function(1, 2, 3)

#NumPy creates an array, a grid of values of the same type and indexed by non-negative integers
import numpy as np
mylist = [1, 2, 3]
x = np.array(mylist)
print(x)

#create an array of even numbers betwee  0 and 30
m.shape
n=np.arange(0, 30, 2)
print(n)
