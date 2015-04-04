'''
    MIS382N: Advanced Predictive Modeling assignment to build Lasso and Ridge Regression models using Sklearn in Python.

    Automobile Dataset including the following variables: MPG, cylinders, displacement, horsepower, weight, acceleration, origin, train
        - "train" is a column indicating if the row of data will be part of the training set
        - determining best parameter for lasso and ridge using cross-validation
        - target Variable is MPG, for which the rest of the variables will be predictors

    Parts 1A & 1B:
        - find the best value for lambda in each Lasso and Ridge Regression
        - use cross-validation to determine the value

    Part 1C:
        - run Least-Squares Regression, Lasso Regression and Ridge Regression on full training data
            - best parameter value found in parts 1A & 1B used for Lasso and Ridge
        - calculate prediction error on test data for each model

    Part 1D:
        - for the best Lasso parameter, determine variables that were NOT dropped
        - run Least-Squares with those variables and find prediction error on test data

    Plots using matplotlib included throughout for depicting best lambda values.

'''

# Import statements and required packages
import pandas as pd
import numpy as np
from sklearn.linear_model import Lasso
from sklearn.linear_model import Ridge
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt


#### Parts 1A and 1B ###

# Load data, split into test/train, append folds column to training set to use for cross-validation
autos = pd.read_csv("autos.csv")

autos_train = autos[(autos["train"] == True)]
autos_train = autos_train.reset_index()
del autos_train['index']
autos_train['fold'] = pd.read_csv("auto.folds",header=None)
del autos_train["train"]

autos_test = autos[(autos["train"] == False)]
del autos_test["train"]

names = autos_train.columns.tolist()

# Set X dataframe to be all data except for MPG/fold columns, y dataframe to contain MPG and fold column
X = autos_train[names[1:len(names)-1]]
y = pd.DataFrame(autos_train['mpg'])
y['fold'] = autos_train['fold']

folds = range(5)

ridge_reg_params = np.array([0.001,0.005,0.01,0.05,0.1,0.5,1,5,10,50,100])
lasso_reg_params = np.array([0.0001,0.0005,0.001,0.005,0.01,0.05,0.1])

# Create Plot for Lasso Coefficients
plt.figure(1)
ax = plt.gca()
ax.set_color_cycle(2* ['b','r','g','c','k','y'])

# Initialize array of coefficients for lasso
k = X.shape[1]
coefs_lasso = np.zeros((len(lasso_reg_params), k))
lasso_mse_list = []
lasso_mse_mean = []

# Loop to build and fit lasso models for each reg_param, run on each of the 5 folds for CV, get MSE and coefficients
for i,a in enumerate(lasso_reg_params):

    lasso_model = Lasso(alpha=a, normalize=True)
    lasso_mse_fold = []

    for j in folds:

        X_fold_test = autos_train[(autos_train['fold'] == j)]
        X_fold_train = autos_train[(autos_train['fold'] != j)]
        y_fold_test = y[(y['fold'] == j)]
        y_fold_train= y[(y['fold'] != j)]
        del X_fold_train['mpg'],X_fold_test['mpg'], X_fold_test['fold'], X_fold_train['fold'], y_fold_train['fold'], y_fold_test['fold']

        lasso_model.fit(X_fold_train.as_matrix(), y_fold_train.as_matrix())
        mse = mean_squared_error(y_fold_test.as_matrix(), lasso_model.predict(X_fold_test.as_matrix()))
        lasso_mse_fold.append(mse)
        coefs_lasso[i] = lasso_model.coef_

    lasso_mse_list.append(lasso_mse_fold)
    lasso_mse_mean.append(np.array(lasso_mse_list).mean())

# Find the best lasso parameter
min_index_lasso = lasso_mse_mean.index(min(lasso_mse_mean))
print "Best Lasso Parameter: ", lasso_reg_params[min_index_lasso], " with MSE= ", min(lasso_mse_mean)

# Plot each coefficient on Lasso plot
for coef in coefs_lasso.T:
    plt.plot(lasso_reg_params, coef)

plt.xlabel('Lambda')
plt.ylabel('Standardized Coefficients')
plt.xlim(min(lasso_reg_params),max(lasso_reg_params))
plt.title('Lasso Model')

# Plot the average Lasso CV Error across folds with a line for the best parameter
plt.figure(2)
plt.plot(-np.log(lasso_reg_params),
    np.sqrt(np.array(lasso_mse_list)).mean(axis=1))
plt.axvline(-np.log(lasso_reg_params[min_index_lasso]), color = 'red')
plt.xlabel(r'-log(lambda)')
plt.ylabel('RMSE (Avg across all folds)')
plt.title('Lasso CV Error')

# Create Plot for Ridge Coefficients
plt.figure(3)
ax = plt.gca()
ax.set_color_cycle(2* ['y','r','g','c','k','b'])

# Loop to build and fit ridge models for each regularization parameter, run model on each of the 5 folds, get MSE and coefficients
coefs_ridge = np.zeros((len(ridge_reg_params), k))
ridge_mse_list = []
ridge_mse_mean = []

