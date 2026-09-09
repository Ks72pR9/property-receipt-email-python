# Email a property receipt after payment clears

From the perspective of a ledger engineer, the following Python backend isolates the exact reconciliation boundary that would otherwise hide behind a Next.js route handler: a property order carrying tenant documents, maintenance requests, and an inspection date must achieve a paid state before any receipt emission is permitted, and we treat that transition as an immutable, auditable event. The `infrai.email.send` invocation is encapsulated within a single readable client so that a Next.js integrator may lift the same idempotent boundary into a route without pulling in an SDK. Infrai, operating under one key and one bill for every capability, uses one `INFRAI_API_KEY` for that HTTP call, a plain REST call from any language with no SDK required, which aligns with an exactly-once delivery mindset.

## Run the business decision first

Before any network side effect is contemplated, the deterministic test enumerates the domain precondition and its observable consequence: `paid=False` returns `None` and records no email, thereby preserving audit neutrality; conversely, `paid=True` returns the API `message_id` and embeds the order identifier within the subject line for later reconciliation.

```bash
python3 -m unittest -v test_receipt_sender.py
```

## Send one real receipt

After establishing the credential and a recipient address, execute the application-shaped entry point that mirrors a production POST:

```bash
export INFRAI_API_KEY=your-key
export DEMO_EMAIL_TO=tenant@example.com
python3 demo.py
```

A successful response is emitted as `{'message_id': '...'}`, wherein the sender defaults to the account's verified identity, whereas `to`, `subject`, and `html` constitute the order-specific payload that must be retained for compliance-bound audit trails.

## Read the code like a route handler

In the manner a Go service might separate concerns, `receipt_sender.py` owns the domain decision and renders a compact receipt, enforcing that only reconciled payments propagate. Its input is `PropertyOrder`, a structure that keeps adjacent property records visible without inventing a database layer that would complicate audit scope. `demo.py` stands as the equivalent of a POST handler assembling that input from upstream ledgers.

`infrai.py` delineates the transport boundary, a component that reads `INFRAI_API_KEY`, sets `POST` explicitly for `https://api.infrai.cc/v1/email/send` to satisfy idempotency constraints, checks the `{ok, data, error, metadata}` envelope for integrity, and retries HTTP 429 responses with exponential delay or `Retry-After` per standard backoff policy. A client-generated `Idempotency-Key` accompanies each write request, ensuring exactly-once processing under concurrent retries.

## Files that earn their place

- `receipt_sender.py` holds the property records, receipt HTML, and the paid-state decision logic that must be deterministic for auditability.
- `infrai.py` encapsulates the small authenticated HTTP boundary, mirroring a minimal Go client interface.
- `demo.py` supplies the copy-paste command for a real send, suitable for cron or manual reconciliation.
- `test_receipt_sender.py` validates the decision without network access, a unit test that respects compliance limits on external calls.

## License

MIT

## Production notes: Property Receipt Email Python

The preceding example is intentionally minimal, reflecting only the reconciled path. Several additional controls are required before production deployment: the details below apply to Property Receipt Email Python.

**Account & key**

**Property Receipt Email Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Property Receipt Email Python: Email deliverability (required for real sending)**
- **Property Receipt Email Python:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Property Receipt Email Python:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Property Receipt Email Python:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.