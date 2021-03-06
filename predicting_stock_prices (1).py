# -*- coding: utf-8 -*-
"""Predicting stock prices.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16bL6eUa2eDCFA_MaCfHduVtSCbHfI9Bc
"""

# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import plotly.express as px
from copy import copy
from scipy import stats
import matplotlib.pyplot as plt
import numpy as np
import plotly.figure_factory as ff
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from tensorflow import keras

# Read stock prices data
stocks_df = pd.read_csv('/content/drive/MyDrive/udemy - Python+Finance/udemy-FinanceAutomation/Part 3. AI and ML in Finance/stock.csv')

# Read the stocks volume data
stocksVolume_df = pd.read_csv('/content/drive/MyDrive/udemy - Python+Finance/udemy-FinanceAutomation/Part 3. AI and ML in Finance/stock_volume.csv')

# Sort the data based on Date
stocks_df = stocks_df.sort_values(by=['Date'])

# Sort the volume data based on Date
stocksVolume_df = stocksVolume_df.sort_values(by=['Date'])

stocksVolume_df.describe()

stocks_df.describe()

# Function to normalize stock prices based on their initial price
def normaliseIt(df):
  x = df.copy()

  for i in df.columns[1:]:
    x[i] = x[i]/x[i][0]

  return x

# Function to plot interactive plots using Plotly Express

def interactivePlot(df, title):
  fig = px.line(title = title)

  for stock in df.columns[1:]:
    fig.add_scatter(x=df['Date'], y=df[stock], name=stock)
  fig.show()

# plot interactive chart for stocks data
interactivePlot(stocks_df, 'Stock prices')

interactivePlot(stocksVolume_df, 'Volume of stocks')

# Function to concatenate the date, stock price, and volume in one dataframe

def individual_stock(price_df, volume_df, stock):
  return (pd.DataFrame({'Date': price_df['Date'], 'Price':price_df[stock], 'Volume':volume_df[stock]}))

def updatedTrading_window(df, days):
  
  n = days
  df['Target'] = df['Price'].shift(-n)
  return df



price_volume_df = individual_stock(stocks_df, stocksVolume_df, 'sp500')

# Let's test the functions and get individual stock prices and volumes for AAPL
price_volume_target_df = updatedTrading_window(price_volume_df, 5)

price_volume_target_df = price_volume_target_df[:-5] 
print(price_volume_target_df)







def updatedScaler(df):
  from sklearn.preprocessing import MinMaxScaler
  sc = MinMaxScaler(feature_range=(0,1))
  return [sc.fit_transform(df.drop(columns=['Date'])), sc]

price_volume_target_scaled_df = updatedScaler(price_volume_target_df)
price_volume_target_scaled_df

#Testing the inverse transform and it is working well 
price_volume_target_scaled_df[1].inverse_transform(price_volume_target_scaled_df[0])

# Create Feature and Target
X = price_volume_target_scaled_df[0][:, :2]
X.shape

y = price_volume_target_scaled_df[0][:, 2:]
y.shape

split = int(0.65*len(price_volume_target_scaled_df[0]))
print(split)

X_train = X[:split]
X_test = X[split:]

X_train

X_test

y_train = y[:split]
y_test = y[split:]

y_train.shape

y_test.shape

# Define a data plotting function
def dataPlot(data, title):
  plt.figure(figsize=(15,7))
  plt.plot(data, linewidth=3)
  plt.title(title)
  plt.grid()
  plt.show()


#This is what we used in the past
# def plot(df, plotName):
#   df.plot(x='Date', figsize=(15,7), linewidth=3, title=plotName)
#   plt.grid()
#   plt.show()

dataPlot(X_train, 'Testing Data')
dataPlot(X_test, 'Test Data')



def updatedPipeline(price_df, volume_df, stock, days):
  stock_individual_df = individual_stock(price_df, volume_df, stock)
  #print(stock_individual_df.shape)
  
  stock_trading_df = updatedTrading_window(stock_individual_df, days)[:-days]
  #print('In hte updatedPipeline')
  #print(stock_trading_df)

  
  #print(trading_window(stock_individual_df).shape)
  #print(trading_window(stock_individual_df)[:-1].shape)
  stock_trading_scaled_df_new = updatedScaler(stock_trading_df) 
  stock_trading_scaled_df = stock_trading_scaled_df_new[0]
  X = stock_trading_scaled_df[:, :2]
  y = stock_trading_scaled_df[:, 2:]
  scale = int(0.7*len(stock_trading_scaled_df))
  X_train = X[:scale]
  X_test = X[scale:]
  y_train = y[:scale]
  y_test = y[scale:]
  return [X_train, X_test, y_train, y_test, X, y, stock_trading_scaled_df_new[0], stock_trading_scaled_df_new[1]]

















