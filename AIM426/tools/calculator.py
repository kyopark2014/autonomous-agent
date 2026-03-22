from strands import tool

@tool
def calculate_expression(expression: str) -> str:
    """Safely evaluate mathematical expressions.
    
    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 3 * 4")
        
    Returns:
        str: Result of the calculation
    """
    try:
        # Safe evaluation of basic math expressions
        allowed_chars = set('0123456789+-*/()%. ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression"
        
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error: {str(e)}"
