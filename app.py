# Imports
import pandas as pd
import numpy as np
import os
import glob
import unicodedata
import plotly.express as px
from dash import Dash, html, dcc, no_update
from dash.dependencies import Input, Output, State
import plotly.graph_objects as grphobj
import dash_bootstrap_components as dbc
# Data Loading
pokemon_data = pd.read_csv('pokemon.csv')
print(pokemon_data.shape)
pokemon_data.columns
pokemon_data['generation'].value_counts()
pokemon_data['type1'].unique()
# Information Retrieval
current_working_directory = os.getcwd()
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def to_normal_text(text):
    txt = text.lower()
    txt = remove_accents(txt)
    txt = txt.replace(' ', '-')
    txt = txt.replace(':', '')
    txt= txt.replace('.', '')
    txt = txt.replace("'", '')
    txt = txt.replace('♀', '-f')
    txt = txt.replace('♂', '-m')
    return txt

def get_image_path(pokemon_name, return_None=True):
    pokemon_name = to_normal_text(pokemon_name)
    if os.path.exists(f'assets\{pokemon_name}.png'):
        return f'assets\{pokemon_name}.png'
    elif os.path.exists(f'assets\{pokemon_name}.jpg'):
        return f'assets\{pokemon_name}.jpg'
    else:  
        img_list = glob.glob(current_working_directory + f"\\assets\{pokemon_name}*.png", recursive=True)
        if(len(img_list)==1):
            return img_list[0][len(current_working_directory)+1:]
        img_list = glob.glob(current_working_directory + f"\\assets\{pokemon_name}*.jpg", recursive=True)
        if(len(img_list)==1):
            return img_list[0][len(current_working_directory)+1:]
        
        if return_None:
            return None
        else:
            return 
get_image_path('Zygarde')
num_images = len(os.listdir('assets'))
image_info = {}
image_info['total_images'] = num_images
image_info['no_img_pokemons'] = []

for pok_name in pokemon_data['name']:
    if(get_image_path(pok_name) is None):
        image_info['no_img_pokemons'].append(pok_name)
image_info
# Preprocessing 
null_cols = pokemon_data.isnull().sum()
for col in null_cols.keys():
    if(null_cols[col]>0):
        print(f"{col}  -->  {null_cols[col]} nulls")
pokemon_data.describe()
pokemon_data.rename(columns = {'base_total':'total_power'}, inplace = True)
pokemon_data = pokemon_data.astype({'is_legendary': 'object'})
pokemon_data.loc[pokemon_data['is_legendary']==1, 'is_legendary'] = 'Legendary'
pokemon_data.loc[pokemon_data['is_legendary']==0, 'is_legendary'] = 'Regular'

