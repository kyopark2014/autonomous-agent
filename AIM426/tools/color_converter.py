from strands import tool

@tool
def convert_color(color_value: str, from_format: str, to_format: str) -> str:
    """Convert colors between different formats (hex, rgb, hsl).
    
    Args:
        color_value: Color value to convert (e.g., "#FF5733", "rgb(255,87,51)")
        from_format: Source format ('hex', 'rgb', 'hsl')
        to_format: Target format ('hex', 'rgb', 'hsl')
        
    Returns:
        str: Converted color value
    """
    def hex_to_rgb(hex_val):
        hex_val = hex_val.lstrip('#')
        return tuple(int(hex_val[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def rgb_to_hsl(r, g, b):
        r, g, b = r/255.0, g/255.0, b/255.0
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        h, s, l = 0, 0, (max_val + min_val) / 2
        
        if max_val == min_val:
            h = s = 0
        else:
            d = max_val - min_val
            s = d / (2 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)
            if max_val == r:
                h = (g - b) / d + (6 if g < b else 0)
            elif max_val == g:
                h = (b - r) / d + 2
            elif max_val == b:
                h = (r - g) / d + 4
            h /= 6
        
        return int(h*360), int(s*100), int(l*100)
    
    # Parse input
    if from_format == 'hex':
        r, g, b = hex_to_rgb(color_value)
    elif from_format == 'rgb':
        # Extract numbers from rgb(r,g,b) format
        import re
        numbers = re.findall(r'\d+', color_value)
        r, g, b = int(numbers[0]), int(numbers[1]), int(numbers[2])
    
    # Convert to target format
    if to_format == 'hex':
        result = rgb_to_hex(r, g, b)
    elif to_format == 'rgb':
        result = f"rgb({r},{g},{b})"
    elif to_format == 'hsl':
        h, s, l = rgb_to_hsl(r, g, b)
        result = f"hsl({h},{s}%,{l}%)"
    
    return f"Input: {color_value} ({from_format})\nOutput: {result} ({to_format})"
