#Python for Informatics    
 
#Chapter 2: Variables, Expressions and Statements
var=2
print(var+2)

string = "Hello world!"
print(string)

inp = "75"
fahr = float(inp) 
cel=(fahr-32.0)*5.0/9.0
print (cel)


#Chapter 3: Conditional Execution
x=5
if x%2==0:
    print("x is even")
else:
    print("x is odd")

try:
    x = int("seven")
except ValueError:
    print ("Oops!  That was no valid number.  Try again...")

#Exercise 3.1
gpay=475
hours=45
rate=10
if hours>40:
    newrate=1.5*rate 
newpay=rate*40+newrate*5


#Chapter 4: Functions
type(7)
int(7)
float(7)
string(7)

#import math functions
import random
for i in range(10):
    x = random.random() 
print (x)

random.randint(5,100)

t=[1,2,3] 
random.choice(t)

import math
decibels=10*math.log10(100)
print(decibels)
print(2**10)
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

    
#Chapter 5: Iteration
n=5 
while n>0:
    print(n)
    n=n-1
print("Blastoff!")

friends = ['Joseph', 'Glenn', 'Sally'] 
for friend in friends:
    print("Happy New Year:", friend) 

count = 0
for itervar in [3, 41, 12, 9, 74, 15]:
    count = count + 1 
print("Count: ", count)

total=0
for itervar in [3, 41, 12, 9, 74, 15]:
    total = total + itervar 
print("Total: ", total)

largest = None
print("Before:", largest)
for itervar in [3, 41, 12, 9, 74, 15]:
    if largest is None or itervar > largest : 
        largest = itervar
    print("Loop:", itervar, largest)
print("Largest:", largest)

#define function that is already available in Python
def min(values):
    smallest = None
    for value in values:
        if smallest is None or itervar < smallest: 
            smallest = value
    return smallest


#Chapter 6: Strings
fruit = 'banana' 
letter = fruit[0]
letter = fruit[1]
length=len(fruit)
last=fruit[length-1]
print(last)
print(fruit[-1])
for char in fruit:
    print(char)
fruit[:3]
fruit[3:]
fruit[:]

a="Monty Python"
print(a[0:5])
b="Hi" + a[5:]
print(b)

count = 0
for letter in fruit:
    if letter == 'a': 
        count = count + 1
print(count)

"a" in fruit
"seed" in fruit

FRUIT=fruit.upper()
print(FRUIT)
index=fruit.find("fruit")
print(index)
fruit.find("na")
fruit.find("na",3)
#find can take second argument to index where begins "na" (remember from back begins with 0)

#removes spaces from text
line=" Here we go! "
line.strip()

line = 'Please have a nice day' 
line.startswith('Please')
line.startswith('p')
line.lower().startswith("p")

nextline = 'X\nY' 
print(nextline)

data = 'From stephen.marquard@uct.ac.za Sat Jan 5 09:14:16 2008' 
atpos = data.find('@')
print(atpos)
sppos = data.find(' ',atpos)
print(sppos)
host = data[atpos+1:sppos]
print(host)

#format operator constructs strings and replaces parts stored in variables
camels=42
"%d"%camels
"I saw %d camels."%camels
'In %d years I have spotted %g %s.' % (3, 0.1, 'camels') 


#Chapter 7: Using Data Files
#NOTE: used to be raw_input; old input() is now eval(input())
text=input()
"the clown ran after the car and the car ran into the tent and the tent fell down on the clown and the car"
print(text)

#use open for large files rather than reading in a file
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
#NOTE: print adds new line at end of line, must include rstrip function to delete

#find and strip specific words from text file
test = '#....... Section 3.2.1 Issue #32 .......'
test.strip('.#! ')

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

#write out file to text
fout = open('output.txt', 'w')
line2 = "This is not a test." 
print(line2)
fout.write(line2)
fout.close()

#example
fhand = open("/Users/wiseer85/Desktop/mbox.txt",'r')
whand = open("/Users/wiseer85/Desktop/mailaddress.txt",'w')
for line in fhand:
    if line.startswith('From:') and line.endswith('umich.edu\n'):
        whand.write(line[6:])
fhand.close()
whand.close()

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
#second parameter is "up to but not including"
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
"book" in stuff
"ipod" in stuff

