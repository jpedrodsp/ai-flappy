# Step 1: Import necessary libraries
import numpy as np
from keras.layers import Dense
from keras.models import Sequential

# Step 2: Define the dataset
# For simplicity, let's use numpy to create a dataset
# Here we create a simple dataset where the output is the sum of the inputs
X = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
Y = np.array([[3], [5], [7], [9]])

# Step 3: Create the model
model = Sequential()
model.add(Dense(2, input_dim=2, activation="relu"))
model.add(Dense(1, activation="linear"))

# Step 4: Compile the model
model.compile(loss="mean_squared_error", optimizer="adam")

# Step 5: Fit the model to the data
model.fit(X, Y, epochs=1000, verbose=0)

# Step 6: Evaluate the model
print(model.predict(X))
