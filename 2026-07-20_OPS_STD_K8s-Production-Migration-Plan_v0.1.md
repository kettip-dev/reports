---
Classification: CL2: INTERNAL
Status: Draft
Version: v0.1
---

<img src="../../../assets/branding/logo-horizontal-transparent.png" alt="DurianX Logo" width="150" style="display: block; margin: 0 0 10px 0;" />

## IT Standard — Kubernetes (K8s) Production Migration Plan & Phased Strategy

| Metadata | Value |
| :--- | :--- |
| **Ref ID** | OPS-STD-2026-002 |
| **Classification** | CL2 Internal |
| **Status** | Draft |
| **Version** | v0.1 |
| **Effective Date** | 2026-07-20 |
| **Domain** | Infrastructure / DevOps |
| **Applies To** | DevOps Team, QA Team, Software Development Managers, EM |

## Document Control & Approval

| Role | Title | Signature / Date |
| --- | --- | --- |
| **Author** | Antigravity AI | 2026-07-20 |
| **Reviewer** | SDM, PMO | |
| **Owner** | CTPO | |
| **Final Approver** | CEO | |

## Revision History

| Version | Date | Author | Description of Change |
| --- | --- | --- | --- |
| v0.1 | 2026-07-20 | Antigravity AI | Initial draft mapping the 4-phase service migration plan |

---

## 1. Objective & Strategic Intent

This standard establishes the master sequence, rules, and procedures for migrating the remaining DurianX services from legacy VM architectures to the production Kubernetes (K8s / RKE2) environment. 

To maintain platform availability, ensure data integrity, and minimize operational risk, a **single-day "lift-and-shift" of all services is strictly forbidden**. Services will be migrated in structured phases grouped by dependency depth, utilizing stateless compute abstractions while keeping database layers external and stable.

---

## 2. Migration Scope & Phased Grouping

The services cataloged in the [Running Services Inventory](./2026-07-17_OPS_STD_Running-Services-Inventory_v1.0.md) are categorized into four migration phases based on a **Tiered Dependency Grouping** model.

```
                  ┌─────────────────────────────────────────┐
                  │ PHASE 1: Gateways & Stateless Engines   │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │ PHASE 2: Portals & Operations Panels     │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │ PHASE 3: Core Identity & Profiles (APIs) │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │ PHASE 4: Transaction & Dispatch Engines │
                  └─────────────────────────────────────────┘
```

### 🗺️ Migration Phases

| Phase | Category | Target Services | Host Port(s) | Primary Purpose / Notes |
| :---: | :--- | :--- | :---: | :--- |
| **1** | **Gateways & Stateless** | `ors-engine-container` <br> `geocode-service-nominatim-1` <br> `durianx-api-gateway-merchant-gateway-1` <br> `durianx-api-gateway-rider-gateway-1` <br> `durianx-api-gateway-dispatch-api-1` (DX Gateway) | 8082 <br> 8027 <br> 8002 <br> 8010 <br> 8013 | Establishes the routing skeleton. ORS & Geocode provide ETA calculations. API Gateways govern token validation and traffic routing. |
| **2** | **Portals & Operations** | `admin-laravel-service-container` <br> `durianx-dispatchment-portal-frontend-1` <br> `durianx-sale-portal-frontend-1` <br> `food-service frontend` (Admin) <br> `dx-sms-email-service-smsandemail.worker-1` | 9000 <br> 8022 <br> 8037 <br> — <br> — | Operational dashboard and administrative portals. Highly isolated; user-facing mobile apps will not experience outages if these panels experience minor disruption. |
| **3** | **Core Identity & Profiles** | `durianx-user-provider-identity-api-1` <br> `durianx-merchant-service-api-1` <br> `durianx-driver-service-api-1` <br> `durianx-api-gateway-notification-api-1` | 8007 <br> 8008 <br> 8011 <br> 8002 | Master profiles and authentication services. These act as directory systems providing user, driver, and merchant profile states to other services. |
| **4** | **Transactions & Dispatch** | `durianx-api-gateway-dispatch-api-1` (Dispatch Engine) <br> `durianx-express-api-1` <br> `durianx-food-provider-api-1` <br> `durianx-websocket-api-1` <br> `dx-call-service-api-1` <br> `durianx-pre-order-service-pre-order-1` | 8013 <br> 8025 <br> — <br> 8019 <br> 6032 <br> 8029 | Core transaction execution engines (Ride dispatch, Express delivery, Food ordering, WebSockets, and Twilio/LiveKit voice routing). High complexity. |

---

## 3. Database & Caching Strategy (State Isolation)

