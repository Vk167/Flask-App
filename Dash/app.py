import random
import dash
import numpy as np
from dash import dcc
from dash import html
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ClientsideFunction, ALL
from scipy import stats
import dash_daq as daq
import pandas as pd
from textwrap import dedent
import plotly.graph_objs as go
import plotly.io as pio
from dash.exceptions import PreventUpdate
from dash import dash_table
from datetime import datetime as datetime
import pymongo
from pymongo import MongoClient
from flask import Flask
import time
import json
import base64
import flask
from Dash.data import *
from app.routes import client, database, collection_mapping, collection_mapping2,summary_collection

def init_dashboard(app: Flask):

    app = dash.Dash(__name__, title='Cp & Cpk Dashboard',external_stylesheets=['assets/style_1.css'],
                    external_scripts=['assets/custom.js','assets/jquery.js'],
                    url_base_pathname="/dashapp/", server=app)
    server = app.server
    app.config['suppress_callback_exceptions'] = True
    pio.templates.default = 'plotly_white'

    user_type = None

    current_machine_layouts = []
    pulse_machine_layouts = []

    for machine_id in num_machines:
        current_machine_layout = html.Div(
            className='three columns machine_layouts_padding',
            children=[
                html.Br(),
                html.Div(className='summary-box', children=[
                    html.Div(
                        children=[
                            html.Span(f'Machine No : ', className='machine_name'),
                            html.A(
                                html.Span(id=f'current-rating-id-{machine_id}', children='',
                                          className='machine_id_link_padding'),
                                id=f'current-rating-link-{machine_id}',
                                n_clicks=0
                            )
                        ],
                        className='machine_layouts_bottom_padding'
                    ),
                    html.Div(
                        id=f'rectangle-{machine_id}',
                        className='rect_dashboard',
                        children=[
                            html.Div(id=f'current_sample_size_label-{machine_id}', children='',
                                     className='rect_label_style'),
                            html.Div(id=f'cp_label-{machine_id}', children='Cp: ', className='rect_label_style'),
                            html.Div(id=f'cpk_label-{machine_id}', children='Cpk:', className='rect_label_style'),
                            html.Div(id=f'current_last_refresh_label-{machine_id}', children='',
                                     className='rect_label_style'),
                        ]
                    )
                ])
            ]
        )
        current_machine_layouts.append(current_machine_layout)

    for machine_id in num_machines:
        pulse_machine_layout = html.Div(
            className='three columns machine_layouts_padding',
            children=[
                html.Br(),
                html.Div(className='summary-box', children=[
                    html.Div(
                        children=[
                            html.Span(f'Machine No : ', className='machine_name'),
                            html.A(
                                html.Span(id=f'pulse-rating-id-{machine_id}', children='',
                                          className='machine_id_link_padding'),
                                id=f'pulse-rating-link-{machine_id}',
                                n_clicks=0
                            )
                        ],
                        className='machine_layouts_bottom_padding'
                    ),
                    html.Div(
                        id=f'rectangle-{machine_id}',
                        className='rect_dashboard',
                        children=[
                            html.Div(id=f'pulse_sample_size_label-{machine_id}', children='',
                                     className="rect_label_style"),
                            html.Div(id=f'cp2_label-{machine_id}', children='Cp: ', className='rect_label_style'),
                            html.Div(id=f'cpk2_label-{machine_id}', children='Cpk: ', className='rect_label_style'),
                            html.Div(id=f'pulse_last_refresh_label-{machine_id}', children='',
                                     className='rect_label_style'),
                        ]
                    )])
            ]
        )
        pulse_machine_layouts.append(pulse_machine_layout)

    initial_machine_names = machine_names(collection_mapping2)


    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        dcc.Store('user-type', data=user_type),
        dcc.Store(id='selected-machine-id', data=None),
        html.Div(id='page-content')
    ])

    login_layout = dbc.Container(fluid = True,children=
    [
      dbc.Row(
          [
              dbc.Col(
                  children=[
                      html.Div(
                          className='login-leftSide',
                          children=[
                              html.Div(
                                  className='login-image',
                                  children=[
                                      html.Img(
                                          src=app.get_asset_url(''),
                                          className='login-logo img-fluid'
                                      )
                                  ]
                              )
                          ]
                      )
                  ],
                  width=8
              ),

              dbc.Col( width=4,children=[
                  html.Div(className='loginTop',children = [
                  html.Div([
                      html.Div(className='logo-header headername', children=[
                          html.Img(src=app.get_asset_url('logo.png'), className='logo'),
                      ]),
                      html.H2('Login to your account',
                              className='mt-5 login_paragraph',
                              ),

                      dbc.Form([
                          dbc.Label('Username',
                                    className='login_input_user_label form-label'),

                          dbc.Input(id='username-input',
                                    type='text',
                                    placeholder='username',
                                    className='login_input_user_box margin_bottom_10'),

                      html.Br(),

                          dbc.Label('Password',
                                    className='login_password_label'),
                          dbc.Input(id='password-input',
                                    type='password',
                                    placeholder='password',
                                    className='login_password_input_box margin_bottom_10'),


                    html.Div(className = 'login-btn',children = [
                      dbc.Button('Login',
                                 id='login-button',
                                 color='primary',
                                 className='mt-3 login_button_color margin_bottom_10',
                                 n_clicks=0,
                                 ),]),
                      ], className='mt-5 formPadding '),

                  ], className='login_page_background'),]),
              ]),
          ]
      )
  ]
    )


    otp_layout = dbc.Container(fluid=True, children=
    [
        dbc.Row(
            [
                dbc.Col(
                    children=[
                        html.Div(
                            className='login-leftSide',
                            children=[
                                html.Div(
                                    className='login-image',
                                    children=[
                                        html.Img(
                                            src=app.get_asset_url(''),
                                            className='login-logo img-fluid'
                                        )
                                    ]
                                )
                            ]
                        )
                    ],
                    width=8
                ),

                dbc.Col(width=4, children=[
                    html.Div(className='loginTop', children=[

                        html.Div([
                            html.Div(className='logo-header headername', children=[
                                html.Img(src=app.get_asset_url('logo.png'), className='logo'),
                            ]),
                            html.H2('Enter OTP',
                                    className='mt-5 login_paragraph',
                                    ),

                            dbc.Form([
                                dbc.Label('OTP', className='otp_label '),
                                dbc.Input(id='otp-input',
                                          type='text',
                                          placeholder='Enter OTP',
                                          className='otp_entry_box  margin_bottom_10'),
                            ], className='mt-3'),

                            html.Div(className='otp-btn',children = [
                            dbc.Button(
                                'Submit OTP',
                                id='otp-submit-button',
                                className='mt-3',
                                class_name='otp_button_color'
                            ),]),

                        ], className='otp_page_background'), ]),
                ]),
            ]
        )
    ]
                                 )

    dashboard_layout = html.Div(
       [ html.Div(className='twelve columns', children=[
           html.Div(
               className="banner",
               children=[
                   html.Div(
                       className="bannerpadding",
                       children=[
                           html.Div(className = 'logo-header-parent',children=[
                           html.Div(className='header-body',children = [
                           html.H5("Cp & Cpk DASHBOARD AND REPORTS"),
                           html.H6("Process Control Reporting")]),]),
                       ]
                   ),
                   html.Div(className='logo-header headername', children=[
                       html.Img(src=app.get_asset_url('logo.png'), className='logo'),
                   ]),
                   html.Div(
                       className='bannerbuttonpadding',
                       children=[
                           html.Button('Logout', id='logout-button', n_clicks=0, className='logout_button'),
                           html.P(id='date-time', className='date-time-color'),
                       ]
                   ),
               ]
           ),

           dcc.Tabs(
               id='tabs',
               value='Dashboards',
               children=[
                   dcc.Tab(
                       label='DASHBOARDS',
                       value='Dashboards',
                       id='tab-1',
                       className='tabs.style',
                       selected_className='tab.selected',
                       children=[
                           dcc.Tabs(
                               id='subtabs',
                               value='subtab-1',
                               className="sub_tabs_style",

                               children=[
                                   dcc.Tab(label='CURRENT',
                                           value='subtab-1',
                                           className="subtab-style",
                                           selected_className="subtab-selected-style",
                                           children=[
                                               html.P("SUMMARY DASHBOARDS", className='tab1_paragraph_style'),
                                               *current_machine_layouts
                                           ]),
                                   dcc.Tab(
                                       id='pulse-subtab',
                                       label='PULSE',
                                       value='subtab-2',
                                       className="subtab-style",
                                       selected_className="subtab-selected-style",
                                       children=[
                                           html.P("SUMMARY DASHBOARDS", className='tab1_paragraph_style'),
                                           *pulse_machine_layouts
                                       ]),
                               ]
                           ),

                       ],
                   ),

                   dcc.Tab(label='SPECIFICATION SETTINGS',
                           id='specification settings',
                           className='tabs.style',
                           selected_className='tab.selected',
                           children=[
                               dcc.Tabs(
                                   id='sub-tabs1',
                                   value='subs-tab-1',
                                   className="sub_tabs_style",
                                   children= [
                               dcc.Tab(
                                       label='MODIFY',
                                       value='subs-tab-1',
                                       className="subtab-style subtab-selected-style",
                                       children=[

                                    html.Div(className='twelve columns  forAlert', children=[

                                   dbc.Alert(
                                       "USL and LSL values are updated Successfully",
                                       id="alert-auto",
                                       is_open=False,
                                       duration=4000,
                                       className='alert-msg'
                                   ),
                                        dbc.Alert(
                                            "Machine name and rating have been marked as 'INACTIVE'",
                                            id="alert-delete-msg",
                                            is_open=False,
                                            duration=4000,
                                            className='alert-msg'
                                        ),
                                    ]
                                        ),

                               html.Div(className='twelve columns spec_space',children=[
                               html.Div(className='two columns', children=
                               [html.Br(),
                                html.Label('Machine Names',
                                           className='specs_machine_name'),

                                dcc.Dropdown(options=[{'label': machine, 'value': machine} for machine in
                                                      initial_machine_names],
                                             id='dropdown1',
                                             searchable=False,
                                             value = '!01',
                                             placeholder='Select machine.....',
                                             ),
                                ]
                                        ),
                               html.Div(className='three columns specs_rating_box_width', children=
                               [html.Br(),
                                html.Label('Ratings',
                                           className='specs_rating_name'),
                                dcc.Dropdown(options=[],
                                             id='rating-dd',
                                             searchable=False,
                                             disabled=False,
                                             value='001 (ALL)',
                                             placeholder='Select ratings.....',
                                             ),
                                ],

                                        ),
                               html.Div(className=' two columns specs_box_styling', children=
                               [
                                   html.Br(),
                                   html.Label('Specifications', className='specs_specs_name'),
                                   html.Label('Welding Current USL', className='specs_label_names'),
                                   html.Label('Welding Current LSL', className='specs_label_names'),
                                   html.Label('Pulse Value USL', className='specs_label_names'),
                                   html.Label('Pulse Value LSL', className='specs_label_names'),
                                   html.Label('Current Change Stroke Number', className='specs_label_names'),
                               ],
                                        ),

                               html.Div(className='two columns specs_hist_box_styling', children=
                               [html.Br(),
                                html.Label('Historical Value',
                                           className='specs_hist_name'),
                                html.Label(id='usl-dd', className='specs_hist_label_name'),
                                html.Label(id='lsl-dd', className='specs_hist_label_name'),
                                html.Label(id='usl-dd2', className='specs_hist_label_name'),
                                html.Label(id='lsl-dd2', className='specs_hist_label_name'),
                                ],
                                        ),

                               html.Div(className='three columns  numWidth numeric_input_box_styling',
                                        children=[html.Br(),
                                                  html.Label('Set new value',
                                                             className='specs_new_value_name'),

                                                  daq.NumericInput(id='ud_usl_input',
                                                                   className='numeric-input-input numeric_input_1',
                                                                   size=200, max=9999999,
                                                                   ),
                                                  daq.NumericInput(id='ud_lsl_input',
                                                                   size=200, max=9999999,
                                                                   className='numeric_input_2'),
                                                  daq.NumericInput(id='ud_usl_input2',
                                                                   size=200, max=9999999,
                                                                   className='numeric_input_3'),
                                                  daq.NumericInput(id='ud_lsl_input2',
                                                                   size=200, max=9999999,
                                                                   className='numeric_input_4'),
                                                  dbc.Input(id='change-current-stroke',

                                                            placeholder='enter stroke number here...',
                                                            className='current-stroke'),

                                                  html.Div(className='twelve columns textEnd', children=[
                                                      html.Button(
                                                          'UPDATE',
                                                          id='update-button',
                                                          n_clicks=0,
                                                          className='specs_update_button'
                                                      ),
                                                      html.Button(
                                                          'CLEAR',
                                                          id='specs-clear-button',
                                                          n_clicks=0,
                                                          className='specs_clear_button'
                                                      ),
                                                      html.Div([
                                                      dcc.ConfirmDialogProvider(
                                                          children=html.Button(
                                                          'INACTIVE',
                                                          id='specs-delete-button',
                                                          n_clicks=0,
                                                          className='specs_clear_button'
                                                      ),
                                                          id='danger-danger-provider',
                                                          message='Do you want to deactivate the rating?'

                                                      ),html.Div(id='output-provider'),
                                                      ]),

                                                  ]),
                                                  html.Div(id='update-result'),

                                                  ]),
                           ]),

                                    ]),
                               dcc.Tab(
                                   id='specs-add',
                                   label='ADD',
                                   value='subs-tab-2',
                                   className="subtab-style",
                                   selected_className="subtab-selected-style",
                                   children=[

                                       html.Div(className='twelve columns  add-alert', children=[
                                           dbc.Alert(
                                               "",
                                               id="alert-add",
                                               is_open=False,
                                               duration=4000,
                                               className='alert-add-msg'
                                           ), ]
                                                ),

                                       html.Div(className='twelve columns spec_space', children=[
                                           html.Div(className='two columns', children=
                                           [html.Br(),
                                            html.Label('Machine Names',
                                                       className='specs_machine_name'),

                                            dcc.Input(id='machine-input',
                                                         type='text',
                                                         placeholder='machine name',
                                                         className='otp_entry_box'
                                                         ),
                                            ]
                                                    ),
                                           html.Div(className='two columns ', children=
                                           [html.Br(),
                                            html.Label('Ratings',
                                                       className='specs_rating_name'),
                                            dcc.Input(id='rating-amp-input',
                                                         type='text',
                                                         placeholder='rating(amp)',
                                                         className='otp_entry_box'
                                                         ),
                                            ],
                                                    ),
                                           html.Div(className='two columns',children = [
                                               html.Br(),
                                           html.Label('Operation Name',
                                                      className='specs_rating_name'),
                                           dcc.Input(id='operation-input',
                                                     type='text',
                                                     placeholder='operation name',
                                                     className='otp_entry_box'
                                                     ),]),
                                           html.Div(className=' three columns add_box_styling', children=
                                           [
                                               html.Br(),
                                               html.Label('Specifications', className='specs_specs_name'),
                                               html.Label('Welding Current USL', className='add_label_names'),
                                               html.Label('Welding Current Mean', className='add_label_names'),
                                               html.Label('Welding Current LSL', className='add_label_names'),
                                               html.Label('Pulse Value USL', className='add_label_names'),
                                               html.Label('Pulse Value Mean', className='add_label_names'),
                                               html.Label('Pulse Value LSL', className='add_label_names'),
                                           ],
                                                    ),

                                           html.Div(className='three columns  numWidth numeric_input_box_styling', children=
                                           [html.Br(),
                                            html.Label('Add New Values',
                                                       className='specs_hist_name'),
                                            dcc.Input(id='current-usl-input',
                                                                        type='text',
                                                                        placeholder='Current USL',
                                                                        className='numeric-input-input add_input_2'),

                                            dcc.Input(id='current-mean-input',
                                                                        type='text',
                                                                        placeholder='Current Mean',
                                                                        className='add_input_2'),
                                            dcc.Input(id='current-lsl-input',
                                                      type='text',
                                                      placeholder='Current LSL',
                                                      className='add_input_2'),
                                            dbc.Input(id='pulse-usl-input',
                                                              type='text',
                                                              placeholder='Pulse USL',
                                                              className='add_input_2'),
                                            dbc.Input(id='pulse-mean-input',
                                                              type='text',
                                                              placeholder='Pulse Mean',
                                                              className='add_input_2'),
                                            dbc.Input(id='pulse-lsl-input',
                                                              type='text',
                                                              placeholder='Pulse LSL',
                                                              className='add_input_2'),

                                            html.Div(className='twelve columns addtextEnd', children=[
                                                html.Button(
                                                                'ADD',
                                                                id='add-delete-button',
                                                                className='specs_update_button',

                                                            ),
                                                html.Button(
                                                                'CLEAR',
                                                                id='add-clear-button',
                                                                n_clicks=0,
                                                                className='specs_update_button'
                                                            ),
                                            ]),
                                            ], ),

                                       ]),
                                   ]),
                                ]),
                           ]),

                   dcc.Tab(
                       label='CONTROL CHARTS DASHBOARD',
                       value='Control charts Dashboard',
                       className='tabs.style',
                       selected_className='tab.selected',
                   ),

                   dcc.Tab(label='REPORTS',
                           className='tabs.style',
                           selected_className='tab.selected',
                           id='report',
                           value='Reports',
                           children=[
                                     html.Br(),
                                     html.Div(className='two columns', children=
                                     [
                                         html.Label('Machine Names',
                                                    className='report_machine_name'),

                                         dcc.Dropdown(
                                             options=[{'label': machine, 'value': machine} for machine in
                                                      initial_machine_names],
                                             id='report-machine',
                                             searchable=False,
                                             placeholder='Select machine.....',
                                             className='report_machine_name_dd'
                                         ), html.Label(id='label1')
                                     ],
                                              ),
                                     html.Div(className='three columns ', children=
                                     [
                                         html.Label('Ratings',
                                                    className='report_machine_name report_rating_dd_width'),
                                         dcc.Dropdown(options=[],
                                                      id='report-rating',
                                                      multi=True,
                                                      searchable=False,
                                                      placeholder='Select rating.....',
                                                      ), html.Label(id='label2')
                                     ],

                                              ),
                                    html.Div(className='four columns', children=[
                                     html.Div(className='four columns', children=
                                     [
                                         html.Label('From Date',
                                                    className='report_from_to_date_name'),
                                         dcc.DatePickerSingle(id='start-date',
                                                              min_date_allowed=datetime(2024, 2, 1),
                                                              clearable=True,
                                                              placeholder='From Date.....',
                                                              display_format='DD/MM/YYYY',
                                                              className='calendar_date',
                                                              ),
                                     ],
                                              ),

                                     html.Div(className='four columns', children=
                                     [
                                         html.Label('To Date',
                                                    className='report_from_to_date_name'),
                                         dcc.DatePickerSingle(id='end-date',
                                                              min_date_allowed=datetime(2024, 2, 1),
                                                              clearable=True,
                                                              placeholder='To Date.....',
                                                              display_format='DD/MM/YYYY',
                                                              className='calendar_date',
                                                              ),
                                     ],
                                              ),]),
                                     html.Div(className='three columns', children=
                                     [
                                         html.Label(
                                             className='div_report_button'),

                                         html.Button(
                                             'SUBMIT',
                                             id='submit-button',
                                             n_clicks=0,
                                             className='report_submit_button'
                                         ),
                                         html.Button(
                                             'CLEAR',
                                             id='clear-button',
                                             n_clicks=0,
                                             className='specs_clear_button'
                                         ),

                                     ]
                                              ),

                                     html.Div(className='twelve columns', children=
                                     [
                                         html.P(className='twelve columns report_paragraph_color', id='output1',

                                                )
                                     ]),
                               dcc.Loading(id="loading-output-1", type="circle",
                                           children=[html.Div(id='datatable'),

                                         html.Div(children=[
                                             dcc.Graph(id="barChart",config={'displaylogo': False}
                                                       , className= 'report-chart'
                                                       ),
                                             dcc.Graph(id="barChart2",config={'displaylogo': False}
                                                       , className = 'report-chart',
                                                       ), ], className= 'report-div')]),
                                     ]
                           ),
               ], className='tabs'
           ),
           html.Div(id='tabs-content'),
       ],
                  )])

    def dashboards_content():
        return html.Div(
            [
                dcc.Interval(id='interval-dashboards', interval=20000, n_intervals=0),
            ])

    def control_charts_dashboard_content():
        return [
            dcc.Interval(id='interval-dashboards', interval=20000, n_intervals=0),
            dcc.Tabs(
                id='sub-tabs',
                value='sub-tab-1',
                className="sub_tabs_style",

                children=[
                    dcc.Tab(
                        label='WELDING CURRENT CHARTS',
                        value='sub-tab-1',
                        className="subtab-style subtab-selected-style",

                        children=[
                            html.Br(),
                            html.Div(className='twelve columns table-div', children=[
                                html.Div(className='table-style', children=[
                                    dash_table.DataTable(
                                        id='current-chart-table',
                                        columns=[{'name': col, 'id': col} for col in
                                                 ['Machine Name', 'Operation Name', 'Rating', 'Sample Size', 'Min Cp',
                                                  'Min Cpk',
                                                  'USL', 'LSL',
                                                  'Mean', 'STD', 'xbar', 'Min', 'Max', 'R(Diff)']],
                                        data=[]
                                    )])]),
                            html.Br(),

                            html.Div([

                                dcc.Graph(
                                    id='run-chart', config={'displaylogo': False}, responsive=True,
                                    className='run_chart welding-runchart'),

                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Br(),
                                                html.H3('Cp (Welding Current)',
                                                        className='cp_welding_current'),
                                                daq.LEDDisplay(id='cp-led',
                                                               value=0,
                                                               size=35
                                                               ),
                                                html.H4(id='current-cp-condition',
                                                        className='cp_welding_current_condition')

                                            ],
                                            className='div_cp_welding_current'
                                        ),
                                        html.Br(),
                                        html.Div(
                                            [
                                                html.H3('Cpk (Welding Current)',
                                                        className='cp_welding_current'),
                                                daq.LEDDisplay(id='cpk-led',
                                                               value=0,
                                                               size=35
                                                               ),
                                                html.H4(id='current-cpk-condition',
                                                        className='cp_welding_current_condition')

                                            ],
                                            className='div_cp_welding_current'
                                        ),
                                    ],
                                    className='led_div_style',
                                ),

                                dcc.Graph(id='bell-curve', config={'displaylogo': False}, responsive=True,
                                          className='bell_curve welding-bellchart'),
                            ], className='subtabs_div_style')

                ]),
                    dcc.Tab(
                        id='pulse-subchart',
                        label='PULSE VALUE CHARTS',
                        value='sub-tab-2',
                        className="subtab-style",
                        selected_className="subtab-selected-style",
                        children=[
                            html.Br(),
                            html.Div(className=' twelve columns table-div', children=[
                                html.Div(className='table-style', children=[
                                    dash_table.DataTable(
                                        id='pulse-chart-table',
                                        columns=[{'name': col, 'id': col} for col in
                                                 ['Machine Name', 'Operation Name', 'Rating', 'Sample Size', 'Min Cp',
                                                  'Min Cpk',
                                                  'USL', 'LSL',
                                                  'Mean', 'STD', 'xbar', 'Min', 'Max', 'R(Diff)']],

                                        data=[]
                                    )])]),
                           html.Br(),
                            html.Div([
                                dcc.Graph(id='run-chart-two', config={'displaylogo': False}, responsive=True,
                                          className='run_chart pulse-runchart'),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Br(),
                                                html.H3('Cp (Pulse Value)',
                                                        className='cp_welding_current'),
                                                daq.LEDDisplay(id='cp-led2',
                                                               value=0,
                                                               size=35
                                                               ),
                                                html.H4(id='pulse-cp-condition',
                                                        className='cp_welding_current_condition')
                                            ],
                                            className='div_cp_welding_current'
                                        ),
                                        html.Br(),
                                        html.Div(
                                            [
                                                html.H3('Cpk (Pulse Value)',
                                                        className='cp_welding_current'),
                                                daq.LEDDisplay(id='cpk-led2',
                                                               value=0,
                                                               size=35
                                                               ),
                                                html.H4(id='pulse-cpk-condition',
                                                        className='cp_welding_current_condition')
                                            ],
                                            className='div_cp_welding_current'
                                        ),
                                    ],
                                    className='led_div_style',
                                ),

                                dcc.Graph(id='bell-curve-two', config={'displaylogo': False}, responsive=True,
                                          className='bell_curve pulse-runchart'),
                            ], className='subtabs_div_style')
                        ]
                    ),
                ],
            ),
        ]


    @app.callback(
        Output('tabs-content', 'children'),
        [Input('tabs', 'value')]
    )
    def update_tab_content(selected_tab):
        if selected_tab == 'Dashboards':
            return dashboards_content()
        elif selected_tab == 'Control charts Dashboard':
            return control_charts_dashboard_content()


        ####### Login Layout Callbacks ########
    @app.callback(
        Output('user-type', 'data'),
        [Input('login-button', 'n_clicks'),
         Input('username-input', 'value')]
    )
    def handle_login(n_clicks, username):
        global user_type
        if username == 'supervisor' or username == 'admin':
            user_type = username
            return user_type


    @app.callback(
        [Output('report', 'style'),
        Output('specification settings', 'style')],
        [Input('user-type', 'data')]
    )
    def update_tabs_visibility(user_type):
        if user_type == 'supervisor' or user_type == 'admin':
            return {}, {}
        else:
            return {'display': 'none'}, {'display': 'none'}

    @app.callback(
        [Output('pulse-subtab', 'style')],
        [Input('user-type', 'data')]
    )
    def update_tabs_visibility(user_type):
        if user_type == 'supervisor' or user_type == 'admin':
            return [{'className': 'subtab-style'}]
        else:
            return [{'display': 'none'}]

    @app.callback(
        [
         Output('pulse-subchart', 'style')
         ],
        [Input('user-type', 'data')]
    )
    def update_tabs_visibility(user_type):
        if user_type == 'supervisor' or user_type == 'admin':
            return [{'className': 'subtab-style'}]
        else:
            return [{'display': 'none'}]


    @app.callback(
        Output('url', 'pathname', allow_duplicate=True),
        Input('login-button', 'n_clicks'),
        [State('username-input', 'value'),
         State('password-input', 'value')],
        prevent_initial_call=True
    )
    def otp_page(n_clicks, username, password):
        if n_clicks > 0:
            db = client.configurationfiles
            collection = db.users
            user = collection.find_one({'username': username, 'password': password})
            if user is not None:
                flask.session['logged_in'] = True
                flask.session['username'] = username
                return '/otp-page'
        return '/dashapp/'

    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Output("logout-button", "n_clicks"),
        [Input("logout-button", "n_clicks")],
        prevent_initial_call=True
    )
    def logout(n_clicks):
        if n_clicks > 0:
            username = get_current_username()
            flask.session['logged_in'] = False
            log_logout_event(username)
            return "/dashapp/", 0
        return "/dashapp/", 0

    @app.callback(
        Output('url', 'pathname'),
        Input('otp-submit-button', 'n_clicks'),
        [State('otp-input', 'value')]
    )
    def login(n_clicks, otp):
        n_clicks = n_clicks or 0
        if n_clicks > 0:
            username = get_current_username()
            users_collection = collection_mapping2['users']
            user = users_collection.find_one({'username': username})
            if user is not None and user['otp'] == otp and user['username'] == username:
                flask.session['logged_in'] = True
                log_login_event(username)
                return '/Cp-Cpk_dashboard_and_reports'
        return '/dashapp/'

    def check_login_status():
        return True

    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')]
    )
    def display_page(pathname):
        if pathname == '/dashapp/':
            return login_layout
        elif pathname == '/otp-page':
            if flask.session.get('logged_in'):
                return otp_layout
        elif pathname == '/Cp-Cpk_dashboard_and_reports':
            if check_login_status():
                if flask.session.get('logged_in'):
                    return dashboard_layout
            else:
                return dcc.Location(pathname='/')
        else:
            return '404 Page Not Found'
        return login_layout

    @app.callback(
        Output('rating-dd', 'options'),
        Input('dropdown1', 'value')
    )
    def update_uni_machines( machine_name):
        if machine_name is None:
            machine_name = "!01"
            uni_ratings = ratings(collection_mapping2, machine_name)
        else:
            uni_ratings = ratings(collection_mapping2, machine_name)
        return uni_ratings

    @app.callback(
        [Output('usl-dd', 'children'),
         Output('lsl-dd', 'children'),
         Output('usl-dd2', 'children'),
         Output('lsl-dd2', 'children')],
        Input('dropdown1', 'value'),
        Input('rating-dd', 'value'),
    )
    def update_labels( machine, rating):
        db = client['configurationfiles']
        current_collection = db['current_usl_lsl']
        pulse_collection = db['pulse_usl_lsl']
        if machine and rating is None:
            complete_machine_name = "!01" + '001' + ':' + 'm'
        elif machine is None:
            complete_machine_name = "!01" + rating[0:3] + ':' + 'm'
        else:
            complete_machine_name = str(machine) + rating[0:3] + ':' + 'm'
        machine_name = complete_machine_name

        current_data = current_collection.find_one({"machine_name": machine_name, "rating(AMP)": rating[5:-1]})
        pulse_data = pulse_collection.find_one({"machine_name": machine_name, "rating(AMP)": rating[5:-1]})

        current_usl = current_data["usl"]
        current_lsl = current_data["lsl"]
        pulse_usl = pulse_data['usl']
        pulse_lsl = pulse_data['lsl']

        current_usl = float(current_usl)
        current_lsl = float(current_lsl)
        pulse_usl = float(pulse_usl)
        pulse_lsl = float(pulse_lsl)

        current_string_usl = current_usl
        current_string_lsl = current_lsl
        pulse_string_usl = pulse_usl
        pulse_string_lsl = pulse_lsl
        return current_string_usl, current_string_lsl, pulse_string_usl, pulse_string_lsl

    @app.callback(
        Output('alert-delete-msg', 'is_open'),
        Output('dropdown1', 'value'),
        Input('specs-delete-button', 'n_clicks'),
        Input('danger-danger-provider', 'submit_n_clicks'),
        State('dropdown1', 'value'),
        State('rating-dd', 'value'),
    )
    def update_new_values(n_clicks,submitted_n_clicks, machine, rating):
        if submitted_n_clicks is None or submitted_n_clicks == 0:
            return False,None
        try:
            db = client['configurationfiles']
            current_collection = db['current_usl_lsl']
            pulse_collection = db['pulse_usl_lsl']
            machine_collection = collection_mapping2['machines']

            if machine and rating is None:
                complete_machine_name = "!01" + '001' + ':' + 'm'
            elif machine is None:
                complete_machine_name = "!01" + rating[0:3] + ':' + 'm'
            else:
                complete_machine_name = str(machine) + rating[0:3] + ':' + 'm'
            machine_name = complete_machine_name

            current_data = current_collection.find_one({"machine_name": machine_name, "rating(AMP)": rating[5:-1]})
            pulse_data = pulse_collection.find_one({"machine_name": machine_name, "rating(AMP)": rating[5:-1]})
            machine_data = machine_collection.find_one({"machine_name": machine_name, "rating(AMP)": rating[5:-1]})

            # Construct change records
            current_change_data = {
                "timestamp": datetime.now(),
                "machine_name": machine_name,
                "rating": rating,
                'action': 'INACTIVE',
            }

            if current_data:
                current_collection.update_one({"_id": current_data["_id"]}, {"$set": {"status": "INACTIVE"}})

            if pulse_data:
                pulse_collection.update_one({"_id": pulse_data["_id"]}, {"$set": {"status": "INACTIVE"}})

            if machine_data:
                machine_collection.update_one({"_id": machine_data["_id"]}, {"$set": {"status": "INACTIVE"}})

            current_change_collection = db['configuration_history']
            current_change_collection.insert_one(current_change_data)
            machine = None
            return True, machine
        except Exception as e:
            return False, None


    @app.callback(
        Output('alert-auto', 'is_open'),
        Input('update-button', 'n_clicks'),
        State('dropdown1', 'value'),
        State('rating-dd', 'value'),
        State('ud_usl_input', 'value'),
        State('ud_lsl_input', 'value'),
        State('ud_usl_input2', 'value'),
        State('ud_lsl_input2', 'value'),
        State('change-current-stroke', 'value'),
    )
    def update_new_values(n_clicks, machine, rating, ud_cur_usl, ud_cur_lsl, ud_pulse_usl, ud_pulse_lsl,current_stroke):
        if n_clicks is None or n_clicks == 0:
            return False
        try:
            current_collection = collection_mapping2['config_data_current']
            pulse_collection = collection_mapping2['config_data_pulse']
            change_records_collection = collection_mapping2['configuration_history']

            if machine is None:
                complete_machine_name = "!01" + rating[0:3] + ':' + 'm'
            else:
                complete_machine_name = str(machine) + rating[0:3] + ':' + 'm'
            machine_name = complete_machine_name

            filter_condition = {"machine_name": machine_name, "rating(AMP)": rating[5:-1]}

            change_data = {
                "timestamp": datetime.now(),
                "machine_name": machine_name,
                "rating": rating,
                'action':'UPDATE',
                "changes": []
            }

            def get_old_value(collection, filter_condition, field):
                document = collection.find_one(filter_condition)
                return document.get(field) if document else None

            current_field_mapping = {
                "ud_cur_usl": "usl",
                "ud_cur_lsl": "lsl",
                "current_stroke": "current_change_stroke"
            }

            pulse_field_mapping = {
                "ud_pulse_usl": "usl",
                "ud_pulse_lsl": "lsl",
                "current_stroke": "current_change_stroke"
            }

            if any((ud_cur_usl, ud_cur_lsl, current_stroke is not None)):
                current_update_data = {}
                current_update_data["$set"] = {}
                for variable_name, field_name in current_field_mapping.items():
                    old_value = get_old_value(current_collection, filter_condition, field_name)
                    new_value = locals().get(variable_name)

                    if new_value is not None:
                        current_update_data["$set"][field_name] = str(new_value)
                        change_data["changes"].append(
                            {"field": field_name, "old_value":  old_value, "new_value": str(new_value)})

                current_collection.update_one(filter_condition, current_update_data)

            if any((ud_pulse_usl, ud_pulse_lsl, current_stroke is not None)):
                pulse_update_data = {}
                pulse_update_data["$set"] = {}
                for variable_name, field_name in pulse_field_mapping.items():
                    old_value = get_old_value(pulse_collection, filter_condition, field_name)

                    new_value = locals().get(variable_name)
                    if new_value is not None:
                        pulse_update_data["$set"][field_name] = str(new_value)
                        change_data["changes"].append(
                            {"field": field_name, "old_value": old_value, "new_value": str(new_value)})

                pulse_collection.update_one(filter_condition, pulse_update_data)

            change_records_collection.insert_one(change_data)

            return True

        except Exception as e:
            return False



    ####### Summary Dashboard Screens Callbacks ########
    @app.callback(
        Output('date-time', 'children'),
        Input('interval-dashboards', 'n_intervals')
    )
    def update_time(n):
        current_datetime = datetime.now()
        date_time_str = current_datetime.strftime('%d/%m/%Y %H:%M:%S')
        date = 'Date: '
        date_color = html.Span(f'{date_time_str}', className='date-time-color')
        return [html.Div([date, date_color])]

    summary_df = upadte_summarycpcpk(summary_collection)

    callbacks = {}
    current_rating = num_machines

    def generate_machine_callback(machine_id):

        @app.callback(
            Output(f'current_sample_size_label-{machine_id}', 'children'),
            Output(f'current-rating-id-{machine_id}', 'children'),
            Output(f'cp_label-{machine_id}', 'children'),
            Output(f'cpk_label-{machine_id}', 'children'),
            Output(f'current_last_refresh_label-{machine_id}', 'children'),
            Input('interval-dashboards', 'n_intervals'),
            Input(f'current-rating-link-{machine_id}', 'n_clicks'),
        )
        def machine_dashboard_tab_update(n, n_clicks, machine_id=machine_id):
            global num_machines

            if n_clicks:
                pass
            new_current_rating = pick_machines(collection_mapping)
            current_rating = num_machines
            summary_df = upadte_summarycpcpk(summary_collection)

            specific_machine_data = None
            if current_rating == new_current_rating:
                for machine in current_rating:
                    if machine == machine_id:
                        specific_machine_data = machine
                        break
            elif current_rating != new_current_rating:
                for machine in current_rating:
                    if machine_id[:3] == machine[:3]:
                        specific_machine_data = machine
                        break

            if specific_machine_data:
                machine = specific_machine_data[0:3]
                df = summary_df[summary_df['machine_name'].str[:3] == machine]
                sample_size = df['sample_size'].iloc[0]
                last_refresh = df['last_refresh'].iloc[0]
                last_machine_name = df['machine_name'].iloc[0]
                current_cp = df['current_cp'].iloc[0]
                current_cpk = df['current_cpk'].iloc[0]

                current_cp_value = np.round(current_cp, 3)
                current_cpk_value = np.round(current_cpk, 3)
                cp_current_color = current_cp_update_color(current_cp_value)
                cpk_current_color = current_cpk_update_color(current_cpk_value)
                sample_size_label = f'Sample Size: {sample_size}'
                last_refresh_label = f'Updated At: '
                cp_current_label = 'Cp: '
                cpk_current_label = 'Cpk: '
                if np.isnan(current_cp_value) or int(current_cp_value) > 100 or int(current_cp_value) < 0:
                    current_cp_value = "NA"
                if np.isnan(current_cpk_value) or int(current_cpk_value) > 100 or int(current_cpk_value) < 0:
                    current_cpk_value = "NA"
                CP_current_value = html.Span(f'{current_cp_value}', style={'color': cp_current_color})
                CPK_current_value = html.Span(f'{current_cpk_value}', style={'color': cpk_current_color})
                refresh_font = html.Span(f'{last_refresh.strftime("%d/%m/%Y %H:%M")}', className='refresh_at_label')

                return [sample_size_label, last_machine_name,
                        html.Div([cp_current_label, CP_current_value]),
                        html.Div([cpk_current_label, CPK_current_value]),
                        html.Div([last_refresh_label, refresh_font]),
                        ]
            else:
                return [html.Div("Machine not found")]

        callbacks[machine_id] = machine_dashboard_tab_update

    for machine_id in num_machines:
        generate_machine_callback(machine_id)

    callbacks = {}
    current_rating = num_machines

    def generate_machine_callback(machine_id):

        @app.callback(
            Output(f'pulse_sample_size_label-{machine_id}', 'children'),
            Output(f'pulse-rating-id-{machine_id}', 'children'),
            Output(f'cp2_label-{machine_id}', 'children'),
            Output(f'cpk2_label-{machine_id}', 'children'),
            Output(f'pulse_last_refresh_label-{machine_id}', 'children'),
            Input('interval-dashboards', 'n_intervals'),
            Input(f'pulse-rating-link-{machine_id}', 'n_clicks'),

        )
        def machine_dashboard_tab_update(n, n_clicks, machine_id=machine_id):
            global num_machines

            if n_clicks:
                pass
            new_current_rating = pick_machines(collection_mapping)
            current_rating = num_machines
            summary_df = upadte_summarycpcpk(summary_collection)

            specific_machine_data = None
            if current_rating == new_current_rating:
                for machine in current_rating:
                    if machine == machine_id:
                        specific_machine_data = machine
                        break
            elif current_rating != new_current_rating:
                for machine in current_rating:
                    if machine_id[:3] == machine[:3]:
                        specific_machine_data = machine
                        break

            if specific_machine_data:
                machine = specific_machine_data[0:3]
                df = summary_df[summary_df['machine_name'].str[:3] == machine]
                sample_size = df['sample_size'].iloc[0]
                last_refresh = df['last_refresh'].iloc[0]
                last_machine_name = df['machine_name'].iloc[0]
                pulse_cp = df['pulse_cp'].iloc[0]
                pulse_cpk = df['pulse_cpk'].iloc[0]

                pulse_cp_value = np.round(pulse_cp, 3)
                pulse_cpk_value = np.round(pulse_cpk, 3)

                sample_size_label = f'Sample Size: {sample_size}'
                last_refresh_label = f'Updated At: '

                cp_pulse_color = current_cp_update_color(pulse_cp_value)
                cpk_pulse_color = current_cpk_update_color(pulse_cpk_value)
                cp_pulse_label = 'Cp: '
                cpk_pulse_label = 'Cpk: '
                if np.isnan(pulse_cp_value) or int(pulse_cp_value) > 100 or int(pulse_cp_value) < 0:
                    pulse_cp_value = "NA"
                if np.isnan(pulse_cpk_value) or int(pulse_cpk_value) > 100 or int(pulse_cpk_value) < 0:
                    pulse_cpk_value = "NA"
                CP_pulse_value = html.Span(f'{pulse_cp_value}', style={'color': cp_pulse_color})
                CPK_pulse_value = html.Span(f'{pulse_cpk_value}', style={'color': cpk_pulse_color})
                refresh_font = html.Span(f'{last_refresh.strftime("%d/%m/%Y %H:%M")}', className='refresh_at_label')

                return [sample_size_label, last_machine_name,
                        html.Div([cp_pulse_label, CP_pulse_value]),
                        html.Div([cpk_pulse_label, CPK_pulse_value]),
                        html.Div([last_refresh_label, refresh_font])
                        ]
            else:
                return [html.Div("Machine not found")]

        callbacks[machine_id] = machine_dashboard_tab_update

    for machine_id in num_machines:
        generate_machine_callback(machine_id)

    @app.callback(
        [Output('selected-machine-id', 'data'),
            Output('tabs', 'value')],
        [*[Input(f'current-rating-link-{current_machine_id}', 'n_clicks') for current_machine_id in num_machines],
        *[Input(f'pulse-rating-link-{pulse_machine_id}', 'n_clicks') for pulse_machine_id in num_machines]]
    )
    def switch_tabs(*n_clicks_list):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        prop_id = ctx.triggered[0]['prop_id']
        machine_id = prop_id.split('-')[-1].split('.')[0]
        n_clicks = ctx.triggered[0]['value']
        return (machine_id, 'Control charts Dashboard' if n_clicks > 0 else 'Dashboards')

    ####### Control Chart Dashboard Screens Callbacks ########
    @app.callback(
        Output('current-chart-table', 'data'),
        Output('pulse-chart-table', 'data'),
        Output("run-chart", "figure"),
        Output("bell-curve", "figure"),
        Output("run-chart-two", "figure"),
        Output("bell-curve-two", "figure"),
        Output("cp-led", "value"),
        Output("cpk-led", "value"),
        Output("current-cp-condition", "children"),
        Output("current-cpk-condition", "children"),
        Output("cp-led2", "value"),
        Output("cpk-led2", "value"),
        Output("pulse-cp-condition", "children"),
        Output("pulse-cpk-condition", "children"),
        [Input('interval-dashboards', 'n_intervals')],
        [Input('selected-machine-id', 'data')],
    )
    def update_charts(n_clicks, machineid):
        df = None
        machine = None
        if n_clicks and n_clicks > 0:
            machine_identifier = machineid[:3]
            collection = collection_mapping.get(machine_identifier)
            if collection is None:
                print(f"No collection found for machine identifier: {machine_identifier}")
                return

            machine_details = Dashboards(machine_identifier, collection_mapping)
            df, last_records_df = machine_details.machine()

            df = df[
                ['machine_name', 'current', 'pulse', 'strokes', 'current_cp', 'current_cpk',
                 'pulse_cp', 'pulse_cpk', 'rating']]
            last = last_records_df
            machine_name = last['machine_name'][0]
            df_new = df[df['machine_name'] == machine_name]
            df = df_new.drop_duplicates(subset='strokes', keep='first')
            df = df.reset_index(drop=True)
            df.replace('', np.nan, inplace=True)
            numeric_columns = ['current_cp', 'current_cpk', 'pulse_cp', 'pulse_cpk']
            df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
            filtered_df = df.dropna(subset=numeric_columns, how='all')

            if filtered_df.empty:
                filtered_df = df
                df = filtered_df
            else:
                filtered_df = pd.concat([df.iloc[:1], filtered_df])
                df = filtered_df

            (current_usl, current_lsl, current_mean, current_rating_detail, current_operation,
             pulse_usl, pulse_lsl, pulse_mean, pulse_rating_detail, pulse_operation) = update_usl_lsl(df, collection_mapping2)

            current_usl = float(current_usl)
            current_lsl = float(current_lsl)
            current_rating = str(current_rating_detail)
            pulse_usl = float(pulse_usl)
            pulse_lsl = float(pulse_lsl)
            pulse_rating = str(pulse_rating_detail)

        filtered_values = df.reset_index(drop=True)
        current_value = pd.to_numeric(filtered_values['current'])
        pulse_value = pd.to_numeric(filtered_values['pulse'])

        mean_current_value = np.mean(current_value)
        std_current_value = np.std(current_value, ddof=1)


        machine_rating = last['rating'][0]
        current_operation = str(current_operation)
        current_rating = machine_rating +'('+str(current_rating)+')'
        current_mean = [current_usl, current_lsl]
        mean_current = round(np.mean(current_mean), 2)
        xbar_current = round(np.mean(current_value), 2)
        std_current = round(np.std(current_value, ddof=1), 2)
        c_min_value = round(np.min(current_value), 2)
        c_max_value = round(np.max(current_value), 2)
        c_r_diff = round(c_max_value - c_min_value, 2)

        current_table = [
            {'Machine Name': machine_name,'Operation Name':current_operation, 'Rating': current_rating,
             'Sample Size': len(current_value),'Min Cp': 1.33, 'Min Cpk': 1.0,'USL': current_usl, 'LSL': current_lsl,
             'Mean': mean_current,'STD': std_current,'xbar': xbar_current,'Min': c_min_value, 'Max': c_max_value,
             'R(Diff)': c_r_diff}
        ]

        mean_pulse_value = np.mean(pulse_value)
        std_pulse_value = np.std(pulse_value, ddof=1)

        pulse_rating = machine_rating+'('+str(pulse_rating)+')'

        pulse_operation = str(pulse_operation)
        pulse_mean = [pulse_usl, pulse_lsl]
        mean_pulse = round(np.mean(pulse_mean), 2)
        xbar_pulse = round(np.mean(pulse_value), 2)
        std_pulse = round(np.std(pulse_value, ddof=1), 2)
        c_min_pulse_value = round(np.min(pulse_value), 2)
        c_max_pulse_value = round(np.max(pulse_value), 2)
        c_r_pulse_diff = round(c_max_pulse_value - c_min_pulse_value, 2)

        pulse_table = [
            {'Machine Name': machine_name, 'Operation Name':pulse_operation,'Rating': pulse_rating,
             'Sample Size': len(pulse_value),'Min Cp': 1.33, 'Min Cpk': 1.0,'USL': pulse_usl, 'LSL': pulse_lsl,
             'Mean': mean_pulse,'STD': std_pulse,'xbar': xbar_pulse,'Min': c_min_pulse_value,
             'Max': c_max_pulse_value,'R(Diff)': c_r_pulse_diff}
        ]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=current_value.index, y=current_value,
                                 mode='lines', name='<b>Current</b>', line=dict(color='#66FF00')))
        fig.add_trace(go.Scatter(x=current_value.index, y=[current_usl] * len(current_value),
                                 mode='lines', name='<b>USL</b>', line=dict(dash='dash', width=1,color='#FF0000')))
        fig.add_trace(go.Scatter(x=current_value.index, y=[mean_current] * len(current_value),
                                 mode='lines', name='<b>Mean</b>', line=dict(dash='dash', width=1, color='#00B000')))
        fig.add_trace(go.Scatter(x=current_value.index, y=[current_lsl] * len(current_value),
                                 mode='lines', name='<b>LSL</b>', line=dict(dash='dash', width=1,color='#FF0000')))

        fig.update_layout(title='<b>Run Chart For Welding Current</b>',
                          xaxis_title='<b>Number of Strokes</b>',
                          yaxis_title='<b>Current (kA)</b>',
                          xaxis=dict(showgrid=False,tickprefix='<b>',tickfont=dict(color='black')),
                          yaxis=dict(showgrid=False,tickprefix='<b>',tickfont=dict(color='black')),
                          uirevision='welding_current',

                          )

        bell_curve_data = np.random.normal(mean_current_value, std_current_value, 1000)

        histogram_trace = go.Histogram(x=bell_curve_data, nbinsx=30, name='<b>Bell Curve</b>', histnorm='probability density',
                                       nbinsy=20, marker=dict(color='#66FF00'))

        x_values = np.linspace(current_value.min(), current_value.max(), 1000)
        y_values = stats.norm.pdf(x_values, mean_current_value, std_current_value)
        bell_curve_trace = go.Scatter(x=x_values, y=y_values, mode='lines', name='<b>probability</b>',
                                      line=dict(color='#1190e5'))
        bell_usl_line = go.Scatter(x=[current_usl, current_usl], y=[0, np.max(y_values)],
                                   mode='lines', name='<b>USL</b>', line=dict(dash='dash', width=1,color='#FF0000'))
        bell_lsl_line = go.Scatter(x=[current_lsl, current_lsl], y=[0, np.max(y_values)],
                                   mode='lines', name='<b>LSL</b>', line=dict(dash='dash', width=1,color='#FF0000'))
        bell_mean_line = go.Scatter(x=[mean_current_value, mean_current_value], y=[0, np.max(y_values)],
                                   mode='lines', name='<b>Mean</b>', line=dict(dash='dash', width=1, color='#00B000'))

        bell_curve_layout = go.Layout(title='<b>Bell Curve for welding Current</b>',
                                      xaxis=dict(title='<b>Value</b>', showgrid=False
                                                 ,tickprefix='<b>',tickfont=dict(color='black')),
                                      yaxis=dict(title='<b>Probability Density</b>', showgrid=False
                                                 ,tickprefix='<b>',tickfont=dict(color='black')),
                                      showlegend=True,
                                      uirevision='welding_current',

                                      )

        bell_curve_with_lines = [histogram_trace, bell_curve_trace, bell_usl_line,bell_mean_line, bell_lsl_line]
        bell_curve_figure = go.Figure(
            data=bell_curve_with_lines, layout=bell_curve_layout
        )

        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(x=pulse_value.index, y=pulse_value, mode='lines', name='<b>Pulse</b>', line=dict(color='#66FF00')))
        fig2.add_trace(go.Scatter(x=pulse_value.index, y=[pulse_usl] * len(pulse_value),
                                  mode='lines', name='<b>USL</b>', line=dict(dash='dash', width=1,color='#FF0000')))
        fig2.add_trace(go.Scatter(x=pulse_value.index, y=[mean_pulse] * len(pulse_value),
                                  mode='lines', name='<b>Mean</b>', line=dict(dash='dash', width=1, color='#00B000')))
        fig2.add_trace(go.Scatter(x=pulse_value.index, y=[pulse_lsl] * len(pulse_value),
                                  mode='lines', name='<b>LSL</b>', line=dict(dash='dash', width=1, color='#FF0000')))

        fig2.update_layout(title='<b>Run Chart For Pulse Value</b>',
                           xaxis_title='<b>Number of Strokes</b>',
                           yaxis_title='<b>Pulse (kA)</b>',
                           xaxis=dict(showgrid=False,tickprefix='<b>',tickfont=dict(color='black')),
                           yaxis=dict(showgrid=False,tickprefix='<b>',tickfont=dict(color='black')),
                           uirevision='pulse_value',

                           )

        bell_curve_data2 = np.random.normal(mean_pulse_value, std_pulse_value, 1000)

        histogram_trace2 = go.Histogram(x=bell_curve_data2, nbinsx=30, name='<b>Bell Curve</b>',
                                        histnorm='probability density',
                                        nbinsy=20, marker=dict(color='#66FF00'))

        x_values2 = np.linspace(pulse_value.min(), pulse_value.max(), 1000)
        y_values2 = stats.norm.pdf(x_values2, mean_pulse_value, std_pulse_value)
        bell_curve_trace2 = go.Scatter(x=x_values2, y=y_values2, mode='lines', name='<b>probability</b>',
                                       line=dict(color='#1190e5'))
        bell_usl_line2 = go.Scatter(x=[pulse_usl, pulse_usl], y=[0, np.max(y_values2)],
                                    mode='lines', name='<b>USL</b>', line=dict(dash='dash', width=1,color='#FF0000'))
        bell_mean_line2 = go.Scatter(x=[mean_pulse_value, mean_pulse_value], y=[0, np.max(y_values2)],
                                    mode='lines', name='<b>Mean</b>', line=dict(dash='dash', width=1, color='#00B000'))
        bell_lsl_line2 = go.Scatter(x=[pulse_lsl, pulse_lsl], y=[0, np.max(y_values2)],
                                    mode='lines', name='<b>LSL</b>', line=dict(dash='dash', width=1, color='#FF0000'))

        bell_curve_layout2 = go.Layout(title='<b>Bell Curve for Pulse Value</b>',
                                       xaxis=dict(title='<b>Value</b>', showgrid=False
                                                  ,tickprefix='<b>',tickfont=dict(color='black')),
                                       yaxis=dict(title='<b>Probability Density</b>', showgrid=False
                                                  ,tickprefix='<b>',tickfont=dict(color='black')),
                                       showlegend=True,
                                       uirevision='pulse_value',

                                       )

        bell_curve_with_lines2 = [histogram_trace2, bell_curve_trace2, bell_usl_line2,bell_mean_line2, bell_lsl_line2]
        bell_curve_figure2 = go.Figure(
            data=bell_curve_with_lines2, layout=bell_curve_layout2
        )

        current_cp = pd.to_numeric(df['current_cp'].iloc[-1], errors='coerce')
        current_cpk = pd.to_numeric(df['current_cpk'].iloc[-1], errors='coerce')
        pulse_cp = pd.to_numeric(df['pulse_cp'].iloc[-1], errors='coerce')
        pulse_cpk = pd.to_numeric(df['pulse_cpk'].iloc[-1], errors='coerce')

        if np.isnan(current_cp) or current_cp > 100 or current_cp < 0:
            current_cp_value = 0
        else:
            current_cp_value = np.round(current_cp, 3)

        if np.isnan(current_cpk) or current_cpk > 100 or current_cpk < 0:
            current_cpk_value = 0
        else:
            current_cpk_value = np.round(current_cpk, 3)

        current_cpcondition,current_cp_color = calculate_condition_cp(current_cp_value)
        current_cpkcondition,current_cpk_color = calculate_condition_cpk(current_cpk_value)

        current_cp_condition = html.Span(f'{current_cpcondition}',style={'color':current_cp_color})
        current_cpk_condition = html.Span(f'{current_cpkcondition}',style={'color':current_cpk_color})

        if np.isnan(pulse_cp) or pulse_cp > 100 or pulse_cp < 0:
            pulse_cp_value = 0
        else:
            pulse_cp_value = np.round(pulse_cp, 3)

        if np.isnan(pulse_cpk) or pulse_cpk > 100 or pulse_cpk < 0:
            pulse_cpk_value = 0
        else:
            pulse_cpk_value = np.round(pulse_cpk, 3)

        pulse_cpcondition,pulse_cp_color = calculate_condition_cp(pulse_cp_value)
        pulse_cpkcondition,pulse_cpk_color = calculate_condition_cpk(pulse_cpk_value)

        pulse_cp_condition = html.Span(f'{pulse_cpcondition}', style={'color': pulse_cp_color})
        pulse_cpk_condition = html.Span(f'{pulse_cpkcondition}', style={'color': pulse_cpk_color})

        return (current_table, pulse_table,fig, bell_curve_figure, fig2, bell_curve_figure2, current_cp_value,
                current_cpk_value, current_cp_condition, current_cpk_condition, pulse_cp_value, pulse_cpk_value,
                pulse_cp_condition,pulse_cpk_condition)

    @app.callback(
        Output('cp-led', 'color'),
        Input('cp-led', 'value'),
    )
    def current_cp_update_color(cp):
        if cp >= 2:
            return '#008000'
        elif 1.33 <= cp < 2:
            return '#FF7518'
        else:
            return '#FF0000'

    @app.callback(
        Output('cpk-led', 'color'),
        Input('cpk-led', 'value')
    )
    def current_cpk_update_color(cpk):
        if cpk >= 1.33:
            return '#008000'
        elif 1 <= cpk < 1.33:
            return '#FF7518'
        else:
            return '#FF0000'

    @app.callback(
        Output('cp-led2', 'color'),
        Input('cp-led2', 'value'),
    )
    def current_cp_update_color(cp):
        if cp >= 2:
            return '#008000'
        elif 1.33 <= cp < 2:
            return '#FF7518'
        else:
            return '#FF0000'

    @app.callback(
        Output('cpk-led2', 'color'),
        Input('cpk-led2', 'value')
    )
    def current_cpk_update_color(cpk):
        if cpk >= 1.33:
            return '#008000'
        elif 1 <= cpk < 1.33:
            return '#FF7518'
        else:
            return '#FF0000'

    ####### Reports Screen Callbacks ########
    @app.callback(
        Output('report-rating', 'options'),
        [Input('report-machine', 'value')],
    )
    def update_ratings(machine_name):
        uni_ratings = []
        if machine_name is not None:
            uni_ratings = ratings(collection_mapping2, machine_name)
        return uni_ratings

    @app.callback(
        Output('datatable', 'children'),
        [Input('submit-button', 'n_clicks')],
        [State('report-machine', 'value'),
         State('report-rating', 'value'),
         State('start-date', 'date'),
         State('end-date', 'date')]
    )
    def update(n_clicks, machine, rating, start_date, end_date):
        machine_name = machine
        ratings = rating
        data = None
        data1 = None
        if n_clicks < 0:
            return []
        if n_clicks > 0:
            hist_collection = collection_mapping.get(machine_name)
            if machine_name is not None and start_date is None and end_date is None and ratings is None:
                data1 = pd.DataFrame(list(hist_collection.find({'machine_name': {'$regex': f'^{machine_name}'}})))
                data = data1
            elif machine_name is not None and start_date is None and end_date is None and len(ratings) == 0:
                data1 = pd.DataFrame(list(hist_collection.find({'machine_name': {'$regex': f'^{machine_name}'}})))
                data = data1

            #### Rating wise report ####
            elif machine_name is not None and ratings and start_date is None and end_date is None:
                complete_machine_names = []
                if ratings:
                    for rating_item in ratings:
                        complete_machine_name = machine_name + rating_item[0:3] + ':' + 'm'
                        complete_machine_names.append(complete_machine_name)

                if not complete_machine_names:
                    data = pd.DataFrame(list(hist_collection.find({'machine_name': {'$regex': f'^{machine_name}'}})))
                else:
                    query = {
                        'machine_name': {'$in': complete_machine_names}
                    }
                    data = pd.DataFrame(list(hist_collection.find(query)))
                    if ratings:
                        data['Rating'] = ratings[0][0]
                data = data.reset_index(drop=True)

            elif machine_name is not None and ratings is not None and len(
                    ratings) != 0 and start_date is not None and end_date is not None:

                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                complete_machine_names = [machine_name + rating_item[0:3] + ':m' for rating_item in ratings]

                query = {
                    'machine_name': {'$in': complete_machine_names},
                    'created_date': {'$gte': start_date, '$lte': end_date}
                }
                data = pd.DataFrame(list(hist_collection.find(query)))
                data = data.reset_index(drop=True)


            #### Machine wise with start and end date ####
            elif machine_name is not None and start_date is not None and end_date is not None and ratings is None:
                if machine_name and start_date and end_date:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d')
                    end_date = datetime.strptime(end_date, '%Y-%m-%d')
                    query = {
                        'machine_name': {'$regex': f'^{machine_name}'},
                        'created_date': {'$gte': start_date, '$lte': end_date}
                    }
                    data1 = pd.DataFrame(list(hist_collection.find(query)))
                    data = data1.reset_index(drop=True)

            elif machine_name is not None and start_date is not None and end_date is not None and len(ratings) == 0:
                if machine_name and start_date and end_date:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d')
                    end_date = datetime.strptime(end_date, '%Y-%m-%d')
                    query = {
                        'machine_name': {'$regex': f'^{machine_name}'},
                        'created_date': {'$gte': start_date, '$lte': end_date}
                    }
                    data1 = pd.DataFrame(list(hist_collection.find(query)))
                    data = data1.reset_index(drop=True)


        if data is not None:
            data1 = operation_name(collection_mapping2, machine_name)

            df = data
            df['current_cp'] = pd.to_numeric(df['current_cp'], errors='coerce')
            df['current_cpk'] = pd.to_numeric(df['current_cpk'], errors='coerce')
            df_size = df
            df = df.dropna(subset=['current_cp'])
            non_zero_df = df[(df['current_cp'] != 0) & (df['current_cpk'] != 0)].copy()

            last_non_zero_values_df = non_zero_df.groupby('machine_name').last().reset_index()
            group_lengths = df_size.groupby('machine_name').size().reset_index(name='group_length')
            last_non_zero_values_df = pd.DataFrame(last_non_zero_values_df)
            group_lengths_df = pd.DataFrame(group_lengths)

            result_df = pd.merge(last_non_zero_values_df, group_lengths_df, on='machine_name')
            report_df = result_df[['machine_name', 'group_length', 'current_cp', 'current_cpk']]
            report_data = pd.merge(result_df, data1, on='machine_name', how='left')
            report_data['From Date'] = start_date
            report_data['To Date'] = end_date
            report_data = report_data[[
                'machine_name', 'operation', 'ratings_schedule', 'group_length', 'usl', 'mean', 'lsl', 'From Date',
                'To Date','current_cp', 'current_cpk']]
            report_data = report_data.rename(columns={
                'machine_name': 'Machine Name',
                'operation': 'Operation Name',
                'ratings_schedule': 'Rating',
                'group_length': 'No. of Strokes',
                'usl': 'USL',
                'mean': 'Mean',
                'lsl': 'LSL',
                'current_cp': 'Cp Current',
                'current_cpk': 'Cpk Current',
            })
            overall_aggregates = {
                'Rating': 'TOTAL',
                'To Date': 'OVERALL',
                'Cp Current': np.round(report_data['Cp Current'].mean(),3),
                'Cpk Current': np.round(report_data['Cpk Current'].mean(),3),
                'No. of Strokes': report_data['No. of Strokes'].sum()
            }

            report_data = pd.concat([report_data, pd.DataFrame([overall_aggregates])], ignore_index=True)

            datatable = dash_table.DataTable(
                columns=[{'name': col, 'id': col} for col in report_data.columns],
                data=report_data.to_dict('records'),
                page_size=10,
                page_action='native',
                fixed_rows={'headers': True},
                export_format='xlsx',
                export_headers='display',
                merge_duplicate_headers=True,
                style_cell={'minWidth': '65px', 'maxWidth': '100px'},  # Adjust column width
                style_header={'minWidth': '65px', 'maxWidth': '100px'}  # Adjust header width
            )
            return datatable
        return []


    @app.callback(
        Output("barChart", "figure"),
        Output("barChart2", "figure"),
        Input('datatable', 'children'),
        State('submit-button','n_clicks')
    )
    def update_bar_chart(data,n_clicks):
        if n_clicks == 0:
            fig1 = go.Figure()
            fig2 = go.Figure()
            return  fig1, fig2
        df = data['props']['data']
        df = pd.DataFrame(df)
        df = df.iloc[:-1]
        name  =df['Machine Name'].iloc[0][:3]
        df['Min CP'] = 1.33
        df['Min CPK'] = 1.0

        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=[str(rating)[:3] for rating in df['Rating']],
                             y=df["Min CP"],
                             name='<b>Cp(Min)</b>',
                             marker_color='#1190e5',
                              text=df["Min CP"],  # Set the text attribute to the 'CPK Current' values
                              textposition='outside',

                             ))
        fig1.add_trace(go.Bar(x=[str(rating)[:3] for rating in df['Rating']],
                             y=df["Cp Current"],
                             name='<b>Actual(Cp)</b>',
                             marker_color='#f9ba2d',
                              text=df["Cp Current"],  # Set the text attribute to the 'CPK Current' values
                              textposition='outside',
                             ))

        fig1.update_layout(
            title=f"<b>Machine Name: {name} - Min Cp</b>",
            xaxis_tickfont_size=12,
            xaxis=dict(
                title='<b>Rating</b>',
                titlefont_size=16,
                tickfont_size=12,
                tickfont_color='black',
                tickprefix='<b>'
            ),
            yaxis=dict(
                title='<b>Cp</b>',
                titlefont_size=16,
                tickfont_size=12,
                tickfont_color='black',
                tickprefix='<b>'
            ),
            barmode='group',
            bargap=0.3,
            bargroupgap=0.1,
            margin=dict(l=50, r=50, t=100, b=50)
        )

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=[str(rating)[:3] for rating in df['Rating']],
                              y=df["Min CPK"],
                              name='<b>Cpk(Min)</b>',
                              marker_color='#1190e5',
                              text=df["Min CPK"],
                              textposition='outside'
                              ))
        fig2.add_trace(go.Bar(x=[str(rating)[:3] for rating in df['Rating']],
                              y=df["Cpk Current"],
                              name='<b>Actual(Cpk)</b>',
                              marker_color='#f9ba2d',
                              text=df["Cpk Current"],
                              textposition='outside'
                              ))

        fig2.update_layout(
            title=f"<b>Machine Name: {name} - Min Cpk</b>",
            xaxis_tickfont_size=12,
            xaxis=dict(
                title='<b>Rating</b>',
                titlefont_size=16,
                tickfont_size=12,
                tickfont_color='black',
                tickprefix='<b>'
            ),
            yaxis=dict(
                title='<b>Cpk</b>',
                titlefont_size=16,
                tickfont_size=12,
                tickfont_color='black',
                tickprefix='<b>'
            ),

            barmode='group',
            bargap=0.3,
            bargroupgap=0.1,
            margin=dict(l=50, r=50, t=100, b=50)
        )
        return fig1,fig2

    @app.callback(
        Output('submit-button', 'n_clicks'),
        Input('clear-button', 'n_clicks'),
    )
    def reset_submit_button_clicks(clear_clicks):
        if clear_clicks and clear_clicks > 0:
            return 0
        else:
            raise dash.exceptions.PreventUpdate

    @app.callback(
        Output('report-machine', 'value'),
        Output('start-date','date'),
        Output('end-date', 'date'),
        Input('clear-button', 'n_clicks'),
    )
    def clear_selections(clear_clicks):
        if clear_clicks and clear_clicks > 0:
            machine_value = None
            start_date = None
            end_date = None
            return machine_value,start_date,end_date
        else:
            return dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        [Output('ud_usl_input', 'value'),
         Output('ud_lsl_input', 'value'),
         Output('ud_usl_input2', 'value'),
         Output('ud_lsl_input2', 'value'),
         Output('change-current-stroke', 'value')],
        [Input('specs-clear-button', 'n_clicks')],
    )
    def clear_input_fields(n_clicks):
        if n_clicks is None:
            return [None] * 5

        return [None] * 5

    @app.callback(
        [
            Output('alert-add', 'is_open'),
            Output('alert-add', 'children'),
            Output('machine-input', 'value'),
            Output('operation-input', 'value'),
            Output('rating-amp-input', 'value'),
            Output('current-usl-input', 'value'),
            Output('current-lsl-input', 'value'),
            Output('current-mean-input', 'value'),
            Output('pulse-usl-input', 'value'),
            Output('pulse-lsl-input', 'value'),
            Output('pulse-mean-input', 'value')
        ],
        [
            Input('add-delete-button', 'n_clicks')
        ],
        [
            State('machine-input', 'value'),
            State('operation-input', 'value'),
            State('rating-amp-input', 'value'),
            State('current-usl-input', 'value'),
            State('current-lsl-input', 'value'),
            State('current-mean-input', 'value'),
            State('pulse-usl-input', 'value'),
            State('pulse-lsl-input', 'value'),
            State('pulse-mean-input', 'value'),
            Input('add-clear-button', 'n_clicks')
        ]
    )
    def add_rating(n_clicks, machine, operation, rating_amp, current_usl, current_lsl, current_mean,
                   pulse_usl, pulse_lsl, pulse_mean, clear_n_clicks):
        if clear_n_clicks > 0:

            return [False, None] + [None] * 9

        if n_clicks is None or n_clicks == 0:
            raise PreventUpdate

        current_collection = collection_mapping2['config_data_current']
        pulse_collection = collection_mapping2['config_data_pulse']
        machine_collection = collection_mapping2['machines']
        change_records_collection = collection_mapping2['configuration_history']
        machine_name = machine
        operation_name = operation
        rating_amp = rating_amp
        current_usl = current_usl
        current_lsl = current_lsl
        current_mean = current_mean
        pulse_usl = pulse_usl
        pulse_lsl = pulse_lsl
        pulse_mean = pulse_mean

        current_data = {
            "machine_name": machine_name, "operation": operation_name,
            "rating(AMP)": rating_amp, "lsl": current_lsl, "mean": current_mean, "usl": current_usl,
        }
        machine_data = {"machine_name": machine_name, "rating(AMP)": rating_amp}
        pulse_data = {
            "machine_name": machine_name, "operation": operation_name,
            "rating(AMP)": rating_amp, "usl": pulse_usl,
            "lsl": pulse_lsl, "mean": pulse_mean
        }
        change_data = {
            "timestamp": datetime.now(),
            "action": 'CREATE',
            "machine_name": machine_name,
            "operation": operation_name,
            "rating(AMP)": rating_amp,"current_usl": current_usl,
            "current_lsl": current_lsl,"current_mean": current_mean,
            "pulse_usl": pulse_usl,"pulse_lsl": pulse_lsl,
            "pulse_mean": pulse_mean
        }
        change_data2 = {
            "timestamp": datetime.now(),
            "action": 'ACTIVE',
            "machine_name": machine_name,
            "operation": operation_name,
            "rating(AMP)": rating_amp, "current_usl": current_usl,
            "current_lsl": current_lsl, "current_mean": current_mean,
            "pulse_usl": pulse_usl, "pulse_lsl": pulse_lsl,
            "pulse_mean": pulse_mean
        }
        existing_curr_document = current_collection.find_one({"machine_name": machine_name,
                                                         "operation":operation_name,
                                                         "usl": current_usl,
                                                         "lsl": current_lsl})
        existing_machine_document = machine_collection.find_one({"machine_name": machine_name,
                                                              "rating(AMP)": rating_amp})
        existing_pulse_document = pulse_collection.find_one({"machine_name": machine_name,
                                                              "operation": operation_name,
                                                              "usl": pulse_usl,
                                                              "lsl": pulse_lsl})


        if existing_curr_document:
            current_collection.update_one({"_id": existing_curr_document["_id"]}, {"$set": {"status": "ACTIVE"}})
            pulse_collection.update_one({"machine_name": existing_curr_document["machine_name"]},
                                        {"$set": {"status": "ACTIVE"}})
            machine_collection.update_one({"_id": existing_machine_document["_id"]}, {"$set": {"status": "ACTIVE"}})
            change_records_collection.insert_one(change_data2)
            alert_message = f"Combination already exists for Machine: {machine_name} in Database. Updated status to ACTIVE."
            return [True, alert_message] + [machine, operation, rating_amp, current_usl, current_lsl, current_mean,
                                            pulse_usl, pulse_lsl, pulse_mean]
        else:
            current_collection.insert_one(current_data)
            pulse_collection.insert_one(pulse_data)
            machine_collection.insert_one(machine_data)
            change_records_collection.insert_one(change_data)
            alert_message = "New rating added successfully"
        return [True, alert_message] + [machine, operation, rating_amp, current_usl, current_lsl, current_mean,
                                        pulse_usl, pulse_lsl, pulse_mean]

    return app.server
