import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from bs4 import BeautifulSoup
import time
import csv
from io import BytesIO, StringIO
from typing import Dict, List, Optional
from urllib.parse import urljoin
import plotly.express as px
import plotly.graph_objects as go
import json
import xlsxwriter


class PyconScraper:
    def __init__(self):
        self.year_selectors = {
             "2024": {
                "name": "#main > section > h1",
                "talks": "h3.card-title a",
                "speakers_list": "div.wafer-speakers-name a",
                "social": {
                    "container": "div.wafer-profile div.col-md-10",
                    "links": "a"
                }
            },
            "2023": {
                "name": "#main > section > h1",
                "talks": "h3.card-title a",
                "speakers_list": "div.wafer-speakers-name a",
                "social": {
                    "container": "div.col-md-10",
                    "links": "a"
                }
            },
            "2022": {
                "name": "#main > section > h1",
                "talks": "h3.card-title a",
                "speakers_list": "div.wafer-speakers-name a",
                "social": {
                    "container": "div.col-md-10",
                    "links": "a"
                }
            },
            "2021": {
                "name": "#main > section > div.row > div.col-md-10 > h1 > a",
                "talks": "h3.card-title a",
                "speakers_list": "div.wafer-speakers-name a",
                "social": {
                    "container": "div.col-md-10",
                    "links": "a"
                }
            },
            "2020": {
                "name": "#main > section > div.row > div.col-md-10 > h1 > a",
                "talks": "h3.card-title a",
                "speakers_list": "div.wafer-speakers-name a",
                "social": {
                    "container": "div.col-md-10",
                    "links": "a"
                }
            },
            "2019": {
                "name": "#main > section > div.row > div.col-md-10 > h1 > a",
                "talks": "h3.card-title a",
                "speakers_list": "div.wafer-speakers-name a",
                "social": {
                    "container": "div.col-md-10",
                    "links": "a"
                }
            },
            "2018": {
                "name": "#main > section > div.row > div.col-md-10 > h1 > a",
                "talks": "div.card-body h3.card-title a",
                "speakers_list": "div.wafer-speakers-name a",
                "social": {
                    "container": "div.col-md-10",
                    "links": "a"
                }
            },
            "2017": {
                "name": "#main > section > div.row > div.col-md-10 > h1",
                "talks": "div.well a",
                "speakers_list": "div.wafer-speakers-name a",
                "social": {
                    "container": "div.col-md-10",
                    "links": "a"
                }
            },
            "2016": {
                "name": "#main > div.row > div.col-md-10 > h1 > a",
                "talks": "div.well a",
                "speakers_list": "div.wafer-speakers-name a",
                "talks_page": "/talks/",
                "speakers_in_talks": "div.well h1 a",
                "social": {
                    "container": "div.col-md-10",
                    "links": "a"
                }
            },
            "2015": {
                "name": "#main > section > div:nth-child(2) > p:nth-child(1) > a",
                "talks": "section.wafer.wafer-talk h1",
                "speakers_list": "section.wafer.wafer-talk div p a",
                "talks_page": "/talks/",
                "speakers_in_talks": "section.wafer.wafer-talk div p a",
                "social": {
                    "container": "div.col-md-10",
                    "links": "a"
                }
            },
            "2014": {
                "name": "#main > div.row > div.col-md-10 > h1 > a",
                "talks": "div.wafer.list div a",
                "speakers_list": "section.wafer.wafer-talk div p a",
                "talks_page": "/talks/",
                "speakers_in_talks": "section.wafer.wafer-talk div p a",
                "social": {
                    "container": "div.col-md-10",
                    "links": "a"
                }
            },
            "2013": {
                "name": "#main > div.row > div.span10 > h1",
                "talks": "div.body table tbody tr td a",
                "speakers_list": "div.body table tbody tr td a",
                "talks_page": "/talks/",
                "speakers_in_talks": "div.body table tbody tr td a[href*='/users/']",
                "social": {
                    "container": "div.span10",
                    "links": "a"
                }
            }
        }

    def get_selectors_for_year(self, year: str) -> Dict:
        if year in self.year_selectors:
            return self.year_selectors[year]
        current_year = max(int(y) for y in self.year_selectors.keys())
        return self.year_selectors[str(current_year)] if int(year) > current_year else self.year_selectors["2014"]

    def get_base_url(self, year: str) -> str:
        year_int = int(year)
    
        # Special cases for recent years
        if year_int >= 2023:
            return f"https://za.pycon.org/talks"
        # For years 2017-2022
        elif 2017 <= year_int <= 2022:
            return f"https://{year}.za.pycon.org/talks"
        # For older years (2013-2016)
        else:
            return f"https://za.pycon.org/talks"

    def get_speaker_links(self, url: str, year: str) -> List[str]:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            selectors = self.get_selectors_for_year(year)
            links = soup.select(selectors["speakers_list"])
            return [urljoin(url, link.get('href')) for link in links if link.get('href')]
        except requests.RequestException as e:
            st.error(f"Error fetching speaker links from {url}: {e}")
            return []
        
    def scrape_profile(self, url: str, year: str) -> Optional[Dict]:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            selectors = self.get_selectors_for_year(year)
            year_int = int(year)
            
            # Get name
            name_element = soup.select_one(selectors["name"]) or soup.select_one('h1')
            name = name_element.text.strip() if name_element else "Name not found"
            
            # Get talks
            if year_int <= 2016:
                # For older years, we need to get talks differently
                talks = []
                if year_int == 2013:
                    # For 2013, get talks from the table
                    talk_elements = soup.select("div.body table tbody tr td a")
                    talks = [talk.text.strip() for talk in talk_elements if not '/users/' in talk.get('href', '')]
                else:
                    # For 2014-2016, get talks from the talk sections
                    talk_elements = soup.select(selectors["talks"])
                    talks = [talk.text.strip() for talk in talk_elements]
            else:
                talks = [talk.text.strip() for talk in soup.select(selectors["talks"])]
            
            # Get social media links
            social_media = {}
            social_selector = selectors.get("social", {})
            container = soup.select_one(social_selector.get("container"))
            
            if container:
                links = container.select(social_selector.get("links", "a"))
                for link in links:
                    href = link.get('href', '')
                    if not href:
                        continue
                    
                    # Handle Twitter iframe for older years
                    if 'twitter-follow-button' in str(link):
                        iframe = link.find('iframe')
                        if iframe and 'screen_name' in iframe.get('src', ''):
                            screen_name = iframe['src'].split('screen_name=')[1].split('&')[0]
                            social_media['Twitter'] = f'https://twitter.com/{screen_name}'
                            continue
                    
                    # Handle GitHub links
                    if 'GitHub:' in link.text:
                        username = link.text.strip().replace('GitHub:', '').strip()
                        social_media['GitHub'] = f'https://github.com/{username}'
                        continue
                    
                    platform = self._determine_platform(href)
                    if platform:
                        social_media[platform] = href

            return {
                'name': name,
                'talks': talks,
                'social_media': social_media
            }
        except requests.RequestException as e:
            st.error(f"Error fetching profile: {e}")
            return None
    

    def _determine_platform(self, url: str) -> Optional[str]:
        self.platform_patterns = {
            'twitter.com': 'Twitter',
            'x.com': 'Twitter',
            'github.com': 'GitHub',
            'linkedin.com': 'LinkedIn',
            'medium.com': 'Medium',
            'youtube.com': 'YouTube',
            'facebook.com': 'Facebook',
            'insightstack.co.za': 'Website',
            'slideshare.net': 'SlideShare',
            'speakerdeck.com': 'SpeakerDeck',
            'blog': 'Blog',
            '.wordpress.com': 'Blog',
            '.blogspot.com': 'Blog',
            'web.': 'Website'
        }
        
        try:
            # Handle empty URLs
            if not url or url.isspace():
                return None
                
            # Convert URL to lowercase for case-insensitive matching
            url_lower = url.lower()
            
            # Check if URL matches any known platform patterns
            for pattern, platform in self.platform_patterns.items():
                if pattern in url_lower:
                    return platform
                    
            # Handle special cases for personal websites
            if any(tld in url_lower for tld in ['.com', '.org', '.net', '.io']):
                if not any(platform in url_lower for platform in self.platform_patterns.keys()):
                    return 'Website'
                    
            return None
            
        except Exception as e:
            print(f"Error determining platform for URL {url}: {e}")
            return None

    def generate_csv(self, data: List[Dict]) -> bytes:
        output = StringIO()
        all_platforms = set()

        for speaker in data:
            all_platforms.update(speaker['social_media'].keys())

        writer = csv.writer(output)
        header = ['Name'] + sorted(all_platforms) + ['Talks']
        writer.writerow(header)

        for speaker in data:
            row = [speaker['name']]
            for platform in sorted(all_platforms):
                row.append(speaker['social_media'].get(platform, ''))
            row.append('; '.join(speaker['talks']))
            writer.writerow(row)

        return output.getvalue().encode('utf-8')
    