print(pokemon_data.info())
pokemon_data.loc[pokemon_data['total_power'].argsort(), ['name', 'total_power', 'is_legendary', 'classfication']].iloc[-10:]
# The Dashboard
pokemon_strength_cols = ['total_power', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed', 'hp']
pokemon_diff_cols = ['type1', 'type2', 'generation', 'is_legendary'] + pokemon_data.columns[1:19].to_list()
img_src2 = 'assets\pik-pok.png'
header_logo_img = 'assets\pokemon_logo.png'
img_src4 = 'assets\icon_pok.png'
### Top Info Cards
def get_info_card(title, info_element_id):
    return dbc.Card(
    dbc.CardBody(
        [
            dbc.CardHeader(
                title, className="card-title", 
                style={"font-weight": "bold", 'font-size':'15px', 'height':'30px', 'padding':'0.1rem', 'color':'black',
            }),#'background-color':'yellow'
            dbc.CardFooter(
                id=info_element_id,
                className="card-text",
                style={'padding':'0.1rem', 'color': 'blue', 'height':'50px', 'font-size':'18px', 'align-items': 'center', 'display':'flex', 'justify-content':'center'}#'background-color':'lightyellow'
            ),
        ], style={'padding':'9px'}
    ),
    style={"width": "180px", 'height':'100px', 'textAlign': 'center', 'border-radius':'6px', 
    'box-shadow':' lightblue 1px 0px 6px 0.2px', 'margin':'0px'}, #'background-color':'yellow'
    
)

card_number_of_types = get_info_card("No. of Types", info_element_id='num-types-card') 

card_number_of_pokemons = get_info_card("No. of Pokemons", info_element_id='num-pokemons-card')

card_heighest_legendary_power = get_info_card("Strongest Legendary", info_element_id='strongest-legendary-card')

card_heighest_regular_power = get_info_card("Strongest Regular", info_element_id='strongest-regular-card')

### Main Layout
get_image_path('Zygarde')
app = Dash(__name__, external_stylesheets=[
           dbc.themes.BOOTSTRAP], title='The Pokémon Dashboard')
server = app.server
server.static_folder = 'assets'
app.layout = dbc.Container([

    ## ------------------ PAGE HEADER ------------------##
    dbc.Row(
        [
            dbc.Col([html.H1("The", style={'textAlign': 'right', 'color': 'black',
                    'font-size': '30px', 'font-weight': 'bold', 'margin': 'auto', })]),
            dbc.Col([html.Img(src=header_logo_img, style={'height': '60px', 'margin': '10px', })], style={
                    'display': 'flex', 'flex-grow': 0, 'justify': 'center'}),
            dbc.Col([html.H1("Dashboard", style={
                    'textAlign': 'left', 'color': 'black', 'font-size': '30px', 'font-weight': 'bold', 'margin': 'auto', })]),
        ],
        align="center",
        style={
            'align-items': 'center', 'height': '100px', 'background-color': 'lightblue',
            'padding': '10px', 'border-radius': '6px', 'box-shadow': ' lightblue 1px 0px 6px 0.2px'
        }
    ),
    html.Br(),

    ## ------------------ INFO CARDS & GENERATION SLIDER ------------------##
    dbc.Row([
        dbc.Col([

                # Cards

                dbc.Row([
                    dbc.Col([card_number_of_pokemons],),
                    dbc.Col([card_number_of_types],),
                    dbc.Col([card_heighest_legendary_power],),
                    dbc.Col([card_heighest_regular_power],),
                ],),

                # Slider

                dbc.Row([
                    dbc.Col([
                            dbc.Row(
                                html.Div([], style={'height': '5px', 'margin-top': '15px', })),
                            dbc.Row(
                                html.H6(
                                    style={'text-align': 'center', 'margin': 'auto',
                                           'padding': '15px', "font-weight": "bold", },
                                    id='slider-cards-value',
                                )
                            ),

                            dbc.Row(
                                [
                                    html.Div(
                                        children=[
                                            dcc.Slider(
                                                id='generation_slider',
                                                value=pokemon_data['generation'].min(
                                                ) - 1,
                                                min=pokemon_data['generation'].min(
                                                ) - 1,
                                                step=1,
                                                max=pokemon_data['generation'].max(
                                                ),
                                                marks={
                                                    '0': 'All', '1': '1st', '2': '2nd', '3': '3td', '4': '4th', '5': '5th', '6': '6th', '7': '7th'},
                                            )
                                        ],
                                        style={
                                            'width': '450px', 'text-align': 'center', 'margin': 'auto', 'padding': '0px',
                                            'box-shadow': ' lightblue 0px 1px 1px 0.2px', 'align': 'center', 'disply': 'block'
                                        },
                                    ),
                                ],
                                style={'margin-left': 'auto',
                                       'margin-right': 'auto', }
                            ),

                            ],
                        style={'textAlign': 'center', 'padding': '10px', },
                            )
                ],),

            ],
            style={'margin': '0px', 'padding-top': '10px', 'box-sizing': 'content-box', },
            width=10
        ),],
        style={'padding': '0px', 'padding-top': '4px', 'margin': 'auto', }, 
        justify='center',
    ),


    # --------------------------------------------------------------------------------------------------------------


    dbc.Row(style={'height': '0px', 'margin': '0px', 'padding': '0px'}),

    # -------------------------------------All Pokemons Scatter Plot--------------------------------------------------------------
    dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        children=[
                            dbc.Col(
                                dcc.Dropdown(
                                    pokemon_data.columns[36:38],
                                    id='pok-scat-dropdown',
                                    multi=False,
                                    value='type1',
                                    placeholder='choose value for x-axis',
                                ),
                                style={'width': '300px', 'text-align': 'center', 'margin': 'auto', 'padding': '15px', }
                            ),

                            dcc.Graph(id='pok-scatter', clear_on_unhover=True,
                                        style={'margin-right': '40px', 'padding': '10px'}),
                            dcc.Tooltip(id="pok-scatter-tooltip"),
                        ], 
                        style={'box-shadow': ' lightblue 0px 1px 6px 0.2px'}
                    ),


                    dbc.Row(style={'height': '7px', 'margin': '0px', 'padding': '0px'}),

    # -------------------------------------Pokemons Distribution across Generations (Histogram)--------------------------------------------------------------

                    html.Div([
                        dbc.Col(
                            dcc.Dropdown(
                                pokemon_strength_cols,
                                id='gen-hist-dropdown',
                                multi=False,
                                value='total_power',
                                placeholder='choose value for x-axis',
                            ),
                            style={'width': '300px', 'text-align': 'center', 'margin': 'auto',
                                    'padding': '15px', }
                        ),
                        dcc.Graph(id='gen-hist',  style={'box-shadow': ' lightblue 0px 1px 6px 0.2px'})
                    ],),

                ],
                width={'size': 7},
            ),

            # ---------------------------------------------------------------------------------------------------------
            dbc.Col(width=1,),
            # ------------------------------------------>> Top Pokemons Table <<----------------------------------------------------

            dbc.Col(
                [
                    dbc.Row(
                        html.Div(
                            html.H6("Top/Last Pokemons ordered by abilities",
                                    style={'margin': '7px'})
                        )
                    ),

                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Div(
                                        children=[
                                            dcc.Dropdown(
                                                pokemon_strength_cols,
                                                id='top-pok-dropdown',
                                                multi=False,
                                                value='total_power',
                                                placeholder='choose a type 1',
                                            )
                                        ], 
                                        style={'width': '200px', 'align': 'left', 'padding': '15px'}
                                    ),
                                ], 
                                style={'size': 2, 'offset': 0, },
                            ),

                            dbc.Col(
                                [
                                    html.Div(
                                        children=[
                                            dbc.Card(
                                                [
                                                    dcc.RadioItems(
                                                        id='top-pok-radio-items', 
                                                        options=['Heighest', 'Lowest'], 
                                                        value='Heighest', 
                                                        inline=True, 
                                                        inputStyle={"margin": "5px"}
                                                    )
                                                ],
                                                style={'backgound-color': 'white', 'width': '170px', 'height': '38px', 'textAlign': 'center', 'padding': '5px'}
                                            )
                                        ],
                                    ),
                                ], 
                                style={'width': '170px', 'textAlign': 'center', 'padding': '15px', },
                            ),
                        ], 
                        style={'size': 2, 'offset': 0, },
                    ),

                    html.Div(id='top-pok-table', style={'textAlign': 'center'}),

                ], 
                width={'size': 4, 'offset': 0}, style={'justify': 'around', 'margin': 'center', }
            ),
        ],
        justify='around',
    ),

    # -----------------------------------------------------------------------------------------------------
    dbc.Row(style={'height': '10px', 'margin': '0px', 'padding': '0px'}),

    # ------------------------------------>> Fighting Pokemons <<---------------------------------------

    dbc.Row([
        ## Pokemon 1
        dbc.Col(
            [
                dbc.Row(
                    dcc.Dropdown(
                        pokemon_data['name'].sort_values(),
                        value='Pikachu',
                        id='fight-first-pok-dropdown',
                        multi=False,
                        placeholder='Pokemon name',
                        style={'textAlign': 'center', 'padding': '5px', 'margin-top': '10px', 'align-items': 'center', 
                            'margin-left': '25px', 'width': '200px', 'height': '25px', }
                    ),
                ),

                html.Img(
                    id='fight-first-avatar', 
                    style={'width': '200px', 'height': '200px', 'margin-left': '50px', 'margin-top': '70px'}, 
                    # width={'size': 3, 'offset': 0}
                ),
            ], 
            style={'box-shadow': ' lightblue 1px 1px 6px 0.2px'}, 
            width=3
        ),


        dbc.Col(
            [
                dcc.Graph(id='pok-fight-radar-graph',)
            ], 
            width={'size': 6, 'offset': 0},
        ),

        ## Pokemon 2
        dbc.Col(
            [
                dbc.Row(
                    dbc.Col(
                        dcc.Dropdown(
                            pokemon_data['name'].sort_values(),
                            value='Squirtle',
                            id='fight-second-pok-dropdown',
                            multi=False,
                            placeholder='Pokemon name',
                            style={'textAlign': 'center', 'padding': '5px', 'margin-top': '10px', 'align-items': 'center', 
                                   'margin-left': '25px', 'width': '200px', 'height': '25px', }
                        ),
                        width=3,
                    )
                ),

                dbc.Row(
                    html.Img(
                        id='fight_second_avatar', 
                        style={'width': '200px', 'height': '200px', 'margin-left': '50px', 'margin-top': '70px', }, 
                        # width={'size': 3, 'offset': 0}
                    ),
                )
            ], 
            style={'box-shadow': ' lightblue 1px 1px 6px 0.2px'}, 
            width=3
        )
    ],),


    # -----------------------------------------------------------------------------------------------------
    dbc.Row(style={'height': '10px', 'margin': '0px', 'padding': '0px'}),

    # ----------------------------------- DISTRIBUTION MAPPING --------------------------------------------

    dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Dropdown(
                                            pokemon_diff_cols,
                                            id='parallel-first-dropdown',
                                            multi=False,
                                            value='generation',
                                            placeholder='choose value',
                                            style={'width': '150px', 'textAlign': 'center', 'margin-left': '5px'}
                                        ),
                                        style={'width': '150px', 'textAlign': 'center', 'margin': '0px','padding': '15px', }, 
                                        width=2
                                    ),

                                    dbc.Col(
                                        dcc.Dropdown(
                                            pokemon_diff_cols,
                                            id='parallel-second-dropdown',
                                            multi=False,
                                            value='type1',
                                            placeholder='choose value',
                                            style={'width': '150px', 'textAlign': 'center', 'margin-left': '30px'}
                                        ),
                                        style={'width': '150px', 'text-align': 'center', 'margin': '0px','padding': '15px', }, 
                                        width=2
                                    ),

                                    dbc.Col(
                                        [
                                            html.Div(
                                                children=[
                                                    dbc.Button(
                                                        id='parallel-graph-submit-btn',
                                                        children='Submit', 
                                                        n_clicks=0, 
                                                        color='primary', 
                                                        className="me-1",
                                                        style={'box-shadow': 'eab967d9 0px 1px 6px 0px', }
                                                    )
                                                ],
                                                style={'width': '200px', 'textAlign': 'right', 'padding': '15px'}
                                            )
                                        ], 
                                        width=2
                                    ),

                                ], 
                                style={'margin-left': '0px', 'margin-right': '0px', 'textAlign': 'center', 'margin': 'auto'}, 
                                justify='right'
                            ),

                            dcc.Graph(id='parallel-graph'),

                        ], 
                        style={'textAlign': 'center'}
                    ),
                ],
                width=6, 
                style={'box-shadow': ' lightblue 0px 1px 6px 0.2px'}
            ),
            
            dbc.Col(
                [
                    dcc.Dropdown(
                        pokemon_data['name'].sort_values(),
                        value=None,
                        id='drop-down-one-pokemon-name',
                        multi=False,
                        placeholder='Pokemon name',
                        style={'textAlign': 'center', 'padding': '5px', 'margin-top': '5px', 'margin-buttom': '20px',
                                'width': '300px', 'height': '20px', }
                    ),
                    dcc.Graph(
                        id='radar-one-pokemon',
                        style={'margin-top': '40px', 'margin-buttom': '20px'},
                    ),
                ],
                width=6,
            ),
        ], 
        style={'box-shadow': ' lightblue 0px 1px 6px 0.2px'}
    ),

    # -----------------------------------------------------------------------------------------------------
    dbc.Row(style={'height': '10px', 'margin': '0px', 'padding': '0px'}),

    # --------------------------------------- POKEMON TREE ------------------------------------------------

    dbc.Row([
        dbc.Col([
            dbc.Row(
                html.Div(
                    html.H6("Pokemon tree based on your selections",
                            style={'margin': '7px'})
                )
            ),
            dbc.Row([
                html.Div(children=[
                    dcc.Dropdown(pokemon_diff_cols,
                                 id='tree-drop-down',
                                 multi=True,
                                 value=None,
                                 placeholder='choose value for x-axis',
                                 ),
                ], style={'width': '600px', 'text-align': 'center',
                          'margin': 'auto', 'margin-right': '0px', 'padding': '10px', }),
                html.Div([
                    dbc.Button(id='tree-button-state', children='Submit', n_clicks=0, color='primary', className="me-1",
                               style={'box-shadow': 'eab967d9 1px 1px 0px 0px', 'width': '120px', 'text-align': 'center', 'padding': '10px', 'textalign': 'center'}),
                ], style={'width': '300px', 'text-align': 'left', 'padding': '5px', 'margin': 'auto', 'margin-leftt': '0px', })
            ]),

            dbc.Row([
                dbc.Col(dcc.Graph(id='tree-graph'), width=12),
            ]),
        ], width=12)
    ], style={'box-shadow': ' lightblue 0px 1px 6px 0.1px'}),


], 
fluid=True,
style={'margin': '0px', 'padding': '0px', 'font-family': "'Trebuchet MS', sans-serif"}
)

