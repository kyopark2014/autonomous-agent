"""
QR Code Generator Tool
"""
from strands import tool
from typing import Dict, Any
import tempfile
from pathlib import Path


@tool
def qr_code(
    data: str,
    output_path: str = None,
    size: int = 10,
    border: int = 4,
) -> Dict[str, Any]:
    """
    Generate a QR code from text/URL data.
    
    Args:
        data: Text or URL to encode in QR code
        output_path: Path to save QR code image (default: temp file)
        size: Size of QR code boxes (default: 10)
        border: Border size in boxes (default: 4)
    
    Returns:
        Dict with status and QR code image path
    """
    try:
        import qrcode
    except ImportError:
        import subprocess
        subprocess.check_call(["pip", "install", "qrcode[pil]"])
        import qrcode
    
    try:
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to file
        if output_path is None:
            output_path = tempfile.mktemp(suffix=".png", prefix="qr_")
        
        output_path = Path(output_path).expanduser()
        img.save(str(output_path))
        
        return {
            "status": "success",
            "content": [{
                "text": f"✅ QR code generated successfully!\n\n📍 Saved to: {output_path}\n📊 Data: {data}\n📐 Size: {size}x{size} boxes\n🖼️  Border: {border} boxes"
            }]
        }
    
    except Exception as e:
        return {
            "status": "error",
            "content": [{"text": f"❌ Failed to generate QR code: {str(e)}"}]
        }
