import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
import os
from pathlib import Path
import numpy as np

#path = Path(os.path.dirname(os.path.abspath(__file__)))
path = Path("/Users/User/Desktop/housing/housing/spiders")
os.chdir(path)

#Connect to Plotly API
api_key = "igtL1li0nh0R0yVFNoEn"
username = "natefduncan"
plotly.tools.set_credentials_file(username=username, api_key=api_key)

mapbox_access_token = "pk.eyJ1IjoibmF0ZWR1bmNhbiIsImEiOiJjam01Z3kzMGMxcm1uM2trOGM1c2x6ZnVsIn0.frI_rzsE819mtoRhxt4m8w"

#Get data.
data = pd.read_csv("realtor_data_2019.3.31.csv")

scl = "Picnic"

data = [
    go.Scattermapbox(
        lat=data.lat.tolist(),
        lon=data.lon.tolist(),
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            color=data.acres_lot.tolist(),
            colorscale=scl,
            cmin=min(data.acres_lot.tolist()),
            cmax=max(data.acres_lot.tolist()),
            reversescale=True,
            opacity=.5
        ),
        text=data.url.tolist(),
    )
]

layout = go.Layout(
    autosize=True,
    hovermode='closest',
    mapbox=go.layout.Mapbox(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(
            lat=32.9,
            lon=-96.3
        ),
        pitch=0,
        zoom=5
    ),
)

fig = go.Figure(data=data, layout=layout)
py.iplot(fig, filename='Housing Data')
