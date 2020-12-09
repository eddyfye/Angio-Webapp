import os
import pandas as pd
import numpy as np
from time import sleep

import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from jupyter_dash import JupyterDash
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from flask import Flask

#############################################################
## Define Working Directory
working_directory = '/home/tanwp/Documents/data_26-8-2020/LAO_straight' # working directory goes here

npz_directory = os.path.join(working_directory, 'npz')
old_csv_directory = os.path.join(working_directory, 'old-csv')
new_csv_directory = os.path.join(working_directory, 'new-csv')

#############################################################
## Build App
server = Flask(__name__)
app = JupyterDash(server=server)

#############################################################
## Defining color template
colors = {
    'background': '#ffffff',
    'text': '#0022ff'
}

#############################################################
## Defining Functions

##### Reading annotation file #####
def reading_csv_file(filename):
    path = os.path.join(old_csv_directory, str(filename))
    df = pd.read_csv(path, header=0)
    df.columns = ['Mean Intensity']
    df['Image No.'] = df.index
    df = df[['Image No.', 'Mean Intensity']]
    return df


##### Listing of npz files #####
def list_of_files(file_directory='', file_format=''):
    ## List the files in the upload directory.
    files = []
    for filename in os.listdir(file_directory):
        ## Isolate files with input file_format
        if filename.endswith(str(file_format)):
            path = os.path.join(file_directory, filename)
            ## if it is a file, add to list of files
            if os.path.isfile(path):
                files.append(filename)
    files.sort()
    return files


##### Create empty dataframe #####
def create_df(frame=1000):
    df = pd.DataFrame(columns=['Image No.', 'Annotation'],
                      index=[i for i in range(frame)],
                      dtype='int')

    df['Image No.'] = df.index
    df['Annotation'] = 1

    return df


##### Initate empty dataframe for annotation DataTable #####
df_annotation = create_df(1000)


## Generating File List

def update_file_list():
    npz_list = list_of_files(npz_directory, '.npz')
    csv_list = list_of_files(old_csv_directory, '.csv')
    new_csv_list = list_of_files(new_csv_directory, '.csv')
    #     print(new_csv_list)
    return npz_list, csv_list, new_csv_list


npz_list, csv_list, new_csv_list = update_file_list()


##### Compiled File List #####
def compiled_files_list(frame=1000):
    ## Updating of file lists
    npz_list, csv_list, new_csv_list = update_file_list()

    df = pd.DataFrame(columns=['Index', 'NPZ File', 'Old CSV File', 'New CSV File'],
                      index=[i for i in range(frame)])
    df['Index'] = df.index + 1

    df1 = pd.DataFrame({'NPZ File': npz_list})
    df2 = pd.DataFrame({'Old CSV File': csv_list})
    df3 = pd.DataFrame({'New CSV File': new_csv_list})

    df.update(df1)
    df.update(df2)
    df.update(df3)

    return df


##### Initate empty dataframe for annotation DataTable #####
compiled_files_df = compiled_files_list(1000)

