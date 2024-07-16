# Anilist Demographic Prediction Project

This repository contains a script for scraping the API maintained by the media cataloging service AniList for a large volume of manga listings. From there code will be used to explore the data, engineer new features, and use a random forest classifier to predict the demographic label of a given manga based on its features.

### Key concepts

[Manga](https://en.wikipedia.org/wiki/Manga) is a type of comic originating from Japan, although AniList uses the term more broadly to also refer to similar works published in Korea, China, and Taiwan.

[AniList](https://anilist.co) is a media tracking site for anime and manga, similar to what [Goodreads](https://www.goodreads.com/) is for books or [Letterboxd](https://letterboxd.com/) is for movies. The site relies largely on user contributions to add new listings and provide up-to-date information for existing listings, although it has a team of moderators to check user contributions as well.

[Manga Demographic Groups](https://en.wikipedia.org/wiki/Sh%C5%8Dnen_manga) refer to the way manga magazine publishers in Japan categorize their magazines by the presumed demographic audience they are attempting to reach. In general, "shounen" is intended for adolescent boys, "shoujo" is intended for adolescent girls, "josei" is intended for adult women, and "seinen" is intended for adult men. The actual readership of these works is often more diverse than these labels suggest, and some have suggested that the meaning of these categories has changed over time, and more suggest a sort of "genre" rather than explicitly attemtping to reach one sort of reader.

This project includes a [data dictionary]("./data/data_dictionary.md") in order to provide a more detailed look into the individual features contained within the data set.

## Sub-projects

This project has been divided up into several sub-projects, each with their own directory in the repository, for clarity.

### [Data Gathering](https://github.com/NoMoreRoads/Manga-Demographic-Prediction/tree/main/1_data_gather)

The data gather script sends iterative requests to the [AniList API](https://anilist.gitbook.io/anilist-apiv2-docs/overview/graphql/getting-started) containing queries written in GraphQL, in order to scrape the API for data on manga listed on the site within specified parameters (over 200 people have it on their "list", it is not considered "adult"). The queried information is then wrangled into a more recognizably rectangular format, rather than the graph structure it is intially returned in. This rectangular structure is placed into a pandas dataframe, and then exported as a csv for further processing.

The tag gather script queries the Anilist API for the full list of media tags (excluding adult tags) with their associated descriptions, formats the result, converts it to pandas dataframe format, and exports the result as a csv which serves as an appendix to the data dictionary.

### [Data Exploration](https://github.com/NoMoreRoads/Manga-Demographic-Prediction/tree/main/2_data_explore)

This Jupyter Notebook utilizes Pandas and other Python libraries to explore the data obtained from AniList, with an eye towards imputing missing values, feature engineering, and eventually leveraging classification algorithms to predict the demographic label. 

The notebook also performs some data wrangling tasks, as the data extracted from the API is not fully formatted the way we need to perform useful analysis.
