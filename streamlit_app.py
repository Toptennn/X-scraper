import streamlit as st
import asyncio
import pandas as pd
import io
from datetime import datetime, date, timedelta
from pathlib import Path
import logging
import nest_asyncio

from config import TwitterConfig, SearchParameters, SearchMode, TwitterCredentials
from scraper import TwitterScraper
from data_utils import TweetDataExtractor

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Configure logging for Streamlit
logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="Twitter Scraper Dashboard",
    layout="wide"
)

class StreamlitTwitterScraper:
    """Streamlit wrapper for the Twitter scraper."""
    
    def __init__(self):
        self.scraper = None
        self.config = None
        self.progress_bar = None
        self.progress_text = None
    
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
    
    def setup_progress_display(self):
        """Setup progress bar and text display."""
        self.progress_bar = st.progress(0)
        self.progress_text = st.empty()
    
    def update_progress(self, progress: float, current: int, total: int):
        """Update progress bar and text."""
        if self.progress_bar and self.progress_text:
            # Ensure progress is between 0 and 1
            progress = min(1.0, max(0.0, progress))
            
            self.progress_bar.progress(progress)
            percentage = int(progress * 100)
            
            # Update progress text with detailed information
            self.progress_text.markdown(
                f"**Progress: {percentage}%** | "
                f"Scraped: {current:,} / {total:,} tweets | "
                f"Remaining: {total - current:,} tweets"
            )
    
    async def scrape_timeline(self, screen_name: str, count: int):
        """Scrape user timeline for specified screen name."""
        user = await self.scraper.get_user_by_screen_name(screen_name)
        tweets = await self.scraper.fetch_user_timeline(
            user.id, 
            count=count, 
            progress_callback=self.update_progress
        )
        return TweetDataExtractor.extract_tweet_data(tweets)
    
    async def scrape_search(self, search_params: SearchParameters):
        """Scrape tweets based on search parameters."""
        tweets = await self.scraper.search_tweets(
            search_params, 
            progress_callback=self.update_progress
        )
        return TweetDataExtractor.extract_tweet_data(tweets)

async def run_scraping_task(scraper_wrapper, scraping_mode, **kwargs):
    """Run the scraping task asynchronously."""
    if scraping_mode == "Timeline":
        return await scraper_wrapper.scrape_timeline(
            kwargs['screen_name'], 
            kwargs['count']
        )
    else:
        return await scraper_wrapper.scrape_search(kwargs['search_params'])

def get_or_create_eventloop():
    """Get or create an event loop for asyncio operations."""
    try:
        # Try to get the current event loop
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            # If the loop is closed, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        # If no event loop exists, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop

async def run_async_task(coro):
    """Helper function to run async tasks safely."""
    try:
        return await coro
    except Exception as e:
        st.error(f"Async task failed: {str(e)}")
        raise

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
    st.title("🐦 X Scraper Dashboard")
    st.markdown("Advanced X scraping tool with real-time progress tracking")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Authentication
        st.subheader("🔐 Authentication")
        auth_id = st.text_input("Auth ID", placeholder="หมายเลขโทรศัพท์ อีเมล หรือ ชื่อผู้ใช้")
        password = st.text_input("Password", type="password", placeholder="รหัสผ่าน")
        
        # Scraping Mode Selection
        st.subheader("📊 Scraping Mode")
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
            timeline_screen_name = st.text_input("Screen Name", placeholder="ชื่อผู้ใช้")
            tweet_count = st.number_input("Number of Tweets", min_value=1, value=50)
            
        else:  # Search modes
            st.subheader("Search Parameters")
            query = st.text_input("Search Query", placeholder="คำค้นหา")
            tweet_count = st.number_input("Number of Tweets", min_value=1, value=50)
            
            if scraping_mode == "Date Range Search":
                col_date1, col_date2 = st.columns(2)
                with col_date1:
                    start_date = st.date_input("Start Date", value=date.today() - timedelta(days=7))
                with col_date2:
                    end_date = st.date_input("End Date", value=date.today())
    
    with col2:
        st.subheader("🚀 Actions")
        
        scrape_button = st.button("Start Scraping", type="primary", use_container_width=True)
        
        if st.button("Clear Results", use_container_width=True):
            if 'scraping_completed' in st.session_state:
                del st.session_state.scraping_completed
            if 'tweet_data' in st.session_state:
                del st.session_state.tweet_data
            st.rerun()
    
    # Scraping execution
    if scrape_button:
        if not auth_id or not password:
            st.error("❌ Please provide authentication credentials")
            return
        
        # Clear previous results
        if 'scraping_completed' in st.session_state:
            del st.session_state.scraping_completed
        
        # Create progress display container
        progress_container = st.container()
        
        with progress_container:
            st.subheader("🔄 Scraping Progress")
            
            try:
                # Get or create event loop
                loop = get_or_create_eventloop()
                
                # Initialize scraper
                scraper_wrapper = StreamlitTwitterScraper()
                
                with st.spinner("🔐 Authenticating with X..."):
                    # Run authentication
                    loop.run_until_complete(
                        run_async_task(scraper_wrapper.initialize_scraper(auth_id, password))
                    )
                
                st.success("✅ Authentication successful!")
                
                # Setup progress tracking
                scraper_wrapper.setup_progress_display()
                
                if scraping_mode == "Timeline":
                    if not timeline_screen_name:
                        st.error("❌ Please enter a screen name")
                        return
                    
                    st.info(f"🎯 Scraping timeline for @{timeline_screen_name}")
                    
                    # Run scraping task
                    tweet_data = loop.run_until_complete(
                        run_async_task(run_scraping_task(
                            scraper_wrapper, 
                            scraping_mode,
                            screen_name=timeline_screen_name,
                            count=tweet_count
                        ))
                    )
                    prefix = f"timeline_{timeline_screen_name}"
                    
                elif scraping_mode == "Date Range Search":
                    if not query:
                        st.error("❌ Please enter a search query")
                        return
                    
                    st.info(f"🔍 Searching tweets for '{query}' from {start_date} to {end_date}")
                    search_params = SearchParameters(
                        query=query,
                        count=tweet_count,
                        mode=SearchMode.DATE_RANGE,
                        start_date=start_date.strftime("%Y-%m-%d"),
                        end_date=end_date.strftime("%Y-%m-%d")
                    )
                    
                    tweet_data = loop.run_until_complete(
                        run_async_task(run_scraping_task(
                            scraper_wrapper,
                            scraping_mode,
                            search_params=search_params
                        ))
                    )
                    prefix = f"date_range_{query.replace('#', '').replace('@', '').replace(' ', '_')}"
                    
                elif scraping_mode == "Popular Search":
                    if not query:
                        st.error("❌ Please enter a search query")
                        return
                    
                    st.info(f"🔥 Searching popular tweets for '{query}'")
                    search_params = SearchParameters(
                        query=query,
                        count=tweet_count,
                        mode=SearchMode.POPULAR
                    )
                    
                    tweet_data = loop.run_until_complete(
                        run_async_task(run_scraping_task(
                            scraper_wrapper,
                            scraping_mode,
                            search_params=search_params
                        ))
                    )
                    prefix = f"popular_{query.replace('#', '').replace('@', '').replace(' ', '_')}"
                    
                else:  # Latest Search
                    if not query:
                        st.error("❌ Please enter a search query")
                        return
                    
                    st.info(f"🆕 Searching latest tweets for '{query}'")
                    search_params = SearchParameters(
                        query=query,
                        count=tweet_count,
                        mode=SearchMode.LATEST
                    )
                    
                    tweet_data = loop.run_until_complete(
                        run_async_task(run_scraping_task(
                            scraper_wrapper,
                            scraping_mode,
                            search_params=search_params
                        ))
                    )
                    prefix = f"latest_{query.replace('#', '').replace('@', '').replace(' ', '_')}"
                           
                # Store results in session state
                st.session_state.tweet_data = tweet_data
                st.session_state.filename_prefix = prefix
                st.session_state.scraping_completed = True
                
                # Final progress update
                scraper_wrapper.update_progress(1.0, len(tweet_data), tweet_count)
                
            except Exception as e:
                st.error(f"❌ Scraping failed: {str(e)}")
                with st.expander("🔍 Error Details"):
                    st.exception(e)
    
    # Display results
    if hasattr(st.session_state, 'scraping_completed') and st.session_state.scraping_completed:
        st.header("📋 Results")
        
        if st.session_state.tweet_data:
            df = pd.DataFrame(st.session_state.tweet_data)
            
            # Display metrics
            st.subheader("📊 Summary Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Tweets", len(df))
            with col2:
                st.metric("Unique Users", df['username'].nunique())
            with col3:
                st.metric("Total Retweets", f"{df['retweet_count'].sum():,}")
            with col4:
                st.metric("Total Favorites", f"{df['favorite_count'].sum():,}")
            
            # Display data table
            st.subheader("📊 Tweet Data")
            
            # Add filters
            col1, col2 = st.columns(2)
            with col1:
                username_filter = st.multiselect(
                    "Filter by Username",
                    options=sorted(df['username'].unique()),
                    default=[]
                )
            with col2:
                lang_filter = st.multiselect(
                    "Filter by Language",
                    options=sorted(df['lang'].unique()),
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
            st.warning("⚠️ No tweets found for the specified criteria.")

if __name__ == "__main__":
    main()