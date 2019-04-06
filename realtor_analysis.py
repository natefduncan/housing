import pandas as pd
from sklearn.linear_model import LinearRegression
from pathlib import Path
import os
import numpy as np

os.getcwd()

os.chdir(Path("/Users/User/Desktop/housing/housing/spiders"))

data = pd.read_csv("realtor_data_2019.3.31.csv")
y = data.price

columns = ["city", "state", "zip", "beds", "baths", "half_baths", "sq_ft", "sqft_lot", "acres_lot", 
           "status", "price_sq_ft", "on_realtor", "type", "built", "style"]

X =  data[columns]

#Encode city, state, zip, type, style
from sklearn.preprocessing import OneHotEncoder

labelencoder = LabelEncoder()

X['city'] = labelencoder.fit_transform(X['city'].astype(str))
X['state'] = labelencoder.fit_transform(X['state'].astype(str))
X['zip'] = labelencoder.fit_transform(X['zip'].astype(str))
X['status'] = labelencoder.fit_transform(X['status'].astype(str))
X['type'] = labelencoder.fit_transform(X['type'].astype(str))
X['style'] = labelencoder.fit_transform(X['style'].astype(str))

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

X = X.replace("", np.nan)
X.loc[:, ["price_sq_ft"]] = [float(get_ints(i)) for i in X.price_sq_ft.tolist()]
X.loc[:, ["on_realtor"]] = [float(get_ints(i)) for i in X.on_realtor.tolist()]

from sklearn.cross_validation import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)

from sklearn.preprocessing import StandardScaler
sc_X = StandardScaler()
X_train = sc_X.fit_transform(X_train)
X_test = sc_X.transform(X_test)
sc_y = StandardScaler()
y_train = sc_y.fit_transform(y_train)