#Ridge rigression model

from sklearn.linear_model import Ridge
# Note that Ridge regression performs linear least squares with L2 regularization.
# Create and train the Ridge Linear Regression  Model

regression_model = Ridge() 
regression_model.fit(X_train, y_train)

y_train

# Test the model and calculate its accuracy 
lr_accuracy = regression_model.score(X_test, y_test)
print("Accuracy on the testing data: {}".format(lr_accuracy))

# Make Prediction
predicted_stock_prices = regression_model.predict(X)
predicted_stock_prices

# Append the predicted values into a list
predicted_prices = []

for i in predicted_stock_prices:
  predicted_prices.append(i[0])
#predicted_prices

len(predicted_prices)

atcual_prices = []
for i in price_volume_target_scaled_df[0]:
  atcual_prices.append(i[0])
#atcual_prices

# Create a dataframe based on the dates in the individual stock data
predictions_df = price_volume_target_df[['Date']]
predictions_df

predictions_df['Atcual'] = atcual_prices
predictions_df

# Add the predicted values to the dataframe
predictions_df['Predicted'] = predicted_prices
predictions_df

# Plot the results
interactivePlot(predictions_df, 'Predicted vs atcual stock prices')

def updatedRRModelStandAlone(stock, alpha, days):
  from sklearn.linear_model import Ridge

  data = updatedPipeline(stocks_df, stocksVolume_df, stock, days)
  X_train = data[0]
  y_train = data[2]
  X_test = data[1]
  y_test = data[3]
  X = data[4]
  y = data[5]
  price_volume_target_scaled_df = data[6]
  scalar_variable = data[7]

  regression_model = Ridge(alpha=alpha)
  regression_model.fit(X_train, y_train)

  lr_accuracy = regression_model.score(X_test, y_test)
  print("Linear Regression Score: ", lr_accuracy) 

  #X = np.concatenate((X_train, X_test)) #

  print(X_train.shape) # 
  print(X_test.shape)  #
  print(np.concatenate((X_train,X_test)).shape) #
  print(np.concatenate((y_train,y_test))==price_volume_target_scaled_df[:, 2:])
  predicted_prices = regression_model.predict(X)


  #predicted_prices = scaler_variable.inverse_transform(predicted_prices) ##
  

  #price_volume = individual_stock(stocks_df, stocksVolume_df, stock) #
  #price_volume_target = updatedTrading_window(price_volume, days)[:-days] #
    #price_volume_target = trading_window(price_volume)[:-1] #
  #price_volume_target_scaled_df = updatedScaler(price_volume_target) #
  #print(scalar_variable.inverse_transform(price_volume_target_scaled_df))
  #price_volume_target_scaled_df = scalar_variable.inverse_transform(price_volume_target_scaled_df)
  price_volume_target_scaled_df_inverse = scalar_variable.inverse_transform(price_volume_target_scaled_df)
  print(price_volume_target_scaled_df_inverse)
  print()



  #This part is for replacing the target column of numpy array 'price_volume_target_scaled_df' by prediction
  dummy = price_volume_target_scaled_df
  
  Predicted = []
  for i in predicted_prices:
    Predicted.append(i[0])
  
  dummy[:, 2] = Predicted
  dummy = scalar_variable.inverse_transform(dummy)
  print(dummy)
  print()

  
  #Dummy is a numpy array, prices, volume and predicted prices are the three columns
  #End of the part above, now the dummy has the prices scaled up 



  predicted_price_original = []
  close_price_original = []
  close_price_shifted_by_nDays = []

  for i in dummy:
    close_price_original.append(i[0])
    predicted_price_original.append(i[2])
  for i in price_volume_target_scaled_df_inverse:
    close_price_shifted_by_nDays.append(i[2])
  print(close_price_original)
  print()
  print(predicted_price_original)
  print()
  print(close_price_shifted_by_nDays)
  
  
  
  price_volume = individual_stock(stocks_df, stocksVolume_df, stock)
  df_predicted = price_volume[['Date']][:-days]
  df_predicted['Close'] = close_price_original
  #df_predicted['Close_Shifted'] = close_price_shifted_by_nDays
   #uncmment this if you want the shifted data as well in the df_predicted
  df_predicted['Prediction'] = predicted_price_original

  #This lines can create the graph in a shifted form 
  #df_predicted = price_volume[['Date']][:-2*days]
  #df_predicted['Close_Shifted'] = close_price_shifted_by_nDays[:-days]
  #df_predicted['Close'] = close_price_original[:days]
  #df_predicted['Prediction'] = predicted_price_original[days:]
  
  sum = 0 
  sum+=np.square(np.array(predicted_price_original)-np.array(close_price_shifted_by_nDays))
  print('MSE between predicted price and the closeShifted prices: {}'.format(np.sum(sum))) 

  sum = 0 
  sum+=np.square(np.array(predicted_price_original)-np.array(close_price_original))
  print('MSE between predicted price and the closing price of a particular day prices: {}'.format(np.sum(sum))) 

  interactivePlot(df_predicted, "Original Vs. Prediction for {} using Ridge Regression".format(stock))

  print(df_predicted)
  return 








  print('Check@1')
  
  #len_stocks = len(Predicted)d#===
  #Predicted = np.array(Predicted)d#===
  #Predicted = np.reshape(Predicted, (Predicted.shape[0], 1))d#===

  close = []
  for i in price_volume_target_scaled_df:
    close.append(i[0])
  #close = np.array(close)d#===
  #close = np.reshape(close, (close.shape[0], 1))d#===
  
  #b = np.zeros((len_stocks,3))#===
  #b[:,:1] = close#===
  #b[:, [1]] = Predicted#===

  #Predicted = scalar_varabile.inverse_transform(Predicted)
  print('#1')


  b = scalar_variable.inverse_transform(b)#===

  df_predicted = price_volume[['Date']][:-days]
  #df_predicted['Close'] = close ===**
  #df_predicted['Prediction'] = Predicted ===**
  df_predicted['Close'] = b[:, 0]#===
  df_predicted['Prediction'] = b[:, 1]#===
  #print(scalar_variable.inverse_transform(df_predicted.drop(columns=['Date'])))
  print(df_predicted.drop(columns=['Date']))
  
  
  interactivePlot(df_predicted, "Original Vs. Prediction for {}".format(stock))

