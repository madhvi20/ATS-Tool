def analyze_sentiment(text):
   
    positive_words = ["good", "great", "excellent"]
    sentiment = "Positive" if any(word in text.lower() for word in positive_words) else "Neutral"
    return sentiment

def summarize_text(text, length=50):
    
    return text[:length] + "..."
