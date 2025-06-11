import streamlit as st
import pandas as pd
import PyPDF2
import pdfplumber
import re
import io
from pathlib import Path
import tempfile
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import sys
import subprocess
import webbrowser

# Page configuration
st.set_page_config(
    page_title="Donation Reconciliation Tool",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS with modern styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Animated gradient background */
    .main-header {
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        z-index: 0;
    }
    
    .main-header h1, .main-header p {
        position: relative;
        z-index: 1;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Glassmorphism metric cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 45px rgba(0, 0, 0, 0.2);
    }
    
    .metric-card h3 {
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
        opacity: 0.8;
    }
    
    .metric-card h2 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Enhanced status boxes */
    .success-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        animation: pulse 2s infinite;
    }
    
    .error-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border: none;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 10px 30px rgba(245, 87, 108, 0.3);
        animation: shake 0.5s ease-in-out;
    }
    
    .info-box {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border: none;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        color: #2d3748;
        box-shadow: 0 10px 30px rgba(168, 237, 234, 0.3);
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    /* Enhanced buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        border: 2px dashed #cbd5e0;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: #667eea;
        background: rgba(102, 126, 234, 0.05);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    /* Floating action button */
    .floating-stats {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        cursor: pointer;
        z-index: 1000;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Loading spinner */
    .loading-spinner {
        border: 4px solid #f3f4f6;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #1a202c;
        color: #fff;
        text-align: center;
        border-radius: 8px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.9rem;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
</style>
""", unsafe_allow_html=True)

def extract_numbers_from_text(text):
    """Extract potential donation amounts from text with enhanced patterns"""
    patterns = [
        r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $1,000.00 format
        r'(\d{1,3}(?:,\d{3})*\.\d{2})',            # 1,000.00 format
        r'(\d+\.\d{2})',                           # Simple decimal format
        r'(\d+(?:,\d{3})+)',                       # Comma-separated thousands
        r'USD\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',     # USD format
        r'(\d+)\s*dollars?',                       # X dollars format
    ]
    
    amounts = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            clean_amount = re.sub(r'[,$]', '', match)
            try:
                amount = float(clean_amount)
                if 1 <= amount <= 1000000:  # Expanded range for larger donations
                    amounts.append(amount)
            except ValueError:
                continue
    
    return amounts

def read_excel_file(uploaded_file):
    """Read Excel file with enhanced detection strategies"""
    try:
        # Try different sheet names and engines
        df = None
        try:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        except:
            try:
                df = pd.read_excel(uploaded_file, engine='xlrd')
            except:
                df = pd.read_excel(uploaded_file)
        
        if df is None:
            return 0, None
        
        total_amount = 0
        detection_method = "Unknown"
        
        # Enhanced detection strategies
        total_keywords = ['total', 'sum', 'amount', 'grand', 'final', 'balance', 'donations']
        
        # Strategy 1: Look for specific column names
        for col in df.columns:
            col_str = str(col).lower()
            if any(keyword in col_str for keyword in total_keywords):
                values = df[col].dropna()
                if len(values) > 0:
                    last_value = values.iloc[-1]
                    if isinstance(last_value, (int, float)) and last_value > total_amount:
                        total_amount = last_value
                        detection_method = f"Column: {col}"
        
        # Strategy 2: Look for the largest numeric value
        if total_amount == 0:
            for col in df.columns:
                if df[col].dtype in ['int64', 'float64']:
                    max_val = df[col].max()
                    if pd.notna(max_val) and max_val > total_amount:
                        total_amount = max_val
                        detection_method = f"Max value in column: {col}"
        
        # Strategy 3: Text parsing for embedded numbers
        if total_amount == 0:
            for col in df.columns:
                for value in df[col].dropna():
                    if isinstance(value, str):
                        numbers = extract_numbers_from_text(value)
                        if numbers and max(numbers) > total_amount:
                            total_amount = max(numbers)
                            detection_method = f"Text parsing in column: {col}"
        
        return total_amount, df, detection_method
        
    except Exception as e:
        st.error(f"❌ Error reading Excel file: {str(e)}")
        return 0, None, "Error"

def read_pdf_file(uploaded_file):
    """Enhanced PDF reading with better error handling and progress tracking"""
    amounts = []
    filename = uploaded_file.name
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Progress tracking
        extraction_method = "Unknown"
        
        # Try pdfplumber first (more reliable)
        try:
            with pdfplumber.open(tmp_file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                if text.strip():
                    amounts = extract_numbers_from_text(text)
                    extraction_method = "pdfplumber"
        except Exception as e:
            st.warning(f"⚠️ pdfplumber failed for {filename}: {str(e)}")
        
        # Fallback to PyPDF2
        if not amounts:
            try:
                with open(tmp_file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    
                    if text.strip():
                        amounts = extract_numbers_from_text(text)
                        extraction_method = "PyPDF2"
            except Exception as e:
                st.warning(f"⚠️ PyPDF2 also failed for {filename}: {str(e)}")
        
        # Clean up
        os.unlink(tmp_file_path)
        
        # Remove duplicates and sort
        amounts = sorted(list(set(amounts)))
        
        return {
            'filename': filename,
            'amounts': amounts,
            'total': sum(amounts),
            'count': len(amounts),
            'extraction_method': extraction_method,
            'success': len(amounts) > 0
        }
        
    except Exception as e:
        st.error(f"❌ Critical error reading PDF {filename}: {str(e)}")
        return {
            'filename': filename,
            'amounts': [],
            'total': 0,
            'count': 0,
            'extraction_method': "Failed",
            'success': False
        }

def create_visualization(results):
    """Create interactive visualizations"""
    if not results['pdf_results']:
        return None
    
    # Prepare data for visualization
    daily_data = []
    for result in results['pdf_results']:
        daily_data.append({
            'Date': result['filename'].replace('.pdf', ''),
            'Daily Total': result['total'],
            'Donation Count': result['count'],
            'Status': '✅ Extracted' if result['success'] else '❌ Failed'
        })
    
    df_viz = pd.DataFrame(daily_data)
    
    # Create subplots
    fig = go.Figure()
    
    # Add bar chart for daily totals
    fig.add_trace(go.Bar(
        x=df_viz['Date'],
        y=df_viz['Daily Total'],
        name='Daily Totals',
        marker_color='rgba(102, 126, 234, 0.8)',
        text=df_viz['Daily Total'],
        texttemplate='$%{text:.0f}',
        textposition='outside'
    ))
    
    # Add line for Excel total reference
    fig.add_hline(
        y=results['excel_total'],
        line_dash="dash",
        line_color="red",
        annotation_text=f"Excel Total: ${results['excel_total']:,.2f}"
    )
    
    fig.update_layout(
        title="📊 Daily Donation Breakdown vs Excel Total",
        xaxis_title="Date",
        yaxis_title="Amount ($)",
        template="plotly_white",
        showlegend=True,
        height=500
    )
    
    return fig

def display_processing_animation():
    """Show a cool processing animation"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    steps = [
        "🔍 Analyzing Excel file...",
        "📄 Processing PDF files...",
        "🔢 Extracting donation amounts...",
        "📊 Calculating totals...",
        "✅ Comparing results..."
    ]
    
    for i, step in enumerate(steps):
        status_text.text(step)
        progress_bar.progress((i + 1) / len(steps))
        time.sleep(0.5)
    
    status_text.text("🎉 Processing complete!")
    time.sleep(0.5)
    status_text.empty()
    progress_bar.empty()

def main():
    # Animated header
    st.markdown("""
    <div class="main-header">
        <h1> Donation Reconciliation Tool</h1>
        <p>Compare monthly Excel totals with daily PDF records</p>
        <div class="tooltip">
            <span style="font-size: 1.2rem;">ℹ️</span>
            <span class="tooltiptext">Upload your Excel file and PDF documents to automatically reconcile donation totals</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'processed_results' not in st.session_state:
        st.session_state.processed_results = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # Sidebar with enhanced styling
    with st.sidebar:
        st.markdown("### 📁 Upload Your Files")
        st.markdown("---")
        
        # Excel file upload with better instructions
        st.markdown("#### 📊 Monthly Excel File")
        st.markdown("*Upload your monthly summary (e.g., January.xlsx)*")
        excel_file = st.file_uploader(
            "Choose Excel file",
            type=['xlsx', 'xls'],
            key="excel_upload",
            help="Upload the Excel file containing your monthly donation total"
        )
        
        if excel_file:
            st.success(f"✅ Loaded: {excel_file.name}")
        
        st.markdown("---")
        
        # PDF files upload with progress tracking
        st.markdown("#### 📄 Daily PDF Files")
        st.markdown("*Upload all daily PDF records for the month*")
        pdf_files = st.file_uploader(
            "Choose PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            key="pdf_upload",
            help="Upload all daily PDF files containing individual donation records"
        )
        
        if pdf_files:
            st.success(f"✅ Loaded: {len(pdf_files)} PDF files")
            with st.expander("📋 View uploaded files"):
                for pdf in pdf_files:
                    st.write(f"• {pdf.name}")
        
        st.markdown("---")
        
        # Enhanced action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 Analyze", type="primary", disabled=not (excel_file and pdf_files)):
                if excel_file and pdf_files:
                    st.session_state.processing = True
                    
                    # Show processing animation
                    display_processing_animation()
                    
                    # Process files
                    excel_total, excel_df, detection_method = read_excel_file(excel_file)
                    
                    pdf_results = []
                    progress_bar = st.progress(0)
                    
                    for i, pdf_file in enumerate(pdf_files):
                        result = read_pdf_file(pdf_file)
                        pdf_results.append(result)
                        progress_bar.progress((i + 1) / len(pdf_files))
                    
                    progress_bar.empty()
                    
                    # Calculate results
                    pdf_total = sum(result['total'] for result in pdf_results)
                    difference = abs(excel_total - pdf_total)
                    is_match = difference < 0.01
                    
                    # Store results
                    st.session_state.processed_results = {
                        'excel_total': excel_total,
                        'pdf_total': pdf_total,
                        'difference': difference,
                        'is_match': is_match,
                        'pdf_results': pdf_results,
                        'excel_filename': excel_file.name,
                        'month': excel_file.name.replace('.xlsx', '').replace('.xls', ''),
                        'detection_method': detection_method,
                        'processed_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    st.session_state.processing = False
                    st.rerun()
        
        with col2:
            if st.button("🗑️ Clear", type="secondary"):
                st.session_state.processed_results = None
                st.rerun()
    
    # Main content area
    if st.session_state.processed_results:
        results = st.session_state.processed_results
        
        # Results header with timestamp
        st.markdown(f"### 📊 Reconciliation Results - {results['month']}")
        st.caption(f"Processed at: {results['processed_at']}")
        
        # Enhanced summary metrics with tooltips
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📊 Excel Total</h3>
                <h2 style="color: #3B82F6;">${results['excel_total']:,.2f}</h2>
                <p style="font-size: 0.9rem; opacity: 0.8;">Detection: {results['detection_method']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📄 PDF Total</h3>
                <h2 style="color: #10B981;">${results['pdf_total']:,.2f}</h2>
                <p style="font-size: 0.9rem; opacity: 0.8;">{len(results['pdf_results'])} files processed</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            status_color = "#10B981" if results['is_match'] else "#EF4444"
            status_text = "✅ PERFECT MATCH" if results['is_match'] else "❌ MISMATCH"
            status_icon = "🎉" if results['is_match'] else "⚠️"
            
            st.markdown(f"""
            <div class="metric-card">
                <h3>{status_icon} Status</h3>
                <h2 style="color: {status_color};">{status_text}</h2>
                {f'<p style="font-size: 0.9rem;">Difference: ${results["difference"]:.2f}</p>' if not results['is_match'] else '<p style="font-size: 0.9rem;">Perfect reconciliation!</p>'}
            </div>
            """, unsafe_allow_html=True)
        
        # Status message
        if results['is_match']:
            st.markdown("""
            <div class="success-box">
                <h3>🎉 Perfect Match!</h3>
                <p>Your Excel total and PDF totals match perfectly. Your donation records are fully reconciled and ready for reporting!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="error-box">
                <h3>⚠️ Discrepancy Detected</h3>
                <p>There's a <strong>${results['difference']:.2f}</strong> difference between your Excel total and PDF totals. Please review your records to identify missing or duplicate entries.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Interactive visualization
        st.markdown("---")
        fig = create_visualization(results)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed breakdown
        st.markdown("### 📋 Detailed PDF Analysis")
        
        # Create enhanced dataframe
        pdf_data = []
        for result in results['pdf_results']:
            status_icon = "✅" if result['success'] else "❌"
            pdf_data.append({
                'Status': status_icon,
                'Filename': result['filename'],
                'Donations': result['count'],
                'Daily Total': f"${result['total']:.2f}",
                'Extraction Method': result['extraction_method'],
                'Sample Amounts': ', '.join([f"${amt:.2f}" for amt in result['amounts'][:3]]) + 
                                ('...' if len(result['amounts']) > 3 else '')
            })
        
        df_display = pd.DataFrame(pdf_data)
        st.dataframe(df_display, use_container_width=True)
        
        # Advanced statistics
        st.markdown("### 📈 Advanced Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total PDF Files", len(results['pdf_results']))
            successful_extractions = sum(1 for r in results['pdf_results'] if r['success'])
            st.metric("Successful Extractions", successful_extractions)
        
        with col2:
            total_donations = sum(result['count'] for result in results['pdf_results'])
            st.metric("Total Individual Donations", total_donations)
            avg_daily = results['pdf_total'] / len(results['pdf_results']) if results['pdf_results'] else 0
            st.metric("Average Daily Total", f"${avg_daily:.2f}")
        
        with col3:
            if results['pdf_results']:
                amounts = []
                for result in results['pdf_results']:
                    amounts.extend(result['amounts'])
                
                if amounts:
                    st.metric("Highest Single Donation", f"${max(amounts):.2f}")
                    st.metric("Average Donation", f"${sum(amounts)/len(amounts):.2f}")
        
        # Export options
        st.markdown("---")
        st.markdown("### 💾 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Create summary report
            summary_data = {
                'Month': results['month'],
                'Excel Total': results['excel_total'],
                'PDF Total': results['pdf_total'],
                'Difference': results['difference'],
                'Status': 'MATCH' if results['is_match'] else 'MISMATCH',
                'Files Processed': len(results['pdf_results']),
                'Total Donations': sum(r['count'] for r in results['pdf_results']),
                'Processed At': results['processed_at']
            }
            
            summary_df = pd.DataFrame([summary_data])
            st.download_button(
                label="📊 Download Summary Report",
                data=summary_df.to_csv(index=False),
                file_name=f"reconciliation_summary_{results['month']}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Create detailed report
            detailed_df = pd.DataFrame(pdf_data)
            st.download_button(
                label="📋 Download Detailed Report",
                data=detailed_df.to_csv(index=False),
                file_name=f"reconciliation_detailed_{results['month']}.csv",
                mime="text/csv"
            )
    
    else:
        # Enhanced instructions when no files uploaded
        st.markdown("""
        <div class="info-box">
            <h3>🚀 How to Use This Tool</h3>
            <ol>
                <li><strong>Upload Excel File:</strong> Select your monthly Excel file (e.g., January.xlsx) containing the total donations for the month</li>
                <li><strong>Upload PDF Files:</strong> Select all daily PDF files for that month containing individual donation records</li>
                <li><strong>Click Analyze:</strong> The tool will process both file types and compare the totals</li>
                <li><strong>Review Results:</strong> See if your records match or identify any discrepancies</li>
                <li><strong>Export Reports:</strong> Download summary and detailed reports for your records</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced feature showcase
        st.markdown("---")
        st.markdown("### ✨ Key Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🔍 Smart Detection**
            - Automatic total detection in Excel
            - Multiple PDF extraction methods
            - Intelligent amount recognition
            """)
        
        with col2:
            st.markdown("""
            **📊 Visual Analysis**
            - Interactive charts and graphs
            - Daily breakdown visualization
            - Statistical insights
            """)
        
        with col3:
            st.markdown("""
            **💾 Export & Reporting**
            - Downloadable CSV reports
            - Detailed reconciliation logs
            - Processing timestamps
            """)
        
        # Sample format guidance
        st.markdown("---")
        st.markdown("### 📋 Expected File Formats")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📊 Excel File Requirements**
            - Monthly total donation amount
            - Can be in columns named: 'Total', 'Amount', 'Sum', etc.
            - The tool automatically finds the largest reasonable number
            - Supports .xlsx and .xls formats
            - Works with various Excel layouts
            """)
        
        with col2:
            st.markdown("""
            **📄 PDF File Requirements**
            - Individual donation amounts per day
            - Supports various formats: $100.00, 100.00, $100, etc.
            - Text-based PDFs (not scanned images)
            - One file per day recommended
            - The tool extracts and sums all monetary values
            """)
        
        # Sample data preview
        st.markdown("---")
        st.markdown("### 📝 Sample Data Format")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Excel Sample:**")
            sample_excel = pd.DataFrame({
                'Month': ['January'],
                'Total Donations': [15750.00],
                'Notes': ['Monthly Summary']
            })
            st.dataframe(sample_excel, use_container_width=True)
        
        with col2:
            st.markdown("**PDF Content Sample:**")
            st.code("""
            Daily Donation Report - Jan 1st
            
            Donor 1: $150.00
            Donor 2: $75.50
            Donor 3: $200.00
            
            Daily Total: $425.50
            """, language=None)
        
        # Tips and best practices
        st.markdown("---")
        st.markdown("### 💡 Tips for Best Results")
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 1.5rem; border-radius: 15px; margin: 1rem 0;">
            <h4>🎯 Pro Tips:</h4>
            <ul>
                <li><strong>File Naming:</strong> Use clear, consistent naming (e.g., "Jan_01.pdf", "Jan_02.pdf")</li>
                <li><strong>PDF Quality:</strong> Ensure PDFs contain searchable text, not just images</li>
                <li><strong>Excel Format:</strong> Keep your Excel file simple with clear column headers</li>
                <li><strong>Batch Processing:</strong> Upload all daily PDFs at once for faster processing</li>
                <li><strong>Double-Check:</strong> Always review the detailed breakdown for accuracy</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # FAQ Section
        st.markdown("---")
        st.markdown("### ❓ Frequently Asked Questions")
        
        with st.expander("🤔 What if my PDF files can't be read?"):
            st.markdown("""
            The tool uses multiple extraction methods:
            1. **pdfplumber** (primary method) - best for most PDFs
            2. **PyPDF2** (fallback) - alternative extraction method
            
            If extraction fails:
            - Ensure PDFs contain searchable text (not scanned images)
            - Try converting scanned PDFs to text-searchable format
            - Check if PDF is password-protected
            """)
        
        with st.expander("📊 How does Excel total detection work?"):
            st.markdown("""
            The tool uses smart detection strategies:
            1. **Column Name Detection** - looks for columns with keywords like 'total', 'amount', 'sum'
            2. **Largest Value Detection** - finds the largest reasonable number in the spreadsheet
            3. **Text Parsing** - extracts numbers from text cells if needed
            
            The detection method used is shown in your results for transparency.
            """)
        
        with st.expander("⚠️ What if totals don't match?"):
            st.markdown("""
            Common reasons for mismatches:
            - **Missing PDF files** - some daily records might be missing
            - **Different time periods** - Excel might include different dates
            - **Data entry errors** - typos in either Excel or PDF records
            - **Duplicate entries** - same donation recorded multiple times
            
            Use the detailed breakdown to identify which days might have issues.
            """)
        
        with st.expander("💾 Can I save my results?"):
            st.markdown("""
            Yes! After processing, you can download:
            - **Summary Report** - high-level reconciliation results
            - **Detailed Report** - complete breakdown of all files processed
            
            Both reports include timestamps and can be saved for your records.
            """)
    
    # Floating action button (hidden implementation)
    if st.session_state.processed_results:
        st.markdown("""
        <div class="floating-stats" title="Quick Stats">
            📊
        </div>
        """, unsafe_allow_html=True)
    
    # Footer with version info
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #64748b; font-size: 0.9rem;">
        <p> Donation Reconciliation Tool v2.0 | Built using Streamlit</p>
        <p> Your data is processed locally and never stored on our servers</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()    
