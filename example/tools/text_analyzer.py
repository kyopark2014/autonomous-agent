from strands import tool

@tool
def analyze_text(text: str) -> str:
    """Analyze text and provide statistics.
    
    Args:
        text: Text to analyze
        
    Returns:
        str: Text analysis results
    """
    words = text.split()
    sentences = text.count('.') + text.count('!') + text.count('?')
    paragraphs = text.count('\n\n') + 1 if text.strip() else 0
    
    return f"""Text Analysis:
- Characters: {len(text)}
- Words: {len(words)}
- Sentences: {sentences}
- Paragraphs: {paragraphs}
- Average words per sentence: {len(words)/max(sentences,1):.1f}"""