### Callbacks
@app.callback(
    Output(component_id='slider-cards-value', component_property='children'),
    Output(component_id='num-pokemons-card', component_property='children'),
    Output(component_id='num-types-card', component_property='children'),
    Output(component_id='strongest-legendary-card', component_property='children'),
    Output(component_id='strongest-regular-card', component_property='children'),
    Input(component_id='generation_slider', component_property='value'),   
)

def update_cards(input_slider):
    gen_dic = {
        0: 'Generation: All',
        1: 'Generation: 1',
        2: 'Generation: 2',
        3: 'Generation: 3',
        4: 'Generation: 4',
        5: 'Generation: 5',
        6: 'Generation: 6',
        7: 'Generation: 7',
    }

    if input_slider == 0:
        gen_val = gen_dic[0]
        num_card = pokemon_data.shape[0]
        num_types = pokemon_data['type1'].nunique()
        heighest_legendary_card = pokemon_data.loc[pokemon_data['total_power'].argsort(), 'name'].loc[pokemon_data['is_legendary'] == 'Legendary'].iloc[-1].capitalize()
        heighest_regular_card = pokemon_data.loc[pokemon_data['total_power'].argsort(), 'name'].loc[pokemon_data['is_legendary'] == 'Regular'].iloc[-1].capitalize()

    else:
        # print(input_slider)
        gen_val = gen_dic[input_slider]
        filtered_data = pokemon_data[pokemon_data['generation'] == input_slider].sort_values(by=['total_power'], ascending=False)
        num_card = filtered_data.shape[0]
        # print(num_card)
        num_types = filtered_data['type1'].nunique()
        # print(num_types)
        heighest_legendary_card = filtered_data[filtered_data['is_legendary'] == 'Legendary'].sort_values(by=['total_power'], ascending=False).iloc[0, :]['name'].capitalize()
        # print(heighest_legendary_card)
        heighest_regular_card = filtered_data[filtered_data['is_legendary'] == 'Regular'].sort_values(by=['total_power'], ascending=False).iloc[0, :]['name'].capitalize()
        # print(heighest_regular_card)
        # filtered_data[filtered_data['is_legendary'] == 'Regular'].sort_values(by=['total_power'], ascending=False).iloc[0, :]['name']

    print(gen_val, num_card, num_types, heighest_legendary_card, heighest_regular_card)

    return  gen_val, num_card, num_types, heighest_legendary_card.capitalize(), heighest_regular_card.capitalize()

