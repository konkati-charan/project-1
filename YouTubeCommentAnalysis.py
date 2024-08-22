import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from googleapiclient.discovery import build
import re
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

def get_comments(video_id, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    comments = []
    next_page_token = None

    while True:
        results = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            textFormat='plainText',
            maxResults=100,  # Fetch 100 comments per request (maximum allowed)
            pageToken=next_page_token
        ).execute()

        for item in results['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)

        # Check if there is a next page of comments
        next_page_token = results.get('nextPageToken')
        if next_page_token is None:
            break

    return comments

def preprocess_comment(comment):
    # Remove URLs
    comment = re.sub(r"http\S+|www\S+|https\S+", '', comment, flags=re.MULTILINE)
    # Remove mentions and hashtags
    comment = re.sub(r'\@\w+|\#', '', comment)
    # Convert to lowercase
    comment = comment.lower()
    
    # Use spaCy for tokenization and lemmatization
    doc = nlp(comment)
    words = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    
    return ' '.join(words)

def get_sentiment(comment):
    # Check if the comment is a question
    if '?' in comment:
        return 'Question'
    
    # Initialize VADER sentiment intensity analyzer
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(comment)
    
    if sentiment_score['compound'] > 0.05:
        return 'Positive'
    elif sentiment_score['compound'] < -0.05:
        return 'Negative'
    else:
        return 'Neutral'

if __name__ == "__main__":
    api_key = 'key'
    video_id = 'id'
    
    comments = get_comments(video_id, api_key)
    print(f"Total Comments Fetched: {len(comments)}")
    
    processed_comments = [preprocess_comment(comment) for comment in comments]
    sentiments = [get_sentiment(comment) for comment in comments]  # Use the original comment for sentiment analysis
    
    for comment, sentiment in zip(comments, sentiments):
        print(f"Comment: {comment} -> Sentiment: {sentiment}")
    
    sentiment_counts = Counter(sentiments)
    
    sns.barplot(x=list(sentiment_counts.keys()), y=list(sentiment_counts.values()))
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    plt.title('Sentiment Analysis of YouTube Comments')
    plt.show()