#personalData1 = pipeline(stocks_df, stocksVolume_df, 'TSLA')
updatedRRModelStandAlone('sp500', 0.0001, 7)

interactivePlot(stocks_df[['Date', 'sp500']], 'Stock prices')



















#THIS IS THE LSTM MODEL IMPLIMENTATION

def updatedLSTMPRedictionPipeline(stock, units, days):
  #stock_pipeline = pipeline(stocks_df, stocksVolume_df, stock)
  data = updatedPipeline(stocks_df, stocksVolume_df, 'sp500', days)
  
  
  
  
  


  X_train = data[0][:, 0] #provides the prices data of the stock for the training set
  X_train = np.reshape(X_train, (len(X_train), 1))
  X_test = data[1][:, 0] #provides the prices data of the stock for the test set
  X_test = np.reshape(X_test, (len(X_test), 1))
  y_train = data[2]
  y_test = data[3]
  X = data[4]
  y = data[5]
  price_volume_target_scaled_df = data[6]
  scalar_variable = data[7]

  X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
  X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
  print(X_train.shape, X_test.shape)


  #PLAYGROUND


  
  # price_volume_target_scaled_df = scaler(trading_window(individual_stock(stocks_df, stocksVolume_df, stock)))[:-1]
  # print(X)
  # print('\n\n\n')
  # print(X_train)
  # print('\n\n\n')
  # print(X_test)



  #price_volume_target_scaled_df = scaler(trading_window(individual_stock(stocks_df, stocksVolume_df, stock))[:-1])
  #price_volume_target_scaled_df = np.reshape(price_volume_target_scaled_df[0], (price_volume_target_scaled_df[0].shape[0],1,1))


  #//X = np.append(X_train, X_test)
  #//X = np.reshape(X, (X.shape[0],1,1))
  # //r1 = individual_stock(stocks_df, stocksVolume_df, stock)
  # //r2 = trading_window(r1)[:-1]
  # //r3 = scaler(r2)
  # price_volume_target_scaled_df = r3
  #//print(stock_pipeline[-2][:, :1].shape)
  #//zr = np.reshape(stock_pipeline[-2][:, :1], (stock_pipeline[-2][:, :1].shape[0],1,1))
  #//print(X==zr)
  #//print(X)
  #//print('\n\n\n')
  #//print(price_volume_target_scaled_df[:, :1])
  #//return 




  #After this much problems, I think 
    # //r1 = individual_stock(stocks_df, stocksVolume_df, stock)
    # //r2 = trading_window(r1)[:-1]
    # //r3 = scaler(r2)
  #was the solution we needed, method works like charm not and do not use the code cells above this function for LSTM 






  # Create the model
  inputs = keras.layers.Input(shape=(X_train.shape[1], X_train.shape[2]))

  x = keras.layers.LSTM(units=units, return_sequences=True)(inputs)
  x = keras.layers.LSTM(units=units, return_sequences=True)(x) #We are creating a hidden layer over here
  x = keras.layers.LSTM(units=units, return_sequences=True)(x)

  outputs = keras.layers.Dense(1, activation='linear')(x)

  model = keras.Model(inputs=inputs, outputs=outputs)
  model.compile(optimizer='adam', loss='mse')
  model.summary()




  # Train the model
  print('\n\nTraining the model')
  history = model.fit(X_train, y_train, batch_size=32, epochs=20, validation_split=0.2)

  #Recreating the input set from training and test data
  X = np.reshape(X[:, 0], (X[:, 0].shape[0], 1, 1))
      #X = np.append(X_train, X_test)
      #X = np.reshape(X, (X.shape[0],1,1))
  #print(X_train.shape, X_test.shape)





  # Make prediction
  predicted_prices = model.predict(X)


  #This part for inversing the original dataFrame
  price_volume_target_scaled_df_inverse = scalar_variable.inverse_transform(price_volume_target_scaled_df)
  print(price_volume_target_scaled_df_inverse)
  print()




  #This part is for replacing the target column of numpy array 'price_volume_target_scaled_df' by prediction
  dummy = price_volume_target_scaled_df
  
  Predicted = []
  for i in predicted_prices:
    Predicted.append(i[0][0])
  
  dummy[:, 2] = Predicted
  dummy = scalar_variable.inverse_transform(dummy)
  print(dummy)
  print()

  
  #Dummy is a numpy array, prices, volume and predicted prices are the three columns
  #End of the part above, now the dummy has the prices scaled up 



  predicted_price_original = []
  close_price_original = []
  close_price_shifted_by_nDays = []

  for i in dummy:
    close_price_original.append(i[0])
    predicted_price_original.append(i[2])
  for i in price_volume_target_scaled_df_inverse:
    close_price_shifted_by_nDays.append(i[2])

  print(close_price_original)
  print()
  print(predicted_price_original)
  print()
  print(close_price_shifted_by_nDays)
  
  
  price_volume = individual_stock(stocks_df, stocksVolume_df, stock)
  df_predicted = price_volume[['Date']][:-days]
  df_predicted['Close'] = close_price_original
  #df_predicted['Close_Shifted'] = close_price_shifted_by_nDays
   #uncmment this if you want the shifted data as well in the df_predicted
  df_predicted['Prediction'] = predicted_price_original

  #This lines can create the graph in a shifted form 
  #df_predicted = price_volume[['Date']][:-2*days]
  #df_predicted['Close_Shifted'] = close_price_shifted_by_nDays[:-days]
  #df_predicted['Close'] = close_price_original[:days]
  #df_predicted['Prediction'] = predicted_price_original[days:]
  
  sum = 0 
  sum+=np.square(np.array(predicted_price_original)-np.array(close_price_shifted_by_nDays))
  print('MSE between predicted price and the closeShifted prices: {}'.format(np.sum(sum))) 

  sum = 0 
  sum+=np.square(np.array(predicted_price_original)-np.array(close_price_original))
  print('MSE between predicted price and the closing price of a particular day prices: {}'.format(np.sum(sum))) 

  interactivePlot(df_predicted, "Original Vs. Prediction for {} using Ridge Regression".format(stock))

  print(df_predicted)
  return 
















  #print("\n\n\n1")
  #Creating the predictions dataFrame 
  test_predicted = []
  for i in predicted_prices:
    test_predicted.append(i[0][0])
  #print("\n\n\n2\n", len(test_predicted))

  predictions_df = individual_stock(stocks_df, stocksVolume_df, stock)[:-1][['Date']]
  #print(predictions_df)
  predictions_df['Prediction'] = test_predicted
  #print("\n\n\n1")
  



  price_volume = individual_stock(stocks_df, stocksVolume_df, stock)
  price_volume_target = trading_window(price_volume)[:-1]
  price_volume_target_scaled_df = scaler(price_volume_target)


  #print(X==price_volume_target_scaled_df[0])

  close = []
  for i in price_volume_target_scaled_df:
    close.append(i[0])  
  #print("\n\n\n1")
  predictions_df['Price'] = close
  

  predictions_df
  interactivePlot(predictions_df, 'Predictions using LSTM for {}'.format(stock))

updatedLSTMPRedictionPipeline('sp500', 500, 1)







