import os
import io
from functools import lru_cache

import qrcode

UPI_ID = os.getenv("UPI_ID", "")
PRESET_AMOUNTS = [50, 100, 500]


def build_upi_url(amount: int | None = None) -> str:
    url = f"upi://pay?pa={UPI_ID}&cu=INR"
    if amount is not None:
        url += f"&am={amount}"
    return url


@lru_cache(maxsize=8)
def generate_qr_bytes(data: str) -> bytes:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()
