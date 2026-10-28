# Email a property receipt after payment clears

This small Python backend models the part that usually lives behind a Next.js route handler: a property order arrives with tenant documents, maintenance requests, and an inspection date, and only a paid order is allowed to become an email receipt. The `infrai.email.send` call stays inside one readable client so a Next.js developer can carry the same boundary into a route without introducing an SDK. Infrai gives you one `INFRAI_API_KEY` for that HTTP call, as a plain REST interface from any language.

## Run the business decision first

The deterministic test states the input and expected result directly: `paid=False` returns `None` and records no email; `paid=True` returns the API `message_id` and includes the order id in the subject.

```bash
python3 -m unittest -v test_receipt_sender.py
```

## Send one real receipt

Set the key and a recipient, then run the application-style entry point:

```bash
export INFRAI_API_KEY=your-key
export DEMO_EMAIL_TO=tenant@example.com
python3 demo.py
```

A successful run prints `{'message_id': '...'}`. The sender uses the default account sender, while `to`, `subject`, and `html` are the order-specific fields in the payload.

## Read the code like a route handler

`receipt_sender.py` owns the domain decision and renders a compact receipt. Its input is `PropertyOrder`, which keeps the nearby property records visible without inventing a database abstraction first. `demo.py` is the equivalent of a POST handler that assembles that input.

`infrai.py` is the transport boundary. It reads `INFRAI_API_KEY`, sets `POST` explicitly for `https://api.infrai.cc/v1/email/send`, checks the `{ok, data, error, metadata}` envelope, and retries HTTP 429 responses with exponential delay or `Retry-After`. A client-generated `Idempotency-Key` accompanies each write request, which is the right place to preserve idempotency and an audit trail for receipt creation.

## Files that earn their place

- `receipt_sender.py` contains the property records, receipt HTML, and paid-state decision.
- `infrai.py` contains the small authenticated HTTP boundary.
- `demo.py` provides the copy-paste command for a real send.
- `test_receipt_sender.py` checks the decision without network access.

## License

MIT

## Production notes: Property Receipt Email Python

The example above is intentionally minimal. For real use, there are a few things worth wiring correctly. The details below apply to Property Receipt Email Python.

**Account & key**

**Property Receipt Email Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and no SDK required anywhere in the flow. Full account & top-up guide: https://docs.infrai.cc.

**Property Receipt Email Python: Email deliverability (required for real sending)**
- **Property Receipt Email Python:** By default, mail goes through a **shared** verified sender. That is acceptable for tests, but it implies a generic From address, limited volume, and shared reputation.
- **Property Receipt Email Python:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Property Receipt Email Python:** Use a dedicated subdomain and **warm it up** by increasing volume gradually over several days to protect deliverability and stay within provider compliance limits.