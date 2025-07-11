import requests
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Tuple
import streamlit as st
import feedparser
import re

class NewsAnalyzer:
    def __init__(self):
        self.market_keywords = {
            'high_impact': [
                'interest rate', 'rbi policy', 'budget', 'gdp', 'inflation',
                'repo rate', 'reverse repo', 'fiscal deficit', 'war', 'pandemic',
                'lockdown', 'vaccine', 'election', 'government policy'
            ],
            'medium_impact': [
                'corporate earnings', 'ipo', 'merger', 'acquisition', 'dividend',
                'bonus', 'split', 'fii', 'dii', 'foreign investment',
                'crude oil', 'currency', 'rupee', 'dollar'
            ],
            'sector_specific': [
                'banking', 'pharma', 'it', 'auto', 'steel', 'cement',
                'energy', 'fmcg', 'telecom', 'real estate','defense','infrastructure',
                'manufacturing','retail','healthcare'
            ]
        }
        
        self.news_sources = {
            'economic_times': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
            'business_standard': 'https://www.business-standard.com/rss/markets-106.rss',
            'moneycontrol': 'https://www.moneycontrol.com/rss/business.xml',
            'livemint': 'https://www.livemint.com/rss/money'
        }
    
    def fetch_rss_news(self, url: str, source: str) -> List[Dict]:
        """Fetch news from RSS feeds"""
        try:
            feed = feedparser.parse(url)
            news_items = []
            
            for entry in feed.entries[:5]:  # Limit to 5 items per source
                news_items.append({
                    'title': entry.get('title', ''),
                    'summary': entry.get('summary', entry.get('description', ''))[:300],
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'source': source
                })
            
            return news_items
        except Exception as e:
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
        
        if any(keyword in text for keyword in ['rbi', 'interest rate', 'policy', 'budget']):
            return 'RBI/Policy'
        elif any(keyword in text for keyword in ['earnings', 'results', 'profit']):
            return 'Corporate Earnings'
        elif any(keyword in text for keyword in ['ipo', 'listing', 'issue']):
            return 'IPO/Listings'
        elif any(keyword in text for keyword in ['fii', 'dii', 'investment', 'inflow']):
            return 'FII/DII Activity'
        elif any(keyword in text for keyword in ['crude', 'oil', 'commodity']):
            return 'Commodities'
        elif any(keyword in text for keyword in ['rupee', 'dollar', 'currency']):
            return 'Currency'
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
            progress_text.text(f"Fetching news from {source_name}...")
            news_items = analyzer.fetch_rss_news(url, source_name)
            
            for item in news_items:
                impact, impact_type = analyzer.analyze_market_impact(
                    item['title'], item['summary']
                )
                category = analyzer.categorize_news(item['title'], item['summary'])
                
                item.update({
                    'market_impact': impact,
                    'impact_type': impact_type,
                    'category': category,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
                all_news.append(item)
                
        except Exception as e:
            continue
    
    progress_text.empty()
    
    # Sort by impact level (High first)
    impact_order = {'High': 3, 'Medium': 2, 'Low': 1}
    all_news.sort(key=lambda x: impact_order.get(x['market_impact'], 0), reverse=True)
    
    # If no real news, return sample data
    if not all_news:
        all_news = [
            {
                'title': 'RBI Monetary Policy Meeting Scheduled',
                'summary': 'Reserve Bank of India to announce policy rates decision. Market expects status quo on repo rates.',
                'link': '#',
                'published': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Sample',
                'market_impact': 'High',
                'impact_type': 'Policy/Macro',
                'category': 'RBI/Policy',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'title': 'Tech Sector Earnings Preview',
                'summary': 'Major IT companies set to announce Q3 results. Analysts expect strong revenue growth.',
                'link': '#',
                'published': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Sample',
                'market_impact': 'Medium',
                'impact_type': 'Corporate/Markets',
                'category': 'Corporate Earnings',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
    
    return all_news[:15]  # Return top 15 news items

def get_market_sentiment() -> Dict:
    """Get overall market sentiment based on news"""
    try:
        news_data = get_latest_news()
        
        high_impact_count = len([n for n in news_data if n['market_impact'] == 'High'])
        total_news = len(news_data)
        
        if high_impact_count > total_news * 0.3:
            sentiment = 'Volatile'
        elif high_impact_count > total_news * 0.1:
            sentiment = 'Cautious'
        else:
            sentiment = 'Stable'
        
        return {
            'sentiment': sentiment,
            'high_impact_news': high_impact_count,
            'total_news': total_news,
            'last_updated': datetime.now().strftime('%H:%M:%S')
        }
    except:
        return {
            'sentiment': 'Unknown',
            'high_impact_news': 0,
            'total_news': 0,
            'last_updated': 'Error'
        }
