from strands import tool

@tool
def convert_base(number: str, from_base: int, to_base: int) -> str:
    """Convert numbers between different bases (2-36).
    
    Args:
        number: Number to convert as string
        from_base: Source base (2-36)
        to_base: Target base (2-36)
        
    Returns:
        str: Converted number result
    """
    if from_base < 2 or from_base > 36 or to_base < 2 or to_base > 36:
        return "Error: Base must be between 2 and 36"
    
    try:
        # Convert from source base to decimal
        decimal_value = int(number, from_base)
        
        # Convert from decimal to target base
        if to_base == 10:
            result = str(decimal_value)
        else:
            digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            if decimal_value == 0:
                result = "0"
            else:
                result = ""
                while decimal_value > 0:
                    result = digits[decimal_value % to_base] + result
                    decimal_value //= to_base
        
        base_names = {2: 'Binary', 8: 'Octal', 10: 'Decimal', 16: 'Hexadecimal'}
        from_name = base_names.get(from_base, f'Base-{from_base}')
        to_name = base_names.get(to_base, f'Base-{to_base}')
        
        return f"{from_name}: {number}\n{to_name}: {result}\nDecimal: {int(number, from_base)}"
        
    except ValueError:
        return f"Error: '{number}' is not a valid number in base {from_base}"
