# news_logic.py - ENHANCED WITH PROPER DATE AND CLICKABLE LINKS
import requests
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Tuple
import streamlit as st
import feedparser
import re
import pytz

class NewsAnalyzer:
    def __init__(self):
        self.market_keywords = {
            'high_impact': [
                'interest rate', 'rbi policy', 'budget', 'gdp', 'inflation',
                'repo rate', 'reverse repo', 'fiscal deficit', 'war', 'pandemic',
                'lockdown', 'vaccine', 'election', 'government policy', 'fed', 'fomc',
                'geopolitics', 'trade war', 'sanctions', 'crude oil', 'natural disaster'
            ],
            'medium_impact': [
                'corporate earnings', 'ipo', 'merger', 'acquisition', 'dividend',
                'bonus', 'split', 'fii', 'dii', 'foreign investment',
                'currency', 'rupee', 'dollar', 'quarterly results', 'exports', 'imports'
            ],
            'sector_specific': [
                'banking', 'pharma', 'it', 'auto', 'steel', 'cement',
                'energy', 'fmcg', 'telecom', 'real estate','defense','infrastructure',
                'manufacturing','retail','healthcare', 'metal', 'chemicals'
            ]
        }
        
        self.news_sources = {
            'economic_times': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
            'business_standard': 'https://www.business-standard.com/rss/markets-106.rss',
            'moneycontrol': 'https://www.moneycontrol.com/rss/business.xml',
            'livemint': 'https://www.livemint.com/rss/money',
            'financial_express': 'https://www.financialexpress.com/market/rss',
            'reuters_india': 'https://feeds.reuters.com/reuters/INbusinessNews',
            'cnbc': 'https://www.cnbctv18.com/commonfeeds/v1/eng/rss/money.xml',
            'hindu_business': 'https://www.thehindu.com/business/feeder/default.rss',
            'zeebusiness': 'https://www.zeebiz.com/rss/india-business-news.xml'
        }
    
    def get_ist_time(self):
        """Get current IST time"""
        ist = pytz.timezone('Asia/Kolkata')
        return datetime.now(ist)
    
    def parse_published_date(self, published_str):
        """Enhanced date parsing with multiple formats"""
        if not published_str:
            return None
            
        # Comprehensive date formats for various RSS feeds
        date_formats = [
            '%a, %d %b %Y %H:%M:%S %z',     # Standard RSS format with timezone
            '%a, %d %b %Y %H:%M:%S GMT',    # GMT timezone
            '%a, %d %b %Y %H:%M:%S +0000',  # UTC timezone
            '%a, %d %b %Y %H:%M:%S IST',    # IST timezone
            '%Y-%m-%d %H:%M:%S',            # Simple format
            '%Y-%m-%dT%H:%M:%S%z',          # ISO format with timezone
            '%Y-%m-%dT%H:%M:%SZ',           # ISO format UTC
            '%d %b %Y %H:%M:%S',            # Alternative format
            '%d/%m/%Y %H:%M:%S',            # Indian date format
            '%a, %d %b %Y %H:%M:%S',        # Without timezone
        ]
        
        for fmt in date_formats:
            try:
                # Clean the published string
                clean_published = published_str.strip()
                
                # Handle special timezone cases
                if 'IST' in clean_published:
                    clean_published = clean_published.replace('IST', '+0530')
                elif 'GMT' in clean_published and '+' not in clean_published:
                    clean_published = clean_published.replace('GMT', '+0000')
                
                # Parse the date
                parsed_date = datetime.strptime(clean_published, fmt)
                
                # Add timezone if not present (assume UTC)
                if parsed_date.tzinfo is None:
                    parsed_date = pytz.UTC.localize(parsed_date)
                
                # Convert to IST
                ist_date = parsed_date.astimezone(pytz.timezone('Asia/Kolkata'))
                return ist_date
                
            except ValueError:
                continue
                
        # If all parsing fails, try to extract date components
        try:
            # Use feedparser's built-in date parsing as fallback
            import email.utils
            parsed_tuple = email.utils.parsedate_tz(published_str)
            if parsed_tuple:
                timestamp = email.utils.mktime_tz(parsed_tuple)
                utc_date = datetime.fromtimestamp(timestamp, tz=pytz.UTC)
                ist_date = utc_date.astimezone(pytz.timezone('Asia/Kolkata'))
                return ist_date
        except:
            pass
                
        return None
    
    def is_recent_news(self, published_date):
        """Check if news is from last 48 hours (extended for better coverage)"""
        if not published_date:
            return True  # Include items without dates rather than exclude
            
        # Get current IST time
        current_ist = self.get_ist_time()
        
        # Check if within last 48 hours (extended for better news coverage)
        time_diff = current_ist - published_date
        return time_diff.total_seconds() < 172800  # 48 hours
    
    def clean_html(self, text):
        """Remove HTML tags and clean text"""
        if not text:
            return ""
        # Remove HTML tags
        clean = re.compile('<.*?>')
        cleaned = re.sub(clean, '', text)
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def create_clickable_link(self, url, title):
        """Create a clickable link for the news item"""
        if not url or url == '#':
            return "🔗 Link unavailable"
        
        # Ensure URL has proper protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Create markdown link that opens in new tab
        return f"🔗 [Read Full Article]({url})"
    
    def format_news_date_time(self, published_date):
        """Format date and time for display"""
        if not published_date:
            current_ist = self.get_ist_time()
            return {
                'date': current_ist.strftime('%d-%m-%Y'),
                'time': current_ist.strftime('%H:%M IST'),
                'relative_time': 'Just now',
                'sort_timestamp': current_ist.timestamp()
            }
        
        current_ist = self.get_ist_time()
        time_diff = current_ist - published_date
        
        # Calculate relative time
        if time_diff.total_seconds() < 3600:  # Less than 1 hour
            minutes = int(time_diff.total_seconds() / 60)
            relative_time = f"{minutes}m ago" if minutes > 0 else "Just now"
        elif time_diff.total_seconds() < 86400:  # Less than 24 hours
            hours = int(time_diff.total_seconds() / 3600)
            relative_time = f"{hours}h ago"
        else:  # More than 24 hours
            days = int(time_diff.total_seconds() / 86400)
            relative_time = f"{days}d ago"
        
        return {
            'date': published_date.strftime('%d-%m-%Y'),
            'time': published_date.strftime('%H:%M IST'),
            'relative_time': relative_time,
            'sort_timestamp': published_date.timestamp()
        }
    
    def fetch_rss_news(self, url: str, source: str) -> List[Dict]:
        """Enhanced RSS news fetching with better error handling"""
        try:
            # Parse RSS feed with custom headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Use requests to fetch with headers, then parse with feedparser
            try:
                response = requests.get(url, headers=headers, timeout=15)
                feed = feedparser.parse(response.content)
            except:
                # Fallback to direct feedparser
                feed = feedparser.parse(url)
            
            if not feed.entries:
                print(f"No entries found for {source}")
                return []
                
            news_items = []
            
            for entry in feed.entries[:20]:  # Get up to 20 items per source
                try:
                    # Get and parse published date
                    published_str = (entry.get('published') or 
                                   entry.get('pubDate') or 
                                   entry.get('updated') or '')
                    
                    published_date = self.parse_published_date(published_str)
                    
                    # Skip if too old (but include items without dates)
                    if published_date and not self.is_recent_news(published_date):
                        continue
                    
                    # Get title and clean it
                    title = self.clean_html(entry.get('title', 'No Title'))
                    
                    # Skip if title is too short or generic
                    if len(title) < 10:
                        continue
                    
                    # Get summary/description
                    summary = (entry.get('summary') or 
                              entry.get('description') or 
                              entry.get('content', [{}])[0].get('value', '') if entry.get('content') else '')
                    
                    summary = self.clean_html(summary)[:500]  # Limit to 500 chars
                    
                    # Get link
                    link = entry.get('link', '#')
                    
                    # Format date and time
                    date_info = self.format_news_date_time(published_date)
                    
                    # Create clickable link
                    clickable_link = self.create_clickable_link(link, title)
                    
                    news_items.append({
                        'title': title,
                        'summary': summary if summary else "Click link to read full article...",
                        'link': link,
                        'clickable_link': clickable_link,
                        'published_str': published_str,
                        'published_date': published_date,
                        'source': source.replace('_', ' ').title(),
                        'date': date_info['date'],
                        'time': date_info['time'],
                        'relative_time': date_info['relative_time'],
                        'sort_timestamp': date_info['sort_timestamp'],
                        'raw_published': published_str  # For debugging
                    })
                    
                except Exception as e:
                    print(f"Error processing entry from {source}: {e}")
                    continue
            
            return news_items
            
        except Exception as e:
            print(f"Error fetching from {source}: {e}")
            return []
    
    def analyze_market_impact(self, title: str, summary: str) -> Tuple[str, str]:
        """Analyze the potential market impact of news"""
        text = (title + " " + summary).lower()
        
        # Check for high impact keywords
        for keyword in self.market_keywords['high_impact']:
            if keyword in text:
                return 'High', 'Policy/Macro'
        
        # Check for medium impact keywords
        for keyword in self.market_keywords['medium_impact']:
            if keyword in text:
                return 'Medium', 'Corporate/Markets'
        
        # Check for sector specific
        for keyword in self.market_keywords['sector_specific']:
            if keyword in text:
                return 'Medium', f'Sector: {keyword.title()}'
        
        return 'Low', 'General'
    
    def categorize_news(self, title: str, summary: str) -> str:
        """Categorize news into different buckets"""
        text = (title + " " + summary).lower()
        
        if any(keyword in text for keyword in ['rbi', 'interest rate', 'policy', 'budget', 'fed', 'fomc']):
            return 'Policy/Central Bank'
        elif any(keyword in text for keyword in ['earnings', 'results', 'profit', 'revenue', 'quarterly']):
            return 'Corporate Earnings'
        elif any(keyword in text for keyword in ['ipo', 'listing', 'issue', 'offer']):
            return 'IPO/Listings'
        elif any(keyword in text for keyword in ['fii', 'dii', 'investment', 'inflow', 'outflow']):
            return 'FII/DII Activity'
        elif any(keyword in text for keyword in ['crude', 'oil', 'commodity', 'gold', 'silver']):
            return 'Commodities'
        elif any(keyword in text for keyword in ['rupee', 'dollar', 'currency', 'forex']):
            return 'Currency'
        elif any(keyword in text for keyword in ['nifty', 'sensex', 'index', 'market']):
            return 'Market Movement'
        elif any(keyword in text for keyword in ['geopolitic', 'war', 'trade', 'sanction', 'china', 'usa']):
            return 'Geopolitics'
        else:
            return 'General Business'

