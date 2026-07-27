---
Classification: CL2: INTERNAL
Status: Draft
Version: v0.1
---

<img src="../../../assets/branding/logo-horizontal-transparent.png" alt="DurianX Logo" width="150" style="display: block; margin: 0 0 10px 0;" />

## IT Standard Operating Procedure — VM to K8s Migration Plan (First Phase)

| Metadata | Value |
| :--- | :--- |
| **Ref ID** | OPS-SOP-2026-001 |
| **Classification** | CL2 Internal |
| **Status** | Draft |
| **Version** | v0.1 |
| **Effective Date** | 2026-07-20 |
| **Domain** | Infrastructure / Operations |
| **Applies To** | DevOps Team, Platform Engineers, QA, SDM |

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
| v0.1 | 2026-07-20 | Antigravity AI | Initial draft for ORS and Admin Laravel migration plan |

---

## 1. Objective & Strategic Intent

This Standard Operating Procedure (SOP) outlines the phased migration plan for moving the **ORS Engine (ors-engine-container)** and **Admin Laravel Web App (admin-laravel-service)** from legacy Virtual Machine (VM) host environments to the production Kubernetes (K8s / RKE2) cluster. 

These two services have been identified as candidates for the **First Phase of Kubernetes Production Migration** due to their low microservice dependency footprints:
1. **ORS Engine (OpenRouteService):** A stateless backend routing utility providing route distance and ETA calculations. It has zero microservice or database dependencies and depends solely on pre-loaded OpenStreetMap (OSM) data graphs.
2. **Admin Laravel Web App:** The internal admin panel dashboard. While it connects to database and caching components, it functions as a standalone client portal with no upstream microservice API calls dependent on it, keeping the blast radius small.

---

## 2. Scope & Applicability

This procedure applies to:
- **DevOps/Platform Team:** Creating Helm charts, provisioning namespace resources, configuring Ingress, and adjusting DNS records.
- **Software Development Team (PHP/Laravel & GIS developers):** Preparing environment variable templates and certifying builds.
- **Operations & Support Teams:** Coordinating maintenance windows and executing User Acceptance Testing (UAT).

**Financial Impact & Costs:**
* Estimated Project Cost: `$0.00 USD (0 KHR)` (Internal engineering hours).
* Expected Revenue Loss during Migration: `$0.00 USD (0 KHR)` (Services will run in parallel; DNS switchover will be seamless).

---

## 3. Roles & Responsibilities (RACI Matrix)

| Role / Team | Responsibility |
| :--- | :--- |
| **DevOps / Platform Engineers (R)** | Configure Helm charts, provision PVCs/Secrets, run migrations, execute DNS switch. |
| **Software Dev Lead (A)** | Code validation, environment configuration, database schema review. |
| **Quality Assurance (C)** | Execute staging and post-migration production smoke tests. |
| **Operations Manager (I)** | Coordinate external alerts, manage support channels, monitor CS issues. |

---

## 4. Architectural Target Layout

```
                        [ External Requests ]
                                 │
                                 ▼
                     [ Ingress Nginx / TLS ]
                                 │
         ┌───────────────────────┴───────────────────────┐
         ▼                                               ▼
  [ Service: admin-laravel ]                  [ Service: ors-engine ]
     (Port 9000 / HTTP)                          (Port 8082 / HTTP)
         │                                               │
         ├─► [ Pod: php-nginx (HA) ]                     ├─► [ Pod: ors (HA) ]
         │                                               │
         ├─► [ Config: K8s Secrets ]                     ├─► [ Volume: OSM Data PVC ]
         │                                               │
         ├─► [ DB: Postgres (External/Local) ]           └─► [ Cache: Routing Graph ]
         └─► [ Object Store: MinIO (Port 8006) ]
```

---

## 5. Phased Migration Plan

### 🚀 Phase 1: Pre-Migration & Staging Validation (Build & Deploy)
1. **Docker Container Stabilization:** 
   - Ensure `ors-engine-container` and `admin-laravel-service-container` are successfully running in the Sandbox/Staging cluster.
   - Target versions must be tagged and pushed to the Harbor registry (`registry.durian-inn.com.kh`). Avoid using the `latest` tag in production namespaces to ensure reproducibility.
2. **Helm Chart Creation:**
   - Define K8s Deployment, Service, ConfigMap, and Ingress templates.
   - For **ORS Engine**:
     - Allocate a PersistentVolumeClaim (PVC) using a fast SSD storage class to hold the raw OSM data and built routing graphs.
     - Set proper CPU/RAM resources. Because ORS builds graphs in-memory at startup, configure memory requests and limits:
       * **Requests:** `2 CPU` and `4Gi RAM`
       * **Limits:** `4 CPU` and `8Gi RAM`
   - For **Admin Laravel**:
     - Configure environment files to inject databases, Redis cache, and S3 variables via `Kubernetes Secrets`.
     - Configure Laravel `SESSION_DRIVER=redis` or `database` to allow horizontal pod scaling without disrupting admin sessions.
