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


