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

## Establishing baseline random forest accuracy (60% of variance explained)
## ============================================================================
set.seed(1234)
baseline_rf <- randomForest::randomForest(
  training_df[,!(colnames(training_df) %in% c("demo") )], 
  training_df[,"demo"],
  strata = training_df$demo,
  sampsize = c(80,80,80,80))