def apply_custom_css():
    # Get current theme
    is_dark_mode = st.session_state.get('dark_mode', False)
    
    # Define colors
    primary_color = "#2563eb"  # Blue
    background_color = "#1e1e1e" if is_dark_mode else "#ffffff"
    text_color = "#ffffff" if is_dark_mode else "#000000"
    
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {background_color};
            color: {text_color};
        }}
        .main {{
            background-color: {background_color};
        }}
        .stButton>button {{
            background-color: {primary_color};
            color: white;
        }}
        .stButton>button:hover {{
            background-color: {primary_color}dd;
        }}
        .css-1d391kg {{
            color: {text_color} !important;
        }}
        h1, h2, h3, h4, h5, h6, p, label {{
            color: {text_color} !important;
        }}
        .stDataFrame {{
            color: {text_color} !important;
        }}
        .js-plotly-plot {{
            background-color: {background_color};
        }}
        .js-plotly-plot .plotly .modebar {{
            background-color: {background_color};
        }}
        .sidebar .sidebar-content {{
            background-color: {primary_color}10;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def generate_plots(df):
    # Set color scheme based on theme
    is_dark_mode = st.session_state.get('dark_mode', False)
    colors = px.colors.qualitative.Set3
    plot_bg_color = "#1e1e1e" if is_dark_mode else "#ffffff"
    text_color = "#ffffff" if is_dark_mode else "#000000"
    
    # Fix for the attendance type error - ensure we're working with flat data
    if 'attendance_type' in df.columns:
        # 1. Bar Chart: Distribution of Participants by Type
        attendance_counts = df['attendance_type'].value_counts().reset_index()
        attendance_counts.columns = ['Type', 'Count']
        
        fig_bar = px.bar(
            attendance_counts,
            x='Type',
            y='Count',
            title='Distribution of Participants by Type',
            color='Type',
            color_discrete_sequence=colors
        )
        fig_bar.update_layout(
            plot_bgcolor=plot_bg_color,
            paper_bgcolor=plot_bg_color,
            font_color=text_color,
            showlegend=False
        )
        st.plotly_chart(fig_bar)
        
        # 2. Modified Treemap: Distribution of Participants by Type
        fig_treemap_type = px.treemap(
            attendance_counts,
            path=['Type'],
            values='Count',
            title='Distribution of Participants by Type (Treemap)',
            color_discrete_sequence=colors
        )
        fig_treemap_type.update_layout(
            plot_bgcolor=plot_bg_color,
            paper_bgcolor=plot_bg_color,
            font_color=text_color
        )
        st.plotly_chart(fig_treemap_type)
    
    # 3. Treemap: Participants by Country
    if 'country' in df.columns:
        country_counts = df['country'].value_counts().head(15)
        country_df = pd.DataFrame({
            'country': country_counts.index,
            'count': country_counts.values
        })
        
        fig_treemap_country = px.treemap(
            country_df,
            path=['country'],
            values='count',
            title='Distribution of Participants by Country (Top 15)',
            color_discrete_sequence=colors
        )
        fig_treemap_country.update_layout(
            plot_bgcolor=plot_bg_color,
            paper_bgcolor=plot_bg_color,
            font_color=text_color
        )
        st.plotly_chart(fig_treemap_country)
        
        # 4. Stacked Bar Chart: Distribution of Attendance Types by Country
        if 'attendance_type' in df.columns:
            top_countries = df['country'].value_counts().head(10).index
            filtered_df = df[df['country'].isin(top_countries)]
            
            country_type_counts = filtered_df.groupby(['country', 'attendance_type']).size().reset_index(name='count')
            
            fig_stacked = px.bar(
                country_type_counts,
                x='country',
                y='count',
                color='attendance_type',
                title='Distribution of Attendance Types by Country (Top 10)',
                labels={'country': 'Country', 'count': 'Number of Participants', 'attendance_type': 'Attendance Type'},
                color_discrete_sequence=colors
            )
            fig_stacked.update_layout(
                plot_bgcolor=plot_bg_color,
                paper_bgcolor=plot_bg_color,
                font_color=text_color,
                xaxis={'tickangle': 45}
            )
            st.plotly_chart(fig_stacked)

def export_analysis(df):
    """
    Create an Excel file containing various analyses of the conference data.
    
    Args:
        df (pd.DataFrame): The input DataFrame containing conference data
        
    Returns:
        bytes: The Excel file as bytes
    """
    # Create a BytesIO object to store the Excel file
    output = BytesIO()
    
    try:
        # Create Excel writer
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Write main statistics
            stats_dict = {
                'Total Participants': len(df),
                'Number of Countries': df['country'].nunique(),
                'Number of Attendance Types': df['attendance_type'].nunique()
            }
            stats_df = pd.DataFrame.from_dict(stats_dict, orient='index', columns=['Value'])
            stats_df.to_excel(writer, sheet_name='Summary')
            
            # Write attendance type distribution
            if 'attendance_type' in df.columns:
                attendance_dist = df['attendance_type'].value_counts().reset_index()
                attendance_dist.columns = ['Attendance Type', 'Count']
                attendance_dist.to_excel(writer, sheet_name='Attendance Distribution', index=False)
            
            # Write country distribution
            if 'country' in df.columns:
                country_dist = df['country'].value_counts().reset_index()
                country_dist.columns = ['Country', 'Count']
                country_dist.to_excel(writer, sheet_name='Country Distribution', index=False)
            
            # Write attendance type by country matrix
            if 'country' in df.columns and 'attendance_type' in df.columns:
                cross_tab = pd.crosstab(df['country'], df['attendance_type'])
                cross_tab.to_excel(writer, sheet_name='Country-Attendance Matrix')
            
            # Add summary statistics
            if 'company_name' in df.columns:
                company_stats = df['company_name'].value_counts().head(20).reset_index()
                company_stats.columns = ['Company', 'Count']
                company_stats.to_excel(writer, sheet_name='Top Companies', index=False)
            
            # Add job title analysis if available
            if 'job_title' in df.columns:
                job_stats = df['job_title'].value_counts().head(20).reset_index()
                job_stats.columns = ['Job Title', 'Count']
                job_stats.to_excel(writer, sheet_name='Top Job Titles', index=False)
    
    except Exception as e:
        st.error(f"Error creating Excel file: {str(e)}")
        return None
    
    # Reset pointer and return bytes
    output.seek(0)
    return output.getvalue()


def main():
    # Initialize session state for dark mode if it doesn't exist
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False

    # Sidebar navigation and theme toggle
    st.sidebar.title("🧭 Navigation")
    with st.sidebar.expander("📊 Data Exploration"):
        page = st.radio("Go to", ["Home", "PyCon ZA", "ITC Vegas", "Analysis", "About Us"])

    # Dark mode toggle in sidebar
    st.sidebar.subheader("🎨 Settings")
    dark_mode = st.sidebar.checkbox("🌚 Dark Mode", value=st.session_state.dark_mode)
    
    # Update dark mode state
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()  # Using rerun() instead of experimental_rerun()

    # Apply custom CSS based on theme
    apply_custom_css()

    if page == "Analysis":
        st.title("📊 Data Analysis Dashboard")
        
        try:
            # Load data
            df = pd.read_csv('itc new new.csv')
            
            # Add high-level statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Participants", len(df))
            with col2:
                st.metric("Number of Countries", df['country'].nunique())
            with col3:
                st.metric("Attendance Types", df['attendance_type'].nunique())
            
            # Generate and display plots
            generate_plots(df)
            
            # Add export button
            analysis_data = export_analysis(df)
            if analysis_data is not None:
                st.download_button(
                    label="⬇️ Download Complete Analysis",
                    data=analysis_data,
                    file_name="conference_analysis.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
        except Exception as e:
            st.error(f"Error loading or processing data: {str(e)}")
            st.write("Please make sure your CSV file exists and contains the required columns.")



    elif page == "ITC Vegas":
        st.title("🔎 ITC Vegas Speaker Search Dashboard")
        
        # Load the data
        df = pd.read_csv('itc new new.csv')

        # Input fields
        name_search = st.text_input("🔍 Search by First name:")
        position_search = st.text_input("🔍 Search by Position (Keyword):")

        columns = ["None"] + df.columns.to_list()
        selected_c = st.selectbox('📁 Choose column', columns)

        if selected_c != "None":
            values = ["None"] + df[selected_c].unique().tolist()
        else:
            values = ["None"]
        selected_v = st.selectbox('📋 Choose value to display', values)

        company_search = st.text_input('🔍 Search for Company')

        # Apply filters
        filtered_df = df.copy()

        if name_search:
            filtered_df = filtered_df[filtered_df["first_name"].str.contains(name_search, case=False, na=False)]
        if position_search:
            filtered_df = filtered_df[filtered_df["job_title"].str.contains(position_search, case=False, na=False)]
        if selected_c != "None" and selected_v != "None":
            filtered_df = filtered_df[filtered_df[selected_c] == selected_v]
        if company_search:
            filtered_df = filtered_df[filtered_df['company_name'].str.contains(company_search, case=False, na=False)]

        valid_values = st.checkbox('🗑️ Remove rows with no contact details')
        if valid_values:
            filtered_df = filtered_df[~filtered_df['email'].str.contains('Contacts visible after Connection', case=False, na=False)]
        st.write(f"Found {len(filtered_df)} result(s):")
        st.dataframe(filtered_df)

        if not filtered_df.empty:
            output = BytesIO()
            filtered_df.to_csv(output, index=False)
            output.seek(0)
            st.download_button(
                label="⬇️ Download Filtered Results as CSV",
                data=output,
                file_name="filtered_speaker_data.csv",
                mime="text/csv"
            )

    elif page == "Analysis":
        st.title("📊 Data Analysis Dashboard")
        try:
            # Load data
            df = pd.read_csv('itc new new.csv')
            
            # Generate and display plots
            generate_plots(df)
            
            # Add export button
            analysis_data = export_analysis(df)
            st.download_button(
                label="⬇️ Download Complete Analysis",
                data=analysis_data,
                file_name="conference_analysis.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"Error loading or processing data: {str(e)}")
    
    elif page == "PyCon ZA":
        st.title("🐍 PyCon ZA Speaker Scraper")
        
        # Initialize scraper
        scraper = PyconScraper()
        
        # Year selection
        years = [str(year) for year in range(2013, 2025)]
        selected_year = st.selectbox("Select Year", years, index=len(years)-1)
        
        # Base URL for the selected year
        base_url = scraper.get_base_url(selected_year)
        speakers_url = f"{base_url}/speakers/"
        
        # Add a scrape button
        if st.button("🔍 Scrape Speaker Data"):
            with st.spinner(f"Scraping speaker data from PyCon ZA {selected_year}..."):
                try:
                    # Get speaker links
                    speaker_links = scraper.get_speaker_links(speakers_url, selected_year)
                    
                    if not speaker_links:
                        st.warning(f"No speaker links found for {selected_year}")
                        return
                    
                    # Initialize progress bar
                    progress_bar = st.progress(0)
                    progress_text = st.empty()
                    
                    # Scrape profiles
                    speakers_data = []
                    for i, link in enumerate(speaker_links):
                        # Update progress
                        progress = (i + 1) / len(speaker_links)
                        progress_bar.progress(progress)
                        progress_text.text(f"Processing speaker {i+1} of {len(speaker_links)}")
                        
                        # Scrape profile
                        profile = scraper.scrape_profile(link, selected_year)
                        if profile:
                            speakers_data.append(profile)
                        time.sleep(0.5)  # Add delay between requests
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    progress_text.empty()
                    
                    if speakers_data:
                        # Convert to DataFrame for display
                        speakers_df = pd.json_normalize(speakers_data)
                        
                        # Display results
                        st.subheader("📊 Results")
                        st.write(f"Found {len(speakers_data)} speakers")
                        st.dataframe(speakers_df)
                        
                        # Generate CSV for download
                        csv_data = scraper.generate_csv(speakers_data)
                        
                        # Add download button
                        st.download_button(
                            label="⬇️ Download Speaker Data as CSV",
                            data=csv_data,
                            file_name=f"pycon_za_{selected_year}_speakers.csv",
                            mime="text/csv"
                        )
                        
                        # Display some basic statistics
                        st.subheader("📈 Quick Statistics")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Total Speakers", len(speakers_data))
                        
                        with col2:
                            total_talks = sum(len(speaker['talks']) for speaker in speakers_data)
                            st.metric("Total Talks", total_talks)
                        
                        with col3:
                            speakers_with_social = sum(1 for speaker in speakers_data if speaker['social_media'])
                            st.metric("Speakers with Social Media", speakers_with_social)
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.write("Please try again or select a different year.")
    
    elif page == "Home":
         st.title("🏠 Speaker Analytics Dashboard")
    
        # Hero section
         st.markdown("""
         <div style='padding: 1.5rem; background-color: #2563eb; color: white; border-radius: 0.5rem; margin-bottom: 2rem;'>
        <h1 style='color: white !important;'>Welcome to Speaker Analytics Dashboard</h1>
        <p style='opacity: 0.9;'>Your comprehensive platform for exploring and analyzing speaker data from tech conferences</p>
        </div>
        """, unsafe_allow_html=True)
    
        # Features section
         col1, col2, col3 = st.columns(3)
    
         with col1:
          st.markdown("""
        ### 🔍 PyCon ZA Scraper
        Extract and analyze speaker data from PyCon ZA conferences dating back to 2013.
        - Multi-year coverage
        - Social media integration
        - Real-time processing
        """)
    
         with col2:
          st.markdown("""
        ### 👥 ITC Vegas Search
        Search and filter ITC Vegas conference participants.
        - Name-based search
        - Position filtering
        - Company lookup
        """)
    
         with col3:
          st.markdown("""
        ### 📊 Data Analysis
        Interactive visualizations and detailed analysis.
        - Demographic insights
        - Trend analysis
        - Custom reports
        """)
    
    # Getting Started section
         st.markdown("""
    ### 🚀 Getting Started
    1. Navigate through different sections using the sidebar menu
    2. Use PyCon ZA scraper to collect speaker data from different years
    3. Search ITC Vegas participants using various filters
    4. Explore data visualizations in the Analysis section
    5. Export your findings in CSV or Excel format
    """)

    elif page == "About Us":
        st.title("🧑‍💻 About Us")
        st.subheader("Welcome to the Speaker Dashboard! 🔘")
        st.write(
        "This application serves as a comprehensive platform for exploring speaker data from PyCon ZA and ITC Vegas events. "
        "Users can scrape speaker profiles, search through participants, and analyze trends in participation."
    )
        st.write("Our mission is to provide insights into the diverse speakers contributing to the Python community.")
        st.write("")

        st.subheader("The Team 👥")

    # Arrange profiles in columns
        profiles = [
        {"name": "Shaun Mapatha", "role": "Data Engineer", "email": "shaun.mapatha@gmail.com", "image": "1709048398610.jpeg"},
        {"name": "Olwethu Zama", "role": "Data Engineer", "email": "khwezizama@gmail.com", "image": "Zama.jpeg"},
        {"name": "Masalesa Britney", "role": "Data Scientist", "email": "mmetjabritney@gmail.com", "image": "Britney.jpeg"},
        {"name": "Refilwe Masapu", "role": "Data Scientist", "email": "skymasapu12@gmail.com", "image": "Refilwe.jpeg"},
        {"name": "Tselane Moeti", "role": "Data Scientist", "email": "tsemoeti24@gmail.com", "image": "Tselane.jpeg"},
        {"name": "Comfort Mphahlele", "role": "Data Scientist", "email": "mphahlelelc02@gmail.com", "image": "Comfort.jpeg"},
        {"name": "Nontobeko Dube", "role": "Data Engineer", "email": "cordydube@gmail.com", "image": "Nonto.jpeg"},
    ]

    # Define the layout using columns
        cols = st.columns(3)  # Adjust the number of columns as needed

        for i, profile in enumerate(profiles):
            with cols[i % 3]:  # Rotate through columns
                st.write(f"**{profile['name']}**")
                st.write(f"Role: {profile['role']}")
                st.write(f"Email: {profile['email']}")
                if profile["image"]:
                   st.image(profile["image"], use_column_width=True)
                st.write("")  # Add some spacing between profiles

   


        st.write("😀 Feel free to explore and utilize the functionalities offered by this dashboard! 😀")


if __name__ == "__main__":
    main()
