### Built 2 types of portfolios --> Equal-weighted and Value-weighted for each of dividend initiations and stock splits ###
### Equal-weighted --> each stock treated equally no matter how small ; Value-weighted --> tilt towards larger stocks ###
### This code calculates the returns for :    ###
###   1) Equal-weighted Stock Split           ###
###   2) Value-weighted Stock Split           ###
###   3) Equal-weighted Dividend Initiation   ###
###   4) Value-weighted Dividend Initiation   ###

### 4 Regressions are run at the end to output the Alphas and Betas of each portfolio ###

library(plyr)

# Read in file created from DataProcessing.R
latest_dt <- read.csv("Data_for_Analysis.csv")

#----------------------------------------------------------------------------#
### CALCULATE RETURNS FOR STOCKS WITH SPLITS ###
latest_dt$split_mktcap <- latest_dt$price*latest_dt$shrout
split_tot_mktcap <- aggregate( split_mktcap ~ date , data = latest_dt[latest_dt$hold_split==1, ] , FUN = sum, na.action = na.omit )
data <- merge(x=data.frame(latest_dt), y=split_tot_mktcap, by.x="date", by.y="date")

# Calculate weights
data$wt_split <- data$split_mktcap.x / data$split_mktcap.y
# Calculate individual weighted return
data$split_ret <- ifelse(data$hold_split == 1, data$return_incl_divs, 0)
data$wt_split_ret <- data$split_ret * data$wt_split
# Calculate equal weighted monthly return
eq_split_mean_ret <- aggregate( split_ret ~ date , data = data[data$hold_split==1, ] , FUN = mean, na.action = na.omit )
# Calculate average weighted monthly return
wt_split_mean_ret <- aggregate( wt_split_ret ~ date , data = data[data$hold_split==1, ] , FUN = sum, na.action = na.omit )

summary_table <- data.frame(eq_split_mean_ret)
names(summary_table)[2] <- "eq_split_ret"
summary_table$wt_split_ret <- wt_split_mean_ret$wt_split_ret

#----------------------------------------------------------------------------#
### CALCULATE RETURNS FOR STOCKS WITH DIVIDEND INITIATIONS ###
data$div_mktcap <- data$price*data$shrout
div_tot_mktcap <- aggregate( div_mktcap ~ date , data = data[data$hold_div==1, ] , FUN = sum, na.action = na.omit )
data <- merge(x=data.frame(data), y=div_tot_mktcap, by.x="date", by.y="date")

# Calculate weights
data$wt_div <- data$div_mktcap.x / data$div_mktcap.y
# Calculate individual weighted return
data$div_ret <- ifelse(data$hold_div == 1, data$return_incl_divs, 0)
data$wt_div_ret <- data$div_ret * data$wt_div
# Calculate equal weighted monthly return
eq_div_mean_ret <- aggregate( div_ret ~ date , data = data[data$hold_div==1, ] , FUN = mean, na.action = na.omit )
# Calculate average weighted monthly return
wt_div_mean_ret <- aggregate( wt_div_ret ~ date , data = data[data$hold_div==1, ] , FUN = sum, na.action = na.omit )

summary_table <- merge(x=summary_table, y=eq_div_mean_ret, by.x="date",by.y="date")
names(summary_table)[4] <- "eq_div_ret"
summary_table$wt_div_ret <- wt_div_mean_ret$wt_div_ret

### REGRESSIONS ###

### Four-factor Model ###
### Create table of factors --> 1) Market Risk-Free Rate, 2) SMB (Small Minus Big), 3) HML (High Minus Low), 4) MOM (Momentum)

# Get factors from data
factors <- unique(data[c("date","market_return","MktRF","SMB","HML","RF","MOM")])

# Sort factors by date and add each type of the returns
factors <- arrange(factors, date)
factors$split_eq_mean_ret <- summary_table$eq_split_ret
factors$split_wt_mean_ret <- summary_table$wt_split_ret
factors$div_eq_mean_ret <- summary_table$eq_div_ret
factors$div_wt_mean_ret <- summary_table$wt_div_ret

### Excess Returns for each regression
factors$y_split.eq <- factors$split_eq_mean_ret - factors$RF
factors$y_split.wt <- factors$split_wt_mean_ret - factors$RF

factors$y_div.eq <- factors$div_eq_mean_ret - factors$RF
factors$y_div.wt <- factors$div_wt_mean_ret - factors$RF

### Equal Weighted Regressions ###
reg.split.eq <- lm(y_split.eq ~ MktRF + SMB + HML + MOM, data=factors)
summary(reg.split.eq)
reg.div.eq <- lm(y_div.eq ~ MktRF + SMB + HML + MOM, data=factors)
summary(reg.div.eq)

### Value Weighted Regressions ###
reg.split.wt <- lm(y_split.wt ~ MktRF + SMB + HML + MOM, data=factors)
summary(reg.split.wt)
reg.div.wt <- lm(y_div.wt ~ MktRF + SMB + HML + MOM, data=factors)
summary(reg.div.wt)
