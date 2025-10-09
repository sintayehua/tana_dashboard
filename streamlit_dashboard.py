
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime

st.set_page_config(
    page_title="DE Africa Lake Tana Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem;
    }
    .alert-critical { background-color: #ffcccc; padding: 10px; border-radius: 5px; }
    .alert-warning { background-color: #fff0cc; padding: 10px; border-radius: 5px; }
    .alert-info { background-color: #ccf2ff; padding: 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_dashboard_data():
    try:
        water_ts = pd.read_csv('./dashboard_data/water_extent_timeseries.csv')
        seasonal = pd.read_csv('./dashboard_data/seasonal_patterns.csv')
        lakes_comp = pd.read_csv('./dashboard_data/lake_comparison.csv')
        
        with open('./dashboard_data/metrics.json', 'r') as f:
            metrics = json.load(f)
        with open('./dashboard_data/insights.json', 'r') as f:
            insights = json.load(f)
            
        lons = np.load('./dashboard_data/longitude_grid.npy')
        lats = np.load('./dashboard_data/latitude_grid.npy')
        water_freq = np.load('./dashboard_data/water_frequency_grid.npy')
        
        return {
            'water_timeseries': water_ts,
            'seasonal_data': seasonal,
            'lake_comparison': lakes_comp,
            'metrics': metrics,
            'insights': insights,
            'spatial_grid': {
                'lons': lons, 'lats': lats, 'water_freq': water_freq
            }
        }
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def main():
    st.markdown('<div class="main-header">💧 Digital Earth Africa - Lake Tana Monitoring Dashboard</div>', 
                unsafe_allow_html=True)
    #st.markdown("### Ethiopia's Largest Lake - Water Resource Management Platform")
    
    data = load_dashboard_data()
    if data is None:
        st.error("Please generate the dashboard data first using the data generation script.")
        return
    
    st.sidebar.header("Dashboard Controls")
    selected_view = st.sidebar.selectbox(
        "Select View:",
        ["Overview", "Time Series Analysis", "Ethiopian Lakes Comparison", "Policy & Action", "Management Insights"]
    )
    
    selected_region = st.sidebar.selectbox(
        "Focus Region:",
        ["Lake Tana", "Lake Abaya", "Lake Chamo", "Comparative View"]
    )
    
    if selected_view == "Overview":
        show_overview(data)
    elif selected_view == "Time Series Analysis":
        show_time_series(data)
    elif selected_view == "Ethiopian Lakes Comparison":
        show_regional_comparison(data)
    elif selected_view == "Policy & Action":
        show_policy_actions(data)
    elif selected_view == "Management Insights":
        show_management_insights(data)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Data Source:** Digital Earth Africa WOfS")
    st.sidebar.markdown("**Last Updated:** " + datetime.now().strftime("%Y-%m-%d"))

def show_overview(data):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🌍 Lake Tana Water Monitoring")
        
        #fig = create_water_frequency_map(data['spatial_grid'])
        #st.plotly_chart(fig, use_container_width=True)
        image = "compare.png"
        st.image(image)
        
        st.subheader("📊 Water Extent Trend (2020-2024)")
        ts_fig = px.line(
            data['water_timeseries'], 
            x='year', 
            y='water_extent_km2',
            markers=True,
            title="Annual Water Extent"
        )
        ts_fig.update_traces(line=dict(width=3), marker=dict(size=8))
        st.plotly_chart(ts_fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Key Metrics")
        
        metrics = data['metrics']
        
        col2_1, col2_2 = st.columns(2)
        
        with col2_1:
            st.metric("Current Water Area", f"{metrics['current_water_extent']:,.0f} km²")
            st.metric("Historical Peak", f"{metrics['peak_water_extent']:,.0f} km²")
            #st.metric("Historical Change", f"{metrics['percent_decline_since_1960']}%")
        
        with col2_2:
            st.metric("Annual Change Rate", f"{metrics['annual_change_rate']}%")
            st.metric("Population Impacted", f"{metrics['population_impacted']/1e6:.1f}M")
            #st.metric("Economic Impact", f"${metrics['economic_impact_million_usd']}M")
        
        # st.subheader("⚠️ Recent Alerts")
        # st.markdown('<div class="alert-info">Dry season water levels within normal range</div>', 
        #            unsafe_allow_html=True)
        # st.markdown('<div class="alert-warning">Rainy season onset delayed by 10 days</div>', 
        #            unsafe_allow_html=True)
    with col2:
        st.plotly_chart(create_health_gauge(data['metrics']), use_container_width=True)

def show_time_series(data):
    st.subheader("📈 Detailed Time Series Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Annual Trends", "Seasonal Patterns", "Statistical Analysis"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Scatter(x=data['water_timeseries']['year'], 
                          y=data['water_timeseries']['water_extent_km2'],
                          name="Water Extent", line=dict(width=4)),
                secondary_y=False,
            )
            
            fig.add_trace(
                go.Bar(x=data['water_timeseries']['year'], 
                      y=data['water_timeseries']['change_percent'],
                      name="Yearly Change", marker_color='green'),
                secondary_y=True,
            )
            
            fig.update_layout(title="Water Extent with Annual Change Percentage")
            fig.update_yaxes(title_text="Water Extent (km²)", secondary_y=False)
            fig.update_yaxes(title_text="Change (%)", secondary_y=True)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Trend Analysis")
            #st.metric("5-Year Change", "+2.2%")
            st.metric("Average Annual Change", "+0.4%")
            st.metric("Stability Index", "High")
    
    with tab2:
        seasonal_2024 = data['seasonal_data'][data['seasonal_data']['year'] == 2024]
        
        fig = px.line(seasonal_2024, x='month', y='water_frequency',
                     title="Seasonal Water Frequency Pattern (2024)")
        #st.plotly_chart(fig, use_container_width=True)
        st.plotly_chart(create_annual_cycle_plot(seasonal_2024), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Peak Season", "September", "Main rainy season")
        with col2:
            st.metric("Lowest Season", "June", "Pre-rainy season")

def show_regional_comparison(data):
    st.subheader("🏔️ Ethiopian Lakes Comparison")
    
    fig = px.bar(data['lake_comparison'], 
                 x='name', y=['area_2020', 'area_2024'],
                 barmode='group', 
                 title="Water Extent Comparison (2020 vs 2024)")
    st.plotly_chart(fig, use_container_width=True)
    
    fig = px.bar(data['lake_comparison'], 
                 x='name', y='change',
                 color='trend',
                 title="Percentage Change (2020-2024)")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Detailed Comparison Table")
    display_df = data['lake_comparison'].copy()
    display_df['area_2020'] = display_df['area_2020'].apply(lambda x: f"{x:,.0f} km²")
    display_df['area_2024'] = display_df['area_2024'].apply(lambda x: f"{x:,.0f} km²")
    display_df['change'] = display_df['change'].apply(lambda x: f"{x}%")
    
    st.dataframe(display_df, use_container_width=True)

def show_management_insights(data):
    insights = data['insights']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Key Findings")
        for finding in insights['key_findings']:
            st.info(f"• {finding}")
        
        st.subheader("🎯 Management Recommendations")
        for recommendation in insights['management_recommendations']:
            st.success(f"✓ {recommendation}")
    
    with col2:
        st.subheader("🌡️ Primary Causes")
        for cause in insights['primary_causes']:
            st.warning(f"⚠ {cause}")
        
        # st.subheader("🛰️ DE Africa Advantages")
        # for advantage in insights['de_africa_advantages']:
        #     st.markdown(f"🌟 {advantage}")
    # --- NEW: INCLUSIVITY AND HUMAN IMPACT SECTION ---
    # st.subheader("👥 Community & Inclusivity Focus")

    # col_i1, col_i2 = st.columns(2)

    # with col_i1:
    #     st.markdown("**Gender & Livelihood Impact**")
    #     st.markdown("""
    #     *   **Women & Water Fetching:** Changes in lake level directly impact the time and effort required for water collection, a task often falling to women and girls.
    #     *   **Smallholder Farmers:** Data on seasonal patterns helps plan planting schedules, securing food and income.
    #     *   **Fisherfolk:** Water quality and extent insights can be linked to fish stock health.
    #     """)

    # with col_i2:
    #     st.markdown("**Engagement & Data Equity**")
    #     st.markdown("""
    #     *   **Open Access:** This dashboard democratizes access to satellite data, previously available only to specialists.
    #     *   **Awareness Raising:** Visualizations help all communities understand the challenges and engage in conservation efforts.
    #     *   **Youth Engagement:** Interactive technology inspires the next generation of water resource professionals.
    #     """)

def create_annual_cycle_plot(seasonal_data):
    """
    Creates a polar plot showing the annual cycle of the lake's water extent.
    """
    # Assuming seasonal_data has 'month' and 'water_frequency'
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=seasonal_data['water_frequency'],
        theta=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        fill='toself',
        name='Water Frequency',
        line=dict(color='#1f77b4')
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1]),
        ),
        showlegend=False,
        title="The Annual Pulse of Lake Tana Region"
    )
    return fig

# In your show_time_series function, replace or supplement the seasonal plot:
# st.plotly_chart(create_annual_cycle_plot(seasonal_2024), use_container_width=True)

def create_water_frequency_map(spatial_data):
    fig = go.Figure(data=go.Heatmap(
        z=spatial_data['water_freq'],
        x=spatial_data['lons'][0],
        y=spatial_data['lats'][:,0],
        colorscale='Blues',
        hoverinfo='z+x+y',
        showscale=True
    ))
    
    fig.update_layout(
        title="Lake Tana Water Frequency Distribution",
        xaxis_title="Longitude",
        yaxis_title="Latitude",
        width=800,
        height=500
    )
    
    return fig

def create_health_gauge(metrics):
    # Calculate a simple index (this is a placeholder)
    # e.g., based on recent change, comparison to historical, etc.
    current = metrics['current_water_extent']
    peak = metrics['peak_water_extent']
    health_index = (current / peak) * 100 # Simple example

    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = health_index,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Historical Gauge"},
        delta = {'reference': 100, 'increasing': {'color': "green"}},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "red"},
                {'range': [50, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "green"}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': health_index}
        }
    ))
    fig.update_layout(height=300)
    return fig

