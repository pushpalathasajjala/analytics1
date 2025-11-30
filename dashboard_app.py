
import streamlit as st
import pandas as pd

import re

st.set_page_config(layout="wide")
st.title('Interactive Data Dashboard')
st.markdown("""
This dashboard provides interactive visualizations of the forecast data.
Use the filters on the sidebar to explore different aspects of the data.
""")

# Load Data
df = pd.read_excel('/content/forcats.xlsx')

# Prepare Data for Dashboard
id_vars = ['Area', 'Category', 'Subcategory', 'Model', 'MAE', 'RMSE', 'MAPE', 'Country_Type']
df_melted = pd.melt(df, id_vars=id_vars, var_name='Year', value_name='Predicted_Value')
df_melted['Year'] = df_melted['Year'].apply(lambda x: int(re.search(r'\d{4}', x).group(0)) if re.search(r'\d{4}', x) else None)
df_melted['Year'] = df_melted['Year'].astype(int)
df_melted = df_melted.rename(columns={'Area': 'Country'})

# Filter Options
st.sidebar.header('Filter Options')

selected_category = st.sidebar.multiselect(
    'Select Category',
    options=df_melted['Category'].unique(),
    default=df_melted['Category'].unique()
)

selected_country = st.sidebar.multiselect(
    'Select Country',
    options=df_melted['Country'].unique(),
    default=df_melted['Country'].unique()
)

min_year = int(df_melted['Year'].min())
max_year = int(df_melted['Year'].max())
selected_year_range = st.sidebar.slider(
    'Select Year Range',
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

filtered_df = df_melted[
    (df_melted['Category'].isin(selected_category)) &
    (df_melted['Country'].isin(selected_country)) &
    (df_melted['Year'] >= selected_year_range[0]) &
    (df_melted['Year'] <= selected_year_range[1])
]

st.write(f"Displaying data for {len(filtered_df)} rows after filtering.")

# Interactive Visualizations
if filtered_df.empty:
    st.warning("No data available for the selected filters.")
else:
    st.subheader('Interactive Visualizations')

    st.write("### 1. Predicted Value Trend Over Years by Category")
    fig_line = px.line(
        filtered_df.groupby(['Year', 'Category'])['Predicted_Value'].mean().reset_index(),
        x='Year',
        y='Predicted_Value',
        color='Category',
        title='Average Predicted Value Trend',
        hover_data={'Predicted_Value': ':.2f'}
    )
    st.plotly_chart(fig_line, width='stretch')

    st.write("### 2. Average Predicted Value by Country")
    fig_bar = px.bar(
        filtered_df.groupby('Country')['Predicted_Value'].mean().reset_index().sort_values(by='Predicted_Value', ascending=False),
        x='Country',
        y='Predicted_Value',
        color='Country',
        title='Average Predicted Value per Country',
        labels={'Predicted_Value': 'Average Predicted Value'},
        hover_data={'Predicted_Value': ':.2f'}
    )
    st.plotly_chart(fig_bar, width='stretch')

    st.write("### 3. MAE vs RMSE by Model")
    fig_scatter = px.scatter(
        filtered_df.dropna(subset=['MAE', 'RMSE']),
        x='MAE',
        y='RMSE',
        color='Model',
        hover_name='Subcategory',
        title='MAE vs RMSE by Model',
        log_x=True,
        log_y=True
    )
    st.plotly_chart(fig_scatter, width='stretch')

    st.write("### 4. Distribution of Predicted Value by Category")
    fig_box = px.box(
        filtered_df,
        x='Category',
        y='Predicted_Value',
        color='Category',
        title='Predicted Value Distribution by Category',
        hover_data={'Predicted_Value': ':.2f'}
    )
    st.plotly_chart(fig_box, width='stretch')

    st.write("### 5. Distribution of All Predicted Values")
    fig_hist = px.histogram(
        filtered_df,
        x='Predicted_Value',
        nbins=50,
        title='Distribution of Predicted Values',
        marginal='rug',
        hover_data={'Predicted_Value': ':.2f'}
    )
    st.plotly_chart(fig_hist, width='stretch')