#len can give number of characters in a string or number of elements in a list
greet="Hello Bob"
print(len(greet))
print(len(numbers))

#range retuns the range of lists
print(range(len(numbers)))

#split breaks string into parts to create a list of strings
#items based on space but considers multiple spaces one split
#you can also split by defining parameter by semicolon, comma or dash etc.
s ='spam-spam-spam' 
delimiter = '-'
s.split(delimiter) 

#parsing lines
fhand = open("/Users/wiseer85/Desktop/mbox.txt",'r') 
for line in fhand:
    line = line.rstrip()
    if not line.startswith('From'): continue 
    words = line.split()
print(words)

#double split pattern 
email=words[1]
pieces=email.split("@")
print(pieces[1])


#Chapter 9: Dictionaries
#Whereas list is a linear collectionof ordered values,
#Dictionary is an assortment of unordered labeled values, similar to a database
#Becuase dictionaries are not ordered, they require labels (or key for values)
purse = dict()
purse['money'] = 12
purse['candy'] = 3
purse['tissues'] = 75
print(purse)

#check if key is in dictionary
print("money" in purse)

#can use dictionaries to count items
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

#find most frequent word by splitting lines into words
text="the clown ran after the car and the car ran into the tent and the tent fell down on the clown and the car"
print(text)
words=text.split()
print(words)
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


#Chapter 10: Tuples
#like lists, tubles is a sequence of values that are immutable
#but they are more efficient when creating a temporary list that is quick to use and will not be changed
t=tuple("lupins")
print(t)

#create a tuple on left hand side of an assignment (parentheses optional)
(x,y)=(4,12)
print(x)

#you can't modify a tuple, but you can replace it with another
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

#shorthand for list comprehension for ascending order
print(sorted([(v,k) for k,v in c.items()]))


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
hand = open("/Users/wiseer85/Desktop/mbox.txt",'r') 
for line in hand:
    line = line.rstrip()
    if re.search('ˆFrom:', line):
        print(line)

fhand = open("/Users/wiseer85/Desktop/mbox.txt",'r') 
for line in fhand:
    line = line.rstrip()
    if not line.startswith('From'): continue 
    words = line.split()
print(words)

#re.findall findas and retrieves a list
hand = open("/Users/wiseer85/Desktop/mbox-short.txt") 
for line in hand:
    line = line.rstrip()
    x = re.findall('\S+@\S+', line) 
    if len(x) > 0 :
        print(x)

#Chapter 12: Networked Programs
#create a sockets 
import socket
mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

#connecting with an application server to send data
mysock.connect(('www.py4inf.com', 80))

#retrieve web page with urllib
#URL is uniform resource locator
#urllib is an application web library that has html embedded protocols
import urllib
fhand = urllib.request.urlopen('http://www.py4inf.com/code/romeo.txt') 
for line in fhand:
    print(line.strip())

#count word frequency
counts = dict()
fhand = urllib.request.urlopen('http://www.py4inf.com/code/romeo.txt') 
for line in fhand:
    words = line.split() 
    for word in words:
        counts[word] = counts.get(word,0) + 1 
print(counts)

#Chapter 13: Using webservices 
#XML or extensible markup language for programs exchanging information
#parsing XML using Tags, Text and Attributes with indentation to display nested structure
import xml.etree.ElementTree as ET
data = '''
<person>
    <name>Chuck</name> 
    <phone type="intl">
        +1 734 303 4456 
        </phone>
        <email hide="yes"/>
</person>'''

tree = ET.fromstring(data)
print('Name:',tree.find('name').text)
print('Attr:',tree.find('email').get('hide'))

#looping through nodes
import xml.etree.ElementTree as ET
input = ''' 
<stuff>
    <users>
        <user x="2">
            <id>001</id>
            <name>Chuck</name> </user>
        <user x="7"> 
            <id>009</id>
            <name>Brent</name> 
        </user>
    </users> 
</stuff>'''

stuff = ET.fromstring(input)
lst = stuff.findall('users/user') 
print('User count:', len(lst))

for item in lst:
    print('Name', item.find('name').text) 
    print('Id', item.find('id').text) 
    print('Attribute', item.get('x'))
#JSON is more friendly than XML, but XML is good for text-based data
#Week 6 videos include JSON examples in python
#Fourth course on databases with SQL, see also SQL for data science course

