# pes/analysis/reports/visualizations.py

"""Visualization generation for reports."""

import json
from typing import Dict, Any

from .schemas import FigureData


def generate_plot_html(figure: FigureData, chart_id: str) -> str:
    """
    Generate HTML/JavaScript for Chart.js plot.

    Args:
        figure: FigureData containing plot specification
        chart_id: Unique ID for the chart element

    Returns:
        HTML string with embedded Chart.js visualization
    """
    chart_config = _build_chartjs_config(figure)

    return f'''
<div class="chart-container">
    <h4>{figure.title}</h4>
    <canvas id="{chart_id}"></canvas>
    {f'<p><em>{figure.caption}</em></p>' if figure.caption else ''}
</div>
<script>
new Chart(document.getElementById('{chart_id}'), {json.dumps(chart_config)});
</script>
'''


def _build_chartjs_config(figure: FigureData) -> Dict[str, Any]:
    """Build Chart.js configuration from FigureData."""

    chart_type_map = {
        'bar': 'bar',
        'line': 'line',
        'scatter': 'scatter',
        'box': 'bar',  # Chart.js doesn't have native box plots
        'heatmap': 'bar'  # Simplified
    }

    config = {
        'type': chart_type_map.get(figure.figure_type, 'bar'),
        'data': figure.data,
        'options': {
            'responsive': True,
            'plugins': {
                'title': {
                    'display': True,
                    'text': figure.title
                }
            }
        }
    }

    if figure.x_label:
        config['options']['scales'] = config['options'].get('scales', {})
        config['options']['scales']['x'] = {'title': {'display': True, 'text': figure.x_label}}

    if figure.y_label:
        config['options']['scales'] = config['options'].get('scales', {})
        config['options']['scales']['y'] = {'title': {'display': True, 'text': figure.y_label}}

    return config
