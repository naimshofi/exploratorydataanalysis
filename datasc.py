import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io 

# Set page config first
st.set_page_config(page_title='Analyze Your Data', layout='wide', page_icon='📊')

st.title('📊 Analyze Your Data')
st.markdown("""
<div style='background-color: #e3f2fd; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #3498db; margin: 1rem 0;'>
    <h3 style='color: #2c3e50; margin-top: 0;'>🚀 Start analyzing your data in 3 steps:</h3>
    <ol style='color: #34495e; font-size: 1.05rem;'>
        <li><strong>Browse files</strong></li>
        <li><strong>Select your file</strong></li>
        <li><strong>Open the file</strong></li>
    </ol>
    <p style='color: #2c3e50; margin-top: 1rem; margin-bottom: 0;'>
        Upload a <strong>CSV</strong> or an <strong>Excel</strong> file to explore your data interactively!
    </p>
</div>
""", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader('📁 Upload CSV or Excel file', type=['csv','xlsx'])

if uploaded_file is not None:
    try:
        file_name = uploaded_file.name
        
        if file_name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        elif file_name.endswith(('.xlsx','.xls')):
            data = pd.read_excel(uploaded_file)

        bool_col = data.select_dtypes(include=['bool','object']).columns
        data[bool_col] = data[bool_col].astype('str')
        
        st.success('✅ File uploaded successfully!')
        
    except Exception as e:
        st.error('❌ Could not read the file.')
        st.exception(e)
        st.stop()

    st.markdown('---')
    
    st.write('### 🔎 Preview Of Data')
    st.dataframe(data.head(), width='stretch')

    st.write('### 📇 Data Overview')
    
    # Create metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rows", f"{data.shape[0]:,}")
    with col2:
        st.metric("Columns", data.shape[1])
    with col3:
        st.metric("Missing Values", f"{data.isnull().sum().sum():,}")
    with col4:
        st.metric("Duplicates", data.duplicated().sum())

    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "📜 Data Summary",
        "📑 Statistical Summary (Numerical)",
        "🧾 Statistical Summary (Non-Numerical)"
    ])

    with tab1:
        st.write("### 📜 Complete Summary Of Dataset")
        buffer = io.StringIO()
        data.info(buf=buffer)
        info_str = buffer.getvalue()
        st.text_area("Dataset Info", info_str, height=300)

    with tab2:
        if not data.select_dtypes(include=["number"]).empty:
            st.write("### 📑 Statistical Summary of Dataset")
            st.dataframe(data.describe(), width='stretch')
        else:
            st.warning("No numerical data available to summarize.")

    with tab3:
        if not data.select_dtypes(include=["bool", "object"]).empty:
            st.write("### 🧾 Statistical Summary of Dataset (Non-Numerical)")
            summary_non_num = data.describe(include=[bool, object]).astype(str)
            st.dataframe(summary_non_num, width='stretch')
        else:
            st.warning("No non-numerical data available to summarize.")

    st.markdown('---')
    
    st.write('### ✂️ Select Desired Column For Further Analysis')
    selected_col = st.multiselect('Choose columns to display:', data.columns.to_list())

    if selected_col:
        num_rows = st.slider('Number of rows to display:', 5, min(len(data), 100), 10)
        st.dataframe(data[selected_col].head(num_rows), width='stretch')
    else:
        st.info('No column selected. Showing all columns instead.')
        st.dataframe(data.head(), width='stretch')

    st.markdown('---')
    
    st.write('### 📈 Data Visualization')
    
    with st.expander("ℹ️ Visualization Settings"):
        st.info('''
        **Note:** Only the first 1000 rows of data will be used for visualization to minimize loading time.
        For best results:
        1. Choose appropriate X and Y axes for your chart type
        2. Pie charts only use data from the X-axis
        3. Ensure your selected columns have compatible data types
        ''')
    
    show_all_data = st.checkbox('Show all available data. **it may cause longer processing time')

    if show_all_data:
        data_viz = data
    else:
        data_viz = data.head(1000)  
    
    columns = data_viz.columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        x_axis = st.selectbox('X-axis:', options=columns, key='x_axis')
    with col2:
        y_axis = st.selectbox('Y-axis:', options=columns, key='y_axis')

    # Check if x_axis and y_axis are the same
    if x_axis == y_axis:
        agg_options = ["Raw"]   # only allow Raw
        st.warning("⚠️ Sum and Average are disabled because X-axis and Y-axis are the same column.")
    else:
        agg_options = ["Raw", "Sum", "Average"]

    agg_option = st.radio(
        "Select how to aggregate data:",
        options=agg_options,
        horizontal=True
    )

    # Apply aggregation if needed
    if agg_option == "Sum":
        data_viz = data_viz.groupby(x_axis)[y_axis].sum().reset_index()
    elif agg_option == "Average":
        data_viz = data_viz.groupby(x_axis)[y_axis].mean().reset_index()
    # Raw = no change

    st.write("##### Select Visualization Type:")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        line_btn = st.button('📈 Line Chart', use_container_width=True)
    with col2:
        scatter_btn = st.button('🔵 Scatter Plot', use_container_width=True)
    with col3:
        bar_btn = st.button('📊 Bar Chart', use_container_width=True)
    with col4:
        pie_btn = st.button('🥧 Pie Chart', use_container_width=True)

    st.write("*Pie chart will only generate values from X-axis")

    if line_btn:
        st.write(f'### 📈 Line Chart: {x_axis} vs {y_axis} ({agg_option})')
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(data_viz[x_axis], data_viz[y_axis], color='#3498db', linewidth=2)
        ax.set_xlabel(x_axis, fontsize=12)
        ax.set_ylabel(y_axis, fontsize=12)
        ax.tick_params(axis="x", rotation=45)
        ax.set_title(f'Line Graph of {x_axis} vs {y_axis} ({agg_option})', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)

    if scatter_btn:
        st.write(f'### 🔵 Scatter Plot: {x_axis} vs {y_axis} ({agg_option})')
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(data_viz[x_axis], data_viz[y_axis], color='#3498db', alpha=0.6)
        ax.set_xlabel(x_axis, fontsize=12)
        ax.set_ylabel(y_axis, fontsize=12)
        ax.tick_params(axis="x", rotation=45)
        ax.set_title(f'Scatter Plot of {x_axis} vs {y_axis} ({agg_option})', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)

    if bar_btn:
        st.write(f'### 📊 Bar Chart: {x_axis} vs {y_axis} ({agg_option})')
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(data_viz[x_axis], data_viz[y_axis], color='#3498db')
        ax.set_xlabel(x_axis, fontsize=12)
        ax.set_ylabel(y_axis, fontsize=12)
        ax.tick_params(axis="x", rotation=90)
        ax.set_title(f'Bar Chart of {x_axis} vs {y_axis} ({agg_option})', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)

    if pie_btn:
        st.write(f'### 🥧 Pie Chart: {x_axis} Distribution ({agg_option})')
        x_axis_counts = data_viz[x_axis].value_counts().head(10)  # Limit to top 10
        fig, ax = plt.subplots(figsize=(8, 8))
        colors = plt.cm.Set3(np.linspace(0, 1, len(x_axis_counts)))
        ax.pie(x_axis_counts.values, labels=x_axis_counts.index, autopct='%1.1f%%',
            colors=colors, startangle=90)
        ax.set_title(f'Distribution of {x_axis} ({agg_option})', fontsize=14, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)

# Add footer when no file is uploaded
if uploaded_file is None:
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #7f8c8d; margin-top: 3rem;'>
        <p>📊 <strong>Data Analysis Tool</strong> | Upload a file to begin analysis</p>
    </div>
    """, unsafe_allow_html=True)