@app.callback(
    Output(component_id='pok-scatter', component_property='figure'),
    Input('pok-scat-dropdown', 'value'),
)

def update_scatter_fig(dropdown_x_y_value):
    if dropdown_x_y_value == None:
        fig = px.scatter(pokemon_data, x="type1", y="total_power", color="type1", animation_frame="generation", 
                                    animation_group="type2", hover_name = 'name')
        fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1000

    else:
        if dropdown_x_y_value == 'type2':
            animat_grp = 'type1'
        else:
            animat_grp = 'type2'
        fig = px.scatter(pokemon_data, x=dropdown_x_y_value, y="total_power", color=dropdown_x_y_value, animation_frame="generation",
                                    animation_group=animat_grp, hover_name = 'name', size='total_power', title="Pokemon Distribution across Types")
        fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1000
    fig = fig.update_traces(hoverinfo="none", hovertemplate=None)
    return fig

@app.callback(
    Output("pok-scatter-tooltip", "show"),
    Output("pok-scatter-tooltip", "bbox"),
    Output("pok-scatter-tooltip", "children"),
    Input("pok-scatter", "hoverData"),
)

def display_hover_scatter(hoverData):
    if hoverData is None:
        return False, no_update, no_update

    # print(hoverData)
    pt = hoverData["points"][0]
    bbox = pt["bbox"]
    name = pt["hovertext"]

    df_row = pokemon_data[pokemon_data['name'] == name].iloc[0]
    img_name = name
    src_img = get_image_path(img_name, return_None=False)
    generation = df_row['generation']
    legendary = df_row['is_legendary']
    all_power = df_row['total_power']
    attack = df_row['attack']
    defense = df_row['defense'] 
    speed = df_row['speed']
    hp = df_row['hp']

    children = [
        html.Div([
            html.Img(src=src_img, style={"width": "100%"}),
            html.H2(f"{name}", style={"color": "darkblue"}),
            html.P(f"Generation = {generation}"),
            html.P(f"Kind = {legendary}"),
            html.P(f"Total Power = {all_power}"),
            html.P(f"Attack = {attack}"),
            html.P(f"Defense = {defense}"),
            html.P(f"Speed = {speed}"),
            html.P(f"HP = {hp}"),
        ], style={'width': '200px', 'white-space': 'normal'})
    ]

    return True, bbox, children

