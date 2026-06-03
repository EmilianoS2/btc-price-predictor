import anthropic
from dotenv import load_dotenv
import feedparser
load_dotenv()

def fetch_headlines():
    titles = []
    headlines = feedparser.parse("https://www.coindesk.com/arc/outboundfeeds/rss/")
    for headline in headlines.entries:
        titles.append(headline.title)        
    return titles[:20]

def score_sentiment(headlines):
    client = anthropic.Anthropic()
    headlines_text = "\n".join(f"- {h}" for h in headlines)
    response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=512,
    tools=[{
    "name": "score_btc_sentiment",
    "description": "Score the sentiment of Bitcoin news headlines",
    "input_schema": {
        "type": "object",
        "properties": {
            "sentiment_score": {
                "type": "number",
                "description": "Only return a range between 1.0 and -1.0"
            },
            "sentiment_label": {
                "type": "string",
                "enum": ["bullish", "bearish", "neutral"],
                "description": "Only return 1 of the 3 values in enum"
            },
            "headline_count": {
                "type": "integer",
                "description": "Only read the recent 20"
            },
            "top_themes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Analyze themes of thumbnails and return the pattern most present"
            }
        },
        "required": ["sentiment_score", "sentiment_label", "headline_count", "top_themes"]
    }
}],
    tool_choice={"type": "tool", "name": "score_btc_sentiment"},
    messages=[{"role": "user", "content": f"Analyze these headlines:\n\n{headlines_text}"}]
    )
    return response.content[0].input

def collect_news_sentiment():
    headlines = fetch_headlines()
    return score_sentiment(headlines)

def validate_sentiment_output(data):
    assert data['sentiment_label'] in ['bullish', 'bearish', 'neutral']
    assert data['sentiment_score'] <= 1.0 and -1.0 >= data['sentiment_score']
    assert isinstance(data['headline_count'], int)
    assert isinstance(data['top_themes'], list)
