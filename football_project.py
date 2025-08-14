import os
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

folder_path = os.path.dirname(os.path.abspath(__file__))

plays = pd.read_csv(os.path.join(folder_path, "plays.csv"), low_memory=False)
defense = pd.read_csv(os.path.join(folder_path, "defense.csv"), low_memory=False)

#Get rid of plays nullified by penalty
plays = plays[plays["is_no_play"] == 0]

plays_subset = plays[["play_id", "offensive_formation_group", "field_position", "expected_points_added"]]
defense_subset = defense[["play_id", "alignment", "def_target"]]

#Merge play_id
df = pd.merge(defense_subset, plays_subset, on="play_id", how="inner").dropna()

#Field positions into four zones
def categorize_zone(x):
    if x <= -20:
        return "Backed Up"
    elif -20 < x <= 0:
        return "Own Territory"
    elif 0 < x <= 40:
        return "Midfield"
    else:
        return "Scoring Range"

df["Field Zone"] = df["field_position"].apply(categorize_zone)

#Neutral Colors
DARK_GRAY = "#333333"
LIGHT_GRAY = "#E0E0E0"
WHITE = "#FFFFFF"

#Dash app
app = Dash(__name__)
app.title = "Passing Defense Dashboard"

#App layout
app.layout = html.Div([
    #Title
    html.Div([
        html.H1("Passing Defense Dashboard", style={
            "color": DARK_GRAY,
            "fontFamily": "'Arial Black', Arial, sans-serif",
            "fontWeight": "bold",
            "margin": "0 20px",
            "textAlign": "center"
        }),
    ], style={
        "padding": "10px",
        "backgroundColor": LIGHT_GRAY,
        "borderRadius": "10px",
        "marginBottom": "15px"
    }),

    #Filters
    html.Div([
        html.Div([
            html.Label("Select Field Zone(s):", style={"fontWeight": "bold", "color": DARK_GRAY}),
            dcc.Dropdown(
                id="zone-filter",
                options=[{"label": z, "value": z} for z in sorted(df["Field Zone"].unique())],
                value=sorted(df["Field Zone"].unique()),
                multi=True,
                placeholder="Select zones",
                style={"color": DARK_GRAY}
            ),
        ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top"}),

        html.Div([
            html.Label("Select Defensive Alignment(s):", style={"fontWeight": "bold", "color": DARK_GRAY}),
            dcc.Dropdown(
                id="alignment-filter",
                options=[{"label": a, "value": a} for a in sorted(df["alignment"].unique())],
                value=sorted(df["alignment"].unique()),
                multi=True,
                placeholder="Select alignments",
                style={"color": DARK_GRAY}
            ),
        ], style={"width": "48%", "display": "inline-block", "float": "right", "verticalAlign": "top"}),
    ], style={"marginBottom": "30px"}),

    #Heatmap 
    dcc.Graph(id="epa-heatmap", style={"marginTop": 40})
], style={"fontFamily": "Arial, sans-serif", "backgroundColor": WHITE, "padding": "20px"})

#Heatmap updates as filter changes
@app.callback(
    Output("epa-heatmap", "figure"),
    Input("zone-filter", "value"),
    Input("alignment-filter", "value"),
)
def update_heatmap(selected_zones, selected_alignments):
    if not selected_zones:
        filtered = df.copy()
    else:
        filtered = df[df["Field Zone"].isin(selected_zones)]

    if selected_alignments:
        filtered = filtered[filtered["alignment"].isin(selected_alignments)]

    if filtered.empty:
        fig = px.imshow([[0]], text_auto=True)
        fig.update_layout(
            title="No data for selected filters",
            xaxis={"visible": False},
            yaxis={"visible": False},
            annotations=[{"text": "No data to display", "xref": "paper", "yref": "paper",
                          "showarrow": False, "font": {"size": 20, "color": DARK_GRAY}}]
        )
        return fig

    summary = (
        filtered.groupby(["alignment", "offensive_formation_group"])["expected_points_added"]
        .mean()
        .reset_index()
    )
    pivot = summary.pivot(index="alignment", columns="offensive_formation_group", values="expected_points_added").fillna(0)

    fig = px.imshow(
        pivot,
        labels={"x": "Offensive Formation", "y": "Defensive Alignment", "color": "Avg EPA"},
        color_continuous_scale=[[0, LIGHT_GRAY], [0.5, WHITE], [1, DARK_GRAY]],
        text_auto=".2f",
        aspect="auto",
        origin="lower",
    )
    fig.update_layout(
        title="Average Expected Points Added (EPA) by Defensive Alignment and Offensive Formation",
        font=dict(color=DARK_GRAY),
    )
    fig.update_xaxes(tickangle=45)
    return fig


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)




