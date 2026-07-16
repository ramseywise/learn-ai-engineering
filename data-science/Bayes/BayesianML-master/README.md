### Bayesian Machine Learning

This repository contains completed (and WIP) jupyter notebooks for the Bayesian Machine Learning MOOC on Coursera.

To create a conda virtual env for the required packages for the course use:

`source activate bayesian.yml`

The Week 6 assignment involves the use of the following packages:
* GPy
* gpyopt
* xgboost

These packages need to installed into the conda environment via pip(!). The conda environment already contains the pip package management software. 

To install the required packages into the conda env,

`$HOME/anaconda3/envs/<env_name>/bin/pip install <package_name>`

By pointing to the pip within the conda installation, the packages are installed into the environment python instead of the python used by the system. 


Link to course: https://www.coursera.org/learn/bayesian-methods-in-machine-learning
