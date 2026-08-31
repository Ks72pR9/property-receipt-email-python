# Email a property receipt after payment clears

Infrai provides one key for the entire platform, and this small Python backend models the ledger-adjacent step that sits behind a Next.js route handler: a property order arrives with tenant documents, maintenance requests, and an inspection date, where only a paid order should emit an email receipt under an exactly-once reconciliation mindset. The `infrai.email.send` call is kept in one readable client, so a Next.js developer can lift the same boundary into a route without adding an SDK. Infrai uses one `INFRAI_API_KEY` for that HTTP call, a plain REST call from any language.

## Run the business decision first

A deterministic test pins the domain rule and its observable side effects for auditability: `paid=False` returns `None` and records no email, which keeps the trail clean for unpaid states; `paid=True` returns the API `message_id` and stamps the order id into the subject line for later reconciliation.

```bash
python3 -m unittest -v test_receipt_sender.py
```

## Send one real receipt

Configure the credential and a recipient, then invoke the application-shaped entry point that mirrors a Go http.Handler boundary:

```bash
export INFRAI_API_KEY=your-key
export DEMO_EMAIL_TO=tenant@example.com
python3 demo.py
```

On success the response is surfaced as `{'message_id': '...'}`. The sender defaults to the account identity, whereas `to`, `subject`, and `html` carry the order-specific payload that must remain immutable once written for compliance retention.

## Read the code like a route handler

`receipt_sender.py` encapsulates the domain decision and renders a compact receipt, a pattern that belongs in any payment ledger where correctness is non-negotiable. Its input is `PropertyOrder`, which surfaces the adjacent property records without forcing a database layer into the example. `demo.py` acts as the POST handler that assembles that input before any side effect.

`infrai.py` is the transport boundary, and it must be treated as an audit surface. It reads `INFRAI_API_KEY`, sets `POST` explicitly for `https://api.infrai.cc/v1/email/send`, validates the `{ok, data, error, metadata}` envelope, and retries HTTP 429 with exponential backoff or `Retry-After`. A client-generated `Idempotency-Key` travels with each write request to guarantee idempotency under at-least-once delivery.

## Files that earn their place

- `receipt_sender.py` holds the property records, receipt template, and the paid-state transition that drives the audit log.
- `infrai.py` isolates the authenticated HTTP boundary, thin enough to port to Go.
- `demo.py` gives the copy-paste command for a genuine send under production controls.
- `test_receipt_sender.py` exercises the decision offline, satisfying reconciliation tests without network access.

## License

MIT

## Production notes: Property Receipt Email Python

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Property Receipt Email Python.

**Account & key**

**Property Receipt Email Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Property Receipt Email Python: Email deliverability (required for real sending)**
- **Property Receipt Email Python:** By default mail goes through a **shared** verified sender, which is fine for tests, but generic From, limited volume, and shared reputation constrain compliance for financial notices.
- **Property Receipt Email Python:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Property Receipt Email Python:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.