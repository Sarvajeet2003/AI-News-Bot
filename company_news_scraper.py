import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

class CompanyNewsScraper:
    """Scrape AI company blogs and announcement pages"""
    
    def __init__(self):
        self.company_sources = {
            'openai_blog': 'https://openai.com/blog/',
            'anthropic_news': 'https://www.anthropic.com/news',
            'google_ai_blog': 'https://ai.googleblog.com/',
            'microsoft_ai': 'https://blogs.microsoft.com/ai/',
            'meta_ai': 'https://ai.meta.com/blog/',
        }
    
    def scrape_openai_blog(self):
        """Scrape OpenAI blog for latest announcements"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get('https://openai.com/blog/', headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                articles = []
                
                # Look for blog post links (this may need adjustment based on OpenAI's current structure)
                blog_posts = soup.find_all('a', href=True)
                
                for post in blog_posts[:5]:  # Get first 5
                    if '/blog/' in post.get('href', ''):
                        title = post.get_text(strip=True)
                        if title and len(title) > 10:  # Filter out short/empty titles
                            articles.append({
                                'title': title,
                                'link': f"https://openai.com{post['href']}",
                                'source': 'OpenAI Blog',
                                'published': 'Recent',
                                'summary': 'Latest announcement from OpenAI'
                            })
                
                return articles[:3]  # Return top 3
        except Exception as e:
            print(f"Error scraping OpenAI blog: {e}")
            return []
    
    def get_company_announcements(self):
        """Get latest company announcements"""
        all_announcements = []
        
        try:
            # For now, just get OpenAI blog posts
            openai_posts = self.scrape_openai_blog()
            if openai_posts and isinstance(openai_posts, list):
                all_announcements.extend(openai_posts)
        except Exception as e:
            print(f"Error getting company announcements: {e}")
        
        return all_announcements  # Always return a list