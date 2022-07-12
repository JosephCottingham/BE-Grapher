import pandas as pd
import numpy as np
import csv, random
import matplotlib.pyplot as plt

Bitcount_High = 65535
G = 9.8

plot_ids = []
source_data = {}

def process_bitcount(data):
    if data > 32768:
        return data-65535
    return data

def remove_all(save=[]):
    for plot_id in plot_ids:
        if plot_id not in save:
            plt.figure(plot_id)
            plt.close()
    
def graph_data(src_paths, resolution, moving_avg_window, color_map, axis_map, update=False, plot_id=0, sps_overide=False):

    # title_base = src_path.split('/')[-1].split('\\')[-1]
    if update == False:
        while plot_id in plot_ids:
            plot_id = random.randint(0,4000)
        plot_ids.append(plot_id)

    graph_data = {}
    for index, src_path in enumerate(src_paths):
        if src_path != '':
            df, csvp = get_graph_data(src_path, sps_overide=sps_overide)
            df, csvp = proccess_graph_data(df, csvp, resolution, moving_avg_window)
        else:
            df = None
            csvp = None
            
        graph_data[index] = {
            'df':df,
            'csvp':csvp
        }

    title = f'res: {resolution} MVA: {moving_avg_window}'
    
    update_graph(plot_id, graph_data, resolution, title, color_map, axis_map, clear=update)
    
    return plot_id

def update_graph(plot_id, graph_data, resolution, title, color_map, axis_map, clear=False):
    if clear:
        plt.figure(plot_id).clear()
    plt.figure(plot_id)
    for test_index, key in enumerate(graph_data.keys()):
        df = graph_data[key]['df']

        if not isinstance(df, pd.DataFrame):
            continue

        time = list(df[::resolution].iloc[:,3])
        for axis_index in range(3):
            color = color_map[test_index][axis_index]
            if axis_map[test_index][axis_index] == True:
                x = list(df[::resolution].iloc[:,axis_index])
                plt.plot(time, x, color=color)

        plt.title(title)
        plt.xlabel("Time (sec)")
        plt.ylabel("Acceleration (m/sec)")
        plt.grid()
        # fig = plt.figure(0)
        # fig.canvas.set_window_title('Window 3D')

        plt.show(block=False)
    return plot_id

def get_graph_data(src_path, sps_overide):
    csvp = read_csvp(src_path.replace('csv', 'csvp'), sps_overide=sps_overide)
    df = pd.read_csv(src_path, header=None, delimiter=',', low_memory=False,engine = 'c')
    
    return df, csvp

def proccess_graph_data(df, csvp, resolution, moving_avg_window):
    df = df.iloc[:, [0,1,2]]

    df.loc[:,0] = df.iloc[:,0].apply(process_bitcount).rolling(moving_avg_window).mean()
    df.loc[:,1] = df.iloc[:,1].apply(process_bitcount).rolling(moving_avg_window).mean()
    df.loc[:,2] = df.iloc[:,2].apply(process_bitcount).rolling(moving_avg_window).mean()

    df = ((df/Bitcount_High)*csvp['ACCEL_SENSITIVITY']*G)

    index_series = df.index.to_series()
    index_series = index_series / csvp['ACCEL_SPS']
    df['time'] = index_series

    return df, csvp

def read_csvp(src_path, sps_overide=False):
    data = {}
    key_map = {
        7:'ACCEL_SPS',
        8:'MAG_SPS',
        9:'ACCEL_SENSITIVITY',
    }
    with open(src_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        index = 0
        for row in reader:
            if key_map.get(index) != None:
                data[key_map.get(index)]=int(row[0])
            index += 1
    if sps_overide:
        data['ACCEL_SPS'] = 2000
    return data