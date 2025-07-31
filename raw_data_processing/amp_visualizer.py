import h5py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


raw_data = 0

with h5py.File('./grace-7302025/raw data/grace-rawData-7302025-0.h5', 'r') as file:
    print("Keys in file: ", list(file.keys()))
    file_path = 'sessions/session_0/group_0/entry_0/result/frame'
    raw = file[file_path]
    print("Raw data:", raw)

    raw_data = np.array(raw)  

# print(raw_data.shape)
frames = raw_data.shape[0]
sweeps = raw_data.shape[1]
bins = raw_data.shape[2]
x = np.array(range(bins))

amps = np.zeros((frames,sweeps,bins))
phases = np.zeros((frames,sweeps,bins))

for frame in range(frames):
    for sweep in range(sweeps):
        for bin in range(bins):
            I = raw_data[frame][sweep][bin][0]
            Q = raw_data[frame][sweep][bin][1]
            iq_pair = complex(I,Q)

            amps[frame][sweep][bin] = abs(iq_pair)
            phases[frame][sweep][bin] = np.angle(iq_pair)



fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.25)

line_1,line_2,line_3,line_4,line_5,line_6,line_7,line_8 = ax.plot(amps[0][0],'r', amps[0][1],'orange', amps[0][2],'yellow',amps[0][3],'green',amps[0][4],'blue',amps[0][5],'indigo',
                        amps[0][6],'violet',amps[0][7],'orangered')

# line_1,line_2,line_3,line_4,line_5,line_6,line_7,line_8,line_9,line_10,line_11,line_12,line_13,line_14,line_15,line_16 = ax.plot(amps[0][0],'r', amps[0][1],'orange', amps[0][2],'yellow',amps[0][3],'green',amps[0][4],'blue',amps[0][5],'indigo',
#                         amps[0][6],'violet',amps[0][7],'orangered',amps[0][8],'peru',amps[0][9], 'olive', amps[0][10],
#                         'lawngreen',amps[0][11],'teal',amps[0][12],'deeppink',amps[0][13], 'lightpink', amps[0][14], 'palegreen', amps[0][15], 'deepskyblue')

slider_ax = plt.axes([0.1, 0.1, 0.8, 0.03], facecolor='lightgoldenrodyellow')
slider = Slider(slider_ax, 'frame', valmin=0, valmax=frames-1, valinit=0, valstep=1)

def update(frame):
    line_1.set_ydata(amps[frame][0])
    line_2.set_ydata(amps[frame][1])
    line_3.set_ydata(amps[frame][2])
    line_4.set_ydata(amps[frame][3])
    line_5.set_ydata(amps[frame][4])
    line_6.set_ydata(amps[frame][5])
    line_7.set_ydata(amps[frame][6])
    line_8.set_ydata(amps[frame][7])
    # line_9.set_ydata(amps[frame][8])
    # line_10.set_ydata(amps[frame][9])
    # line_11.set_ydata(amps[frame][10])
    # line_12.set_ydata(amps[frame][11])
    # line_13.set_ydata(amps[frame][12])
    # line_14.set_ydata(amps[frame][13])
    # line_15.set_ydata(amps[frame][14])
    # line_16.set_ydata(amps[frame][15])

    ax.relim()
    ax.autoscale_view()
    fig.canvas.draw_idle()

slider.on_changed(update)



plt.show()
