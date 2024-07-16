# Data Dictionary

Note that the information listed here is derived from a combination of [AniList's API documentation](https://anilist.github.io/ApiV2-GraphQL-Docs/) and domain knowledge of the author, where the former source does not give clear documentation on the meaning of raw data.

The appendix to this data dictionary, which includes the site-generated descriptions of all "tag" features, can be accessed [here](../data/tag_reference.csv)

*note that for all features involving characters, a limiatation of the current data collection process is that only 50 of each character role type (main, supporting, and background) are collected. For media with more than 50 of any one of these roles listed, the count may be artificially limited.*

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
The following are features whose names are not hard-coded during the data collection process, but rather are named according to some programmatic process. The names given here may not match the feature names present in the data, but some explanation will be given as to the format of the name. Dyanmic portions of the tag name will be enclosed in square brackets \[\].

### scored_\[##\]_count:
The number of users who have given the manga a score (bounded between 1 and 100, inclusive) that the site considers to fall within a given \[##\] bucket. AniList's precise methodology for determining these buckets is not clear.

### status_\[statusname\]_count:
The number of users who have the work listed under a given status \[statusname\] on their list. Usually "PLANNING" indicates that they intend to read it, "DROPPED" indicates that they began reading the work but did not finish, etc.

### \[genre\]:
A series of binary features indicating whether the work is listed as being of the genre \[genre\]. Genres are not mutually exclusive, and a work can be listed under multiple genres. The possible genres are: Action, Adventure, Comedy, Drama, Ecchi, Fantasy, Horror, Mahou Shoujo, Mecha, Music, Mystery, Psychological, Romance, Sci-Fi, Slice of Life, Sports, Supernatural, and Thriller.

### \[tag\]:
A series of features indicating the score (0 to 100, inclusive) users have given to a given tag \[tag\]. The score is meant to represent how central a theme the tag is to the work, where zero indicates that no user has submitted the tag to the work, and 100 indicates that it is a central theme. Each tag is associated with a given category ("category"). **the site-generated descriptions of each tag are enumerated in the appendix to this data dictionary, which can be accessed [here](../data/tag_reference.csv).**

### relation_\[relationtype\]:
A feature indicating the number of related media that are related in a given way \[relationtype\]. Examples may include the number of sequels, prequels, or spinoffs a work has.

### relationmedia_\[mediatype\]:
A feature indicating the number of related media that are of a given format type \[meditype\]. Examples my include the number of novels related to the work, or the number of movies.

### \[gender\]_\[type\]_roles:
The number of characters associated with the property who have a given gender \[gender\] and role type \[type\]. Note that gender can be any string, and role type can be one of "main", "supporting", or "background". Excludes characters with a missing gender value.
