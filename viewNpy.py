import numpy as np

data = np.load('breathingData-h15-d0.6-side.npy')
np.savetxt('sensorData-h15-d0.6-side.csv', data, delimiter=',')
print(data)