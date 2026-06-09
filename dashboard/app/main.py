from __future__ import annotations

import os
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from dash import Dash, Input, Output, dcc, html

API_BASE_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000/api/v1")

app = Dash(__name__, title="Mobile Network Intelligence Dashboard")
server = app.server


def _fetch_json(endpoint: str) -> list[dict[str, Any]] | dict[str, Any]:
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return [] if endpoint != "/analytics/summary" else {}


def _summary_cards(summary: dict[str, Any]) -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.H4("Total Samples"),
                    html.P(str(summary.get("total_samples", 0))),
                ],
                className="metric-card",
            ),
            html.Div(
                [
                    html.H4("Active Users"),
                    html.P(str(summary.get("active_users", 0))),
                ],
                className="metric-card",
            ),
            html.Div(
                [
                    html.H4("Avg RSSI"),
                    html.P(f"{summary.get('avg_rssi', 0):.2f} dBm"),
                ],
                className="metric-card",
            ),
        ],
        style={"display": "grid", "gridTemplateColumns": "repeat(3, minmax(0, 1fr))", "gap": "12px"},
    )


app.layout = html.Div(
    [
        html.H2("AI-Powered Mobile Network Intelligence"),
        dcc.Interval(id="refresh", interval=60 * 1000, n_intervals=0),
        html.Div(id="summary-panels"),
        dcc.Graph(id="heatmap"),
        dcc.Graph(id="live-map"),
        dcc.Graph(id="operator-comparison"),
        dcc.Graph(id="signal-trend"),
        dcc.Graph(id="ai-predictions"),
    ],
    style={"maxWidth": "1200px", "margin": "0 auto", "padding": "16px"},
)


@app.callback(
    Output("summary-panels", "children"),
    Output("heatmap", "figure"),
    Output("live-map", "figure"),
    Output("operator-comparison", "figure"),
    Output("signal-trend", "figure"),
    Output("ai-predictions", "figure"),
    Input("refresh", "n_intervals"),
)
def refresh_dashboard(_: int):
    summary = _fetch_json("/analytics/summary")
    heatmap_data = _fetch_json("/analytics/heatmap")
    operator_data = _fetch_json("/analytics/operator-comparison")
    trend_data = _fetch_json("/analytics/trend?hours=24")

    heatmap_df = pd.DataFrame(heatmap_data)
    operator_df = pd.DataFrame(operator_data)
    trend_df = pd.DataFrame(trend_data)

    if heatmap_df.empty:
        empty_map = go.Figure().update_layout(title="No heatmap data")
        live_map = go.Figure().update_layout(title="No live map data")
    else:
        heatmap = px.density_mapbox(
            heatmap_df,
            lat="latitude",
            lon="longitude",
            z="avg_rssi",
            radius=20,
            color_continuous_scale="Turbo",
            zoom=3,
            map_style="open-street-map",
            title="Network Heatmap",
        )
        live_map = px.scatter_mapbox(
            heatmap_df,
            lat="latitude",
            lon="longitude",
            size="sample_count",
            color="avg_rssi",
            color_continuous_scale="RdYlGn",
            zoom=3,
            map_style="open-street-map",
            title="Live Signal Map",
        )
        empty_map = heatmap

    if operator_df.empty:
        operator_fig = go.Figure().update_layout(title="No operator data")
        ai_fig = go.Figure().update_layout(title="No AI prediction data")
    else:
        operator_fig = px.bar(
            operator_df,
            x="operator_name",
            y="avg_rssi",
            color="sample_count",
            title="Operator Comparison (Average RSSI)",
        )
        ai_fig = go.Figure()
        ai_fig.add_bar(name="Dead-Zone Rate", x=operator_df["operator_name"], y=operator_df["dead_zone_rate"])
        ai_fig.add_bar(name="Avg RSSI", x=operator_df["operator_name"], y=operator_df["avg_rssi"])
        ai_fig.update_layout(title="AI Prediction Panels", barmode="group")

    if trend_df.empty:
        trend_fig = go.Figure().update_layout(title="No trend data")
    else:
        trend_fig = px.line(
            trend_df,
            x="bucket",
            y="avg_rssi",
            markers=True,
            title="Signal Trend Analysis (24h)",
        )
        trend_fig.update_xaxes(title="Time")
        trend_fig.update_yaxes(title="Average RSSI (dBm)")

    return _summary_cards(summary), empty_map, live_map, operator_fig, trend_fig, ai_fig


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
