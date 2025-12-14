from pathlib import Path


TEMPLATES_DIR = Path(__file__).parent / "templates"


def _render_template(template_name: str, context: dict) -> str:
    template_path = TEMPLATES_DIR / template_name
    template = template_path.read_text()
    return template.format(**context)


def send_email(to_email: str, subject: str, body: str) -> None:
    """
    Fake email sender for now.
    This is intentionally simple.
    """
    print("---- EMAIL ----")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print(body)
    print("---------------")


def send_booking_confirmation(payload: dict) -> None:
    body = _render_template(
        "booking_confirmation.txt",
        payload,
    )
    send_email(
        to_email=payload["user_email"],
        subject="Booking Confirmed",
        body=body,
    )


def send_payment_failure(payload: dict) -> None:
    body = _render_template(
        "payment_failure.txt",
        payload,
    )
    send_email(
        to_email=payload["user_email"],
        subject="Payment Failed",
        body=body,
    )


def send_refund_issued(payload: dict) -> None:
    body = _render_template(
        "refund_issued.txt",
        payload,
    )
    send_email(
        to_email=payload["user_email"],
        subject="Refund Issued",
        body=body,
    )
