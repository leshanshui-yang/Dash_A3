# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px

import os
import json
import requests
import urllib3 # Mute requests insecure warnings 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# =============================================================================
# Global Variables
# =============================================================================
# For downloading files from HDFS
from hdfs import InsecureClient
client_hdfs = InsecureClient(os.environ["HDFS_URL"], user = "hdfs")
url = os.environ["APP_URL"]

# Getting model names
models_url = url + "/8081/models/"
models = requests.get(models_url, verify=False)._content.decode("utf-8").replace('\n', '').replace(' ', '')
models = [d['modelName'] for d in json.loads(s=models)['models']]
options = [dict(label=model, value=model) for model in models]


def post(data, model_name, serve_url=url, data_type='json'):
    """Inference with POST requests """
    if data_type == 'json':
        headers = {'Content-Type': 'application/json'}
    pred_url = serve_url + '/8080/predictions/' + model_name
    if type(data) == str: # if batch size = 1
        data = [data,] 
    data = json.dumps(data)
    response = requests.post(pred_url, headers=headers, data=data, verify=False)
    response = response._content.decode('utf-8')
    try:
        response = json.loads(response)
    except:
        pass
    # Force to put single str object in a list
    if type(response)==str:
        return [response]
    else:
        return response


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], url_base_pathname=os.environ["SAAGIE_BASE_PATH"]+"/")


# =============================================================================
# Layout and Design
# =============================================================================
colors = {
        'background_deep': '#1E3047',
        'background':'#253C5B',
        'text':'#E7EEF8'
}

app.layout = dbc.Container(fluid=True,children=[
    # Title
    html.H1(children = 'Torch Serve Language Models (Demo)',
           style = {'textAlign':'center', 'fontSize': '200%', 'height': 120,
                    'color': colors['text'], 'backgroundColor': colors['background_deep'],
                    'margin-bottom': 0, 'padding-top': 30}),
    dbc.Row([
        # Multi-Checklist
        dbc.Col([
            dcc.Checklist(options=options, value=[], id='checklist', labelStyle={'display': 'block'},
                          style = {'textAlign':'left', 'height': 800, 
                                   'color': colors['text'], 'backgroundColor': colors['background'],
                                   'padding-left': 50, 'padding-top': 40,} 
                          )
            ], width=3), 
        # Text IO
        dbc.Col([
            # Text-Input
            dcc.Textarea(id='text_in', value='input something here', style = {'height': 180, 'width': '100%'}),
            # Inference-Output
            dcc.Markdown(id='pred_out', style = {'width': '100%', 'display': 'block', 'padding-top': 20})
            ], 
            style = {'padding-top': 30}, width=8)
        ]
        ),
    ], 
    style = {'margin':False})


# =============================================================================
# Callback function
# =============================================================================
@app.callback(
    Output(component_id = 'pred_out', component_property = 'children'),
    [Input(component_id = 'text_in', component_property = 'value'),
     Input(component_id = "checklist", component_property = "value")]
)
def update_output_div(input_value, input_choices):
    input_value = input_value.split('\n')
    if len(input_choices) > 0:
        out_list = ['**%s :**\n\n%s'%(model_name, '\n\n'.join(post(input_value, model_name))) for model_name in input_choices]
        spliter = '\n\n'+'-'*32+'\n\n'
        pred = spliter.join(out_list)
    else:
        pred = 'Please select a model.'
    return pred 


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=False, port=8051)



