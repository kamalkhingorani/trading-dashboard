import requests
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict
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
                'energy', 'fmcg', 'telecom', 'real estate','defense','manufacturing',
                 'infrastructure'
            ]
        }
        
        self.news_sources = {
            'economic_times': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
            'business_standard': 'https://www.business-standard.com/rss/markets-106.rss',
            'moneycontrol': 'https://www.moneycontrol.com/rss/business.xml',
            'livemint': 'https://www.livemint.com/rss/money',
            'financial_express': 'https://www.financialexpress.com/market/rss'
        }
    
    def fetch_rss_news(self, url: str, source: str) -> List[Dict]:
        """Fetch news from RSS feeds"""
        try:
            feed = feedparser.parse(url)
            news_items = []
            
            for entry in feed.entries[:10]:  # Limit to 10 items per source
                news_items.append({
                    'title': entry.get('title', ''),
                    'summary': entry.get('summary', entry.get('description', ''))[:300],
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'source': source
                })
            
            return news_items
        except Exception as e:
            st.warning(f"Error fetching from {source}: {str(e)}")
            return []
    
    def analyze_market_impact(self, title: str, summary: str) -> Tuple[str, str]:
        """Analyze the potential market impact of news"""
        text = (title + " " + summary).lower()
        
        # Check for high impact keywords
        for keyword in self.market_keywords['high_impact']:
            if keyword in text:
                return
