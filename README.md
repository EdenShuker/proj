# Malware Detection
This project main goal is to classify benign files and variants of malware files into their respective families. It consist of 2 parts, each one is a different approach to achieve this goal: one with XGBoost model and the second with deep learning model.

XGBoost Model:
Machine learning model using xgboost - a scalable and accurate implementation of gradient boosting machines.

Second model - Deep Learning:
Classification model based on convolutional network taken from 'Malware Detection by Eating a Whole EXE' paper written by Edward Raf, Jon Barker, Jared Sylvester, Robert Brandon, Bryan Catanzaro and Charles Nicholas (link: https://arxiv.org/pdf/1710.09435.pdf).


RESULTS:

XGBoost model was run over one class of benign files and 3 classes of malware taken from the Kaggle contest of 2015. Each file is Windows8 PE without the PE header. Those are the results:
........................................


Deep learning model was run one time as multiclass classifier for 3 classes and second time as binary classifier.
multiclass 
........................................



RUNNING INTRUCTIONS:

Required packages: XGBoost, Pytorch, Pefile, Capstone, Numpy

Their are 2 shell scripts in project directory:
    1. run_ml_model.sh - runs xgboost model
    2. run_deep_model.sh - runs deep learning model

In order to run each model you only need to suit the parameters of the .py files in each shell script.
We'll describe here exactly how to do it and what is every parameter:

1. run_ml_model.sh



2. run_deep_model.sh
    
        split_data.py  [train_labals.csv]  [target_dir_path]  [split_ratio]

                train_labels.csv - csv file contains mapping from file path to its label for each file in train set.

                target_dir_path - dir to put in the train_set.csv and test_set.csv created from split. both csv files mapping path to label

                split_ratio - ratio size to give test set (validation set).


        model.py [...]  [..]  [..]






















