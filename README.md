# Malware Detection
This project main goal is to classify benign files and variants of malware files into their respective families. It consist of 2 parts, each one is a different approach to achieve this goal: one with XGBoost model and the second with deep learning model.

XGBoost Model:
Machine learning model using xgboost - a scalable and accurate implementation of gradient boosting machines.

Second model - Deep Learning:
Classification model based on convolutional network taken from 'Malware Detection by Eating a Whole EXE' paper written by Edward Raf, Jon Barker, Jared Sylvester, Robert Brandon, Bryan Catanzaro and Charles Nicholas (link: https://arxiv.org/pdf/1710.09435.pdf).

RESULTS:
XGBoost model was run over one class of benign files and 3 classes of malware taken from the Kaggle contest of 2015. Each file is Windows8 PE without the PE header. Those are the results:



Deep learning model was run one time as binary classifier and second time as multiclass classifier for 3 classes.




