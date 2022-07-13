import pandas as pd
import numpy as np
import csv, random
import matplotlib.pyplot as plt
import mplcursors

Bitcount_High = 65535
G = 9.8

plot_ids = []
source_data = {}
lines = {

}

master_plot_id=0
master_annot=None

data_label = ['Data 1:', 'Data 2:', 'Data 3:']
axis_label = ['X', 'Y', 'Z']
raw_data_list = []
master_time = None
master_cursors = []
master_color_map={}
master_point_annoations = False

def get_label_str(data_index, axis_index):
    return data_label[data_index] + ' ' + axis_label[axis_index]

def process_bitcount(data):
    if data > 32768:
        return data-65535
    return data

def remove_all(save=[]):
    for plot_id in plot_ids:
        if plot_id not in save:
            plt.figure(plot_id)
            plt.close()
    
def graph_data(src_paths, resolution, moving_avg_window, color_map, axis_map, update=False, plot_id=0, sps_overide=False, point_annoations=False):
    global master_point_annoations
    master_point_annoations = point_annoations

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
    master_plot_id = plot_id
    

    
    lines[plot_id] = {}
    line_list = []
    global master_time
    global raw_data_list
    global master_color_map
    master_color_map = color_map
    for test_index, key in enumerate(graph_data.keys()):
        df = graph_data[key]['df']

        if not isinstance(df, pd.DataFrame):
            continue

        raw_data_list = []
    
        master_time = list(df[::resolution].iloc[:,3])

        for axis_index in range(3):
            color = color_map[test_index][axis_index]
            if axis_map[test_index][axis_index] == True:
                x = list(df[::resolution].iloc[:,axis_index])
                raw_data_list.append(x)
                line_list.append(plt.plot(master_time, x, color=color, label=get_label_str(test_index, axis_index)))

    plt.title(title)
    legend = plt.legend(loc="upper right")
    line_legends = legend.get_lines()
    for i in range(len(line_legends)):
        lines[plot_id][line_legends[i]] = line_list[i]
        line_legends[i].set_picker(True)
        line_legends[i].set_pickradius(10)

    plt.xlabel("Time (sec)")
    plt.ylabel("Acceleration (m/sec)")
    plt.grid()
    # fig = plt.figure(0)
    # fig.canvas.set_window_title('Window 3D')

    plt.connect('pick_event', on_legend_click)
    # plt.connect("motion_notify_event", data_hover)

    # global master_annot
    # master_annot = plt.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
    # master_annot.set_visible(False)
    
    def show_datapoints(sel, data_index, axis_index):
        global master_point_annoations
        if master_point_annoations == False:
            sel.annotation.remove()
            return

        text = sel.annotation.get_text().split(' ')
        print(type(sel.annotation))
        axis_map_letter = {
            'X':0,
            'Y':1,
            'Z':2
        }

        data_index, axis_index = int(text[1].replace(':', ''))-1, axis_map_letter[text[2][0]]
        print(f'{data_index } : {axis_index}')

        xi, yi = sel[0], sel[0]
        xi, yi = xi._xorig.tolist(), yi._yorig.tolist()
        sel.annotation.set_backgroundcolor(master_color_map[data_index][axis_index])
        sel.annotation.set_text('x: '+ str(xi[round(sel.index)]) +'\n'+ 'y: '+ str(yi[round(sel.index)])) 

    global master_cursors
    master_cursors = []
    data_index = 0
    axis_index = 0
    for l in line_list:
        master_cursors.append(mplcursors.cursor(l, hover=True).connect('add', lambda sel: show_datapoints(sel, data_index=data_index, axis_index=axis_index)))
        axis_index+=1
        if data_index == 2:
            data_index+=1
            axis_index = 0

    plt.show(block=False)
    return plot_id

def get_graph_data(src_path, sps_overide):
    csvp = read_csvp(src_path.replace('csv', 'csvp'), sps_overide=sps_overide)
    df = pd.read_csv(src_path, header=None, delimiter=',', low_memory=False,engine='c')
    
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

# MATPLOTLIB Callbacks
def on_legend_click(event):
    legend = event.artist
    isVisible = legend.get_visible()
    lines[master_plot_id][legend][0].set_visible(not isVisible)
    legend.set_visible(not isVisible)

    plt.figure(master_plot_id).canvas.draw()

# def update_annot(ind, legend):
#     pos = lines[master_plot_id][legend].get_offsets()[ind["ind"][0]]
#     master_annot.xy = pos
#     text = "{}, {}".format(" ".join(list(map(str,ind["ind"]))), 
#                            " ".join([names[n] for n in ind["ind"]]))
#     print(text)
#     master_annot.set_text(text)
#     master_annot.get_bbox_patch().set_facecolor(cmap(norm(c[ind["ind"][0]])))
#     master_annot.get_bbox_patch().set_alpha(0.4)

# def data_hover(event):
#     vis = master_annot.get_visible()
#     print(list(lines[master_plot_id])[0])
#     if event.inaxes == lines[master_plot_id][list(lines[master_plot_id])[0]]:
#         cont, ind = lines[master_plot_id][list(lines[master_plot_id])[0]].contains(event)
#         print(f'cont: {cont}')
#         print(f'cont: {ind}')
#         if cont:
#             update_annot(ind)
#             master_annot.set_visible(True)
#             fig.canvas.draw_idle()
#         else:
#             if vis:
#                 master_annot.set_visible(False)
#                 fig.canvas.draw_idle()