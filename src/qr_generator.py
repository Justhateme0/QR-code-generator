import qrcode
from PIL import Image
import io
from src.config import QR_STYLES

def create_qr_code(text: str, style: str = 'classic') -> io.BytesIO:
    """Create a QR code with the specified style."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    style_config = QR_STYLES.get(style, QR_STYLES['classic'])
    qr_image = qr.make_image(fill_color=style_config['fill_color'], back_color=style_config['back_color'])
    
    # Save QR code to bytes
    bio = io.BytesIO()
    bio.name = 'qr.png'
    qr_image.save(bio, 'PNG')
    bio.seek(0)
    return bio 