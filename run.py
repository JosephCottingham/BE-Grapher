from operator import truediv
import os

import PySimpleGUI as sg

from Data_Grapher import graph_data, remove_all
import threading

color_map = {
    0:{
        0:'#FF0000',
        1:'#f48e03',
        2:'#ede903'
    },
    1:{
        0:'#4100fc',
        1:'#008000',
        2:'#800080'
    },
    2:{
        0:'#ff8de5',
        1:'#00fca8',
        2:'#000000'
    },
}

layout = [
        [
            [sg.Text("Choose a source file Data 1: "), sg.Input(), sg.FileBrowse()],
            [sg.Text("Choose a source file Data 2: "), sg.Input(), sg.FileBrowse()],
            [sg.Text("Choose a source file Data 3: "), sg.Input(), sg.FileBrowse()],
        ],
        # [sg.Text('Start Row', size =(15, 1)), sg.InputText()],
        # [sg.Text('End Row', size =(15, 1)), sg.InputText()],
        [
            [sg.Text('Resolution', size =(15, 3)), sg.InputText()],
            [sg.Text('Moving AVG window', size =(15, 3)), sg.InputText()],
        ],
        [
            [sg.Text('Data 1 X:', background_color=color_map[0][0]), sg.Checkbox('', default=True)],
            [sg.Text('Data 1 Y:', background_color=color_map[0][1]), sg.Checkbox('', default=True)],
            [sg.Text('Data 1 Z:', background_color=color_map[0][2]), sg.Checkbox('', default=True)],
            [sg.Text('Data 2 X:', background_color=color_map[1][0]), sg.Checkbox('', default=True)],
            [sg.Text('Data 2 Y:', background_color=color_map[1][1]),sg.Checkbox('', default=True)],
            [sg.Text('Data 2 Z:', background_color=color_map[1][2]),sg.Checkbox('', default=True)],
            [sg.Text('Data 3 X:', background_color=color_map[2][0]), sg.Checkbox('', default=True)],
            [sg.Text('Data 3 Y:', background_color=color_map[2][1]), sg.Checkbox('', default=True)],
            [sg.Text('Data 3 Z:', background_color=color_map[2][2]), sg.Checkbox('', default=True)]
        ],
        [sg.Text('SPS Overide (2000 SPS): '), sg.Checkbox('', default=True)],
        [sg.Text('Enable Point Annotation '), sg.Checkbox('', default=True)],
        # [sg.Listbox(values=['Welcome Drink', 'Extra Cushions', 'Organic Diet','Blanket', 'Neck Rest'], select_mode='extended', key='fac', size=(30, 6))],
        [sg.Text('No Error', key='-ERROR-')],
        [sg.Button("Create Graph")],
        [sg.Button("Update Graph")],
    ]

# Create the window
window = sg.Window("Data Grapher", layout)
windows = []
w = None
# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window or
    # presses the OK button
    if event == sg.WIN_CLOSED:
        break
    if event == "Create Graph" or event == "Update Graph":
        src_files = []
        src_files.append(values[0])
        src_files.append(values[1])
        src_files.append(values[2])
        
        resolution = int(values[3])
        moving_avg_window = int(values[4])
        axis_index = 0
        data_index = 0
        axis_map = {
            0:{},
            1:{},
            2:{}
        }
        for i in range(5, 14):
            axis_map[data_index][axis_index] = bool(values[i])

            if axis_index == 2:
                data_index += 1
                axis_index = 0
            else:
                axis_index += 1
        sps_overide = bool(values[14])
        point_annoations = bool(values[15])

        # th = threading.Thread(target=graph_data,  args=(src_file, resolution, moving_avg_window))
        # th.start()
        if (event == "Create Graph"):
            plot_id = graph_data(src_files, resolution, moving_avg_window, color_map, axis_map, sps_overide=sps_overide, point_annoations=point_annoations)
            remove_all([plot_id, ])
        if (event == "Update Graph"):
            plot_id = graph_data(src_files, resolution, moving_avg_window, color_map, axis_map, update=True, plot_id=plot_id, sps_overide=sps_overide, point_annoations=point_annoations)