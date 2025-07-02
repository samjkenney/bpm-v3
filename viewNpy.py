import numpy as np

data = np.load('breathingData.npy')
np.savetxt('outputData.csv', data, delimiter=',')
print(data)