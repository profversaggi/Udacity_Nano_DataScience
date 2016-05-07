#!/usr/bin/python


# Setup and Imports
#
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.tools.plotting import scatter_matrix
from sklearn.preprocessing import StandardScaler
from sklearn import cross_validation
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.cross_validation import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import BaggingClassifier
import sys

sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data


### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".

# These 15 Features come from External Experiments (See SelectKBest in Experiments File for Details):
#
features_list = ['poi','bonus', 'deferred_income','exercised_stock_options', 'expenses','loan_advances',
                 'long_term_incentive','other','restricted_stock','restricted_stock_deferred','salary',
                 'total_payments','total_stock_value', 'deferral_payments', 'director_fees', 'shared_receipt_with_poi'] 

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)
    
# Convert the Python Dictionary to a Pandas DataFrame:
raw_dataframe = pd.DataFrame(data_dict)    
    
# Transposed DataFrame, switching it's colum and axis.
dataset = raw_dataframe.T 
    
# DF TRANFORM : Replace DataType OBJECT with better dtypes for object columns for entire DF
mydataset = dataset.convert_objects(convert_dates=True, convert_numeric=True, convert_timedeltas=True, copy=True)   
    
# DF TRANFORM : Replace NaN's with Zero's for entire DF
mydataset = mydataset.fillna(0)  
    
# DF TRANSFORM POI from [True/False] to [1/0]
mydataset['poi'] = mydataset['poi'].astype(int) 
    
# DF TRANSFORM - EMAIL ADDRESSES TO [1/0] per NaN or not (Run ONLY Once)
mydataset['email_address'] = mydataset['email_address'].apply(lambda x: 0 if x == 'NaN' else 1)  
        
# DF TRANSFORM - Get Column List so we can rearrange the columns 
reordered_column_list = [ 'bonus',
 'deferral_payments',
 'deferred_income',
 'director_fees',
 'email_address',
 'exercised_stock_options',
 'expenses',
 'from_messages',
 'from_poi_to_this_person',
 'from_this_person_to_poi',
 'loan_advances',
 'long_term_incentive',
 'other',
 'restricted_stock',
 'restricted_stock_deferred',
 'salary',
 'shared_receipt_with_poi',
 'to_messages',
 'total_payments',
 'total_stock_value',
 'poi'
]   
    
# DF TRANSFORM - Column ReOrdering
mydataset = mydataset[reordered_column_list]  
    
# DF TRANSFORM - Column Absolute Value (Some SKLearn Algorithms do not like negative numbers) ==> The WHOLE DF
mydataset = mydataset.abs()
    
    
### Task 2: Remove outliers 
###   
###

# REMOVE OUTLIER: The Row "TOTAL" is an obvious outlier and is deleted entirely
mydataset.drop(mydataset.index[130], inplace=True)   
    
# REMOVE OUTLIER: The Row "THE TRAVEL AGENCY IN THE PARK" is also an obvious outlier and is deleted entirely
mydataset.drop(mydataset.index[127], inplace=True)  
    
    
### Task 3: Create new feature(s)
# - Feature Engineering or feature reduction / scaling, transformations
### Store to my_dataset for easy export below.
# FORM: my_dataset = data_dict   
    
Highly_Paid = mydataset['salary'] + mydataset['bonus'] + mydataset['loan_advances'] + mydataset['other']   
High_Net_Worth = mydataset['exercised_stock_options'] + mydataset['restricted_stock']
big_shot = Highly_Paid + High_Net_Worth
mydataset['big_shot'] = big_shot  
mydataset['ratio_to'] = mydataset['from_this_person_to_poi'] / mydataset['to_messages']
mydataset['ratio_from']= mydataset['from_poi_to_this_person'] / mydataset['from_messages']

reordered_column_list = [ 'bonus',
 'deferral_payments',
 'deferred_income',
 'director_fees',
 'email_address',
 'exercised_stock_options',
 'expenses',
 'from_messages',
 'from_poi_to_this_person',
 'from_this_person_to_poi',
 'loan_advances',
 'long_term_incentive',
 'other',
 'restricted_stock',
 'restricted_stock_deferred',
 'salary',
 'shared_receipt_with_poi',
 'to_messages',
 'total_payments',
 'total_stock_value',
 'ratio_to',
 'ratio_from',
 'big_shot',
 'poi'
]
    
# DF TRANSFORM - Column ReOrdering
mydataset = mydataset[reordered_column_list]
    
# Fill in the NaN's with Zero's 
mydataset = mydataset.fillna(0)    
    
    
# Create a temp DF of the feature reduced df
temp_mydataset = mydataset.copy(deep=True)  
    
