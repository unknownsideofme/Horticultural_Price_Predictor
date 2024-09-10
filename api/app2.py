import numpy as np 
from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
app = FastAPI()  
import pickle 


with open('proj1/rice.pkl' , 'rb') as f :
    model = pickle.load(f)
    
df = pd.read_csv('rice.csv')
df1 = df.drop(columns=['Date'])
scaler=MinMaxScaler(feature_range=(0,1))
df1=scaler.fit_transform(np.array(df1).reshape(-1,1))


def prediction(days, dataset =df1   ):
    arr = np.array(dataset[-120:])
    output = []
    for i in range(days):
        forecast = model.predict(arr.reshape(-1, 1))  # ensure shape is (120, 1)
        forecast = scaler.inverse_transform(forecast)[0][0]  # extract the single value
        arr = np.roll(arr, -1)  # shift the array to make room for the new value
        arr[-1] = forecast  # add the new value to the end of the array
        output.append(forecast)
    return output


@app.post('/forecasting')

def forecasting(datas: int):
    pred = prediction(datas, df1)
    return [float(x) for x in pred]