#----------------------------------Top Pokemons Table----------------------------------------
@app.callback(
    Output(component_id='top-pok-table', component_property='children'),
    Input(component_id='top-pok-dropdown', component_property='value'),
    Input(component_id='top-pok-radio-items', component_property='value')
)

def update_table(type_of_power, radio_selection):
    if type_of_power == None:
        type_of_power = 'total_power'
    columns = ['name', type_of_power]
    
    if radio_selection == 'Heighest':
        sorted_data = pokemon_data[columns].sort_values([type_of_power], ascending=False).iloc[:10,:]
    else:
        sorted_data = pokemon_data[columns].sort_values([type_of_power], ascending=True).iloc[:10,:]
        
    pics = []
    for name in sorted_data['name'].values:
        pics.append(get_image_path(name, return_None=False))

    sorted_data['Picture'] = np.array(pics)

    table = html.Table(
        # Header
        [html.Tr([html.Th(col, style={'padding':'5px', 'color':'black',}) for col in sorted_data.columns],) ] + 
        # Body
        [html.Tr([
            html.Td(sorted_data.iloc[i][col] if col != 'Picture' else html.Img(src=sorted_data.iloc[i][col],
             style={'width':'90px', 'height':'90px',}), 
            style={"font-size":20,"width":"300px","height":"50px",'color':'black','padding':'5px', }) for col in sorted_data.columns 
        ]) for i in range(len(sorted_data))], #'background-color':'#FFFFE0'
        style={'margin-left':'5px', 'margin-right':'5px', 'margin-bottom':'5px', 'margin-top':'5px'}
    )
    return table

