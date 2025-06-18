import streamlit as st
import asyncio
import pandas as pd
import io
from datetime import datetime, date
from pathlib import Path
import logging

from config import TwitterConfig, SearchParameters, SearchMode, TwitterCredentials
from scraper import TwitterScraper
from data_utils import TweetDataExtractor

# Configure logging for Streamlit
logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="Twitter Scraper Dashboard",
    page_icon="🐦",
    layout="wide"
)

class StreamlitTwitterScraper:
    """Streamlit wrapper for the Twitter scraper."""
    
    def __init__(self):
        self.scraper = None
        self.config = None
    
    async def initialize_scraper(self, auth_id: str, password: str):
        """Initialize and authenticate the scraper."""
        credentials = TwitterCredentials(
            auth_id=auth_id,
            password=password,
            cookies_file='cookies.json'
        )
        
        self.config = TwitterConfig(
            credentials=credentials,
            output_dir='output'
        )
        
        self.scraper = TwitterScraper(self.config)
        await self.scraper.authenticate()
    
    async def scrape_timeline(self, screen_name: str, count: int):
        """Scrape user timeline for specified screen name."""
        user = await self.scraper.get_user_by_screen_name(screen_name)
        tweets = await self.scraper.fetch_user_timeline(user.id, count=count)
        return TweetDataExtractor.extract_tweet_data(tweets)
    
    async def scrape_search(self, search_params: SearchParameters):
        """Scrape tweets based on search parameters."""
        tweets = await self.scraper.search_tweets(search_params)
        return TweetDataExtractor.extract_tweet_data(tweets)

def create_download_link(df: pd.DataFrame, filename: str, file_format: str):
    """Create download link for DataFrame."""
    if file_format == 'csv':
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        data = output.getvalue()
        mime_type = 'text/csv'
    elif file_format == 'excel':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Tweets')
        data = output.getvalue()
        mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    return st.download_button(
        label=f"📥 Download {file_format.upper()}",
        data=data,
        file_name=f"{filename}.{file_format}",
        mime=mime_type
    )

