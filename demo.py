"""Runnable local entry point: send one settled property receipt."""
import os
from infrai import infrai
from receipt_sender import PropertyOrder, send_receipt


def main() -> None:
    recipient = os.environ.get("DEMO_EMAIL_TO")
    if not recipient:
        raise RuntimeError("DEMO_EMAIL_TO is required")
    order = PropertyOrder("LEASE-104", "Mina Chen", recipient, 185000, True)
    print({"message_id": send_receipt(order, infrai)})


if __name__ == "__main__":
    main()
