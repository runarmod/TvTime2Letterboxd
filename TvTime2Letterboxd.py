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


def to_csv(df: pd.DataFrame, filename: str, batch_size: int = 1900):
    if len(df) <= batch_size:
        df.to_csv(filename, index=False)
        return

    name, ext = filename.rsplit(".", maxsplit=1)
    for file_nr, _df in enumerate(
        [df.iloc[i : i + batch_size] for i in range(0, len(df), batch_size)],
        start=1,
    ):
        _df.to_csv(
            name + f"_{file_nr}.{ext}",
            index=False,
        )


watched_df = get_watched_movies(df)
to_csv(watched_df, "letterboxd.csv")

watchlist_df = get_watchlist_movies(df, watched_df)
to_csv(watchlist_df, "letterboxd_watchlist.csv")
