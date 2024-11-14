import streamlit as st
import dataiku
import numpy as np
import pandas as pd
import altair as alt

DATE_TIME_COL = "date/time"

#############
# Functions #
#############

@st.experimental_singleton
def load_data(nrows):
    data = dataiku.Dataset("uber_raw_data_sep14") \
        .get_dataframe(limit=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_TIME_COL] = pd.to_datetime(data[DATE_TIME_COL],
                                       format="%m/%d/%Y %H:%M:%S")
    return data

@st.experimental_memo
def histdata(df):
    hist = np.histogram(df[DATE_TIME_COL].dt.hour, bins=24, range=(0, 24))[0]
    return pd.DataFrame({"hour": range(24), "pickups": hist})

##############
# App layout #
##############

# Load a sample from the source Dataset
data = load_data(nrows=10000)

st.title('Uber pickups in NYC')

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

# Histogram

chart_data = histdata(data)
st.write(
    f"""**Breakdown of rides per hour**"""
)

st.altair_chart(
    alt.Chart(chart_data)
    .mark_area(
        interpolate="step-after",
    )
    .encode(
        x=alt.X("hour:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("pickups:Q"),
        tooltip=["hour", "pickups"],
    )
    .configure_mark(opacity=0.2, color="red"),
    use_container_width=True,
)

# Map and slider

hour_to_filter = st.slider('', 0, 23, 17)
filtered_data = data[data[DATE_TIME_COL].dt.hour == hour_to_filter]
st.subheader(f"Map of all pickups at {hour_to_filter}:00")
st.map(filtered_data)
