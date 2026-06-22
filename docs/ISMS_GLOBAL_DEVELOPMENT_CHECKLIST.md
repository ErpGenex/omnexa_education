# ISMS Global Development Checklist

**App:** `omnexa_education` · **Target:** Global #1 (score ≥ 4.90/5.00)  
**References:** ISMS Spec AR · IMS Global · FERPA · GDPR · WCAG 2.2  
**Legend:** ✅ Done · 🟡 Partial · ⬜ Not started · 🔗 Laravel · 💰 Finance-critical

---

## A. Integration & Account Lifecycle (P0)

| # | Task | Owner | Status | Evidence / Path |
|---|------|-------|--------|-----------------|
| A1 | Laravel settings in `Education Settings` | ErpGenEx | ⬜ | `doctype/education_settings/` |
| A2 | `Education Student.user` + `laravel_user_id` | ErpGenEx | ⬜ | `doctype/education_student/` |
| A3 | `account_access_status` + `financial_hold` fields | ErpGenEx | ⬜ | student doctype |
| A4 | `laravel_client.py` — HTTP client + retry | ErpGenEx | ⬜ | `api/laravel_client.py` |
| A5 | `student_account_lifecycle.py` — provision/suspend/resume | ErpGenEx | ⬜ | `api/` |
| A6 | Webhook receiver `laravel_webhooks.py` | ErpGenEx | ⬜ | `api/laravel_webhooks.py` |
| A7 | `Education Account Access Log` DocType | ErpGenEx | ⬜ | new doctype |
| A8 | `Education Laravel Sync Queue` + scheduler | ErpGenEx | ⬜ | `hooks.py` |
| A9 | 💰 Auto suspend on overdue invoice | ErpGenEx | ⬜ | `billing.py` + hook on SI |
| A10 | 💰 Manual suspend/resume from Finance desk | ErpGenEx | ⬜ | Student form buttons |
| A11 | Roles: Student · Parent · Teacher portal | ErpGenEx | ⬜ | `install.py` |
| A12 | Add `Laravel TLMS` to LMS provider select | ErpGenEx | ⬜ | `education_lms_course_link.json` |
| A13 | Replace `sync_lms_enrollment` stub | ErpGenEx | 🟡 | `api/education_lms.py` |
| A14 | 🔗 Laravel provision API | Laravel | ⬜ | `POST /users/provision` |
| A15 | 🔗 Laravel suspend/resume API | Laravel | ⬜ | `/users/{id}/suspend` |
| A16 | 🔗 OAuth2/OIDC SSO | Both | ⬜ | shared JWT |
| A17 | Integration tests (mock Laravel) | ErpGenEx | ⬜ | `tests/test_laravel_integration.py` |
| A18 | Report: Student Account Access Status | ErpGenEx | ⬜ | new report |

---

## B. ISMS Module 1 — Admissions & Enrollment (§2)

| # | Task | Status | Notes |
|---|------|--------|-------|
| B1 | Public admission announcement (website) | ⬜ | Web Form + portal |
| B2 | Stage-based admission fees | 🟡 | `Education Fee Item` |
| B3 | Payment methods (cash, card, bank, COD) | 🟡 | ERP Payment Entry |
| B4 | Entrance exam + pass/fail workflow | 🟡 | DocType exists |
| B5 | Waitlist by capacity / class density | 🟡 | `Education Waitlist` |
| B6 | Parent interview step | ⬜ | workflow state |
| B7 | Auto-enroll only after exam + interview pass | ⬜ | server script |
| B8 | Admission → Student record promotion | 🟡 | `education_admissions.py` |
| B9 | OneRoster org/user export on enroll | ⬜ | Phase 1 |

---

## C. ISMS Module 2 — Academics & Curriculum (§3)

