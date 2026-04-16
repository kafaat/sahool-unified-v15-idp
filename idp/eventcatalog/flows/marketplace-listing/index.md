---
id: marketplace-listing
name: Marketplace Listing Creation
version: 1.0.0
summary: A farmer creates a marketplace listing; billing records the fee and a notification confirms the listing.
steps:
  - id: sahool.marketplace.listing_created
    title: Listing Created
    service: marketplace-service
  - id: sahool.billing.fee_charged
    title: Listing Fee Charged
    service: billing-core
  - id: sahool.notification.sent
    title: Confirmation Sent
    service: notification-service
---

The farmer submits a new produce listing through the mobile or web app. Kong routes the request to the marketplace-service which persists it in PostgreSQL. A listing-created event is published; billing-core charges the listing fee and notification-service sends a confirmation to the farmer with listing details.

```mermaid
sequenceDiagram
    participant F as Farmer (Mobile/Web)
    participant K as Kong Gateway
    participant MKT as marketplace-service
    participant PG as PostgreSQL
    participant NATS as NATS JetStream
    participant BC as billing-core
    participant NS as notification-service

    F->>K: POST /api/v1/marketplace/listings
    K->>MKT: forward request
    MKT->>PG: INSERT listing
    MKT-->>K: 201 Created
    K-->>F: listing confirmation
    MKT->>NATS: publish sahool.marketplace.listing_created
    par Billing
        NATS->>BC: deliver sahool.marketplace.listing_created
        BC->>BC: charge listing fee
    and Notification
        NATS->>NS: deliver sahool.marketplace.listing_created
        NS->>F: push notification (listing live)
    end
```