# Make a new DF of ONLY the POI's in the temp FR DF (ie. isolate only the POI's rows)
MyPoiDF = mydataset.loc[mydataset['poi'] == 1].copy(deep=True)  
    
# Do this ONLY ONCE per oversampling run to initialize.
start_range = 0 

# Calculate Proper Range Values for this individual DF
end_range = len(MyPoiDF)

# RESET the Temp POI DF (for unique indexes)
MyPoiDF.index=range(start_range, end_range + start_range)
   
# Begin the process of oversampling by appending the isolated POI's rows to an existing df
over_sampled_df = temp_mydataset.append(MyPoiDF)   
    
    
### Extract features and labels from dataset for local testing
# data = featureFormat(my_dataset, features_list, sort_keys = True)
# labels, features = targetFeatureSplit(data)    
#
### Did not use, replaced by the below code:


# Create a dataset from a feature reduced columns (per KBest feature picking process + Tweeks) : 16 Total

mydataset_os_fr = over_sampled_df[['bonus','deferral_payments','deferred_income','director_fees',
                                   'exercised_stock_options','expenses','loan_advances','long_term_incentive',
                                   'other','restricted_stock','restricted_stock_deferred','salary',
                                   'shared_receipt_with_poi','total_payments','total_stock_value','poi']]

# Split-out validation dataset 
array = mydataset_os_fr.values

# separate array into input and output components
X = array[:,0:15].astype(float) # NOTE: There are 16 columns, the category class is the 15th, therefore exclude it.
Y = array[:,15]                 # NOTE: This is the isolated output class (or the 15th column)
validation_size = 0.20          # Validation Set Size 20%
seed = 7                        # Seed of 7

# Split into train / validation sets 
X_train, X_validation, Y_train, Y_validation = cross_validation.train_test_split(X, Y,
    test_size=validation_size, random_state=seed)


### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Provided to give you a starting point. Try a variety of classifiers.
# from sklearn.naive_bayes import GaussianNB
# clf = GaussianNB()


# Prepare the DecisionTreeClassifier (CART) model
#
# Scale the input data
scaler = StandardScaler().fit(X_train)
rescaledX = scaler.transform(X_train)

# Model Construction
# Variations of inputs
model_DTC = DecisionTreeClassifier( criterion='gini', max_features='auto', min_samples_split=2, splitter='random', class_weight= {1: 1} ) 

# Train (fit) the model    
model_DTC.fit(rescaledX, Y_train)


### Task 5: Tune your classifier to achieve better than .3 'precision' and 'recall' 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html


# Ensemble Method: Bagged Decision Trees for Classification => DecisionTreeClassifier

# Scale the input data
scaler = StandardScaler().fit(X_train)
rescaledX = scaler.transform(X_train)

# KFold Input constants
num_folds = 10
num_instances = len(X_train)
seed = 7
kfold = cross_validation.KFold(n=num_instances, n_folds=num_folds, random_state=seed)

# CART Model
# cart = DecisionTreeClassifier( criterion='gini', max_features='auto', min_samples_split=2, splitter='random', class_weight= {1: 1} ) 

# KNN = KNeighborsClassifier Model            
knn = KNeighborsClassifier(n_neighbors=1)


# Model: Extra Trees Classifier parameters
num_trees = 100
max_features = 7
min_sam_split = 2

model_ETC = ExtraTreesClassifier(n_estimators=6, max_features='sqrt', min_samples_split=2, criterion='gini', class_weight={0: 0.5} )
                                 
# Model Bagging Classifier: => DecisionTreeClassifier
# num_trees = 100                       
# model_BC = BaggingClassifier(base_estimator=cart, n_estimators=num_trees, random_state=seed)   


# Example starting point. Try investigating other evaluation techniques!
# from sklearn.cross_validation import train_test_split
# features_train, features_test, labels_train, labels_test = \
#    train_test_split(features, labels, test_size=0.3, random_state=42)
#
    
    
### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.


# Re-Transpose DF to original form to prepare it for Transformation into Python Dictionary
reverted_df = over_sampled_df.T


# Transform Transposed DF into Python Dictionary 
# Here we COULD lose data because of duplicate Colums with the same name so we make sure they are all unique.
reverted_dict = reverted_df.to_dict()


### Store to my_dataset for easy export below.
my_dataset = reverted_dict


# Model Execution
#
# clf = model_BC      # BaggingClassifier => DecisionTreeClassifier
clf = model_ETC       # ExtraTreesClassifier => KNN

# Dump Model for Testing
dump_classifier_and_data(clf, my_dataset, features_list)







