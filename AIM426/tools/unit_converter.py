from strands import tool

@tool
def convert_temperature(value: float, from_unit: str, to_unit: str) -> str:
    """Convert temperature between Celsius, Fahrenheit, and Kelvin.
    
    Args:
        value: Temperature value to convert
        from_unit: Source unit ('C', 'F', or 'K')
        to_unit: Target unit ('C', 'F', or 'K')
        
    Returns:
        str: Converted temperature result
    """
    # Convert to Celsius first
    if from_unit.upper() == 'F':
        celsius = (value - 32) * 5/9
    elif from_unit.upper() == 'K':
        celsius = value - 273.15
    else:  # Celsius
        celsius = value
    
    # Convert from Celsius to target
    if to_unit.upper() == 'F':
        result = celsius * 9/5 + 32
    elif to_unit.upper() == 'K':
        result = celsius + 273.15
    else:  # Celsius
        result = celsius
    
    return f"{value}°{from_unit.upper()} = {result:.2f}°{to_unit.upper()}"
