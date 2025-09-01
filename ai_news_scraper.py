import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AINewsScraper:
    def __init__(self):
        self.sources = {
            'techcrunch_ai': 'https://techcrunch.com/category/artificial-intelligence/feed/',
            'venturebeat_ai': 'https://venturebeat.com/ai/feed/',
            'the_verge_ai': 'https://www.theverge.com/ai-artificial-intelligence/rss/index.xml',
            'ars_technica': 'https://feeds.arstechnica.com/arstechnica/technology-lab',
            'ai_news': 'https://artificialintelligence-news.com/feed/',
        }
        self.seen_articles = set()
    
    def fetch_rss_feed(self, url):
        """Fetch and parse RSS feed"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            entries = []
            
            # Handle both RSS and Atom feeds
            items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            for item in items:
                entry = {}
                
                # Get title
                title_elem = item.find('title') or item.find('.//{http://www.w3.org/2005/Atom}title')
                entry['title'] = title_elem.text if title_elem is not None else ''
                
                # Get link
                link_elem = item.find('link') or item.find('.//{http://www.w3.org/2005/Atom}link')
                if link_elem is not None:
                    entry['link'] = link_elem.text if link_elem.text else link_elem.get('href', '')
                else:
                    entry['link'] = ''
                
                # Get description/summary
                desc_elem = (item.find('description') or 
                           item.find('.//{http://www.w3.org/2005/Atom}summary') or
                           item.find('.//{http://www.w3.org/2005/Atom}content'))
                entry['summary'] = desc_elem.text if desc_elem is not None else ''
                
                # Get published date
                pub_elem = (item.find('pubDate') or 
                          item.find('.//{http://www.w3.org/2005/Atom}published') or
                          item.find('.//{http://www.w3.org/2005/Atom}updated'))
                entry['published'] = pub_elem.text if pub_elem is not None else ''
                
                entries.append(entry)
            
            return entries
            
        except Exception as e:
            logger.error(f"Error fetching RSS from {url}: {e}")
            return []
    
    def is_recent(self, published_date, hours=24):
        """Check if article is from last N hours"""
        try:
            if isinstance(published_date, str):
                # Try to parse common date formats
                from dateutil import parser
                pub_time = parser.parse(published_date)
            else:
                return True  # If we can't parse date, include it
            
            cutoff = datetime.now() - timedelta(hours=hours)
            return pub_time.replace(tzinfo=None) > cutoff
        except:
            return True  # If we can't parse date, include it
    
    def extract_ai_keywords(self, text):
        """Check if content contains AI product/release keywords"""
        # Focus on actual AI product releases and company announcements
        ai_product_keywords = [
            # Company releases
            'openai', 'anthropic', 'google ai', 'microsoft ai', 'meta ai', 'nvidia ai',
            'chatgpt', 'claude', 'gemini', 'copilot', 'bard', 'llama',
            
            # Product releases
            'releases', 'launches', 'announces', 'unveils', 'introduces',
            'new model', 'ai model', 'language model', 'llm',
            
            # Specific AI products/agents
            'ai agent', 'ai assistant', 'chatbot', 'voice assistant',
            'gpt-4', 'gpt-5', 'claude-3', 'gemini pro', 'dall-e', 'midjourney',
            
            # AI capabilities
            'multimodal', 'text-to-image', 'text-to-video', 'code generation',
            'reasoning', 'function calling', 'tool use',
            
            # Business/funding
            'funding', 'investment', 'valuation', 'startup', 'acquisition',
            'partnership', 'collaboration',
            
            # Avoid academic terms
        ]
        
        # Exclude academic/research terms
        exclude_keywords = [
            'paper', 'research', 'study', 'arxiv', 'conference',
            'journal', 'publication', 'dataset', 'benchmark'
        ]
        
        text_lower = text.lower()
        
        # Must contain AI product keywords
        has_ai_keywords = any(keyword in text_lower for keyword in ai_product_keywords)
        
        # Must not be academic content
        is_academic = any(keyword in text_lower for keyword in exclude_keywords)
        
        return has_ai_keywords and not is_academic
    
    def get_latest_news(self, hours=24):
        """Get latest AI news from all sources"""
        all_articles = []
        
        try:
            for source_name, url in self.sources.items():
                logger.info(f"Fetching from {source_name}...")
                try:
                    entries = self.fetch_rss_feed(url)
                    
                    # Ensure entries is iterable
                    if not entries or not isinstance(entries, list):
                        continue
                        
                    for entry in entries:
                        try:
                            # Check if article is recent
                            if entry.get('published') and not self.is_recent(entry.get('published'), hours):
                                continue
                            
                            # Check if content is AI-related
                            content = f"{entry.get('title', '')} {entry.get('summary', '')}"
                            if not self.extract_ai_keywords(content):
                                continue
                            
                            # Avoid duplicates
                            article_id = entry.get('link', entry.get('title', ''))
                            if article_id in self.seen_articles:
                                continue
                            
                            self.seen_articles.add(article_id)
                            
                            article = {
                                'title': entry.get('title', 'No title'),
                                'link': entry.get('link', ''),
                                'summary': entry.get('summary', '')[:300] + '...' if len(entry.get('summary', '')) > 300 else entry.get('summary', ''),
                                'source': source_name,
                                'published': entry.get('published', 'Unknown date')
                            }
                            
                            all_articles.append(article)
                        except Exception as e:
                            logger.error(f"Error processing entry from {source_name}: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error fetching from {source_name}: {e}")
                    continue
            
            return all_articles[:10]  # Return top 10 most recent
            
        except Exception as e:
            logger.error(f"Error in get_latest_news: {e}")
            return []  # Always return a list, even on error
    
    def format_article_message(self, article):
        """Format article for Telegram message using HTML"""
        # Clean title and summary for HTML
        title = self.clean_html_text(article.get('title', 'No title'))
        summary = self.clean_html_text(article.get('summary', ''))
        
        message = f"🤖 <b>{title}</b>\n\n"
        message += f"📰 Source: {article.get('source', 'Unknown')}\n"
        message += f"📅 Published: {article.get('published', 'Unknown date')}\n\n"
        
        # Only add summary if it exists
        if summary:
            message += f"📝 {summary}\n\n"
        
        message += f"🔗 <a href=\"{article.get('link', '')}\">Read more</a>"
        
        return message
    
    def clean_html_text(self, text):
        """Clean text for Telegram HTML formatting"""
        if not text:
            return ""
        
        # Escape HTML special characters
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        
        return text