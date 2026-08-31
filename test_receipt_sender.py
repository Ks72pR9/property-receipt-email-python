import unittest
from receipt_sender import PropertyOrder, send_receipt


class RecordingSender:
    def __init__(self):
        self.calls = []
        self.email = self

    def send(self, **payload):
        self.calls.append(payload)
        return {"message_id": "msg-test-1"}


class ReceiptDecisionTest(unittest.TestCase):
    def test_unpaid_order_does_not_send(self):
        sender = RecordingSender()
        order = PropertyOrder("LEASE-7", "Rae", "rae@example.com", 5000, False)
        self.assertIsNone(send_receipt(order, sender))
        self.assertEqual(sender.calls, [])

    def test_paid_order_sends_receipt_and_returns_message_id(self):
        sender = RecordingSender()
        order = PropertyOrder("LEASE-8", "Rae", "rae@example.com", 5000, True)
        self.assertEqual(send_receipt(order, sender), "msg-test-1")
        self.assertEqual(sender.calls[0]["to"], "rae@example.com")
        self.assertIn("LEASE-8", sender.calls[0]["subject"])


if __name__ == "__main__":
    unittest.main()
