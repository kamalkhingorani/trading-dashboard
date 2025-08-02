# news_logic.py - FIXED WITH WORKING CLICKABLE LINKS
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
            'reuters_india': 'https://feeds.reuters.com/reuters/INbusinessNews'
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
            '%a, %d %b %Y %H:%M:%S +0000',
            '%a, %d %b %Y %H:%M:%S IST',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%SZ',
            '%d %b %Y %H:%M:%S',
            '%a, %d %b %Y %H:%M:%S'
        ]
        
        for fmt in date_formats:
            try:
                clean_published = published_str.strip()
                
                # Handle timezone cases
                if 'IST' in clean_published:
                    clean_published = clean_published.replace('IST', '+0530')
                elif 'GMT' in clean_published and '+' not in clean_published:
                    clean_published = clean_published.replace('GMT', '+0000')
                
                parsed_date = datetime.strptime(clean_published, fmt)
                
                if parsed_date.tzinfo is None:
                    parsed_date = pytz.UTC.localize(parsed_date)
                
                ist_date = parsed_date.astimezone(pytz.timezone('Asia/Kolkata'))
                return ist_date
                
            except ValueError:
                continue
        
        # Fallback using email utils
        try:
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
        """Check if news is from last 48 hours"""
        if not published_date:
            return True  # Include items without dates
            
        current_ist = self.get_ist_time()
        time_diff = current_ist - published_date
        return time_diff.total_seconds() < 172800  # 48 hours
    
    def clean_html(self, text):
        """Remove HTML tags and clean text"""
        if not text:
            return ""
        clean = re.compile('<.*?>')
        cleaned = re.sub(clean, '', text)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
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
        if time_diff.total_seconds() < 3600:
            minutes = int(time_diff.total_seconds() / 60)
            relative_time = f"{minutes}m ago" if minutes > 0 else "Just now"
        elif time_diff.total_seconds() < 86400:
            hours = int(time_diff.total_seconds() / 3600)
            relative_time = f"{hours}h ago"
        else:
            days = int(time_diff.total_seconds() / 86400)
            relative_time = f"{days}d ago"
        
        return {
            'date': published_date.strftime('%d-%m-%Y'),
            'time': published_date.strftime('%H:%M IST'),
            'relative_time': relative_time,
            'sort_timestamp': published_date.timestamp()
        }
    
    def fetch_rss_news(self, url: str, source: str) -> List[Dict]:
        """Fetch news from RSS feeds with proper link handling"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            try:
                response = requests.get(url, headers=headers, timeout=15)
                feed = feedparser.parse(response.content)
            except:
                feed = feedparser.parse(url)
            
            if not feed.entries:
                print(f"No entries found for {source}")
                return []
                
            news_items = []
            
            for entry in feed.entries[:15]:
                try:
                    # Get and parse published date
                    published_str = (entry.get('published') or 
                                   entry.get('pubDate') or 
                                   entry.get('updated') or '')
                    
                    published_date = self.parse_published_date(published_str)
                    
                    if published_date and not self.is_recent_news(published_date):
                        continue
                    
                    # Get title and clean it
                    title = self.clean_html(entry.get('title', 'No Title'))
                    
                    if len(title) < 10:
                        continue
                    
                    # Get summary/description
                    summary = (entry.get('summary') or 
                              entry.get('description') or '')
                    
                    summary = self.clean_html(summary)[:400]
                    
                    # FIXED: Get proper link
                    link = entry.get('link', '')
                    
                    # Clean and validate link
                    if link:
                        # Ensure proper protocol
                        if not link.startswith(('http://', 'https://')):
                            if link.startswith('//'):
                                link = 'https:' + link
                            elif link.startswith('/'):
                                # Relative link - add domain based on source
                                if 'economictimes' in url:
                                    link = 'https://economictimes.indiatimes.com' + link
                                elif 'business-standard' in url:
                                    link = 'https://www.business-standard.com' + link
                                elif 'moneycontrol' in url:
                                    link = 'https://www.moneycontrol.com' + link
                                elif 'livemint' in url:
                                    link = 'https://www.livemint.com' + link
                                elif 'financialexpress' in url:
                                    link = 'https://www.financialexpress.com' + link
                                else:
                                    link = ''
                            else:
                                link = 'https://' + link
                        
                        # Validate link format
                        if not any(domain in link for domain in ['economictimes', 'business-standard', 'moneycontrol', 'livemint', 'financialexpress', 'reuters']):
                            # If link doesn't contain expected domains, it might be malformed
                            pass  # Keep the link as is, let browser handle it
                    
                    # Format date and time
                    date_info = self.format_news_date_time(published_date)
                    
                    news_items.append({
                        'title': title,
                        'summary': summary if summary else "Click link to read full article...",
                        'link': link,  # Store the actual link
                        'published_str': published_str,
                        'published_date': published_date,
                        'source': source.replace('_', ' ').title(),
                        'date': date_info['date'],
                        'time': date_info['time'],
                        'relative_time': date_info['relative_time'],
                        'sort_timestamp': date_info['sort_timestamp']
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
    """Get latest market news with working links"""
    analyzer = NewsAnalyzer()
    all_news = []
    
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
    
    # Sort by published date (most recent first)
    all_news.sort(key=lambda x: x.get('sort_timestamp', 0), reverse=True)
    
    # Remove duplicates based on title similarity
    unique_news = []
    seen_titles = set()
    
    for news in all_news:
        title_normalized = news['title'].lower().strip()
        title_words = set(re.findall(r'\b\w+\b', title_normalized))
        
        # Check for duplicates
        is_duplicate = False
        for seen_title in seen_titles:
            seen_words = set(re.findall(r'\b\w+\b', seen_title))
            if (len(title_words.intersection(seen_words)) > len(title_words) * 0.6 and
                abs(len(title_words) - len(seen_words)) < 3):
                is_duplicate = True
                break
        
        if not is_duplicate and len(unique_news) < 25:
            unique_news.append(news)
            seen_titles.add(title_normalized)
    
    if len(unique_news) == 0:
        st.warning("No recent news found. This could be due to network issues or weekend/holiday period.")
    else:
        st.success(f"✅ Loaded {len(unique_news)} unique news items from {sources_processed} sources")
    
    return unique_news

def get_market_sentiment() -> Dict:
    """Get market sentiment analysis"""
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
        
        # Sentiment calculation
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
            'sources_checked': len(analyzer.news_sources),
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
