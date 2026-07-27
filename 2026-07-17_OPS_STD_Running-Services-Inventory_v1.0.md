# DurianX — Running Services Inventory

---

| Field        | Value                                                       |
| :----------- | :---------------------------------------------------------- |
| **Document** | 2026-07-17_OPS_STD_Running-Services-Inventory_v1.0         |
| **Type**     | Standard / Inventory                                        |
| **Audience** | Engineering · Operations · DevOps                           |
| **Status**   | Draft                                                       |
| **Author**   | Product & Development Team                                  |
| **Version**  | v1.0                                                        |
| **Date**     | 2026-07-17                                                  |
| **Source**   | Docker `docker ps` snapshot — Sandbox + Production nodes    |

---

## Table of Contents

1. [Overview](#1-overview)
2. [Backend Microservices (.NET / dotnet)](#2-backend-microservices-net--dotnet)
3. [API Gateways](#3-api-gateways)
4. [Frontend Portals (Nginx)](#4-frontend-portals-nginx)
5. [Infrastructure & Support Services](#5-infrastructure--support-services)
6. [Third-Party & Integration Services](#6-third-party--integration-services)
7. [Port Reference Table](#7-port-reference-table)
8. [Service Health Summary](#8-service-health-summary)

---

## 1. Overview

This document catalogs all DurianX services currently running across **Sandbox** and **Production** environments as observed from the Docker container inventory. Services are deployed via **GitLab CI/CD → ArgoCD → Kubernetes**, using images pulled from `registry.durian-inn.com.kh`.

### Environment Tags

| Tag | Meaning |
| :--- | :--- |
| `sandbox` | Staging / QA environment — non-production |
| `prd` / `prod` | Production environment — live traffic |
| `latest` | Production-tagged image |
| `alpha` | Pre-release feature branch |

### Runtime Summary

| Category | Count |
| :--- | :---: |
| Backend Microservices (.NET) | 13 |
| API Gateways | 4 |
| Frontend Portals | 5 |
| Infrastructure / Support | 7 |
| Third-Party / Integrations | 6 |
| **Total** | **~35** |

---

## 2. Backend Microservices (.NET / dotnet)

These are the core DurianX business-logic services, running as `.dotnet` containers.

| # | Service Name | Container / Image | Version | Port(s) | Environment | Domain |
| ---: | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Merchant Service** | `durianx-merchant-service-api-1` | 2.8.0-alpha.2 | 8008→80 | Sandbox | Merchants |
| 2 | **User Service** | `durianx-user-provider-identity-api-1` | 1.1.4-alpha.1 | 8007→80 | Sandbox | Consumers |
| 3 | **AR Service** | `durianx-ar-service-api-1` | latest | 8028→80 | Production | Accounts Receivable |
| 4 | **Dispatch Service** | `durianx-api-gateway-dispatch-api-1` | 1.1.27-alpha | 8013→80 | Sandbox | Dispatch |
| 5 | **Notification Service** | `durianx-api-gateway-notification-api-1` | 1.3.2-alpha.2 | 8002→80, 8036→80 | Sandbox | Notifications |
| 6 | **Express Service** | `durianx-express-api-1` | 1.0.9-alpha | 8025→80 | Sandbox | Express Logistics |
| 7 | **Driver Service** | `durianx-driver-service-api-1` | 1.0.3-alpha | 8011→80 | Sandbox | Rider Partner |
| 8 | **Driver Log Service** | `durianx-driver-location-recording-service-a` | latest | 8016→80 | Production | Rider Partner |
| 9 | **Food Service** | `durianx-food-provider-api-1` | 1.1.1-alpha.1 | — | Sandbox | Food Delivery |
| 10 | **Call Service** | `dx-call-service-api-1` | 1.0.0-alpha.5 | 6032→80 | Sandbox | CS Call / LiveKit |
| 11 | **WebSocket Service** | `durianx-websocket-api-1` | 2.1.0-alpha.1 | 8019→80 | Sandbox | Real-time / Chat |
| 12 | **Rating Service** | `durianx-rating-api-1` | latest | 8040→80 | Production | Ratings |
| 13 | **FeeCharge Service** | `durianx-charge-engine-api-1` | latest | 8024→80 | Production | Billing / Fees |
| 14 | **Pre-Order Service** | `durianx-pre-order-service-pre-order-1` | 1.0.0-alpha.7 | 8029→80 | Sandbox | Pre-Order |

### Service Descriptions

| Service | Purpose |
| :--- | :--- |
| **Merchant Service** | Manages merchant registration, profile, commission config, and POS integration |
| **User Service** | Handles consumer identity, authentication, and profile management |
| **AR Service** | Accounts Receivable — manages merchant/user outstanding balances |
| **Dispatch Service** | Core order-to-driver matching engine (proximity, tier, auto-accept logic) |
| **Notification Service** | Push notifications for order events, promotions, and CS alerts |
| **Express Service** | Courier/parcel logistics — Standard and Merchant Express (Receiver Pay / Merchant Pay) |
| **Driver Service** | Rider Partner profile, wallet, tier (Member → Silver → Gold → Platinum), and quest/gems |
| **Driver Log Service** | Real-time GPS location recording and replay for driver tracking |
| **Food Service** | Restaurant menu, order lifecycle, and Merchant POS injection |
| **Call Service** | CS call routing via LiveKit — links CS agents to consumers/drivers |
| **WebSocket Service** | Real-time bidirectional events (order status push, chat) |
| **Rating Service** | Post-trip/order rating collection and storage |
| **FeeCharge Service** | Dynamic fee calculation — late cancel fee, express metered billing, extra location charge |
| **Pre-Order Service** | Scheduled ride/order booking for future time slots |

---

## 3. API Gateways

API Gateways front the microservices and route external traffic.

| # | Gateway Name | Container | Port(s) | Environment | Routes To |
| ---: | :--- | :--- | :--- | :--- | :--- |
| 1 | **Merchant Gateway** | `durianx-api-gateway-merchant-gateway-1` | 8002→80 | Sandbox | Merchant Service |
| 2 | **Rider Gateway** | `durianx-api-gateway-rider-gateway-1` | 8010→80, 8037→80 | Sandbox | Driver Service |
| 3 | **Consumer Gateway** | `durianx-api-gateway-consumer-gateway-1` | 8004→80 | Production | User Service / Food / Express |
| 4 | **DX Gateway (Main)** | `durianx-api-gateway-dispatch-api-1` | 8013→80 | Sandbox | Dispatch Service |

> **NOTE:** All gateways enforce JWT authentication, rate limiting, and route isolation per service domain. Do not expose raw microservice ports externally.

---

## 4. Frontend Portals (Nginx)

Web portals served via Nginx reverse proxy (`/entrypoint.sh nginx`).

| # | Portal Name | Container | Port(s) | Environment | Users |
| ---: | :--- | :--- | :--- | :--- | :--- |
| 1 | **Dispatch Portal** | `durianx-dispatchment-portal-frontend-1` | 8022→80 | Sandbox | OPS Team — order dispatch monitoring |
| 2 | **Merchant Portal** | `durianx-merchant-portal-frontend-1` | 8001→80 | Production | Merchant Admins — POS & order management |
| 3 | **Sale Portal** | `durianx-sale-portal-frontend-1` | 8037→80 | Sandbox | Sales Team — CRM & merchant acquisition |
| 4 | **Food Portal (Admin)** | *(food-service frontend)* | — | Sandbox | Food Ops — menu and restaurant management |
| 5 | **Mini App (Consumer TG)** | `telegram-mini-app-vuets-consumer-mini-app-t` | 8003→80 | Production | Consumers via Telegram Mini App |

---

## 5. Infrastructure & Support Services

Core infrastructure components that support all other services.

| # | Service Name | Container | Port(s) | Purpose |
| ---: | :--- | :--- | :--- | :--- |
| 1 | **MinIO (File Storage)** | `dx-file-minio-prd` | 8006→80 | S3-compatible object storage — receipts, images, recordings |
| 2 | **Nginx (Alpine)** | `nginx:alpine` | 8055→80 | Edge reverse proxy / static file serving |
| 3 | **Geocode Service** | `geocode-service-nominatim-1` | 8027→80, 5432→80 | Local OpenStreetMap geocoding (Nominatim) — address → coordinates |
| 4 | **Proget (Package Registry)** | `proget` | 8624→80 | Internal NuGet / Docker image registry |
| 5 | **SMS Email Worker** | `dx-sms-email-service-smsandemail.worker-1` | — | Background worker — SMS and email dispatch (OTP, alerts) |
| 6 | **Telegram Bot (Consumer)** | `bot-telegram-consumer-service-nest-app-1` | 3000 | Telegram bot service for consumer-facing interactions |
| 7 | **Web App (Admin Laravel)** | `admin-laravel-service-container` | 9000 | Admin panel backend (Laravel/PHP) |

---

## 6. Third-Party & Integration Services

External integrations and partner tools running within the DurianX environment.

| # | Service Name | Container | Port(s) | Purpose |
| ---: | :--- | :--- | :--- | :--- |
| 1 | **AI Search (Web UI)** | `ai-search-web-ui` | 8501→80, 8502→80 | Internal AI-powered search — Bong X feature |
| 2 | **TikTok Sync API** | `tiktok_sync_api` | — | Syncs product catalog / promotions to TikTok Shop |
| 3 | **ORS Engine** | `ors-engine-container` | 8082→80 | OpenRouteService — routing engine for ETA calculation |
| 4 | **Dispatch Portal (Prod)** | `dx-prod-dispatch-portal` | 8055→80 | Production dispatch dashboard |
| 5 | **Super App Sync** | `durianx-sync-service-prod` | 8015→80 | Cross-service data synchronisation (super app aggregator) |
| 6 | **Order Web App** | `durianx-order-web-app-ar-portal-1` | — | AR Portal web app for order/account reconciliation |

---

## 7. Port Reference Table

Complete port allocation map to avoid conflicts during new service deployments.

| Port (Host) | Service | Environment |
| :---: | :--- | :--- |
| 3000 | Telegram Bot Consumer | Production |
| 5432 | Geocode Service (Nominatim DB) | Production |
| 6032 | Call Service API | Sandbox |
| 8001 | Merchant Portal (Frontend) | Production |
| 8002 | Notification Service / Merchant Gateway | Sandbox |
| 8003 | Telegram Mini App | Production |
| 8004 | Consumer API Gateway | Production |
| 8006 | MinIO File Storage | Production |
| 8007 | User Service | Sandbox |
| 8008 | Merchant Service | Sandbox |
| 8010 | Rider API Gateway | Sandbox |
| 8011 | Driver Service | Sandbox |
| 8012 | *(reserved — call service alt)* | — |
| 8013 | Dispatch Service / Gateway | Sandbox |
| 8015 | Super App Sync Service | Production |
| 8016 | Driver Log / Location Recording | Production |
| 8019 | WebSocket Service | Sandbox |
| 8021 | User Service (alt) | Production |
| 8022 | Dispatch Portal (Frontend) | Sandbox |
| 8024 | FeeCharge / Charge Engine | Production |
| 8025 | Express Service | Sandbox |
| 8027 | Geocode Service (HTTP) | Production |
| 8028 | AR Service | Production |
| 8029 | Pre-Order Service | Sandbox |
| 8036 | Notification Service (alt) | Sandbox |
| 8037 | Rider Gateway / Sale Portal | Sandbox |
| 8040 | Rating Service | Production |
| 8055 | Nginx / Dispatch Portal Prod | Production |
| 8082 | ORS Routing Engine | Production |
| 8501–8502 | AI Search Web UI | Production |
| 8624 | Proget Package Registry | Production |
| 9000 | Admin Laravel Web App | Production |
| 9902 | TikTok Sync API | Production |

> **CAUTION:** Before allocating a new port for a service, verify it is not already in use in this table. Port conflicts cause silent routing failures in Kubernetes.

---

## 8. Service Health Summary

> Reference this section during on-call incidents or release Go/No-Go checks.

### Age Since Last Deploy

| Age | Services |
| :--- | :--- |
| **< 24 hours** | Merchant Service, User Service, AR Service, Dispatch Service |
| **2–3 days** | Notification Service, DX Gateway (Merchant/Notification) |
| **3–6 days** | Driver Service, Express Service, Driver Log |
| **1–2 weeks** | Food Portal, Dispatch Portal, Call Service, WebSocket, Rating |
| **2–8 weeks** | Pre-Order, Merchant Portal, FeeCharge, Sale Portal |
| **1–7 months** | SMS Worker, Telegram Bot, MinIO, Nginx, Super App Sync, TikTok Sync, ORS Engine |

### Key Observations

| # | Observation | Recommended Action |
| :--- | :--- | :--- |
| 1 | **Call Service** on port 6032 is non-standard (all others use 80xx range) | Document as intentional or migrate to 8032 |
| 2 | **Driver Log** and **AR Service** are on `latest` tag — no pinned version | Pin to a specific version tag for traceability |
| 3 | **SMS / Email Worker** has no exposed port — background worker pattern | Confirm health check is via internal heartbeat or queue depth |
| 4 | Several services are still on `alpha` versions in Sandbox | Ensure Sandbox → Production promotion is tracked in the Release Register |
| 5 | **ORS Engine** and **Geocode (Nominatim)** are self-hosted | Ensure regular OSM data updates are scheduled |

---

*Document maintained by: DurianX DevOps / Engineering Team*
*For port allocation requests, contact: Engineering Manager (EM)*
*For service ownership questions, contact: Software Development Manager (SDM)*