To ensure high availability and prevent data loss, the following mandates apply:
1. **Production Databases Remain External:** All live production PostgreSQL databases MUST remain on their existing dedicated bare-metal or VM database hosts. No primary transaction databases may be containerized inside the Kubernetes cluster during this migration sequence.
2. **External Caching Layer:** Redis cache servers supplying real-time session, dispatch, and driver coordinates must remain on dedicated host servers outside Kubernetes to prevent replication lag and cache warming outages during pod redeployments.
3. **Internal Connection Configuration:** Kubernetes pods will access these external data layers via secure connection strings injected dynamically using `Kubernetes Secrets` (refer to the [Secure SDLC Standard](../Release%20Managentment%20Pipeline/2026-06-16_SEC_STD_Secure-SDLC_v1.0.md)).

---

## 4. Route Switchover & DNS Cut-Over Procedure

During each migration phase, traffic must be redirected from the legacy VM servers to the Kubernetes Ingress Controller using a hybrid routing approach:

```
[Public Ingress Traffic] ──► [DNS Domain Router]
                                    │
                        ┌───────────┴───────────┐
                        ▼                       ▼
            [Portals & Frontend]       [Microservice APIs]
                        │                       │
                        ▼                       ▼
            [DNS CNAME Update]         [API Gateway Config]
            (admin.durianx.com.kh)      (Internal Route DNS)
                        │                       │
                        └───────────┬───────────┘
                                    ▼
                         [Kubernetes Pod Groups]
```

### 4.1. Internal Microservice APIs (Phases 1, 3, and 4)
* **Mechanism:** Dynamic Gateway Re-routing.
* **Steps:** 
  1. Deploy the new service container inside the `production` namespace.
  2. Modify the target destination URI inside the central API Gateways (`durianx-api-gateway-consumer-gateway-1` / `durianx-api-gateway-dispatch-api-1`) to map from VM IPs to internal cluster DNS service endpoints:
     `http://<service-name>.production.svc.cluster.local:<port>`
  3. Re-apply configurations using ArgoCD.

### 4.2. Public Portals and Frontends (Phase 2)
* **Mechanism:** DNS CNAME record swap with low Time-To-Live (TTL).
* **Steps:**
  1. 24 hours prior to migration, reduce the TTL of the target DNS record (e.g., `admin.durianx.com.kh`) to 300 seconds (5 minutes).
  2. Put the legacy VM application into maintenance mode.
  3. Run any final schema migrations from the K8s admin pod.
  4. Update the DNS CNAME record to point to the production Ingress Controller load balancer IP.
  5. Monitor propagation and confirm DNS traffic matches the new Ingress routes.

---

## 5. Pre-Cutover Validation & QA Testing

To guarantee correctness before live users encounter the newly migrated deployments:
1. **Private Ingress Testing:** Deploy each service configuration in the production K8s namespace mapped to a private, non-public Ingress hostname (e.g., `admin-k8s-dryrun.durianx.com.kh`).
2. **Local Hosts Bypass:** QA Engineers and DevOps staff must modify their local workstations' hosts files to route production domain traffic directly to the Kubernetes Ingress IP:
   `10.36.100.200  admin.durianx.com.kh`
3. **Verification Checklist:** Complete end-to-end regression workflows (such as order checkout, route calculation, or user profile updates) using the hosts override before updating public DNS records.

---

## 6. Post-Migration Soak & Rollback Rules

1. **72-Hour Soak Period:** Once traffic is shifted to Kubernetes, the legacy VM hosts must remain in an **active, hot-standby state for 72 hours**. Docker containers on VM hosts must not be stopped or modified during this soak window.
2. **Rollback Trigger Criteria:** A rollback MUST be immediately initiated if:
   * Production crash rates delta exceeds the SLA target of `0.25%`.
   * Mean Time to Recover (MTTR) a critical downstream connection exceeds 15 minutes.
   * Internal telemetry alerts high-severity CPU/Memory throttling on K8s nodes.
3. **Rollback Actions:**
   * **Portals:** Revert DNS CNAME records to the legacy VM IP address.
   * **APIs:** Revert the API Gateway configuration values in GitLab to target the VM IP address and sync via ArgoCD.

---

## 7. Financial Ledger Compliance
> [!NOTE]
> This is an infrastructure and deployment Standard. It does not involve any movement of funds, financial ledger entries, or currency conversions. Therefore, no double-entry ledger table (Dr/Cr) is required.

---

## 8. Migration SOP Index
Refer to these specific domain migration SOPs for detail:
* [Phase 1 & 2: ORS Engine & Admin Laravel Migration SOP](./2026-07-20_OPS_SOP_VM-to-K8s-Migration-Plan_v0.1.md)
