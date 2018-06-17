# Malware Detection
This project's main goal is to classify benign files and variants of malware files into their respective families. It consist of 2 parts, each one has a different approach to achieve this goal: one with XGBoost model and the second with deep learning model.

XGBoost Model:
Machine learning model using xgboost - a scalable and accurate implementation of gradient boosting machines.

Second model - Deep Learning:
Classification model based on convolutional network taken from 'Malware Detection by Eating a Whole EXE' paper written by Edward Raf, Jon Barker, Jared Sylvester, Robert Brandon, Bryan Catanzaro and Charles Nicholas (link: https://arxiv.org/pdf/1710.09435.pdf).


## Results:

XGBoost model was run over one class of benign files and 3 classes of malware taken from the Kaggle contest of 2015. Each file is Windows8 PE without the PE header. Those are the results:
........................................


Deep learning model was run one time as multiclass classifier for 3 classes and second time as binary classifier.
![alt text](http://docs.google.com/uc?export=open&id=1du29cO38sOwU6Nxx2VZlM1cbaszHhuFU)

........................................

![alt text](http://docs.google.com/uc?export=open&id=1dCmBKuiF3_mqKQKPX4DU2qa6BZM5FcnH)

........................................

![alt text](http://docs.google.com/uc?export=open&id=15-IryeZv5P_c6vRjnz9Jgl7FPc89INfg)


## Running Instructions:

Required packages: XGBoost, Pytorch, Pefile, Capstone, Numpy

There are 2 shell scripts in project directory:

    1. run_ml_model.sh - runs xgboost model
    2. run_deep_model.sh - runs deep learning model

In order to run each model you only need to suit the parameters of the .py files in each shell script.
We'll describe here exactly how to do it and what is every parameter:

1. run_ml_model.sh

        split_data.py  [train_labals.csv]  [target_dir_path]  [split_ratio]

                train_labels.csv - csv file contains mapping from file path to its label for each file in train set.

                target_dir_path - dir to put in the train_set.csv and test_set.csv created from split. both csv files mapping path to label

                split_ratio - ratio size to give test set (validation set).
                
              
        ml_code/extract_ngrams.py -n [$i] -p [path/train_set.csv]
        
                $i - number of class
                
                path/train_set.csv - path to train_set.csv created before.
                
                This script goes over all files of specific class and extract 10,000 most common ngrams.
         
         
        ml_code/join_ngrams.py
            
                Pick 750 ngrams for each class by using cross-entropy and creates ngrams array = 750 * # classes


        ml_code/extract_segments.py
        
                For each file in train_set.csv - extract a list of segment names
                
                
        ml_code/f2v.py [path/train_set.csv]  [path_to_train.f2v_file]
        
                path/train_set.csv - path to train_set.csv created before.
                
                path_to_train.f2v_file - path to f2v file to create
                
                Go over all files in train set and represents them as vectors of features. Output file called train.f2v which maps every file to its features vec.
                

        ml_code/f2v.py [path/test_set.csv]  [path_to_test.f2v_file]
        
                path/test_set.csv - path to test_set.csv created before.
                
                path_to_test.f2v_file - path to f2v file to create
                
                Output file called test.f2v which maps every file in test set to its features vec.



2. run_deep_model.sh
    
        split_data.py  [train_labals.csv]  [target_dir_path]  [split_ratio]  --- same as before
                

        deep_code/model.py [...]  [..]  [..]


