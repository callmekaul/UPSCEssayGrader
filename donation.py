import os
import io

import qrcode
import streamlit as st

UPI_ID = os.getenv("UPI_ID", "")

PRESET_AMOUNTS = [50, 100, 500]


def _build_upi_url(amount: int | None = None) -> str:
    url = f"upi://pay?pa={UPI_ID}&cu=INR"
    if amount is not None:
        url += f"&am={amount}"
    return url


@st.cache_data
def _generate_qr_bytes(data: str) -> bytes:
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


@st.dialog("Support This Project")
def show_donation_dialog():
    if not UPI_ID:
        st.warning("Donation is not configured yet.")
        return

    st.markdown(
        "If you found this tool helpful, consider supporting its development!"
        "Scan the QR code or tap the button below to pay via UPI."
    )

    amount_options = [f"\u20b9{a}" for a in PRESET_AMOUNTS] + ["Custom"]
    selected = st.radio("Choose an amount", options=amount_options, horizontal=True)

    if selected == "Custom":
        amount = None
        st.caption("You can enter any amount in your UPI app after scanning.")
    else:
        amount = int(selected.replace("\u20b9", ""))

    upi_url = _build_upi_url(amount)
    qr_bytes = _generate_qr_bytes(upi_url)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(qr_bytes, caption="Scan with any UPI app", width=220)

    st.markdown(
        f'<div style="text-align:center; margin-top:8px;">'
        f'<a href="{upi_url}" target="_blank" '
        f'style="display:inline-block; padding:10px 24px; '
        f"background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); "
        f'color:white; border-radius:8px; text-decoration:none; '
        f'font-weight:600; font-size:15px;">'
        f"\u20b9 Open UPI App</a></div>",
        unsafe_allow_html=True,
    )

    # st.caption("This is a voluntary donation. No payment is required to use this tool.")
