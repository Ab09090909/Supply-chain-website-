import streamlit as st
import plotly.graph_objects as go
from engines.demand import forecast_demand

def render_demand_forecast(category: str, sector: str, region: str):
    """
    Renders a 30-day demand forecast chart.
    """
    st.subheader("📊 30-Day Demand Forecast")
    
    try:
        forecast = forecast_demand(category, sector, region)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=forecast["forecast_dates"],
            y=forecast["predicted_demand"],
            mode='lines+markers',
            name='Predicted Demand',
            line=dict(color='#2E86C1', width=3),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title=f"Demand Forecast for {category} in {region}",
            xaxis_title="Date",
            yaxis_title="Predicted Demand (Units)",
            template="plotly_dark",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Failed to generate forecast: {str(e)}")
