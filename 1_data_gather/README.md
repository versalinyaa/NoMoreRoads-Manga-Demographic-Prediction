## AniList Data Gathering

*NOTE: see the [full project readme for additional context](https://github.com/NoMoreRoads/Manga-Demographic-Prediction/tree/main); this is a sub-project of a larger undertaking.*

The data gather script sends iterative requests to the [AniList API](https://anilist.gitbook.io/anilist-apiv2-docs/overview/graphql/getting-started) containing queries written in GraphQL, in order to scrape the API for data on manga listed on the site within specified parameters (over 200 people have it on their "list", it is not considered "adult"). The queried information is then wrangled into a more recognizably rectangular format, rather than the graph structure it is intially returned in. This rectangular structure is placed into a pandas dataframe, and then exported as a csv for further processing.

The tag gather script queries the Anilist API for the full list of media tags (excluding adult tags) with their associated descriptions, formats the result, converts it to pandas dataframe format, and exports the result as a csv which serves as an appendix to the data dictionary.