3. **Staging Deploy & UAT:**
   - Deploy to the `staging` namespace using ArgoCD.
   - Verify that ORS staging endpoint can calculate route vectors for the Express service.
   - Verify that the Laravel Admin panel is operational, can perform DB operations, and syncs file uploads with staging MinIO storage.

### 🔄 Phase 2: Production Setup & Parallel Run (Dry Run)
1. **Namespace Provisioning:**
   - Deploy the Helm charts to the `production` namespace (`prd`) using ArgoCD.
   - Ensure the Ingress rule is configured with a non-public host name (e.g., `admin-k8s-dryrun.durianx.com.kh`) for internal testing.
2. **Data & Storage Initialization:**
   - **ORS Engine:** Populate the OSM data volume. This can be pre-downloaded via an `initContainer` from the internal MinIO bucket or mapped from an existing network storage volume. Start the pods and verify the routing graphs compile successfully (this process may take 15–45 minutes depending on geographic graph size).
   - **Admin Laravel:** Ensure the database configuration points to the live PostgreSQL instance. Run a validation run of any pending database schemas:
     ```bash
     kubectl exec -it <laravel-pod-name> -- php artisan migrate --pretend
     ```
3. **Internal Smoke Testing:**
   - QA team tests both endpoints directly by bypassing the current public routing.
   - Verify that K8s-hosted ORS returns coordinates matching the legacy VM ORS engine outputs.

### ⚡ Phase 3: Traffic Switch & Cut-Over (Go-Live)
To minimize risk, execute the cut-over during the standard off-peak maintenance window: **Saturday / Sunday 10:00 PM ICT to 12:00 AM ICT (2 Hours)**.

#### Step 3.1: ORS Engine Cut-Over (API Routing)
1. ORS is stateless to the caller. Modify the API routing configuration in the main API Gateways (e.g., `durianx-api-gateway-consumer-gateway-1` and `durianx-api-gateway-dispatch-api-1`) via their ConfigMaps or Helm values.
2. Re-point the ORS backend host destination from `http://<LEGACY_VM_IP>:8082` to the cluster-internal DNS service name:
   `http://ors-engine-service.production.svc.cluster.local:8082`
3. Apply the changes via ArgoCD.
4. Verify routing endpoints immediately via the Dispatch Service logs.

#### Step 3.2: Admin Laravel Cut-Over (DNS Update)
1. Set the DNS TTL for the admin domain (`admin.durianx.com.kh`) to 300 seconds (5 minutes) 24 hours prior to the migration.
2. During the maintenance window, place the admin application on the legacy VM into maintenance mode:
   ```bash
   php artisan down --secret="k8smigration2026"
   ```
3. Run the database migration script in the production Kubernetes pod to apply any final schema updates:
   ```bash
   kubectl exec -it <laravel-prod-pod-name> -- php artisan migrate --force
   ```
4. Change the DNS CNAME record of `admin.durianx.com.kh` to point to the production Kubernetes Ingress Controller's load balancer IP.
5. Once DNS propagates, verify login sessions and dashboard writes.

### 📊 Phase 4: Post-Migration Monitoring & Soak Period
1. **Soak Period (48-72 Hours):**
   - Keep the legacy VM running in an active state but receiving no traffic.
   - Monitor Prometheus/Grafana dashboard telemetry. 
   - Key indicators: HTTP 5xx error rates, response latencies (target `< 200ms` for API endpoints), CPU/Memory spikes.
2. **Decommissioning:**
   - Once the services demonstrate stability (e.g., `< 0.25%` production crash rate delta), shut down the docker containers on the legacy VM.
   - Clean up VM resources after a 7-day safety period.

---

## 6. Rollback / Backout Plan

In the event of critical anomalies, resource exhaustion, or service failure during the 2-hour maintenance window:

1. **ORS Engine Rollback:**
   - Revert the API Gateway host configuration change to point back to `http://<LEGACY_VM_IP>:8082`.
   - Re-sync/apply the API Gateway via ArgoCD.
2. **Admin Laravel Rollback:**
   - Revert the DNS CNAME record for `admin.durianx.com.kh` back to the legacy VM IP address.
   - Run `php artisan up` on the VM application.
   - Note: Because Laravel database schemas are backward-compatible, database rollbacks are generally not executed unless a destructive schema migration occurred. In that case, restore the database backup taken immediately prior to the cut-over.

---

## 7. Operational & SLA Targets

During and after the migration, the services must continue meeting the platform's global SLAs:
* **Production Crash Rate Delta:** `< 0.25%`
* **Lead time for migration deployment:** `< 48 hours`
* **First Response SLA for any migration issues:** `< 15 minutes`

---

## 8. Financial Ledger Compliance
> [!NOTE]
> This is an infrastructure and deployment Standard Operating Procedure. It does not involve any movement of funds, financial ledger entries, or currency conversions. Therefore, no double-entry ledger table (Dr/Cr) is required.

---

## 9. Next Steps & Approval Action Items
1. Review this draft with the Software Development Manager (SDM) and Platform Lead.
2. Schedule the dry-run window for the Staging environment.
3. Submit the formal IT Change Request (CR) once this SOP is reviewed.
