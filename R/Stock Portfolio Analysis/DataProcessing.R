### Project to analyze portfolio returns based on 1) company dividend initiations and 2) company stock splits  ###
### Dataset is 2.5 million rows with over 20,000 unique stocks spanning between Jan 1980 and Dec 2014 --> 220 MB in size ###
### 1) Dividend paid out whenever column "return_incl_divs" and "return_ex_divs" are not equal ###
### 2) Criteria for dividend intiation was if a company has not paid a dividend in over 13 months ###
### 3) Stock splits occur when value in "shrout_adj_factor" is not NA ###

### If a stock initiated a dividend, then we would hold that stock in the portfolio for 1 year (or until the end of that stock's time on the market), beginning the month after the initiation ###
### If a stock split occurred, we would also hold the stock in the portfolio for 1 year or until current time ###

### Result of this code is a dataset containing columns for 1) when you would hold a stock in your portfolio based on dividend initations
### and 2) when you would hold a stock in your portfolio based on stock splits

library(zoo)
library(dplyr)
library(plyr)
library(data.table)
options(gsubfn.engine = "R")
library(sqldf)

setwd("~/Desktop/Spring 2015/RM294 - Quant Investments/Assignment1")
data <- read.csv("HW1 Data.csv")

data$date <- as.Date(data$date,"%d%b%Y")

# Remove Nulls, Duplicates, and add stock split / dividend payout columns
data2 <- data[!is.na(data$price),]
data2 <- data2[!is.na(data2$return_incl_divs),]
data2 <- sqldf("SELECT DISTINCT * FROM data2")
data2$divflag <- ifelse(data2$return_incl_divs == data2$return_ex_divs, 0, 1)
data2$split <- data2$shrout_adj_factor
data2$split[is.na(data2$split)] = 0
data2$splitflag <- ifelse(data2$split != 0, 1, 0)

# Table with only only stocks/months with dividend payouts
div_table <- data2[which(data2$divflag == 1),]

### DIVIDENDS ###
# Use data table to lag dates by stock_ID for date comparison
div_dt <- data.table(div_table,key=c("stock_ID","date"))
div_dt <- div_dt %>%group_by(stock_ID) %>% filter( !((duplicated(date)|duplicated(date,fromLast=TRUE)) & is.na(shrout_adj_factor)))
div_dt[,lag.date:=c(NA,date[-.N]),by=stock_ID]
div_dt$lag.date <- as.Date(div_dt$lag.date,origin = "1970-01-01")

# Calculate time difference in months between previous dividend paid next
div_dt$time_diff <- (as.yearmon(strptime(div_dt$date, format = "%Y-%m-%d"))-as.yearmon(strptime(div_dt$lag.date, format = "%Y-%m-%d")))*12
div_dt$div_init <- ifelse(div_dt$time_diff > 13, 1, 0)
div_dt$div_init <- ifelse(is.na(div_dt$div_init), 1, div_dt$div_init)

# Prep data tables for merge
# Remove rows that have the same stock_ID and date
data2_dt <- data.table(data2,key=c("stock_ID","date","divflag"))
data2_dt <- data2_dt %>% group_by(stock_ID) %>% filter( !((duplicated(date)|duplicated(date,fromLast=TRUE)) & is.na(shrout_adj_factor)))
col_remove <- names(div_dt)[c(3:13,15:16)]
div_dt <- div_dt[,(col_remove):=NULL]
setkeyv(div_dt,cols=c("stock_ID","date","divflag"))

# Merge data2 with div_dt on stock_ID, date
data2_dt <- div_dt[data2_dt,]

# Prepare for adding 1s when dividend is declared multiple times for same stock_ID by creating table of indices for 
div_all_ones <- data.frame(which(data2_dt$div_init == 1))
colnames(div_all_ones)[1] <- "index"
data2_df <- data.frame(data2_dt)
div_ind <- data2_df[div_all_ones$index,"stock_ID"]
ones_stocks <- cbind(div_all_ones,div_ind)
colnames(ones_stocks)[2] <- "stock_ID"
ones_stocks_dt <- data.table(ones_stocks, key="stock_ID")

div_ii <- data2_dt[,.N,by=stock_ID]
div_ii[,start := cumsum(N) - N + 1][,end := cumsum(N)][, N := NULL]
setkeyv(div_ii, cols="stock_ID")

