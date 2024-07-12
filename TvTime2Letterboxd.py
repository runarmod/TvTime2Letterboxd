import pandas as pd

df = pd.read_csv("tracking-prod-records.csv", sep=",", encoding="utf-8")

# Only keep movies with a name
df.dropna(subset=["movie_name", "release_date", "created_at"], inplace=True)

# Use Letterboxd column names
df.rename(
    columns={
        "movie_name": "Title",
        "release_date": "Year",
        "created_at": "WatchedDate",
    },
    inplace=True,
)

# Format the dates as Letterboxd expects
df["WatchedDate"] = pd.to_datetime(df["WatchedDate"]).dt.date
df["Year"] = pd.to_datetime(df["Year"]).dt.year

# Only keep movies
df = df[df["entity_type"] == "movie"]


def get_watched_movies(df):
    watched_df = df[df["type"] == "watch"]

    return watched_df[["Title", "Year", "WatchedDate"]]


def get_watchlist_movies(df, watched_df):
    watchlist_df = df[df["type"] == "towatch"]

    # Remove movies that are already watched based on Title and Year
    watchlist_df = watchlist_df.merge(
        watched_df, on=["Title", "Year"], how="left", indicator=True
    )
    watchlist_df = watchlist_df[watchlist_df["_merge"] == "left_only"]

    return watchlist_df[["Title", "Year"]]


watched_df = get_watched_movies(df)
watched_df.to_csv("letterboxd.csv", index=False)

watchlist_df = get_watchlist_movies(df, watched_df)
watchlist_df.to_csv("letterboxd_watchlist.csv", index=False)