| # | Task | Status | Notes |
|---|------|--------|-------|
| C1 | Curriculum per grade | ✅ | `Education Curriculum` |
| C2 | Fee structure per grade | ✅ | `Education Fee Plan` |
| C3 | Secondary subject selection (G10–12) | ⬜ | new wizard |
| C4 | Core vs elective rules + prerequisites | ⬜ | validation engine |
| C5 | Auto fee = tuition + exam + base fees | 🟡 | extend `billing.py` |
| C6 | Parent approval before payment lock | ⬜ | portal workflow |
| C7 | Approved selection → billing + Laravel enroll | ⬜ | depends A* |

---

## D. ISMS Module 3 — Activities & Events (§4)

| # | Task | Status | Notes |
|---|------|--------|-------|
| D1 | Annual activities calendar | ⬜ | `Education Event` |
| D2 | Free vs paid activities | ⬜ | fee link |
| D3 | Subscription + renewal | ⬜ | |
| D4 | Portal enrollment + ERP payment | ⬜ | |

---

## E. ISMS Module 4 — Teaching & Learning (§5) 🔗 Laravel

| # | Task | Status | Notes |
|---|------|--------|-------|
| E1 | Teacher dossier (courses, curricula) | ⬜ | Laravel |
| E2 | Course/subject assignment to teachers | 🟡 | ErpGenEx master |
| E3 | Timetable draft by scheduler | 🟡 | `Education Timetable` |
| E4 | Admin review + approve/reject workflow | ⬜ | Laravel + webhook |
| E5 | Live lessons | ⬜ | Laravel |
| E6 | Recorded lessons | ⬜ | Laravel |
| E7 | E-assessments | ⬜ | Laravel |
| E8 | Grade sync → ErpGenEx | ⬜ | webhook |
| E9 | Publish requires approval (settings flag) | 🟡 | `grade_publish_requires_approval` |

---

## F. ISMS Module 5 — Parent Portal (§6)

| # | Task | Status | Notes |
|---|------|--------|-------|
| F1 | Academic performance view | 🟡 | stub page |
| F2 | Attendance in/out monitoring | 🟡 | `Education Attendance` |
| F3 | Grades & report cards | 🟡 | reports exist |
| F4 | Exam schedule | ⬜ | |
| F5 | Student engagement metrics | ⬜ | xAPI from Laravel |
| F6 | Complaints / feedback | ⬜ | |
| F7 | Fee approval (links C6) | ⬜ | |
| F8 | PWA mobile (`public/pwa/`) | 🟡 | manifest exists |
| F9 | Arabic RTL UI | 🟡 | `education-rtl.css` |

---

## G. ISMS Modules 6–11 — Operations

| Module | Key deliverables | Status |
|--------|------------------|--------|
| §7 HR | Attendance, payroll, HR cycle | 🟡 via ERPNext HR |
| §8 Warehouse | Stock in/out, consumption | 🟡 via inventory app |
| §9 Transport | Bus subscription, GPS, cameras | ⬜ |
| §10 Security | Gate logs, visitor appointments | ⬜ |
| §11 Assets | Asset register + lifecycle | 🟡 via assets module |
| §12 Maintenance | Cleaning + IT/fleet maintenance | 🟡 partial |

---

## H. Finance & ERP (Cross-cutting) 💰

| # | Task | Status | Path |
|---|------|--------|------|
| H1 | Student → Customer auto-create | ✅ | `auto_create_customer` |
| H2 | Fee Plan → Billing Cycle → Sales Invoice | ✅ | tests pass |
| H3 | Discount rules | ✅ | `billing.py` |
| H4 | Late fee rules | ✅ | `billing.py` |
| H5 | **Financial hold → account suspend** | ⬜ | **P0** |
| H6 | Aging report for student fees | 🟡 | ERP reports |
| H7 | Finance desk: bulk suspend overdue | ⬜ | workcenter page |
| H8 | Payment gateway (card) for portal | ⬜ | Payment Request |

---

## I. Global Standards & Compliance

