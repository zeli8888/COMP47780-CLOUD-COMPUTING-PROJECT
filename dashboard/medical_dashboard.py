#!/usr/bin/env python3
"""
Medical Appointment Behavior Analysis Dashboard
zeli8888.ccproject.patient_behavior
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Medical Appointment Analysis System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

class MedicalDashboard:
    def __init__(self, data_file='patient_demographics_results.txt'):
        self.data = self.load_data(data_file)
        self.processed_data = self.process_data()
        
    def load_data(self, file_path):
        """Load MapReduce output data"""
        data = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '\t' in line:
                        key, value = line.strip().split('\t')
                        data[key] = int(value)
            st.success(f"Successfully loaded {len(data)} analysis records")
        except FileNotFoundError:
            st.error(f"Data file not found: {file_path}")
            st.info("Please ensure patient_demographics_results.txt is in the current directory")
            return {}
        return data
    
    def process_data(self):
        """Process data for visualization"""
        processed = {
            'gender': {},
            'age_groups': {},
            'detailed_age': {},
            'health_conditions': {},
            'neighbourhoods': {},
            'risk_groups': {},
            'sms_intervention': {},
            'lead_time': {}
        }
        
        for key, value in self.data.items():
            # Gender analysis
            if key.startswith('GENDER'):
                parts = key.split('_')
                gender = parts[1]
                status = parts[2]
                if gender not in processed['gender']:
                    processed['gender'][gender] = {'Attended': 0, 'NoShow': 0}
                processed['gender'][gender][status] = value
                
            # Age group analysis
            elif key.startswith('AGE_GROUP_BEHAVIOR'):
                parts = key.split('_')
                age_group = parts[3] + '_' + parts[4]
                status = parts[5]
                if age_group not in processed['age_groups']:
                    processed['age_groups'][age_group] = {'Attended': 0, 'NoShow': 0}
                processed['age_groups'][age_group][status] = value
                
            # Detailed age analysis
            elif key.startswith('DETAILED_AGE'):
                parts = key.split('_')
                age_range = parts[2]
                status = parts[3]
                if age_range not in processed['detailed_age']:
                    processed['detailed_age'][age_range] = {'Attended': 0, 'NoShow': 0}
                processed['detailed_age'][age_range][status] = value
                
            # Health conditions analysis
            elif key.startswith('HEALTH_'):
                parts = key.split('_')
                condition = parts[1]
                if len(parts) > 3 and parts[2].isdigit():  # Multiple diseases
                    condition = f"{parts[1]}_{parts[2]}_DISEASES"
                status = parts[-1]
                if condition not in processed['health_conditions']:
                    processed['health_conditions'][condition] = {'Attended': 0, 'NoShow': 0}
                processed['health_conditions'][condition][status] = value
                
            # Neighborhood analysis
            elif key.startswith('NEIGHBOURHOOD_'):
                parts = key.split('_')
                # Handle neighborhood names that may contain multiple underscores
                neighborhood_parts = parts[1:-1]  # All parts except first and last
                neighborhood = '_'.join(neighborhood_parts)
                status = parts[-1]
                if neighborhood not in processed['neighbourhoods']:
                    processed['neighbourhoods'][neighborhood] = {'Attended': 0, 'NoShow': 0}
                processed['neighbourhoods'][neighborhood][status] = value
                
            # Risk groups
            elif key.startswith('RISK_GROUP_'):
                parts = key.split('_')
                risk_group = '_'.join(parts[2:-1])
                status = parts[-1]
                if risk_group not in processed['risk_groups']:
                    processed['risk_groups'][risk_group] = {'Attended': 0, 'NoShow': 0}
                processed['risk_groups'][risk_group][status] = value
                
            # SMS intervention
            elif key.startswith('SMS_'):
                parts = key.split('_')
                sms_group = parts[1] + '_' + parts[2]
                status = parts[3]
                if sms_group not in processed['sms_intervention']:
                    processed['sms_intervention'][sms_group] = {'Attended': 0, 'NoShow': 0}
                processed['sms_intervention'][sms_group][status] = value
                
            # Lead time analysis - FIXED
            elif key.startswith('LEAD_TIME_'):
                parts = key.split('_')
                # Extract lead time category (everything between LEAD_TIME and status)
                lead_time_parts = parts[2:-1]  # Parts between 'LEAD_TIME' and status
                lead_time = '_'.join(lead_time_parts)
                status = parts[-1]
                if lead_time not in processed['lead_time']:
                    processed['lead_time'][lead_time] = {'Attended': 0, 'NoShow': 0}
                processed['lead_time'][lead_time][status] = value
                
        return processed
    
    def calculate_no_show_rate(self, attended, noshow):
        """Calculate no-show rate"""
        total = attended + noshow
        return (noshow / total * 100) if total > 0 else 0
    
    def display_overview(self):
        """Display overview dashboard"""
        st.header("📊 Overview Dashboard")
        
        # Calculate overall data
        total_attended = sum([v['Attended'] for category in self.processed_data.values() 
                             for v in category.values() if 'Attended' in v]) // 10  # Avoid double counting
        total_noshow = sum([v['NoShow'] for category in self.processed_data.values() 
                           for v in category.values() if 'NoShow' in v]) // 10
        
        total = total_attended + total_noshow
        noshow_rate = self.calculate_no_show_rate(total_attended, total_noshow)
        
        # Create metric cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Appointments Attended", f"{total_attended:,}")
        
        with col2:
            st.metric("Total No-Shows", f"{total_noshow:,}")
        
        with col3:
            st.metric("Total Records", f"{total:,}")
        
        with col4:
            st.metric("Overall No-Show Rate", f"{noshow_rate:.1f}%")
        
        # Overall trend gauge
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode = "gauge+number+delta",
            value = noshow_rate,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Overall No-Show Rate"},
            gauge = {
                'axis': {'range': [None, 40]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 15], 'color': "lightgreen"},
                    {'range': [15, 25], 'color': "yellow"},
                    {'range': [25, 40], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 25
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    def display_gender_analysis(self):
        """Display gender analysis"""
        st.header("🚻 Gender Analysis")
        
        if not self.processed_data['gender']:
            st.warning("No gender analysis data available")
            return
            
        gender_data = []
        for gender, stats in self.processed_data['gender'].items():
            rate = self.calculate_no_show_rate(stats['Attended'], stats['NoShow'])
            gender_data.append({
                'Gender': 'Female' if gender == 'F' else 'Male',
                'Appointments_Attended': stats['Attended'],
                'No_Shows': stats['NoShow'],
                'No_Show_Rate': rate
            })
        
        df = pd.DataFrame(gender_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart
            fig = px.pie(df, values='Appointments_Attended', names='Gender', 
                        title='Gender Distribution - Appointments Attended')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Bar chart
            fig = px.bar(df, x='Gender', y='No_Show_Rate',
                        title='No-Show Rate by Gender',
                        color='No_Show_Rate',
                        color_continuous_scale='RdYlGn_r')
            fig.update_layout(yaxis_title='No-Show Rate (%)')
            st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader("Detailed Data")
        st.dataframe(df.style.format({
            'Appointments_Attended': '{:,}',
            'No_Shows': '{:,}', 
            'No_Show_Rate': '{:.1f}%'
        }), use_container_width=True)
    
    def display_age_analysis(self):
        """Display age analysis"""
        st.header("🎂 Age Group Analysis")
        
        if not self.processed_data['age_groups']:
            st.warning("No age analysis data available")
            return
            
        # Main age group analysis
        age_data = []
        for age_group, stats in self.processed_data['age_groups'].items():
            rate = self.calculate_no_show_rate(stats['Attended'], stats['NoShow'])
            age_data.append({
                'Age_Group': age_group.replace('_', ' '),
                'Appointments_Attended': stats['Attended'],
                'No_Shows': stats['NoShow'],
                'No_Show_Rate': rate
            })
        
        df_ages = pd.DataFrame(age_data).sort_values('No_Show_Rate', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(df_ages, x='Age_Group', y='No_Show_Rate',
                        title='No-Show Rate by Age Group',
                        color='No_Show_Rate',
                        color_continuous_scale='RdYlGn_r')
            fig.update_layout(xaxis_title='Age Group', yaxis_title='No-Show Rate (%)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Detailed age analysis
            detailed_age_data = []
            for age_range, stats in self.processed_data['detailed_age'].items():
                if stats['Attended'] + stats['NoShow'] > 50:  # Filter small sample groups
                    rate = self.calculate_no_show_rate(stats['Attended'], stats['NoShow'])
                    detailed_age_data.append({
                        'Age_Range': age_range,
                        'Appointments_Attended': stats['Attended'],
                        'No_Shows': stats['NoShow'],
                        'No_Show_Rate': rate
                    })
            
            if detailed_age_data:
                df_detailed = pd.DataFrame(detailed_age_data)
                fig = px.line(df_detailed, x='Age_Range', y='No_Show_Rate',
                             title='Detailed Age No-Show Rate Trend', markers=True)
                fig.update_layout(xaxis_title='Age Range', yaxis_title='No-Show Rate (%)')
                st.plotly_chart(fig, use_container_width=True)
        
        # Display TOP5 highest no-show rate age groups
        st.subheader("🚨 High-Risk Age Groups (TOP5)")
        top5_high_risk = df_ages.head(5)
        st.dataframe(top5_high_risk.style.format({
            'Appointments_Attended': '{:,}',
            'No_Shows': '{:,}',
            'No_Show_Rate': '{:.1f}%'
        }), use_container_width=True)
    
    def display_health_analysis(self):
        """Display health conditions analysis"""
        st.header("🏥 Health Conditions Analysis")
        
        if not self.processed_data['health_conditions']:
            st.warning("No health conditions analysis data available")
            return
            
        health_data = []
        for condition, stats in self.processed_data['health_conditions'].items():
            if stats['Attended'] + stats['NoShow'] > 100:  # Filter small sample groups
                rate = self.calculate_no_show_rate(stats['Attended'], stats['NoShow'])
                health_data.append({
                    'Condition': condition.replace('_', ' '),
                    'Appointments_Attended': stats['Attended'],
                    'No_Shows': stats['NoShow'],
                    'No_Show_Rate': rate
                })
        
        if not health_data:
            return
            
        df_health = pd.DataFrame(health_data).sort_values('No_Show_Rate')
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(df_health, x='No_Show_Rate', y='Condition', orientation='h',
                        title='No-Show Rate by Health Condition',
                        color='No_Show_Rate',
                        color_continuous_scale='RdYlGn')
            fig.update_layout(yaxis_title='Health Condition', xaxis_title='No-Show Rate (%)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Appointment count comparison
            fig = px.pie(df_health, values='Appointments_Attended', names='Condition',
                        title='Appointment Distribution by Health Condition')
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Health Conditions Detailed Data")
        st.dataframe(df_health.style.format({
            'Appointments_Attended': '{:,}',
            'No_Shows': '{:,}',
            'No_Show_Rate': '{:.1f}%'
        }), use_container_width=True)
    
    def display_geographical_analysis(self):
        """Display geographical analysis"""
        st.header("🗺️ Geographical Analysis")
        
        if not self.processed_data['neighbourhoods']:
            st.warning("No geographical analysis data available")
            return
            
        neighbourhood_data = []
        for neighbourhood, stats in self.processed_data['neighbourhoods'].items():
            total = stats['Attended'] + stats['NoShow']
            if total > 50:  # Only show neighborhoods with sufficient samples
                rate = self.calculate_no_show_rate(stats['Attended'], stats['NoShow'])
                neighbourhood_data.append({
                    'Neighborhood': neighbourhood.replace('_', ' '),
                    'Appointments_Attended': stats['Attended'],
                    'No_Shows': stats['NoShow'],
                    'Total_Appointments': total,
                    'No_Show_Rate': rate
                })
        
        if not neighbourhood_data:
            return
            
        df_neighbourhood = pd.DataFrame(neighbourhood_data)
        
        # Sort and display highest and lowest neighborhoods
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚨 High No-Show Rate Neighborhoods (TOP10)")
            high_risk_areas = df_neighbourhood.nlargest(10, 'No_Show_Rate')
            fig = px.bar(high_risk_areas, x='No_Show_Rate', y='Neighborhood', orientation='h',
                        title='Top 10 High No-Show Rate Neighborhoods',
                        color='No_Show_Rate', color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("✅ Low No-Show Rate Neighborhoods (TOP10)")
            low_risk_areas = df_neighbourhood.nsmallest(10, 'No_Show_Rate')
            fig = px.bar(low_risk_areas, x='No_Show_Rate', y='Neighborhood', orientation='h',
                        title='Top 10 Low No-Show Rate Neighborhoods',
                        color='No_Show_Rate', color_continuous_scale='Greens')
            st.plotly_chart(fig, use_container_width=True)
        
        # Interactive data table
        st.subheader("Neighborhood Data Query")
        search_term = st.text_input("Search neighborhood name:")
        
        if search_term:
            filtered_data = df_neighbourhood[
                df_neighbourhood['Neighborhood'].str.contains(search_term, case=False, na=False)
            ]
        else:
            filtered_data = df_neighbourhood
        
        st.dataframe(filtered_data.style.format({
            'Appointments_Attended': '{:,}',
            'No_Shows': '{:,}',
            'Total_Appointments': '{:,}',
            'No_Show_Rate': '{:.1f}%'
        }), use_container_width=True, height=400)
    
    def display_intervention_analysis(self):
        """Display intervention analysis"""
        st.header("📱 SMS Intervention Analysis")
        
        if not self.processed_data['sms_intervention']:
            st.warning("No intervention analysis data available")
            return
            
        intervention_data = []
        for intervention, stats in self.processed_data['sms_intervention'].items():
            rate = self.calculate_no_show_rate(stats['Attended'], stats['NoShow'])
            intervention_data.append({
                'Intervention_Group': 'SMS Received' if 'SMS_RECEIVED' in intervention else 'No SMS',
                'Appointments_Attended': stats['Attended'],
                'No_Shows': stats['NoShow'],
                'No_Show_Rate': rate
            })
        
        df_intervention = pd.DataFrame(intervention_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(df_intervention, x='Intervention_Group', y='No_Show_Rate',
                        title='SMS Intervention Effectiveness',
                        color='No_Show_Rate',
                        color_continuous_scale='RdYlGn_r')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Appointment count comparison
            fig = px.pie(df_intervention, values='Appointments_Attended', names='Intervention_Group',
                        title='Appointment Distribution by Intervention Group')
            st.plotly_chart(fig, use_container_width=True)
        
        # Display key insights
        st.subheader("Key Findings")
        sms_received = df_intervention[df_intervention['Intervention_Group'] == 'SMS Received']['No_Show_Rate'].iloc[0]
        no_sms = df_intervention[df_intervention['Intervention_Group'] == 'No SMS']['No_Show_Rate'].iloc[0]
        
        if sms_received > no_sms:
            st.error(f"🚨 Important Finding: Patients who received SMS had higher no-show rate ({sms_received:.1f}%) than those who didn't ({no_sms:.1f}%)")
            st.info("""
            Potential reasons:
            - SMS reminders made patients more aware of appointments they could easily cancel
            - SMS content or timing needs optimization
            - Further analysis needed for different demographic responses to SMS
            """)
        else:
            st.success(f"✅ SMS Intervention Effective: Patients who received SMS had lower no-show rate ({sms_received:.1f}%) than those who didn't ({no_sms:.1f}%)")
    
    def display_risk_groups(self):
        """Display high-risk groups analysis"""
        st.header("⚠️ High-Risk Groups Analysis")
        
        if not self.processed_data['risk_groups']:
            st.warning("No high-risk groups analysis data available")
            return
            
        risk_data = []
        for risk_group, stats in self.processed_data['risk_groups'].items():
            rate = self.calculate_no_show_rate(stats['Attended'], stats['NoShow'])
            risk_data.append({
                'Risk_Group': risk_group.replace('_', ' '),
                'Appointments_Attended': stats['Attended'],
                'No_Shows': stats['NoShow'],
                'No_Show_Rate': rate
            })
        
        df_risk = pd.DataFrame(risk_data).sort_values('No_Show_Rate', ascending=False)
        
        fig = px.bar(df_risk, x='Risk_Group', y='No_Show_Rate',
                    title='No-Show Rate by Risk Group',
                    color='No_Show_Rate',
                    color_continuous_scale='RdYlGn_r')
        fig.update_layout(xaxis_title='Risk Group', yaxis_title='No-Show Rate (%)')
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Risk Groups Detailed Data")
        st.dataframe(df_risk.style.format({
            'Appointments_Attended': '{:,}',
            'No_Shows': '{:,}',
            'No_Show_Rate': '{:.1f}%'
        }), use_container_width=True)
    
    def display_lead_time_analysis(self):
        """Display lead time analysis"""
        st.header("⏰ Appointment Lead Time Analysis")
        
        if not self.processed_data['lead_time']:
            st.warning("No lead time analysis data available")
            return
            
        lead_time_data = []
        for lead_time, stats in self.processed_data['lead_time'].items():
            rate = self.calculate_no_show_rate(stats['Attended'], stats['NoShow'])
            lead_time_data.append({
                'Lead_Time_Category': lead_time.replace('_', ' '),
                'Appointments_Attended': stats['Attended'],
                'No_Shows': stats['NoShow'],
                'No_Show_Rate': rate
            })
        
        df_lead_time = pd.DataFrame(lead_time_data).sort_values('No_Show_Rate', ascending=False)
        
        fig = px.bar(df_lead_time, x='Lead_Time_Category', y='No_Show_Rate',
                    title='No-Show Rate by Lead Time',
                    color='No_Show_Rate',
                    color_continuous_scale='RdYlGn_r')
        fig.update_layout(xaxis_title='Lead Time Category', yaxis_title='No-Show Rate (%)')
        st.plotly_chart(fig, use_container_width=True)
        
        # Display trend insights
        if len(df_lead_time) > 1:
            st.subheader("Key Insights")
            max_rate = df_lead_time['No_Show_Rate'].max()
            min_rate = df_lead_time['No_Show_Rate'].min()
            max_group = df_lead_time.loc[df_lead_time['No_Show_Rate'].idxmax(), 'Lead_Time_Category']
            min_group = df_lead_time.loc[df_lead_time['No_Show_Rate'].idxmin(), 'Lead_Time_Category']
            
            st.info(f"""
            📈 **Lead Time Trend**: 
            - Longest lead time group (`{max_group}`) no-show rate: **{max_rate:.1f}%**
            - Shortest lead time group (`{min_group}`) no-show rate: **{min_rate:.1f}%**
            - **Difference**: {max_rate - min_rate:.1f} percentage points
            """)

def main():
    st.title("🏥 Medical Appointment Behavior Analysis Dashboard")
    st.markdown("**Hadoop/MapReduce Based Patient No-Show Risk Analysis System**")
    st.markdown("---")
    
    # Initialize dashboard
    dashboard = MedicalDashboard()
    
    if not dashboard.data:
        st.error("Unable to load data. Please check if data file exists.")
        return
    
    # Sidebar navigation
    st.sidebar.title("Navigation Menu")
    analysis_option = st.sidebar.selectbox(
        "Select Analysis Dimension",
        [
            "Overview Dashboard",
            "Gender Analysis", 
            "Age Analysis",
            "Health Conditions Analysis",
            "Geographical Analysis",
            "Intervention Analysis",
            "High-Risk Groups",
            "Lead Time Analysis"
        ]
    )
    
    # Display selected analysis dimension
    if analysis_option == "Overview Dashboard":
        dashboard.display_overview()
    elif analysis_option == "Gender Analysis":
        dashboard.display_gender_analysis()
    elif analysis_option == "Age Analysis":
        dashboard.display_age_analysis()
    elif analysis_option == "Health Conditions Analysis":
        dashboard.display_health_analysis()
    elif analysis_option == "Geographical Analysis":
        dashboard.display_geographical_analysis()
    elif analysis_option == "Intervention Analysis":
        dashboard.display_intervention_analysis()
    elif analysis_option == "High-Risk Groups":
        dashboard.display_risk_groups()
    elif analysis_option == "Lead Time Analysis":
        dashboard.display_lead_time_analysis()
    
    # Footer information
    st.sidebar.markdown("---")
    st.sidebar.info(
        """
        **Development Information**
        - Package: zeli8888.ccproject.patient_behavior
        - Tech Stack: Hadoop/MapReduce + Python + Streamlit
        - Data Source: Medical Appointment No Shows Dataset
        """
    )

if __name__ == "__main__":
    main()