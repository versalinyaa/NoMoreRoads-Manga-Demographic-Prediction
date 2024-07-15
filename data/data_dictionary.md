# Data Dictionary

Note that the information listed here is derived from a combination of [AniList's API documentation](https://anilist.github.io/ApiV2-GraphQL-Docs/) and domain knowledge of the author, where the former source does not give clear documentation on the meaning of raw data.

## Static Feature Names
The following are features whose names are hard-coded during the data collection process.

### id:
A unique identifier for each manga entry.

### eng_title:
The official english-language title for the manga. Usually if blank, indicates that the work has not been licensed and officially released in the English-speaking world.

### rom_title:
The native-language title in romaji (in other words, the native title written phonetically in the roman alphabet).

### popularity:
The number of AniList users who have the manga on their “list”.

### mean_score:
Users can give a score ranging from 1 to 100 (inclusive) to a manga. This measure reports the mean for all users who have scored the manga.

### status:
The release status of the media-- for instance if it has not yet begun serialization, or if it has been completed.

### chapters:
The number of chapters a work was released in after completion, or at the point it was cancelled or put on hiatus.

### volumes:
The number of volumes the work was released in after completion, or at the point it was cancelled or put on hiatus.

### start_year:
The year the work initially released in.

### start_month:
The month the work initially released in.

### start_day:
The day the work initially released on.

### end_year:
The year the work finished or was canceled in.

### end_month:
The month the work  finished or was canceled in.

### end_day:
The day the work  finished or was canceled on.

### favorites:
The number of AniList users who have marked the manga as a "favorite".

### source:
The type of media the work is an adaptation of. If it is not an adaptation of another work, it is listed as "ORIGINAL".

### country:
The country of origin of the work.

### total_main_roles;
The number of characters AniList users have associated with the work who are listed as having a "main" cast role in the work.

### total_supporting_roles:
The number of characters AniList users have associated with the work who are listed as having a "supporting" cast role in the work.

### total_background_roles:
The number of characters AniList users have associated with the work who are listed as having a "supporting" cast role in the work.

## Dynamic Feature Names
The following are features whose names are not hard-coded during the data collection process, but rather are named according to some programmatic process. The names given here may not match the feature names present in the data, but some explanation will be given as to the format of the name.

## scored_##_count:
The number of users who have given the manga a score (bounded between 1 and 100, inclusive) that the site considers to fall within a given "##" bucket. AniList's precise methodology for determining these buckets is not clear.
