"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv', sep=',')
    departments = pd.read_csv('data/departments.csv', sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged_df = pd.merge(
        departments,
        regions,
        how='left',
        left_on='region_code',
        right_on='code'
    )

    merged_df.rename(
        columns={
            'code_y': 'code_reg',
            'name_y': 'name_reg',
            'code_x': 'code_dep',
            'name_x': 'name_dep'
            },
        inplace=True)

    merged_df = merged_df[['code_reg', 'name_reg', 'code_dep', 'name_dep']]

    return merged_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code'].apply(
        lambda x: x.zfill(2))
    merged_df = pd.merge(
        referendum,
        regions_and_departments,
        how='left',
        left_on='Department code',
        right_on='code_dep'
    )

    merged_df = merged_df.dropna()

    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    res_df = referendum_and_areas.groupby('code_reg').agg(
        {'name_reg': 'first',
         'Registered': 'sum',
         'Abstentions': 'sum',
         'Null': 'sum',
         'Choice A': 'sum',
         'Choice B': 'sum'}
    )

    res_df = res_df[
        ['name_reg', 'Registered', 'Abstentions',
            'Null', 'Choice A', 'Choice B']
    ]

    return res_df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file('data/regions.geojson')
    merged_df = geo_data.merge(
        referendum_result_by_regions,
        left_on='nom',
        right_on='name_reg'
    )
    merged_df['ratio'] = (merged_df['Choice A']
                          / (merged_df['Registered']
                             - merged_df['Abstentions']
                             - merged_df['Null']))
    merged_df.plot(column='ratio', legend=True)

    return merged_df


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