| # | Standard | Requirement | Status |
|---|----------|-------------|--------|
| I1 | **OneRoster 1.2** | Users, classes, enrollments sync | ⬜ |
| I2 | **LTI 1.3** | Launch lessons from portal | ⬜ |
| I3 | **CASE / CASE Network** | Curriculum standards mapping | ⬜ |
| I4 | **xAPI / Caliper** | Learning analytics | ⬜ |
| I5 | **FERPA** | Access audit + consent | 🟡 | `education_compliance.py` |
| I6 | **GDPR** | Data export, erasure, consent | 🟡 |
| I7 | **ISO 27001** | Security controls documentation | ⬜ |
| I8 | **WCAG 2.2 AA** | Portal accessibility | ⬜ |
| I9 | **OpenAPI 3.1** | Public API documentation | ⬜ |
| I10 | **Ed-Fi** (optional US) | Data standard adapter | ⬜ |

---

## J. Benchmark vs Global Leaders

| Dimension | PowerSchool | Banner | Workday | omnexa target | Current |
|-----------|-------------|--------|---------|---------------|---------|
| Admissions | 4.7 | 4.6 | 4.8 | **4.90** | 🟡 4.90* |
| SIS Core | 4.7 | 4.7 | 4.7 | **4.90** | 🟡 scaffold |
| Scheduling | 4.7 | 4.6 | 4.8 | **4.88** | 🟡 partial |
| Assessment | 4.8 | 4.6 | 4.8 | **4.92** | ⬜ Laravel |
| Fees/Finance | 4.7 | 4.7 | 4.8 | **4.88** | ✅ strong |
| Portals | 4.8 | 4.5 | 4.8 | **4.90** | 🟡 stubs |
| Compliance | 4.7 | 4.7 | 4.8 | **4.92** | 🟡 partial |
| **Weighted** | 4.70 | 4.65 | 4.75 | **≥ 4.90** | 🟡 4.89 placeholder |

\*Scores in `education_global_benchmark.py` are targets, not verified implementation scores.

**Gate to claim #1:** All P0 items in sections A, B8, C7, E8, H5, I1, I5 + load test pass.

---

## K. Sprint Plan (Recommended)

### Sprint 1 (P0 — Account Control)
- A1–A13, A17, A18, H5, H7

### Sprint 2 (P0 — Laravel MVP)
- A14–A16, E1–E4, E8 (Laravel team parallel)

### Sprint 3 (P0 — Admissions + Academics)
- B7–B9, C3–C7

### Sprint 4 (P1 — Parent Portal)
- F1–F9

### Sprint 5 (Global Gate)
- I1–I9, benchmark audit, penetration test

---

## L. Definition of Done (each checklist item)

- [ ] Code merged + `bench migrate` clean
- [ ] Unit/integration test ≥ 1 case
- [ ] Arabic + English label in DocType
- [ ] Permission matrix updated
- [ ] Entry in workspace (`education_workspace.py`) if user-facing
- [ ] Audit log for PII/financial actions

---

## M. Quick verification commands

```bash
# Migrate
bench --site erpgenex.local.site migrate

# Run education tests
bench --site erpgenex.local.site run-tests --app omnexa_education

# Global score API
bench --site erpgenex.local.site execute omnexa_education.education_global_benchmark.get_global_sis_score

# Laravel ping (after implementation)
bench --site erpgenex.local.site execute omnexa_education.api.laravel_client.ping
```

---

**Progress tracker**

| Section | Total | ✅ | 🟡 | ⬜ |
|---------|-------|----|----|-----|
| A Integration | 18 | 0 | 1 | 17 |
| B Admissions | 9 | 0 | 5 | 4 |
| C Academics | 7 | 2 | 2 | 3 |
| D Activities | 4 | 0 | 0 | 4 |
| E TLMS | 9 | 0 | 2 | 7 |
| F Parent Portal | 9 | 0 | 5 | 4 |
| G Operations | 6 | 0 | 4 | 2 |
| H Finance | 8 | 4 | 1 | 3 |
| I Standards | 10 | 0 | 2 | 8 |
| **Total** | **80** | **6** | **22** | **52** |

*Last updated: 2026-06-06 · omnexa_education ISMS checklist v1.0*
