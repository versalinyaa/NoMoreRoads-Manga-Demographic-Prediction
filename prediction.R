## Importing libraries
## ============================================================================
library(dplyr)
library(tidyr)
library(randomForest)

# testing
library(fastDummies)

## Loading data
## ============================================================================
manga_raw <- read.csv("manga.csv")

## Doing some final data wrangling in preparation for ML
## ============================================================================
zeroed_df <- manga_raw %>% 
  mutate(run_length = end_date_days - start_date_days) %>%
  mutate(across(where(is.numeric) & !starts_with("run_"), \(x) replace_na(x, 0) ) ) %>%
  mutate(source = if_else(source=="", "UNKNOWN", source) ) %>%
  select(-c(id:start_date), -end_date, -end_date_days, -status_COMPLETED_count) %>%
  dummy_cols(., remove_selected_columns = T)

## Building some new features from existing features
## ============================================================================
vars_computed_df

## Checking for predictor variables which tend to look different between the
## training set and test set, which will cause our model to overfit
## ============================================================================
set_for_time_dependence_checking <- zeroed_df %>% 
  mutate(which_set = if_else(is.na(run_length), 
                             "incomplete_manga", 
                             "complete_manga"), which_set = factor(which_set)) %>%
  select(-run_length)

set.seed(1234)
time_dependence_rf <- randomForest::randomForest(
  set_for_time_dependence_checking[,!(colnames(set_for_time_dependence_checking) %in% c("which_set") )], 
  set_for_time_dependence_checking[,"which_set"], 
  strata = set_for_time_dependence_checking$which_set, 
  sampsize = c(440, 440), 
  importance = T)

# The model does a good job predicting which set the observations are in
time_dependence_rf

# Getting variable importance list
time_dependence_var_importance <- time_dependence_rf$importance %>% data.frame()


## Checking for highly correlated predictors (work in progress)
## ============================================================================
Highly_Correlated <- zeroed_df %>%
  cor() %>%
  as.data.frame() %>%
  mutate(var1 = rownames(.)) %>%
  gather(var2, value, -var1) %>%
  arrange(desc(value)) %>% filter(var1 != var2, value >= .75)

## Splitting into training set and set of unfinished manga whose run lengths
## we will predict
## ============================================================================
training_df <- zeroed_df %>% filter(!is.na(run_length))
testing_df <- zeroed_df %>% filter(is.na(run_length))

## Establishing baseline random forest accuracy (60% of variance explained)
## ============================================================================
set.seed(1234)
baseline_rf <- randomForest::randomForest(
  training_df[,!(colnames(training_df) %in% c("run_length") )], 
  training_df[,"run_length"],
  importance = T)

## Adjusting some hyperparameters
## ============================================================================

set.seed(1234)
randomForest::randomForest(
  training_df[,!(colnames(training_df) %in% c("run_length") )], 
  training_df[,"run_length"],  nodesize = 10 )