#############################################################
## Container for the app
app.layout = html.Div(
    style={
        'backgroundColor': colors['background']
        # ,'columnCount' : 2
    },

    children=[

        ## Top Section
        html.Div([
            ## Spilt Top Bar, 1
            ## The title for the webpage
            html.Div([
                html.H1(
                    children="Dash for Angio Analysis v2.1",
                    style={'textAlign': 'center', 'color': colors['text']}
                ),

                html.Div(
                    children='Detailed instructions located at the bottom, kindly read before using the webapp',
                    style={'textAlign': 'center', 'color': colors['text']}
                ),

            ], style={'width': '30%', 'float': 'left', 'display': 'inline-block'}
            ),

            ## Spilt Top Bar, 2
            html.Div([
                html.Br(),
                html.Label(
                    children='Select a npz file',
                    style={'textAlign': 'center', 'color': colors['text']},
                ),

                ## Text Input for npz file directory
                dcc.Dropdown(
                    id='npz-list',
                    value=0,
                    placeholder='Select a npz file',
                    options=[{'label': i, 'value': i} for i in npz_list]
                ),
            ], style={'width': '40%', 'float': 'left', 'display': 'inline-block'}
            ),

            ## Spilt Top Bar, 3
            html.Div([
                html.Br(),
                html.Label(
                    children='Annotate and Save CSV',
                    style={'textAlign': 'center', 'color': colors['text']},
                ),

                html.Br(),
                html.Br(),

                ## Annotation Button goes here
                html.Button(children='Annotate',
                            id='button',
                            n_clicks=0,
                            style={'height': '50px', 'width': '100px'}
                            ),

            ], style={'textAlign': 'center', 'width': '10%', 'float': 'left', 'display': 'inline-block'}
            ),

            ## Spilt Top Bar, 4 (Disabled reject button for latest update 2020/11/30)
            html.Div([
                # html.Br(),
                # html.Label(
                #     children='Reject and Skip File',
                #     style={'textAlign': 'center', 'color': colors['text']},
                # ),
                #
                # html.Br(),
                # html.Br(),
                #
                # # ## Reject Button goes here
                # # html.Button(children='Reject',
                # #             id='reject-button',
                # #             n_clicks=0,
                # #             style={'height': '50px', 'width': '100px'}
                # #             ),

            ], style={'textAlign': 'center', 'width': '10%', 'float': 'left', 'display': 'inline-block'}
            ),

        ], style={'height': '120px'}
        ),

        html.Hr(),

        # html.Div([
        #     html.Video(
        #
        #     )
        # ])

        ## Middle section, Display lower bound image
        html.Div([
            html.Div(id='npz-lower')
        ], style={'width': '100%', 'height': '450px', 'display': 'inline-block'}
        ),

        html.Br(),
        html.Br(),

        ## Middle Section, Display upper bound image
        html.Div([
            html.Div(id='npz-upper')
        ], style={'width': '100%', 'height': '450px', 'display': 'inline-block'}
        ),

        html.Hr(),

        ## Graph to plot annotation
        html.Div([
            dcc.Graph(id='annotation_plot'),
        ], style={'width': '100%', 'height': '450px', 'display': 'inline-block'}
        ),

        html.Br(),

        ## Lower bound Text and Slider
        html.Div([
            html.Div(
                id='slider-output-1',
                style={'textAlign': 'center', 'color': colors['text']}
            ),
            html.Div([
                dcc.Slider(
                    id='lower_slider',
                    min=0,
                    max=0,
                    step=1,
                    value=0,
                    marks={},
                ),
            ], style={'margin-left': '50px', 'margin-right': '50px'},
            ),
        ],
        ),

        html.Br(),

        ## Upper bound Text and Slider
        html.Div([
            html.Div(
                id='slider-output-2',
                style={'textAlign': 'center', 'color': colors['text']}
            ),
            html.Div([
                dcc.Slider(
                    id='upper_slider',
                    min=0,
                    max=0,
                    step=1,
                    value=0,
                    marks={},
                ),
            ], style={'margin-left': '50px', 'margin-right': '50px'},
            ),
        ]),

        html.Br(),
        html.Hr(),

        ## Dash DataTable for Annotation File
        html.Div([
            html.Div([
                ## CSV DataTable Title
                html.H5('New Annotation DataTable'),

                ## New Annotation DataTable, not displayed indicated with 'none'
                dash_table.DataTable(
                    id='new-datatable',
                    data=df_annotation.to_dict('rows'),
                    columns=[{'name': i, 'id': i} for i in df_annotation.columns],
                    filter_action='native',
                    editable=True,
                    page_action='native',
                    page_size=100,
                    export_format='csv',
                ),
            ], style={'display': 'none'}
                #             style={'width': '49%', 'float': 'right', 'display': 'inline-block'},
            ),
        ]),

        html.Div([
            ## Left Side
            html.Div([
                html.H1('Instructions'),
                dcc.Textarea(id='instructions',
                             value=('For first time users:\n'
                                    '1) Before using the webapp, maximise the browser window and zoom out till you can see the lower slider\n'
                                    '2) Change working directory stated in the main.py file\n'
                                    '3) Create the ‘npz’, ‘old-csv’, and ‘new-csv’ sub-folders\n'
                                    '3-1) ‘npz’ folder stores the preprocessed image files in npz format\n'
                                    '3-2) ‘old-csv’ folder stores the predicted annotations from the trained model in csv format\n'
                                    '3-3) ‘new-csv’ folder stores the manually corrected annotations in csv format\n'
                                    '\n'
                                    '\n'
                                    'File format:\n'
                                    'npz files -> preprocessed image files in (frame, channel, width, height), width and height = 128, channel = 1\n'
                                    'csv files -> csv files saved as frame, annotation format\n'
                                    '\n'
                                    '\n'
                                    'Step-by-step guide:\n'
                                    '1) Select npz file from the dropdown list\n'
                                    '2) Use the sliders to view or adjust the lower and upper boundary images and annotations on the graph\n'
                                    '3) When the desired good frames range have been selected using the sliders, click on the annotation button located at the top right-hand corner\n'
                                    '\n'
                                    '\n'
                                    'Note: When the npz file has multiple good frames flanked by bad frames, just move on to the next file. (do not annotate the npz file)\n'
                                    '\n'
                                    '\n'
                                    ),
                             rows=200,
                             style={'width': '100%', 'height': '100%'},
                             disabled=True
                             ),

            ], style={'width': '49%', 'float': 'left', 'display': 'inline-block'},
            ),

            ## Right Side
            html.Div([
                ## CSV DataTable Title
                html.H5('List of files in directory'),

                ## New Annotation DataTable, not displayed indicated with 'none'
                dash_table.DataTable(
                    id='files-datatable',
                    data=compiled_files_df.to_dict('rows'),
                    columns=[{'name': i, 'id': i} for i in compiled_files_df.columns],
                    filter_action='native',
                    editable=False,
                    page_action='native',
                    page_size=100,
                ),
            ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'},
            ),
        ]),

        html.Div(id='placeholder'),
        html.Div(id='placeholder-2'),

    ])


###############################################################################
#############################################################
## Callback for csv/xls file upload -> Annotation plot (CB1)
@app.callback(
    Output('annotation_plot', 'figure'),
    [Input('npz-list', 'value'),
     Input('new-datatable', 'data')])
def update_graph(filename, anno_table):
    btm_scatter = go.Figure()
    #     {
    #         'layout': go.Layout(
    #             plot_bgcolor=colors["background"],
    #             paper_bgcolor=colors["background"])
    #     }

    if filename != 0:
        csv_filename = ''.join(['csv-', filename[4:-4], '.csv'])
        df = reading_csv_file(str(csv_filename))
        df1 = pd.DataFrame(anno_table)

        btm_scatter = go.Figure(
            go.Scatter(
                name='Original Annotation',
                x=df['Image No.'],
                y=df['Mean Intensity'],
                mode='markers'
            )
        )

        btm_scatter.add_trace(
            go.Scatter(
                name='New Annotation',
                x=df1['Image No.'],
                y=df1['Annotation'],
                mode='markers'
            )
        )

        btm_scatter.update_layout(legend=dict(yanchor="top", y=0.60, xanchor="left", x=0.01))
        btm_scatter.update_xaxes(range=[0, df.index.shape[0]], title_text='Image No.')
        btm_scatter.update_yaxes(title_text='Annotation')
        btm_scatter.update_traces()

    return btm_scatter


#############################################################
## Update images with input from npz dropdown list (CB2)
@app.callback([Output('lower_slider', 'max'),
               Output('lower_slider', 'marks'),
               Output('lower_slider', 'value'),
               Output('upper_slider', 'max'),
               Output('upper_slider', 'marks'),
               Output('upper_slider', 'value')],
              [Input('npz-list', 'value')])
def update_slider(filename):
    ## Get npz file location
    if filename != 0:
        path = os.path.join(npz_directory, str(filename))
        image_array = np.load(path)

        ## Setting the min value of slider
        slider_min = 0

        ## Determining the max value of slider
        slider_max = image_array['arr_0'].shape[0] - 1

        ## Returning the marks for the slider
        slider_marks = {
            i: '{}'.format(i) for i in range(slider_max) if i % 10 == 0
        }

        return slider_max, slider_marks, slider_min, slider_max, slider_marks, slider_max
    else:
        raise PreventUpdate


#############################################################
## Callback for lower bound slider position (CB3)
@app.callback(Output('slider-output-1', 'children'),
              [Input('lower_slider', 'value')])
def update_test_output(value):
    return 'Lower Bound Image {}'.format(value)


#############################################################
## Callback for upper bound slider position (CB4)
@app.callback(Output('slider-output-2', 'children'),
              [Input('upper_slider', 'value')])
def update_test_output(value):
    return 'Upper Bound Image {}'.format(value)


#############################################################
## Update lower bound image with input from npz dropdown list (CB5)
@app.callback(Output('npz-lower', 'children'),
              [Input('npz-list', 'value'),
               Input('lower_slider', 'value')])
def update_image(filename, frame):

    ## Get npz file location and load it as an np.array
    if filename != 0:

    ## Loading 5 images in a shot
        # if file_number >= 2:
        image_array = np.load(os.path.join(npz_directory, str(filename)))
        image_array = image_array.f.arr_0

        if frame - 2 >= 0:
            image_neg2 = image_array[frame-2,0,:,:]
            image_neg2 = np.repeat(image_neg2[:,:, np.newaxis], 3, axis = 2)
        else:
            image_neg2 = np.zeros((128,128,3))

        if frame - 1 >= 0:
            image_neg1 = image_array[frame-1,0,:,:]
            image_neg1 = np.repeat(image_neg1[:,:, np.newaxis], 3, axis = 2)
        else:
            image_neg1 = np.zeros((128,128,3))

        image_centre = image_array[frame,0,:,:]
        print(image_array.shape)
        image_centre = np.repeat(image_centre[:,:, np.newaxis], 3, axis = 2)

        if frame + 1 < image_array.shape[0]:
            image_pos1 = image_array[frame+1,0,:,:]
            image_pos1 = np.repeat(image_pos1[:,:, np.newaxis], 3, axis = 2)
        else:
            image_pos1 = np.zeros((128,128,3))

        if frame + 1 < image_array.shape[0]:
            image_pos2 = image_array[frame+2,0,:,:]
            image_pos2 = np.repeat(image_pos2[:,:, np.newaxis], 3, axis = 2)
        else:
            image_pos2 = np.zeros((128, 128, 3))

    ## Plotting using subplots
        fig = make_subplots(rows=1, cols=5,
                            subplot_titles=('Frame {}'.format(frame-2),
                                            'Frame {}'.format(frame-1),
                                            'Center Frame {}'.format(frame),
                                            'Frame {}'.format(frame+1),
                                            'Frame {}'.format(frame+2)),
                            horizontal_spacing=0,
                            vertical_spacing=0)
    ## Plotting image_neg2
        fig.add_trace(
            go.Image(z = image_neg2), 1, 1
        )
    ## Plotting image_neg1
        fig.add_trace(
            go.Image(z = image_neg1), 1, 2
        )
    ## Plotting image_centre
        fig.add_trace(
            go.Image(z = image_centre), 1, 3
        )
    ## Plotting image_pos1
        fig.add_trace(
            go.Image(z = image_pos1), 1, 4
        )
    ## Plotting image_pos2
        fig.add_trace(
            go.Image(z = image_pos2), 1, 5
        )

        # fig.update_layout(title_text = 'Frame {} | Frame {} | Center Frame {} | Frame {} | Frame {}'.format(frame-2,frame-1,frame,frame+1,frame+2))
        fig.update_layout(coloraxis_showscale=False)
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)
        # fig.show()

        ## Filling npz_fig with graph
        npz_fig = html.Div([
            dcc.Graph(
                figure=fig
            ),
        ])

        return npz_fig
    else:
        raise PreventUpdate