def get_latest_news() -> List[Dict]:
    """Enhanced function to get latest market news with proper date handling"""
    analyzer = NewsAnalyzer()
    all_news = []
    
    # Create a progress indicator
    progress_text = st.empty()
    
    sources_processed = 0
    total_sources = len(analyzer.news_sources)
    
    for source_name, url in analyzer.news_sources.items():
        try:
            progress_text.text(f"Fetching latest news from {source_name}... ({sources_processed + 1}/{total_sources})")
            news_items = analyzer.fetch_rss_news(url, source_name)
            
            for item in news_items:
                # Analyze impact and categorize
                impact, impact_type = analyzer.analyze_market_impact(
                    item['title'], item['summary']
                )
                category = analyzer.categorize_news(item['title'], item['summary'])
                
                item.update({
                    'market_impact': impact,
                    'impact_type': impact_type,
                    'category': category
                })
                
                all_news.append(item)
            
            sources_processed += 1
                
        except Exception as e:
            print(f"Error processing {source_name}: {e}")
            sources_processed += 1
            continue
    
    progress_text.empty()
    
    # Sort by published date (most recent first) using sort_timestamp
    all_news.sort(key=lambda x: x.get('sort_timestamp', 0), reverse=True)
    
    # Enhanced duplicate removal based on title similarity
    unique_news = []
    seen_titles = set()
    
    for news in all_news:
        # Create a normalized title for comparison
        title_normalized = news['title'].lower().strip()
        # Remove common words and punctuation for better comparison
        title_words = set(re.findall(r'\b\w+\b', title_normalized))
        
        # Check for duplicates
        is_duplicate = False
        for seen_title in seen_titles:
            seen_words = set(re.findall(r'\b\w+\b', seen_title))
            # If more than 60% words match and similar length, consider duplicate
            if (len(title_words.intersection(seen_words)) > len(title_words) * 0.6 and
                abs(len(title_words) - len(seen_words)) < 3):
                is_duplicate = True
                break
        
        if not is_duplicate and len(unique_news) < 30:  # Limit to 30 news items
            unique_news.append(news)
            seen_titles.add(title_normalized)
    
    # If no news found, provide helpful message
    if len(unique_news) == 0:
        st.warning("No recent news found. This could be due to:")
        st.write("• Weekend/holiday when news sources have limited updates")
        st.write("• Network connectivity issues")
        st.write("• RSS feed temporary unavailability")
        st.write("• Try refreshing after a few minutes")
    else:
        st.success(f"✅ Loaded {len(unique_news)} unique news items from {sources_processed} sources")
    
    return unique_news