#---------------------------Generation Histogram-----------------------------------------

@app.callback(
    Output(component_id='gen-hist', component_property='figure'),
    Input(component_id='gen-hist-dropdown', component_property='value')
)
def update_hist(dropdown_val):
    if dropdown_val == None:
        fig = px.histogram(pokemon_data, x='total_power', y='generation', color='generation', 
        animation_frame="generation",).update_yaxes(categoryorder='total ascending', type='category')
    else:
        reordered_df = pokemon_data.sort_values(f"{dropdown_val}", ascending=False)
        fig = px.histogram(reordered_df, x=dropdown_val, y='generation', color='generation', 
                                title='Abilities across Generations', orientation='h').update_yaxes(categoryorder='total ascending', type='category')

    return fig


# @app.callback(
#     Output(component_id='pie-fig', component_property='figure'),
#     Input(component_id='pie-slider', component_property='value'),
#     Input(component_id='pie-radio-items', component_property='value'),
# )
# def parallel_graph(gen_selection, radio_selection):
#     if radio_selection == None:
#         radio_selection = 'type1'
#     if gen_selection == 0:
#         fig = px.pie(pokemon_data, names = radio_selection, hole=0.3,)
#     else:
#         filtered_data = pokemon_data[pokemon_data['generation'] == gen_selection]
#         fig = px.pie(filtered_data, names = radio_selection, hole=0.3)

