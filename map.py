import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
import os
from pathlib import Path
import numpy as np

#path = Path(os.path.dirname(os.path.abspath(__file__)))
path = Path("/Users/User/Desktop/housing")
os.chdir(path)

#Connect to Plotly API
api_key = "igtL1li0nh0R0yVFNoEn"
username = "natefduncan"
plotly.tools.set_credentials_file(username=username, api_key=api_key)

mapbox_access_token = "pk.eyJ1IjoibmF0ZWR1bmNhbiIsImEiOiJjam01Z3kzMGMxcm1uM2trOGM1c2x6ZnVsIn0.frI_rzsE819mtoRhxt4m8w"

#Get data.
data = pd.read_csv("data.csv")

scl = "Picnic"

desc = []
data.columns
for i,j,k,l,m,n,o,p,q,r,s in zip(data.url, data.price, data.beds, data.baths, 
                         data.half_baths, data.sq_ft, data.acres_lot,
                         data.on_realtor, data.built, data.preds, data.expected_diff):
    desc.append(
            '''
            Url: %s
            Price: %s
            Beds: %s
            Full Bath: %s
            Half Bath: %s
            Square Feet: %s
            Acres: %s
            On the Market: %s
            Built: %s
            Predicted Price: %s
            Difference w/ Actual: %s
            ''' % (str(i), str(j),str(k),str(l),
            str(m),str(n),str(o),str(p),str(q),str(r),str(s))
            )

data['desc'] = desc
data_good = data[(data.expected_diff < 0) & (data.price < 250000) & (data.type == 'Single Family Home')]
data_bad = data[(data.expected_diff > 0) & (data.price < 250000) & (data.type == 'Single Family Home')]
from scipy.stats import percentileofscore

data = [
    go.Scattermapbox(
        lat=data_good.lat.tolist(),
        lon=data_good.lon.tolist(),
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=[percentileofscore(data_good.expected_diff.tolist(), i)*10/100 + 5 for i in data_good.expected_diff.tolist()],
            color='green',
            opacity=.5
        ),
        text=data_good.desc.tolist()
    ),
    go.Scattermapbox(
        lat=data_bad.lat.tolist(),
        lon=data_bad.lon.tolist(),
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=[percentileofscore(data_bad.expected_diff.tolist(), i)*10/100 + 5 for i in data_bad.expected_diff.tolist()],
            color='red',
            opacity=.5
        ),
        text=data_bad.desc.tolist()
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
