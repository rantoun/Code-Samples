### Logistic Ridge Regression Model ###
### Short Sample ###
### Target variable is binomial ("g" or "b") ###

# Read in and prepare data
ionosphere <- read.table("http://archive.ics.uci.edu/ml/machine-learning-databases/ionosphere/ionosphere.data",sep=",")

# Remove 2nd column (all zeros) and standardize the dataset
ionosphere_clean <- ionosphere[-2]
scaled_ionosphere_clean <- data.frame(scale(ionosphere_clean[1:33]), ionosphere_clean[34])

# Randomly split data into training and test (70%, 30%)
sample_size <- floor(0.70 * nrow(scaled_ionosphere_clean))
train_samp <- sample(seq_len(nrow(scaled_ionosphere_clean)), size = sample_size)

train.x <- as.matrix(scaled_ionosphere_clean[train_samp,1:33])
train.y <- as.matrix(as.numeric(scaled_ionosphere_clean[train_samp,34]))
test.x <- as.matrix(scaled_ionosphere_clean[-train_samp,1:33])
test.y <- as.matrix(as.numeric(scaled_ionosphere_clean[-train_samp,34]))

# Perform 10-fold cross validation to find best lambda and use for predictions
library(glmnet)
cv_out <- cv.glmnet(train.x, train.y, alpha=0)
best_lambda = cv_out$lambda.min
# best_lambda = 0.193331
ridge_logit <- glmnet(train.x, train.y, family="binomial", alpha=0)
trainpred.y <- predict(ridge_logit, s=best_lambda, newx = train.x, type = "class")
testpred.y <- predict(ridge_logit, s=best_lambda, newx = test.x, type = "class")

# Get classification tables for train and test
train_accuracy <- table(trainpred.y, train.y)
train_accuracy

test_accuracy <- table(testpred.y, test.y)
test_accuracy