#     return fig


#------------------------------ONE POKEMON RADAR-----------------------------

@app.callback(
    Output(component_id='radar-one-pokemon', component_property='figure'),
    Input(component_id='drop-down-one-pokemon-name', component_property='value')
)
def get_pokemon_data(pokemon_name):
    
    if pokemon_name == None:
        pokemon_name = 'Pikachu'
    
    pok_data = pokemon_data[pokemon_data["name"] == pokemon_name].iloc[0]

    trace = grphobj.Scatterpolar(
        r=[
            pok_data['hp'], pok_data['attack'], pok_data['defense'], pok_data['sp_attack'],
            pok_data['sp_defense'], pok_data['speed'], pok_data['hp']
        ],
        theta=['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed'],
        fill='toself',
        name=pokemon_name
    )

    layout = grphobj.Layout(
        xaxis=dict(
            domain=[0, 0.45]
        ),
        yaxis=dict(
            domain=[0, 0.45]
        ),
        xaxis2=dict(
            domain=[0.55, 1]
        ),
        xaxis3=dict(
            domain=[0, 0.45],
            anchor='y3'
        ),
        xaxis4=dict(
            domain=[0.55, 1],
            anchor='y4'
        ),
        yaxis2=dict(
            domain=[0, 0.45],
            anchor='x2'
        ),
        yaxis4=dict(
            domain=[0.55, 1],
            anchor='x4'
        ),

        showlegend=True,
        title= "Visualize any Pokemon"
    )
    data = [trace]
    fig = grphobj.Figure(data=data, layout=layout,)
    fig.add_layout_image(
        dict(
            source=get_image_path(pokemon_name),
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=1, sizey=1,
            xanchor="center",
            yanchor="middle",
            layer="above",
            opacity=0.5,
        ),
        sizex=0.5,
        sizey=0.5,
    )

    return fig
#----------------------------Parallel Graph-------------------------------
@app.callback(
    Output(component_id='parallel-graph', component_property='figure'),
    State(component_id='parallel-second-dropdown', component_property='value'),
    State(component_id='parallel-first-dropdown', component_property='value'),
    Input(component_id='parallel-graph-submit-btn', component_property='n_clicks')
)
def parallel_graph(first_drop_val, second_drop_val, n_clicks):
    
    if first_drop_val != second_drop_val :
        fig = px.parallel_categories(pokemon_data, dimensions=[second_drop_val, first_drop_val], color="generation", title='How Many Pokemons Found in both Sides',)

    return fig