#############################################################
## Update upper bound image with input from npz dropdown list (CB6)
@app.callback(Output('npz-upper', 'children'),
              [Input('npz-list', 'value'),
               Input('upper_slider', 'value')])
def update_image(filename, frame):

    ## Get npz file location and load it as an np.array
    if filename != 0:

    ## Loading 5 images in a shot
        # if file_number >= 2:
        image_array = np.load(os.path.join(npz_directory, str(filename)))
        image_array = image_array.f.arr_0

        if frame - 2 >= 0:
            image_neg2 = image_array[frame-2,0,:,:]
            image_neg2 = np.repeat(image_neg2[:,:, np.newaxis], 3, axis = 2)
        else:
            image_neg2 = np.zeros((128,128,3))

        if frame - 1 >= 0:
            image_neg1 = image_array[frame-1,0,:,:]
            image_neg1 = np.repeat(image_neg1[:,:, np.newaxis], 3, axis = 2)
        else:
            image_neg1 = np.zeros((128,128,3))

        image_centre = image_array[frame,0,:,:]
        print(image_array.shape)
        image_centre = np.repeat(image_centre[:,:, np.newaxis], 3, axis = 2)

        if frame + 1 < image_array.shape[0]:
            image_pos1 = image_array[frame+1,0,:,:]
            image_pos1 = np.repeat(image_pos1[:,:, np.newaxis], 3, axis = 2)
        else:
            image_pos1 = np.zeros((128,128,3))

        if frame + 1 < image_array.shape[0]:
            image_pos2 = image_array[frame+2,0,:,:]
            image_pos2 = np.repeat(image_pos2[:,:, np.newaxis], 3, axis = 2)
        else:
            image_pos2 = np.zeros((128, 128, 3))

    ## Plotting using subplots
        fig = make_subplots(rows=1, cols=5,
                            subplot_titles=('Frame {}'.format(frame-2),
                                            'Frame {}'.format(frame-1),
                                            'Center Frame {}'.format(frame),
                                            'Frame {}'.format(frame+1),
                                            'Frame {}'.format(frame+2)),
                            horizontal_spacing=0,
                            vertical_spacing=0)
    ## Plotting image_neg2
        fig.add_trace(
            go.Image(z = image_neg2), 1, 1
        )
    ## Plotting image_neg1
        fig.add_trace(
            go.Image(z = image_neg1), 1, 2
        )
    ## Plotting image_centre
        fig.add_trace(
            go.Image(z = image_centre), 1, 3
        )
    ## Plotting image_pos1
        fig.add_trace(
            go.Image(z = image_pos1), 1, 4
        )
    ## Plotting image_pos2
        fig.add_trace(
            go.Image(z = image_pos2), 1, 5
        )

        # fig.update_layout(title_text = 'Frame {} | Frame {} | Center Frame {} | Frame {} | Frame {}'.format(frame-2,frame-1,frame,frame+1,frame+2))
        fig.update_layout(coloraxis_showscale=False)
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)
        # fig.show()

        ## Filling npz_fig with graph
        npz_fig = html.Div([
            dcc.Graph(
                figure=fig
            ),
        ])

        return npz_fig
    else:
        raise PreventUpdate


