import pandas as pd
from pathlib import Path
import os
import numpy as np

os.getcwd()

os.chdir(Path("/Users/User/Desktop/housing/housing/spiders"))

data = pd.read_csv("realtor_data_2019.3.31.csv")

def get_ints(x): #Gets only the numbers from a string. 
    x = str(str(x).split(".")[0])
    output = []
    for p in x:
        try:
            float(p)
            output.append(p)
        except:
            pass
    return "".join(output)

data = data.replace("No Info", np.nan)
data['on_realtor'] = [get_ints(i) for i in data['on_realtor'].tolist()]
urls = data.url.tolist()
house_type = data.type.tolist()

data[['on_realtor']] = data[['on_realtor']].apply(pd.to_numeric, args=('coerce',))
        
#Sq ft to acres
acre_conversion = 43560 

acre_lot = []

for i,j in zip(data.sqft_lot.tolist(), data.acres_lot.tolist()):
    if ~np.isnan(i):
        acre_lot.append(float(i)/acre_conversion)
    else:
        acre_lot.append(j)

data['acres_lot'] = acre_lot

data = data.drop(['sqft_lot', 'price_sq_ft'], axis=1)

#Encode city, state, zip, type, style
from sklearn.preprocessing import LabelEncoder

labelencoder = LabelEncoder()

city_en =LabelEncoder()
state_en =LabelEncoder()
zip_en = LabelEncoder()
status_en =LabelEncoder()
type_en =LabelEncoder()
style_en =LabelEncoder()

data['city'] = city_en.fit_transform(data['city'].astype(str))
data['state'] = state_en.fit_transform(data['state'].astype(str))
data['zip'] = zip_en.fit_transform(data['zip'].astype(str))
data['status'] = status_en.fit_transform(data['status'].astype(str))
data['type'] = type_en.fit_transform(data['type'].astype(str))
data['style'] = style_en.fit_transform(data['style'].astype(str))

keep_cols = ['lat', 'lon', 'url', 'city', 'state', 'zip', 'status', 'type', 'style','price', "beds", "baths", "half_baths", "sq_ft", "acres_lot",  "on_realtor", "built"]

data=data[keep_cols]
data.url = urls

#half baths
where_nan = [np.isnan(i) for i in data.half_baths.tolist()]
data['half_baths'][where_nan] = 0 

data = data.dropna()

y = data.price

columns = ['city', 'state', 'zip', 'status', 'type', 'style', "beds", "baths", "half_baths", "sq_ft", "acres_lot",  "on_realtor", "built"]

X =  data[columns]

from sklearn.cross_validation import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
# Fit only to the training data
scaler.fit(X_train)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)
X[columns] = scaler.transform(X[columns])

from sklearn.neural_network import MLPRegressor

mlp = MLPRegressor(hidden_layer_sizes=(30,30,30))

mlp.fit(X_train,y_train)

predictions = mlp.predict(X_test)
mlp.score(X_test, y_test)
mlp.get_params()

from sklearn.metrics import r2_score, explained_variance_score
print(r2_score(y_test,predictions))
print(explained_variance_score(y_test, predictions))

import seaborn as sns

sns.lmplot("x", "y", data=pd.DataFrame({"x":y_test, "y" : predictions}))


preds = mlp.predict(X)

data['preds'] = preds

data['expected_diff'] = [i-j for i,j in zip(data.price.tolist(), data.preds.tolist())]

sns.distplot(data['expected_diff'])

data['city'] = list(city_en.inverse_transform(data['city']))
data['state'] = state_en.inverse_transform(data['state'])
data['zip'] = zip_en.inverse_transform(data['zip'])
data['status'] = status_en.inverse_transform(data['status'])
data['type'] = type_en.inverse_transform(data['type'])
data['style'] = style_en.inverse_transform(data['style'])

data.to_csv("../../data.csv")