#------------------Tree------------------------------------
@app.callback(
    Output(component_id='tree-graph', component_property='figure'),
    State(component_id='tree-drop-down', component_property='value'),
    Input(component_id='tree-button-state', component_property='n_clicks')
)
def update_tree(tree_levels, n_clicks):
    if tree_levels == None or n_clicks == 0:
        fig = px.treemap(pokemon_data, path=[px.Constant("Pokemons"), 'generation', 'name'], values='total_power',
                  color='name', hover_data=['classfication'],
                  color_continuous_scale='RdBu',
                  color_discrete_sequence=px.colors.qualitative.Prism,
                  color_continuous_midpoint=np.average(pokemon_data['total_power'], weights=pokemon_data['generation']))
    else:
        final_tree_levels = [px.Constant("Pokemons")]
        final_tree_levels.extend(tree_levels)
        final_tree_levels.append('name')
        fig = px.treemap(pokemon_data, path=final_tree_levels, values='total_power',
                    color='name', hover_data=['classfication'],
                    color_continuous_scale='RdBu',
                    color_discrete_sequence=px.colors.qualitative.Prism,
                    color_continuous_midpoint=np.average(pokemon_data['total_power'], weights=pokemon_data['generation']))
    
    fig.update_layout(margin = dict(t=25, l=25, r=25, b=25),)
        
    return fig

#------------------POKEMON FIGHT--------------------------------

@app.callback(
    Output(component_id='fight-first-avatar', component_property='src'),
    Output(component_id='fight_second_avatar', component_property='src'),
    Output(component_id='pok-fight-radar-graph', component_property='figure'),
    Input(component_id='fight-first-pok-dropdown', component_property='value'),
    Input(component_id='fight-second-pok-dropdown', component_property='value'),
)


def update_pokemon_pic(input_first_pokemon, input_second_pokemon):
    # if input_first_pokemon == None :
    #     input_first_pokemon = 'Pikachu'
    # if input_second_pokemon == None:
    #     input_second_pokemon = 'Raichu'

    if input_first_pokemon == None:
        input_first_pokemon = 'Pikachu'
    
    pok_data = pokemon_data[pokemon_data["name"] == input_first_pokemon].iloc[0]

    trace = grphobj.Scatterpolar(
        r=[
            pok_data['hp'], pok_data['attack'], pok_data['defense'], pok_data['sp_attack'],
            pok_data['sp_defense'], pok_data['speed'], pok_data["hp"]
        ],
        theta=['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed'],
        fill='toself',
        name=input_first_pokemon
    )

    if input_second_pokemon == None:
        input_second_pokemon = 'Raichu'
    
    pok_data2 = pokemon_data[pokemon_data["name"] == input_second_pokemon].iloc[0]

    trace2 = grphobj.Scatterpolar(
        r=[
            pok_data2['hp'], pok_data2['attack'], pok_data2['defense'], pok_data2['sp_attack'],
            pok_data2['sp_defense'], pok_data2['speed'], pok_data2["hp"]
        ],
        theta=['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed'],
        fill='toself',
        name=input_second_pokemon
    )

    img_src_first_pokemon = get_image_path(input_first_pokemon)
    img_src_second_pokemon = get_image_path(input_second_pokemon)


    layout = grphobj.Layout(
        xaxis=dict(
            domain=[0, 0.45]
        ),
        yaxis=dict(
            domain=[0, 0.45]
        ),
        xaxis2=dict(
            domain=[0.55, 1]
        ),
        xaxis3=dict(
            domain=[0, 0.45],
            anchor='y3'
        ),
        xaxis4=dict(
            domain=[0.55, 1],
            anchor='y4'
        ),
        yaxis2=dict(
            domain=[0, 0.45],
            anchor='x2'
        ),
        yaxis4=dict(
            domain=[0.55, 1],
            anchor='x4'
        ),

        showlegend=True,
        title="Pokemon Battle"
    )
    data = [trace, trace2]
    fig = grphobj.Figure(data=data, layout=layout,)

    return img_src_first_pokemon, img_src_second_pokemon, fig
# Running the App
app.run_server(debug=True, use_reloader=False)