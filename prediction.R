# Copyright 2024 Zach Lesher <lesher.zachary@protonmail.com>
# SPDX-License-Identifier: MIT

## Importing libraries
## ============================================================================
library(dplyr)
library(tidyr)
library(ranger)
#library(caret)
library(smotefamily)
library(purrr)
#library(randomForest)

# testing
library(fastDummies)

## Loading data
## ============================================================================
manga_raw <- read.csv("manga.csv")

## Testing to see if any columns have more than 1 genre tag
## ============================================================================
demo_tags <- c("Shoujo", "Shounen", "Seinen", "Josei")

## Doing some final data wrangling in preparation for ML
## ============================================================================
zeroed_df <- manga_raw %>% 
  mutate(across(where(is.numeric), \(x) replace_na(x, 0) ) ) %>%
  mutate(source = if_else(source=="", "UNKNOWN", source) ) %>%
  select(-c(id:start_date), -end_date, -end_date_days) %>%
  dummy_cols(., remove_selected_columns = T) %>%
  mutate(demo = if_else( Shoujo+Shounen+Josei+Seinen == 0, 
                         "None", 
                         colnames(select(., all_of(demo_tags)))[max.col(select(., all_of(demo_tags)))] )) %>%
  select(-all_of(demo_tags)) %>% 
  mutate( popularity = rowSums(across(starts_with("status_"))) ) %>% 
  mutate(across(starts_with("status_"), \(x) x/popularity  ),
         favorites = favorites/popularity, 
         users_scored = rowSums(across(starts_with("scored_"))),
         across(starts_with("scored_"), \(x) x/users_scored  ),
         users_scored_pct = users_scored/popularity) %>%
  select(-users_scored)


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
training_df <- zeroed_df %>% filter(demo != "None") %>% mutate(demo = factor(demo))
testing_df <- zeroed_df %>% filter(demo == "None")

## Establishing baseline random forest performance
## ============================================================================
wt_shounen <- nrow(training_df) / (4*sum(training_df$demo == "Shounen"))
wt_shoujo <- nrow(training_df) / (4*sum(training_df$demo == "Shoujo"))
wt_seinen <- nrow(training_df) / (4*sum(training_df$demo == "Seinen"))
wt_josei <- (nrow(training_df) / (4*sum(training_df$demo == "Josei")) )

caseweight <- case_when(training_df$demo == "Shounen" ~ wt_shounen,
                        training_df$demo == "Shoujo" ~ wt_shoujo,
                        training_df$demo == "Seinen" ~ wt_seinen,
                        training_df$demo == "Josei" ~ wt_josei)

baseline_rf <- ranger::ranger(formula = demo~., 
                              data = training_df, 
                              num.trees = 1300, 
                              importance = "impurity", 
                              case.weights = caseweight,
                              class.weights = c(wt_josei, wt_seinen, wt_shoujo, wt_shounen),
                              seed = 1234)

## Attempting to deal with poor recall for the Josei class by using SMOTE
## ===========================================================================

validation_indices_vector <- sample(1:nrow(training_df), replace = F, size = nrow(training_df)*.2)

training_df_2 <- training_df[-validation_indices_vector,]
validation_df <- training_df[validation_indices_vector,]

training_df_josei_only <- training_df_2 %>% filter(demo == "Josei")

synthetic_josei_manga <- SMOTE( X = subset(training_df_josei_only, select = -c(demo)), 
                                target = training_df_josei_only$demo,
                                K = 1)
