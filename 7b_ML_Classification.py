#######################################################
# Machine Learning (Stanford)
#######################################################
get_ipython().magic('matplotlib inline')
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy.io #Used to load the OCTAVE *.mat files
import scipy.misc #Used to show matrix as an image
import matplotlib.cm as cm #Used to display images in a specific colormap
import random #To pick random images to display
from scipy.special import expit #Vectorized sigmoid function
from scipy import optimize
import scipy.io
from pandas import read_csv
from time import sleep
from numpy import ones, zeros, append, linspace, reshape, mean ,std, sum, array, dot,concatenate
from pylab import plot, scatter, xlabel, ylabel, contour,figure, show, axes, imshow
from scipy.optimize import fmin_bfgs, fmin_cg
get_ipython().magic('matplotlib inline')
get_ipython().magic('pylab inline')
from matplotlib.animation import FuncAnimation
from numpy.random import randint

#Multi-class Classification
#import the images which are separated in a gray scale intensity in a 20x20 array
dataA = scipy.io.loadmat('/Users/wiseer85/Desktop/data/ex3data1.mat')
data = append(dataA['X'],dataA['y'],axis=1) 

x = dataA['X']
y = dataA['y']

#check the form of the arrays

print(x.shape)
print(y.shape)
print("There are 5000 examples which correspond to hte number of rows and each image 20x20 array has been flatten into a row")
print("We choose 10 random examples and print their label (number), there is no zero, 0 is represented by 10")
print(y[randint(y.shape[0],size = 20)].T)

#Visualizing the data
#take sample array and convert it into an image in gray scale
def showNumbers(x):
    im_number = 200
    imv = empty((20,0))
    imag = []
    for i in range(im_number):
        im = reshape(x[i],(20,20)).T
        imv = append(imv,im,axis=1)
        if (i+1) % 20 == 0:
            imag.append(imv)
            imv = empty((20,0))
    image = concatenate((imag[:]),axis = 0)
    imshow(image, cmap = cm.Greys_r)
    
#Display 200 numbers randomly
shuffle(data)
showNumbers(data[:,:-1])
print('This are some 200 examples of the images that serve as the training set')

#define functions
def sigmoid(z):
    return 1/(1+exp(-z))

def costFunction(theta,x,y, lamda=0):
    theta = reshape(theta,(theta.size,1))
    pred = sigmoid(dot(x,theta))
    J = mean(-y*log(pred)-(1-y)*log(1-pred))
    J = J + lamda*sum(square(theta[1:]))/(2*m)
    return J

def gradient(theta,x,y,lamda=0):
    theta = reshape(theta,(theta.size,1))
    pred = sigmoid(dot(x,theta))
    grad = dot(x.T,pred-y)/m
    grad[1:] = grad[1:] + lamda*theta[1:]/m
    return grad.flatten()

def prediction(theta,x,polDeg,mu=0,sigma=1):
    theta = reshape(theta,(theta.size,1))
    x.shape = (1,x.shape[0])
    x = (x-mu)/sigma
    X = createPolynomialFeatures(x, polDeg)
    pred = sigmoid(dot(X,theta))
    return pred

def accuracy(pred,y):
    pred.shape = (pred.size,1)
    return sum(pred == y%10)/float(y.shape[0])*100

#This function checks the probability of being number C and not C
def oneVsAll(theta,x,y,lamda,C,miter):
    Y = (y == C).astype(int)
    theta = fmin_cg(costFunction,inTheta,fprime = gradient,args=(X,Y,lamda), maxiter = miter,disp = 0)
    return theta  

X = append(ones((x.shape[0],1)),x,axis=1)
m = X.shape[0]
n = X.shape[1]
inTheta = zeros(n)
lamda = .1;
maxIterations = 20
#run configuration for numbers C
Theta = empty((10,n))
for C in range(1,11):
    Theta[C % 10,:] = oneVsAll(inTheta,X,y,lamda, C, maxIterations)
    print('Finished oneVsAll checking number: %d' %C)
print('All the numbers have been checked')

#keep the prediction that gives the highest probability
allProb = sigmoid(dot(X,Theta.T))
prob = amax(sigmoid(dot(X,Theta.T)),axis=1)
pred = argmax(sigmoid(dot(X,Theta.T)),axis=1)

#calculate the accuracy of the algorithm by cross-referencing with y
acc = accuracy(pred,y)
print('The algorithm correctly predicts %f %% of the sample' %acc)

#show an animation showing the drawing and the prediction of the algorithm
def arrayToImage(i):
    X = reshape(x[i],(20,20)).T
    return X

def animate(*args):
    i = randint(5000)
    im = ax.imshow(arrayToImage(i), cmap = 'gray')
    prediction.set_text('Prediction: %d'%pred[i])
    return im,prediction

fig = plt.figure()
ax = plt.axes()
im = ax.imshow(arrayToImage(0), cmap = 'gray')
prediction = ax.text(.5, 1, '', color= 'white')

anim = FuncAnimation(fig, animate,interval = 1500)