def main():
    st.title("🐦 Twitter Scraper Dashboard")
    st.markdown("Professional Twitter scraping tool with multiple search modes")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Authentication
        st.subheader("Authentication")
        auth_id = st.text_input("Auth ID", value="***REMOVED***")
        password = st.text_input("Password", type="password", value="***REMOVED***")
        
        # Scraping Mode Selection
        st.subheader("Scraping Mode")
        scraping_mode = st.selectbox(
            "Select Mode",
            ["Timeline", "Date Range Search", "Popular Search", "Latest Search"]
        )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(f"📊 {scraping_mode}")
        
        # Mode-specific parameters
        if scraping_mode == "Timeline":
            st.subheader("Timeline Parameters")
            timeline_screen_name = st.text_input("Screen Name")
            tweet_count = st.number_input("Number of Tweets", min_value=1, max_value=1000, value=20)
            
        else:  # Search modes
            st.subheader("Search Parameters")
            query = st.text_input("Search Query", value="#Python")
            tweet_count = st.number_input("Number of Tweets", min_value=1, max_value=1000, value=50)
            
            if scraping_mode == "Date Range Search":
                col_date1, col_date2 = st.columns(2)
                with col_date1:
                    start_date = st.date_input("Start Date", value=date(2024, 1, 1))
                with col_date2:
                    end_date = st.date_input("End Date", value=date(2024, 1, 2))
    
    with col2:
        st.subheader("🚀 Actions")
        
        if st.button("Start Scraping", type="primary", use_container_width=True):
            if not auth_id or not password:
                st.error("Please provide authentication credentials")
                return
            
            try:
                with st.spinner("Initializing scraper..."):
                    # Initialize scraper
                    scraper_wrapper = StreamlitTwitterScraper()
                    asyncio.run(scraper_wrapper.initialize_scraper(auth_id, password))
                
                # Execute scraping based on mode
                with st.spinner(f"Scraping {scraping_mode.lower()}..."):
                    if scraping_mode == "Timeline":
                        tweet_data = asyncio.run(scraper_wrapper.scrape_timeline(timeline_screen_name, tweet_count))
                        prefix = f"timeline_{timeline_screen_name}"
                        
                    elif scraping_mode == "Date Range Search":
                        search_params = SearchParameters(
                            query=query,
                            count=tweet_count,
                            mode=SearchMode.DATE_RANGE,
                            start_date=start_date.strftime("%Y-%m-%d"),
                            end_date=end_date.strftime("%Y-%m-%d")
                        )
                        tweet_data = asyncio.run(scraper_wrapper.scrape_search(search_params))
                        prefix = f"date_range_{query.replace('#', '').replace(' ', '_')}"
                        
                    elif scraping_mode == "Popular Search":
                        search_params = SearchParameters(
                            query=query,
                            count=tweet_count,
                            mode=SearchMode.POPULAR
                        )
                        tweet_data = asyncio.run(scraper_wrapper.scrape_search(search_params))
                        prefix = f"popular_{query.replace('#', '').replace(' ', '_')}"
                        
                    else:  # Latest Search
                        search_params = SearchParameters(
                            query=query,
                            count=tweet_count,
                            mode=SearchMode.LATEST
                        )
                        tweet_data = asyncio.run(scraper_wrapper.scrape_search(search_params))
                        prefix = f"latest_{query.replace('#', '').replace(' ', '_')}"
                
                # Store results in session state
                st.session_state.tweet_data = tweet_data
                st.session_state.filename_prefix = prefix
                st.session_state.scraping_completed = True
                
                st.success(f"✅ Successfully scraped {len(tweet_data)} tweets!")
                
            except Exception as e:
                st.error(f"❌ Scraping failed: {str(e)}")
                st.exception(e)
    
    # Display results
    if hasattr(st.session_state, 'scraping_completed') and st.session_state.scraping_completed:
        st.header("📋 Results")
        
        if st.session_state.tweet_data:
            df = pd.DataFrame(st.session_state.tweet_data)
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Tweets", len(df))
            with col2:
                st.metric("Unique Users", df['username'].nunique())
            with col3:
                st.metric("Total Retweets", df['retweet_count'].sum())
            with col4:
                st.metric("Total Favorites", df['favorite_count'].sum())
            
            # Display data table
            st.subheader("📊 Tweet Data")
            
            # Add filters
            col1, col2 = st.columns(2)
            with col1:
                username_filter = st.multiselect(
                    "Filter by Username",
                    options=df['username'].unique(),
                    default=[]
                )
            with col2:
                lang_filter = st.multiselect(
                    "Filter by Language",
                    options=df['lang'].unique(),
                    default=[]
                )
            
            # Apply filters
            filtered_df = df.copy()
            if username_filter:
                filtered_df = filtered_df[filtered_df['username'].isin(username_filter)]
            if lang_filter:
                filtered_df = filtered_df[filtered_df['lang'].isin(lang_filter)]
            
            # Display filtered data
            st.dataframe(
                filtered_df,
                use_container_width=True,
                column_config={
                    "created_at": st.column_config.DatetimeColumn("Created At"),
                    "username": st.column_config.TextColumn("Username"),
                    "text": st.column_config.TextColumn("Tweet Text", width="large"),
                    "url": st.column_config.LinkColumn("Tweet URL"),
                    "retweet_count": st.column_config.NumberColumn("Retweets"),
                    "favorite_count": st.column_config.NumberColumn("Favorites"),
                    "reply_count": st.column_config.NumberColumn("Replies")
                }
            )
            
            # Download options
            st.subheader("💾 Download Options")
            col1, col2 = st.columns(2)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{st.session_state.filename_prefix}_{timestamp}"
            
            with col1:
                create_download_link(filtered_df, filename, 'csv')
            with col2:
                create_download_link(filtered_df, filename, 'excel')
        
        else:
            st.warning("No tweets found for the specified criteria.")

if __name__ == "__main__":
    main()