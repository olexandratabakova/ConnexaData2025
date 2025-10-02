import os
import logging
from collections import Counter
from dash import html, dcc
import plotly.express as px
import pandas as pd
import networkx as nx

def safe_file_operation(func):
    def wrapper(file_path, *args, **kwargs):
        try:
            if not os.path.exists(file_path):
                return None
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return func(file, *args, **kwargs)
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {str(e)}")
            return None

    return wrapper


@safe_file_operation
def count_occurrences(file):
    counter = Counter()
    for line in file:
        line = line.strip()
        if not line:
            continue
        parts = line.split(';')
        if len(parts) != 2:
            continue
        node1, node2 = map(str.strip, parts)
        if node1:
            counter[node1] += 1
        if node2:
            counter[node2] += 1
    return counter or None


@safe_file_operation
def calculate_influence(file):
    G = nx.Graph()
    for line in file:
        line = line.strip()
        if not line:
            continue
        parts = line.split(';')
        if len(parts) != 2:
            continue
        node1, node2 = map(str.strip, parts)
        if node1 and node2:
            G.add_edge(node1, node2)

    if G.number_of_nodes() == 0:
        return None

    isolates = list(nx.isolates(G))
    if isolates:
        G.remove_nodes_from(isolates)

    return dict(G.degree()) if G else None


def create_visualization(data, title, color):
    if not data:
        return html.Div(f"No data available for {title}", style={'color': 'gray'})
    try:
        filtered_data = {k: v for k, v in data.items() if v > 3}
        if not filtered_data:
            return html.Div(f"No significant data for {title} (all values ≤3)", style={'color': 'gray'})
        df = pd.DataFrame(filtered_data.items(), columns=["Object", "Count"])
        df = df.sort_values("Count", ascending=False).head(50)
        fig = px.bar(
            df,
            x="Object",
            y="Count",
            title=title,
            labels={"Object": "Object", "Count": "Count"},
            text_auto=True,
            color_discrete_sequence=[color],
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            template="plotly_white",
            margin=dict(l=40, r=40, t=40, b=40),
            height=400
        )
        return dcc.Graph(figure=fig)
    except Exception as e:
        logging.error(f"Visualization error: {str(e)}")
        return html.Div(f"Error creating {title} visualization", style={'color': 'red'})