from strands import tool

@tool
def convert_units(value: float, from_unit: str, to_unit: str, unit_type: str) -> str:
    """Convert between different units (length, weight, volume).
    
    Args:
        value: Numeric value to convert
        from_unit: Source unit (e.g., 'km', 'lb', 'ml')
        to_unit: Target unit (e.g., 'mi', 'kg', 'oz')
        unit_type: Type of unit ('length', 'weight', 'volume')
        
    Returns:
        str: Conversion result
    """
    conversions = {
        'length': {
            'mm': 0.001, 'cm': 0.01, 'm': 1, 'km': 1000,
            'in': 0.0254, 'ft': 0.3048, 'yd': 0.9144, 'mi': 1609.34
        },
        'weight': {
            'mg': 0.001, 'g': 1, 'kg': 1000, 'oz': 28.3495, 
            'lb': 453.592, 'ton': 1000000
        },
        'volume': {
            'ml': 1, 'l': 1000, 'gal': 3785.41, 'qt': 946.353,
            'pt': 473.176, 'cup': 236.588, 'fl_oz': 29.5735
        }
    }
    
    if unit_type not in conversions:
        return f"Error: Unknown unit type '{unit_type}'"
    
    unit_map = conversions[unit_type]
    
    if from_unit not in unit_map or to_unit not in unit_map:
        available = list(unit_map.keys())
        return f"Error: Units must be from {available}"
    
    # Convert to base unit, then to target unit
    base_value = value * unit_map[from_unit]
    result = base_value / unit_map[to_unit]
    
    return f"{value} {from_unit} = {result:.4f} {to_unit}"
