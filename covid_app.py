import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
import sys
import altair as alt
import pydeck as pdk

import json
import pathlib
from typing import Optional
import geopandas as gpd
from bokeh.models import ColorBar, GeoJSONDataSource, LinearColorMapper
from bokeh.palettes import brewer  # pylint: disable=no-name-in-module
from bokeh.plotting import figure

import time
import random

if sys.version_info[0] < 3:
    reload(sys) # noqa: F821 pylint:disable=undefined-variable
    sys.setdefaultencoding("utf-8")

@st.cache
def get_data(url):
    df = pd.read_csv(url, error_bad_lines=False)
    return df


df = get_data('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/03-18-2020.csv')
df = df.replace({"US": "United States of America"})
confirmed = pd.DataFrame(df.groupby("Country/Region")["Confirmed"].agg(np.sum))
location = df.groupby("Country/Region")["Longitude", "Latitude"].agg(np.median)
grouped = confirmed.merge(location, on="Country/Region").reset_index()

st.write("COVID-19 Cases", df.sort_index())
midpoint = (np.average(df["Latitude"]), np.average(df["Longitude"]))
st.write("Worldwide Cases", pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 1,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=df[["Latitude", "Longitude", "Confirmed"]],
            get_position=["Longitude", "Latitude"], # radius=100,
            radiusScale=10  ,
            get_radius="Confirmed",
            get_fill_color='[180, 0, 200, 140]',
            pickable=True,
            extruded=True,
        ),
    ],
))


us_data = df[df["Country/Region"] == "United States of America"][["Province/State", "Latitude", "Longitude", "Confirmed"]]
st.write("US COVID-19 Cases", us_data.sort_index())
midpoint = (np.average(us_data["Latitude"]), np.average(us_data["Longitude"]))
st.write("US Cases", pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 2.5,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=us_data[["Latitude", "Longitude", "Confirmed"]],
            get_position=["Longitude", "Latitude"], # radius=100,
            radiusScale=100,
            get_radius="Confirmed",
            get_fill_color='[180, 0, 200, 140]',
            pickable=True,
            extruded=True,
        ),
    ],
))

ts_data = get_data("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv")
recovered = get_data("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv")
deaths = get_data("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv")
# ts_data = ts_data[ts_data["Country/Region"] == "US"]
#st.write(ts_data[~ts_data["Province/State"].str.contains(",")])
ts_data = ts_data.reset_index(drop=True)

# ts_data = ts_data.loc[:51]

# recovered = recovered[recovered["Country/Region"] == "US"]
recovered["Long"] = [i + 0.2 for i in recovered["Long"]]
# recovered = recovered[~recovered["Province/State"].str.contains(",")]
recovered = recovered.reset_index(drop=True)
# recovered = recovered.loc[:51]

# deaths = deaths[deaths["Country/Region"] == "US"]
deaths["Long"] = [i - 0.2 for i in deaths["Long"]]
# ts_data = ts_data[~ts_data["Province/State"].str.contains(",")]
deaths = deaths.reset_index(drop=True)
# deaths = deaths.loc[:51]

dates = ts_data.columns[4:]

date_val = st.empty()
date_slider = st.empty()
map = st.empty()
midpoint = (np.average(ts_data["Lat"]), np.average(ts_data["Long"]))
def render_slider(date):
    key = random.random() if animation_speed else None
    val = date_slider.slider("", 0, len(dates), value=date,
                                 format="", key=key)
    date_val.subheader(dates[date])

def render_map(date):
    temp_ts_data = ts_data.rename(columns={dates[date]: "Confirmed"})
    temp_recovered = recovered.rename(columns={dates[date]: "Recovered"})
    temp_deaths = deaths.rename(columns={dates[date]: "Deaths"})
    map.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": midpoint[0],
            "longitude": midpoint[1],
            "zoom": 1,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
                "ColumnLayer",
                data=temp_ts_data[["Lat", "Long", "Confirmed"]],
                disk_resolution=12,
                radius=130000,
                elevation_scale=100,
                get_position=["Long", "Lat"],
                get_fill_color=[253, 116, 31, 255], #180, 0, 200, 140
                get_elevation="Confirmed"
            ),
            pdk.Layer(
                "ColumnLayer",
                data=temp_recovered[["Lat", "Long", "Recovered"]],
                disk_resolution=12,
                radius=130000,
                elevation_scale=100,
                get_position=["Long", "Lat"],
                get_fill_color=[113, 99, 56, 255], #180, 0, 200, 140
                get_elevation="Recovered"
            ),
            pdk.Layer(
                "ColumnLayer",
                data=temp_deaths[["Lat", "Long", "Deaths"]],
                disk_resolution=12,
                radius=130000,
                elevation_scale=100,
                get_position=["Long", "Lat"],
                get_fill_color=[253, 31, 57, 255], #180, 0, 200, 140
                get_elevation="Deaths"
            ),
        ],
    ))

animation_speed = 0.05
if animation_speed:
    for i in range(len(dates)):
        time.sleep(animation_speed)
        render_slider(i)
        render_map(i)



st.markdown("Taken from: https://github.com/dmnfarrell/teaching/blob/master/geo/maps_python.ipynb")
shapefile = 'data/ne_110m_admin_0_countries.shp'
#Read shapefile using Geopandas
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
#Rename columns.
gdf.columns = ['country', 'country_code', 'geometry']
gdf = gdf.drop(gdf.index[159])
gdf = gdf.merge(grouped, left_on="country", right_on="Country/Region", how="left")

def get_geodatasource(gdf):
    """Get getjsondatasource from geopandas object"""
    json_data = json.dumps(json.loads(gdf.to_json()))
    return GeoJSONDataSource(geojson = json_data)

def bokeh_plot_map(gdf, column=None, title=''):
    """Plot bokeh map from GeoJSONDataSource """

    geosource = get_geodatasource(gdf)
    palette = brewer['OrRd'][8]
    palette = palette[::-1]
    vals = gdf[column]
    #Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
    color_mapper = LinearColorMapper(palette = palette, low = vals.min(), high = vals.max())
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=500, height=20,
                         location=(0,0), orientation='horizontal')

    tools = 'wheel_zoom,pan,reset'
    p = figure(title = title, plot_height=400 , plot_width=850, toolbar_location='right', tools=tools)
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    #Add patch renderer to figure
    p.patches('xs','ys', source=geosource, fill_alpha=1, line_width=0.5, line_color='black',
              fill_color={'field' :column , 'transform': color_mapper})
    #Specify figure layout.
    p.add_layout(color_bar, 'below')
    return p

p = bokeh_plot_map(gdf, "Confirmed", title="")
#export_png(p, filename="plot.png")
# pn.pane.Bokeh(p)
st.bokeh_chart(p)