def generate_policy_brief(data):
    """Generate a text-based policy brief"""
    metrics = data['metrics']
    
    brief = f"""
LAKE TANA WATER MONITORING - POLICY BRIEF
==========================================

KEY FINDINGS:
• Current Water Area: {metrics['current_water_extent']} km²
• Historical Change since 1960: {metrics['percent_decline_since_1960']}%
• {metrics['population_impacted']/1e6:.1f} million people depend on Lake Tana

PRIORITY RECOMMENDATIONS:
1. Sedimentation Control: Target watershed management in high-erosion areas
2. Smart Water Allocation: Use seasonal forecasts for irrigation planning
3. Ecological Conservation: Monitor and protect wetland ecosystems

DATA SOURCE: Digital Earth Africa WOfS
TIME PERIOD: 2020-2024
GENERATED ON: {datetime.now().strftime("%Y-%m-%d")}
"""
    return brief

def show_policy_actions(data):
    st.subheader("🚀 Data-Driven Policy & Actions")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Priority Interventions")
        st.markdown("""
        **1. Sedimentation Control:**
        *   **Action:** Target watershed management in areas with high soil loss.
        *   **Rationale:** The analysis identifies sedimentation as a key pressure.

        **2. Smart Water Allocation:**
        *   **Action:** Use seasonal forecasts for irrigation planning.
        *   **Rationale:** Maximizes productivity while minimizing waste.
        """)

    with col2:
        st.markdown("### Scaling Potential")
        st.markdown("""
        **This model can be replicated across Africa:**
        *   **Lake Victoria** (Kenya, Uganda, Tanzania)
        *   **Lake Chad** (Nigeria, Niger, Chad, Cameroon)
        """)
    
    # Download section
    st.markdown("---")
    st.subheader("📋 Download Resources")
    
    # Generate and offer the policy brief
    brief_text = generate_policy_brief(data)
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            label="📄 Download Policy Brief (TXT)",
            data=brief_text,
            file_name="lake_tana_policy_brief.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col_d2:
        # Optional: Add other download types
        st.download_button(
            label="📊 Download Key Data (CSV)",
            data=data['water_timeseries'].to_csv(index=False),
            file_name="lake_tana_water_extent.csv",
            mime="text/csv",
            use_container_width=True
        )

if __name__ == "__main__":
    main()