def get_market_sentiment() -> Dict:
    """Enhanced market sentiment analysis"""
    try:
        news_data = get_latest_news()
        
        if not news_data:
            return {
                'sentiment': 'Unknown - No Data',
                'high_impact_news': 0,
                'total_news': 0,
                'last_updated': 'No data available'
            }
        
        high_impact_count = len([n for n in news_data if n['market_impact'] == 'High'])
        medium_impact_count = len([n for n in news_data if n['market_impact'] == 'Medium'])
        total_news = len(news_data)
        
        # Enhanced sentiment calculation
        impact_ratio = high_impact_count / total_news if total_news > 0 else 0
        medium_ratio = medium_impact_count / total_news if total_news > 0 else 0
        
        if impact_ratio > 0.25:
            sentiment = 'High Volatility - Major Events'
        elif impact_ratio > 0.15 or medium_ratio > 0.4:
            sentiment = 'Moderate Volatility - Active News Flow'
        elif medium_ratio > 0.2:
            sentiment = 'Cautious - Normal Activity'
        else:
            sentiment = 'Stable - Quiet News Environment'
        
        ist_time = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist_time)
        
        return {
            'sentiment': sentiment,
            'high_impact_news': high_impact_count,
            'medium_impact_news': medium_impact_count,
            'total_news': total_news,
            'sources_checked': len(NewsAnalyzer().news_sources),
            'last_updated': current_time.strftime('%d-%m-%Y %H:%M:%S IST')
        }
    except Exception as e:
        print(f"Error getting market sentiment: {e}")
        ist_time = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist_time)
        return {
            'sentiment': 'Error loading data',
            'high_impact_news': 0,
            'medium_impact_news': 0,
            'total_news': 0,
            'sources_checked': 0,
            'last_updated': current_time.strftime('%d-%m-%Y %H:%M:%S IST'),
            'error': str(e)
        }
