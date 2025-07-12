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
                'lockdown', 'vaccine', 'election', 'government policy', 'fed', 'fomc'
            ],
            'medium_impact': [
                'corporate earnings', 'ipo', 'merger', 'acquisition', 'dividend',
                'bonus', 'split', 'fii', 'dii', 'foreign investment',
                'crude oil', 'currency', 'rupee', 'dollar', 'quarterly results'
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
            'cnbc': 'https://www.cnbctv18.com/commonfeeds/v1/eng/rss/money.xml'
        }
    
    def get_ist_time(self):
        """Get current IST time"""
        ist = pytz.timezone('Asia/Kolkata')
        return datetime.now(ist)
    
    def parse_published_date(self, published_str):
        """Parse various date formats and convert to IST"""
        if not published_str:
            return None
            
        # Common date formats in RSS feeds
        date_formats = [
            '%a, %d %b %Y %H:%M:%S %z',
            '%a, %d %b %Y %H:%M:%S GMT',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S%z',
            '%a, %d %b %Y %H:%M:%S +0000',
            '%Y-%m-%dT%H:%M:%SZ'
        ]
        
        for fmt in date_formats:
            try:
                # Parse the date
                parsed_date = datetime.strptime(published_str.strip(), fmt)
                
                # Add timezone if not present
                if parsed_date.tzinfo is None:
                    parsed_date = pytz.UTC.localize(parsed_date)
                
                # Convert to IST
                ist_date = parsed_date.astimezone(pytz.timezone('Asia/Kolkata'))
                return ist_date
            except ValueError:
                continue
                
        return None
    
    def is_recent_news(self, published_date):
        """Check if news is from last 24 hours"""
        if not published_date:
            return False
            
        # Get current IST time
        current_ist = self.get_ist_time()
        
        # Check if within last 24 hours
        time_diff = current_ist - published_date
        return time_diff.total_seconds() < 86400  # 24 hours
    
    def clean_html(self, text):
        """Remove HTML tags from text"""
        if not text:
            return ""
        # Remove HTML tags
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
    
    def fetch_rss_news(self, url: str, source: str) -> List[Dict]:
        """Fetch news from RSS feeds with proper error handling"""
        try:
            # Parse RSS feed
            feed = feedparser.parse(url, agent='Mozilla/5.0')
            
            if not feed.entries:
                print(f"No entries found for {source}")
                return []
                
            news_items = []
            
            for entry in feed.entries[:15]:  # Get up to 15 items per source
                try:
                    # Get and parse published date
                    published_str = entry.get('published') or entry.get('pubDate', '')
                    published_date = self.parse_published_date(published_str)
                    
                    # Skip if not recent
                    if published_date and not self.is_recent_news(published_date):
                        continue
                    
                    # Get title and clean it
                    title = self.clean_html(entry.get('title', 'No Title'))
                    
                    # Get summary/description
                    summary = entry.get('summary') or entry.get('description', '')
                    summary = self.clean_html(summary)[:400]  # Limit to 400 chars
                    
                    # Get link
                    link = entry.get('link', '#')
                    
                    # Format time for display
                    if published_date:
                        display_date = published_date.strftime('%Y-%m-%d')
                        display_time = published_date.strftime('%H:%M IST')
                    else:
                        display_date = self.get_ist_time().strftime('%Y-%m-%d')
                        display_time = self.get_ist_time().strftime('%H:%M IST')
                    
                    news_items.append({
                        'title': title,
                        'summary': summary if summary else "Click to read full article...",
                        'link': link,
                        'published': published_str,
                        'published_date': published_date,
                        'source': source.replace('_', ' ').title(),
                        'date': display_date,
                        'time': display_time,
                        'timestamp': published_date.isoformat() if published_date else datetime.now().isoformat()
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
        else:
            return 'General Business'

def get_latest_news() -> List[Dict]:
    """Main function to get latest market news"""
    analyzer = NewsAnalyzer()
    all_news = []
    
    # Create a progress indicator
    progress_text = st.empty()
    
    for source_name, url in analyzer.news_sources.items():
        try:
            progress_text.text(f"Fetching latest news from {source_name}...")
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
                
        except Exception as e:
            print(f"Error processing {source_name}: {e}")
            continue
    
    progress_text.empty()
    
    # Sort by published date (most recent first)
    all_news.sort(key=lambda x: x.get('published_date') or datetime.min.replace(tzinfo=pytz.UTC), reverse=True)
    
    # Remove duplicates based on title similarity
    unique_news = []
    seen_titles = set()
    
    for news in all_news:
        # Create a normalized title for comparison
        title_normalized = news['title'].lower().strip()
        title_words = set(title_normalized.split())
        
        # Check for duplicates
        is_duplicate = False
        for seen_title in seen_titles:
            seen_words = set(seen_title.split())
            # If more than 70% words match, consider duplicate
            if len(title_words.intersection(seen_words)) > len(title_words) * 0.7:
                is_duplicate = True
                break
        
        if not is_duplicate and len(unique_news) < 25:  # Limit to 25 news items
            unique_news.append(news)
            seen_titles.add(title_normalized)
    
    # If no news found, return empty list (don't add fake news)
    if len(unique_news) == 0:
        st.warning("No recent news found. Please check your internet connection or try again later.")
    
    return unique_news

def get_market_sentiment() -> Dict:
    """Get overall market sentiment based on news"""
    try:
        news_data = get_latest_news()
        
        if not news_data:
            return {
                'sentiment': 'Unknown',
                'high_impact_news': 0,
                'total_news': 0,
                'last_updated': 'No data'
            }
        
        high_impact_count = len([n for n in news_data if n['market_impact'] == 'High'])
        total_news = len(news_data)
        
        # Sentiment based on high impact news ratio
        impact_ratio = high_impact_count / total_news if total_news > 0 else 0
        
        if impact_ratio > 0.3:
            sentiment = 'Volatile - High Impact Events'
        elif impact_ratio > 0.15:
            sentiment = 'Cautious - Moderate Activity'
        else:
            sentiment = 'Stable - Normal Trading'
        
        ist_time = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist_time)
        
        return {
            'sentiment': sentiment,
            'high_impact_news': high_impact_count,
            'total_news': total_news,
            'last_updated': current_time.strftime('%H:%M:%S IST')
        }
    except Exception as e:
        print(f"Error getting market sentiment: {e}")
        return {
            'sentiment': 'Error',
            'high_impact_news': 0,
            'total_news': 0,
            'last_updated': 'Error loading data'
        }