###############################################################################
# Update the datatable with annotation_input upon button click (CB7)
@app.callback(
    Output('new-datatable', 'data'),
    [Input('lower_slider', 'value'),
     Input('upper_slider', 'value')],
    [State('new-datatable', 'data')]
)
def update_table_annotation(lower_bound, upper_bound, data):
    for i in range(0, 1000):
        data[i]['Annotation'] = 1
    for i in range(int(lower_bound), (int(upper_bound) + 1)):
        data[i]['Annotation'] = 0
    return data


###############################################################################
## Save a new annotation file with the lower and upper boundary (CB8)
@app.callback(
    Output('placeholder', 'children'),
    [Input('button', 'n_clicks')],
    [State('lower_slider', 'value'),
     State('upper_slider', 'value'),
     State('upper_slider', 'max'),
     State('npz-list', 'value')]
)
def export_anno_file(clicks, lower_bound, upper_bound, upper_max, npz_filename):
    if clicks != 0:

        ## If empty file exist, delete it
        empty_filename = ''.join(['new-', str(npz_filename[4:-4]), '-rejected.csv'])
        print(empty_filename)
        empty_path = os.path.join(new_csv_directory, str(empty_filename))
        print(empty_path)

        if os.path.exists(empty_path):
            os.remove(empty_path)

        ## Create annotated CSV file

        anno_file = create_df(upper_max+1)

        for i in range(lower_bound, upper_bound + 1):
            anno_file['Annotation'][i] = 0

        anno_filename = ''.join(['new-', str(npz_filename[4:-4]), '.csv'])
        path = os.path.join(new_csv_directory, str(anno_filename))

        np.savetxt(path, anno_file, delimiter=',', fmt='%d')


    else:
        raise PreventUpdate


