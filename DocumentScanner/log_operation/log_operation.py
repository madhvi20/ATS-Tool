def clean_text(text):
    """Remove unwanted characters from text."""
    cleaned_text = text.replace("\n", " ").strip()
    return cleaned_text

def count_words(text):
    """Count the number of words in a text."""
    words = text.split()
    return len(words)