div_ones_stocks_dt <- div_ii[ones_stocks_dt]
div_ones_stocks_dt$chcklast <- ifelse(div_ones_stocks_dt$end - div_ones_stocks_dt$index < 13, 1, 0) 

# Find indices of 1s in div_init and add 1s to hold_divs starting month after div_init
div_hold <- rep(0,nrow(data2_dt))
for(i in 1:nrow(div_ones_stocoks_dt))
{
  if(div_ones_stocks_dt$chcklast[i] == 0){
    indices <- seq((div_ones_stocks_dt$index[i] + 1), (div_ones_stocks_dt$index[i] + 12))
    div_hold[indices] <- 1
  }
  else if(div_ones_stocks_dt$chcklast[i] == 1){
    indices <- seq((div_ones_stocks_dt$index[i] + 1), div_ones_stocks_dt$end[i])
    div_hold[indices] <- 1
  }
  else if(div_ones_stocks_dt$index[i] == div_ones_stocks_dt$end[i]){
    div_hold <- 0
  }
}

data2_dt$hold_div <- div_hold

### Remove issue where first month of stock had stock being held
div_firsts <- data2_dt[J(unique(stock_ID)), mult = "first"]
div_firsts_vec <- div_firsts[which(div_firsts$hold_div == 1),]
div_firsts$hold_div <- 0
col_remove2 <- names(div_firsts)[c(3:19,21)]
div_firsts <- div_firsts[,(col_remove2):=NULL]
setkeyv(div_firsts,cols=c("stock_ID","date"))

latest_dt <- div_firsts[data2_dt]
names(latest_dt)[21] <- "hold_div_keep"

latest_dt$hold_div <- ifelse(is.na(latest_dt$hold_div),1,0)
old_hold <- latest_dt$hold_div
new_hold <- latest_dt$hold_div_keep

new_hold <- ifelse(old_hold == 0, 0, new_hold)
latest_dt$hold_div_keep <- new_hold
latest_dt$hold_div <- NULL
names(latest_dt)[20] <- "hold_div"

### STOCK SPLITS ###
# Prepare for adding 1s when dividend is declared multiple times for same stock_ID by creating table of indices for 
split_all_ones <- data.frame(which(latest_dt$splitflag == 1))
colnames(split_all_ones)[1] <- "index"
latest_df <- data.frame(latest_dt)
split_ind <- latest_df[split_all_ones$index,"stock_ID"]
split_ones_stocks <- cbind(split_all_ones,split_ind)
colnames(split_ones_stocks)[2] <- "stock_ID"
split_ones_stocks_dt <- data.table(split_ones_stocks, key="stock_ID")

split_ii <- latest_dt[,.N,by=stock_ID]
split_ii[,start := cumsum(N) - N + 1][,end := cumsum(N)][, N := NULL]
setkeyv(split_ii, cols="stock_ID")

split_ones_stocks_dt <- split_ii[split_ones_stocks_dt]
split_ones_stocks_dt$chcklast <- ifelse(split_ones_stocks_dt$end - split_ones_stocks_dt$index < 13, 1, 0) 

# Find indices of 1s in splitflag and add 1s to hold_divs starting month after splitflag
split_hold <- rep(0,nrow(latest_dt))
for(i in 1:nrow(split_ones_stocks_dt))
{
  if(split_ones_stocks_dt$chcklast[i] == 0){
    indices <- seq((split_ones_stocks_dt$index[i] + 1), (split_ones_stocks_dt$index[i] + 12))
    split_hold[indices] <- 1
  }
  else if(split_ones_stocks_dt$chcklast[i] == 1){
    indices <- seq((split_ones_stocks_dt$index[i] + 1), split_ones_stocks_dt$end[i])
    split_hold[indices] <- 1
  }
  else if(split_ones_stocks_dt$index[i] == split_ones_stocks_dt$end[i]){
    split_hold <- 0
  }
}

latest_dt$hold_split <- split_hold

# Create column indicating if there was a stock split OR a dividend initiation
latest_dt$hold_divORsplit <- ifelse(latest_dt$hold_div == 1 | latest_dt$hold_split == 1, 1, 0)

write.csv(latest_dt,"Data_for_Analysis.csv")