###############################################################################
# ## Create an empty csv file for rejected frames (CB9) (Disabled reject button for latest update 2020/11/30)
# @app.callback(
#     Output('placeholder-2', 'children'),
#     [Input('reject-button', 'n_clicks')],
#     [State('npz-list', 'value')])
# def export_rejected_file(clicks, npz_filename):
#     if clicks != 0:

#         ## If anno file exist, delete it
#         anno_filename = ''.join(['new-', str(npz_filename[4:-4]), '.csv'])
#         print(anno_filename)
#         anno_path = os.path.join(new_csv_directory, str(anno_filename))
#         print(anno_path)

#         if os.path.exists(anno_path):
#             os.remove(anno_path)

#         ## Create and save empty file
#         empty_file = pd.DataFrame({})
#         empty_filename = ''.join(['new-', str(npz_filename[4:-4]), '-rejected.csv'])
#         empty_file_path = os.path.join(new_csv_directory, str(empty_filename))

#         np.savetxt(empty_file_path, empty_file, delimiter=',')

#     else:
#         raise PreventUpdate


#############################################################
# Callback for files-datatable
@app.callback(
    [Output('files-datatable', 'data'),
     Output('files-datatable', 'columns')],
    [Input('button', 'n_clicks'),
     Input('reject-button', 'n_clicks')])
def update_files_datatable(anno_clicks, reject_clicks):
    ## When annotate button is clicked, compiled_files_list data is updated
    if anno_clicks or reject_clicks != 0:

        ## Adding a delay to ensure file list gets updated
        sleep(0.5)

        ## Create a new DataFrame with updated file list
        df = compiled_files_list(1000)
        print(df)

        data = df.to_dict('rows')
        columns = [{'name': i, 'id': i} for i in df.columns]

        return data, columns
    else:
        raise PreventUpdate


#############################################################
## JupyterDash
app.run_server(port=8061, mode='external')