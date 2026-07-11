import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def render_ml_performance():
    if st.session_state.get("role") != "admin":
        st.switch_page("app.py")
        
    st.title("🤖 AI Model Performance")
    st.markdown("Monitor the health and accuracy of the platform's AI engines.")
    
    # Mock data for model performance
    models_data = {
        "Model": ["Fraud Detection", "Supplier Matching", "Price Recommendation", "Demand Forecasting"],
        "Type": ["Classification (XGBoost)", "Clustering (K-Means)", "Regression (Random Forest)", "Time Series (LSTM)"],
        "Accuracy / R2": [0.94, 0.88, 0.91, 0.85],
        "Precision": [0.92, 0.89, 0.90, 0.86],
        "Recall": [0.95, 0.85, 0.92, 0.84],
        "ROC-AUC": [0.96, 0.87, 0.93, 0.88],
        "Last Trained": ["2026-06-15", "2026-05-20", "2026-06-01", "2026-04-10"],
        "Status": ["Healthy", "Healthy", "Healthy", "Needs Retraining"]
    }
    
    df = pd.DataFrame(models_data)
    
    st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    
    # Visualize performance metrics
    st.subheader("📊 Model Metrics Comparison")
    
    fig = go.Figure()
    
    metrics = ["Accuracy / R2", "Precision", "Recall", "ROC-AUC"]
    for metric in metrics:
        fig.add_trace(go.Bar(
            name=metric,
            x=df["Model"],
            y=df[metric]
        ))
        
    fig.update_layout(
        barmode='group',
        title="AI Model Performance Metrics",
        xaxis_title="Model",
        yaxis_title="Score",
        template="plotly_dark"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Warnings
    needs_retraining = df[df["Status"] == "Needs Retraining"]
    if not needs_retraining.empty:
        st.warning("⚠️ The following models require retraining:")
        for _, row in needs_retraining.iterrows():
            st.markdown(f"- **{row['Model']}** (Last trained: {row['Last Trained']})")
