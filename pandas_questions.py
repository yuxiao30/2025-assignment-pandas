"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd


VOTE_COLS = ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]


def load_data():
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";", encoding="utf-8")
    regions = pd.read_csv("data/regions.csv", sep=",", encoding="utf-8")
    departments = pd.read_csv("data/departments.csv", sep=",", encoding="utf-8")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame are:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    reg = regions[["code", "name"]].copy()
    dep = departments[["region_code", "code", "name"]].copy()

    reg = reg.rename(columns={"code": "code_reg", "name": "name_reg"})
    dep = dep.rename(
        columns={
            "region_code": "code_reg",
            "code": "code_dep",
            "name": "name_dep",
        }
    )

    merged = pd.merge(reg, dep, on="code_reg", how="inner")
    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    Drops DOM-TOM-COM departments and French living abroad, whose codes contain
    'Z'.
    """
    ref = referendum.copy()
    rad = regions_and_departments.copy()

    ref["Department code"] = ref["Department code"].astype(str).str.zfill(2)
    ref = ref[~ref["Department code"].astype(str).str.contains("Z", na=False)]

    merged = ref.merge(rad, left_on="Department code", right_on="code_dep")
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The returned DataFrame is indexed by `code_reg` and has columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas.copy()

    result = (
        df.groupby(["code_reg", "name_reg"], as_index=False)[VOTE_COLS]
        .sum()
        .set_index("code_reg")
    )

    result = result[["name_reg"] + VOTE_COLS]
    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the referendum results.

    Loads geo data from `regions.geojson`, merges into the results, and plots
    the ratio of 'Choice A' over expressed ballots (A + B).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame including a 'ratio' column.
    """
    geo = gpd.read_file("data/regions.geojson").rename(columns={"code": "code_reg"})
    res = referendum_result_by_regions.reset_index().copy()

    gdf = geo.merge(res, on="code_reg", how="inner")

    expressed = gdf["Choice A"] + gdf["Choice B"]
    gdf["ratio"] = gdf["Choice A"] / expressed

    ax = gdf.plot(
        column="ratio",
        cmap="Reds",
        legend=True,
        edgecolor="black",
        linewidth=0.4,
    )
    ax.set_axis_off()
    ax.set_title("Choice A votes by region")
    plt.show()

    return gdf


def main():
    """Run the full pipeline and plot the map."""
    referendum, regions, departments = load_data()

    regions_and_departments = merge_regions_and_departments(regions, departments)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(referendum_and_areas)

    print(referendum_results)
    plot_referendum_map(referendum_results)


if __name__ == "__main__":
    main()