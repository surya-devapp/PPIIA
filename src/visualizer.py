import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_timeline(events):
    """
    Generates a timeline of events.
    Expected events format: [{'date': 'YYYY-MM-DD', 'event': 'Description'}]
    """
    if not events:
        return go.Figure()
        
    df = pd.DataFrame(events)
    # Ensure dates are datetime objects
    try:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date']) # Drop events with unparseable dates
        df = df.sort_values('date')
    except Exception as e:
        # If basically no dates work, return empty or handle gracefully
        return go.Figure().update_layout(title=f"Could not parse timeline dates: {str(e)}")

    if df.empty:
         return go.Figure().update_layout(title="No valid dates found for timeline")

    # Stagger Y values to prevent overlap: 1, 2, 3, 4, 1, 2...
    # This creates vertical separation between timeline events
    y_values = [(i % 4) + 1 for i in range(len(df))]
    
    import textwrap
    # Wrap text to avoid extremely wide labels
    df['wrapped_event'] = df['event'].apply(lambda x: "<br>".join(textwrap.wrap(str(x), width=30)))

    # Enhanced Scatter plot
    fig = go.Figure(data=[go.Scatter(
        x=df['date'],
        y=y_values,
        text=df['wrapped_event'],
        mode='markers+text+lines', # Add lines to connect drops if we wanted (stem plot style), but strictly markers+text here
        textposition="top center",
        marker=dict(size=14, color='#1f77b4', line=dict(width=2, color='DarkSlateGrey')),
        textfont=dict(size=14, color='black') # Larger, readable font
    )])
    
    # Add vertical lines (stems) for a lollipop chart effect to ground the points?
    # For now, just keeping scattered points but staggered.
    
    fig.update_layout(
        title=dict(text="Legislative Timeline", font=dict(size=20)),
        xaxis=dict(title="Date", showgrid=True),
        yaxis=dict(visible=False, range=[0, 6]), # Hide Y axis ticks but ensure space for text
        height=500, # Taller plot
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor='rgba(240,240,240,0.5)' # Light background
    )
    return fig

def create_impact_chart(impact_data):
    """
    Generates a bar chart or heatmap for sector impact.
    Expected data: {'Agriculture': 'High', 'Tech': 'Medium', ...}
    """
    if not impact_data:
        return go.Figure()

    sectors = list(impact_data.keys())
    # Map levels to numbers for visualization
    level_map = {'High': 3, 'Medium': 2, 'Low': 1, 'Negative': -1, 'Positive': 1} # Simplified
    # Better mapping strategy:
    # If values are text descriptions, we might just list them.
    # If values are sentiment/scores:
    
    # Let's assume input might be categories like "Positive", "Negative", "Neutral" or numerical.
    # For now, let's just plot a simple categorization if possible.
    
    # If data is simple dict, convert to DF
    df = pd.DataFrame(list(impact_data.items()), columns=['Sector', 'Impact'])
    
    fig = px.bar(df, x='Sector', y='Impact', title="Sector Impact Overview")
    return fig