for i,a in enumerate(ridge_reg_params):

    ridge_model = Ridge(alpha=a, normalize=True)
    ridge_mse_fold = []

    for j in folds:

        X_fold_test = autos_train[(autos_train['fold'] == j)]
        X_fold_train = autos_train[(autos_train['fold'] != j)]
        y_fold_test = y[(y['fold'] == j)]
        y_fold_train= y[(y['fold'] != j)]
        del X_fold_train['mpg'],X_fold_test['mpg'], X_fold_test['fold'], X_fold_train['fold'], y_fold_train['fold'], y_fold_test['fold']

        ridge_model.fit(X_fold_train.as_matrix(), y_fold_train.as_matrix())
        mse = mean_squared_error(y_fold_test.as_matrix(), ridge_model.predict(X_fold_test.as_matrix()))
        ridge_mse_fold.append(mse)

    coefs_ridge[i] = ridge_model.coef_[0]
    ridge_mse_list.append(ridge_mse_fold)
    ridge_mse_mean.append(np.array(ridge_mse_list).mean())

# Find the best ridge parameter
min_index_ridge = ridge_mse_mean.index(min(ridge_mse_mean))
print "Best Ridge Parameter: ", ridge_reg_params[min_index_ridge], "with MSE= ", min(ridge_mse_mean)   

# Plot each coefficient on Ridge plot
for coef in coefs_ridge.T:
    plt.plot(ridge_reg_params, coef)

plt.xlabel('Alpha')
plt.ylabel('Standardized Coefficients')
plt.xlim(min(ridge_reg_params),max(ridge_reg_params))
plt.title('Ridge Model')

# Plot the average Ridge CV Error across folds with a line for the best parameter
plt.figure(4)
plt.plot(-np.log(ridge_reg_params),
    np.sqrt(np.array(ridge_mse_list)).mean(axis=1))
plt.axvline(-np.log(ridge_reg_params[min_index_ridge]), color = 'red')
plt.xlabel(r'-log(lambda)')
plt.ylabel('RMSE (Avg across all folds)')
plt.title('Ridge CV Error')

plt.show()


### Part 1C ###

autos_1c = pd.read_csv("autos.csv")

autos_train_1c = autos_1c[(autos_1c["train"] == True)]
del autos_train_1c["train"]
autos_test_1c = autos_1c[(autos_1c["train"] == False)]
del autos_test_1c["train"]

names = autos_train_1c.columns.tolist()

X_train = autos_train_1c[names[1:len(names)]]
X_test = autos_test_1c[names[1:len(names)]]
y_train = autos_train_1c[names[0]]
y_test = autos_test_1c[names[0]]

train = np.matrix(X_train)
test = np.matrix(X_test)

# Build and fit models - for Lasso/Ridge, alpha chosen from results of 1A and 1B
lasso_model_1c = Lasso(alpha=0.01, normalize=True)
ridge_model_1c = Ridge(alpha=0.05, normalize=True)
linreg_model_1c = LinearRegression()

lasso_model_1c.fit(X_train.as_matrix(), y_train.as_matrix())
ridge_model_1c.fit(X_train.as_matrix(), y_train.as_matrix())
linreg_model_1c.fit(train, y_train.as_matrix())

lasso_model_1c.predict(X_test.as_matrix())
ridge_model_1c.predict(X_test.as_matrix())
linreg_model_1c.predict(test)

mse_lasso = mean_squared_error(y_test.as_matrix(), lasso_model_1c.predict(X_test.as_matrix()))
mse_ridge = mean_squared_error(y_test.as_matrix(), ridge_model_1c.predict(X_test.as_matrix()))
mse_linreg = mean_squared_error(y_test.as_matrix(), linreg_model_1c.predict(test))

print "Lasso MSE: ", mse_lasso
print "Ridge MSE: ", mse_ridge
print "Least Squares MSE: ", mse_linreg


### Part 1D ###
 
# Find the variables that got dropped in Lasso
print 'Deg. Coefficient'
print pd.Series(np.r_[lasso_model_1c.intercept_, lasso_model_1c.coef_]) , "\n"

# Remove "displacement" and "acceleration" variables from data and rerun the model
X_train_new = X_train.drop('displacement', axis=1)
X_train_new = X_train.drop('acceleration', axis=1)
X_test_new = X_test.drop('displacement', axis=1)
X_test_new = X_test.drop('acceleration', axis=1)

new_train = np.matrix(X_train_new)
new_test = np.matrix(X_test_new)
y_train = autos_train_1c[names[0]]
y_test = autos_test_1c[names[0]]

linreg_model_1c_new = LinearRegression()
linreg_model_1c_new.fit(new_train,y_train.as_matrix())
linreg_model_1c_new.predict(new_test)

mse_linreg_new = mean_squared_error(y_test.as_matrix(), linreg_model_1c_new.predict(new_test))
print "Linear Regression MSE: ", mse_linreg_new
