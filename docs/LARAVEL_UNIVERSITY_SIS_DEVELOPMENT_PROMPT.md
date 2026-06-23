# Laravel University SIS — Development Prompt (ErpGenEx ↔ Laravel TLMS)

> **Status:** ErpGenEx side **ready** · Laravel **to build** using this prompt  
> **Arabic guide:** [LARAVEL_TLMS_INTEGRATION_GUIDE_AR.md](LARAVEL_TLMS_INTEGRATION_GUIDE_AR.md)  
> **Base integration:** [LARAVEL_TLMS_INTEGRATION_PROMPT.md](LARAVEL_TLMS_INTEGRATION_PROMPT.md)  
> **Desk:** `/app/education-laravel-integration`

---

## OBJECTIVE

Build **Laravel 11+ University SIS / TLMS** integrated with **ErpGenEx EduSphere** for:

- **Student registration** (Banner / Workday Student parity)
- **Program & course catalog** (credit hours, degree levels)
- **Course registration & enrollment**
- **Teaching & learning** (LMS: live/recorded, assessments)
- **Grades & attendance** webhook back to ErpGenEx
- **Financial hold** suspend/resume (ErpGenEx is source of truth)
- **International standards:** OBE-ready, NCAAA/ABET-friendly structure

**Rule:** ErpGenEx controls account lifecycle. Laravel **never** creates students independently.

---

## ERPGENEX ENDPOINTS (ALREADY IMPLEMENTED)

| Action | Method |
|--------|--------|
| Test connection | `omnexa_education.api.laravel_client.ping` |
| Sync programs (HE) | `omnexa_education.api.laravel_client.sync_institution_programs_to_laravel` |
| Process sync queue | `omnexa_education.api.laravel_client.process_sync_queue` |
| Provision student | `omnexa_education.api.student_account_lifecycle.provision_student` |
| Webhook IN | `POST /api/method/omnexa_education.api.laravel_webhooks.receive` |

**Branch demo:** Branch → Demo data → Education → select **University** / **International School** → **Activate EduSphere Demo**

---

## LARAVEL MUST IMPLEMENT — UNIVERSITY MODEL

### Academic Structure

```
University
  └── College (Faculty)
        └── Department
              └── Program (BSc, MSc, Diploma)
                    └── Course (credit_hours)
                          └── Section (term offering)
                                └── Enrollment (student)
```

### Database Tables (minimum)

- `institutions`, `colleges`, `departments`
- `programs` (degree_level, total_credits, accreditation_code)
- `courses`, `course_program` (many-to-many)
- `academic_terms`, `sections`
- `users` (laravel_user_id, external_id, account_status)
- `enrollments`, `course_enrollments`
- `assessments`, `grades`, `attendance_sessions`
- `sync_logs`, `webhook_outbox`

---

## INBOUND API (ErpGenEx → Laravel)

**Base:** `{laravel_base_url}/api/v1`  
**Auth:** `Authorization: Bearer {laravel_api_key}`  
**Header:** `X-ErpGenEx-School: {institution_id}`

### Health

```
GET /health
→ { "status": "ok", "message": "pong", "version": "1.0" }
```

### Users (lifecycle controlled by ErpGenEx)

```
POST /users/provision
POST /users/{laravel_user_id}/suspend
POST /users/{laravel_user_id}/resume
```

**Provision payload (university):**

```json
{
  "external_id": "EDU-STU-0001",
  "student_code": "2026-001",
  "email": "student@demo.education",
  "role": "student",
  "institution_id": "MH-UNIV",
  "institution_type": "University",
  "program_id": "MH-PROG-CS-BSC",
  "academic_model": "university",
  "account_status": "active",
  "enrollments": [
    {
      "course_external_id": "CS101",
      "section_external_id": "CS101-A-FALL2026",
      "role": "student"
    }
  ]
}
```

### Programs & Courses (NEW — university sync)

```
POST /programs/sync
```

**Payload:**

```json
{
  "institution_id": "MH-UNIV",
  "institution_type": "University",
  "programs": [
    {
      "name": "MH-PROG-CS-BSC",
      "program_code": "CS-BSC",
      "program_name": "Computer Science BSc",
      "degree_level": "Bachelor"
    }
  ],
  "courses": [
    {
      "name": "MH-CRS-CS101",
      "course_code": "CS101",
      "course_name": "Introduction to Programming",
      "credit_hours": 3,
      "program": "MH-PROG-CS-BSC"
    }
  ],
  "standards": { "obe": true, "credit_hours": true, "sis": "erpgenex-education-v1" }
}
```

### Enrollments

```
POST /enrollments/sync
POST /classes/sync
POST /academic-calendar/sync
```

---

## OUTBOUND WEBHOOKS (Laravel → ErpGenEx)

**URL:** `{ERPGENEX_BASE_URL}/api/method/omnexa_education.api.laravel_webhooks.receive`  
**Signature:** `X-ErpGenEx-Signature` = HMAC-SHA256(body, shared webhook secret)

| Event | Purpose |
|-------|---------|
| `grade.posted` | Final grade → ErpGenEx Assessment Result |
| `attendance.session_closed` | Attendance → ErpGenEx Attendance Session |
| `assessment.submitted` | Mid-term scores |
| `course.progress` | Completion % for analytics |

---

## K12 / INTERNATIONAL SCHOOL VARIANT

When `institution_type` = `International School`:

- Use `grade_level` + `section` instead of `program_id`
- `academic_model`: `"k12"`
- Sections map to homeroom classes; parents linked via `guardian_email`

---

## GLOBAL BENCHMARK ALIGNMENT

| Standard | Laravel Module |
|----------|----------------|
| Banner Student | Program registration, degree audit hooks |
| Workday Student | Academic periods, enrollment status |
| PowerSchool | K12 grade/section model |
| OBE / CLO-PLO | Learning outcome tags on courses |
| QA / Accreditation | Evidence export API |

**Target SIS score:** 4.85 (ErpGenEx static matrix + live portal readiness)

---

## ACCEPTANCE TESTS

1. Branch demo → University → 8 role users login to correct home routes  
2. Provision student → Laravel user within 30s  
3. `sync_institution_programs_to_laravel` → programs visible in Laravel admin  
4. Overdue invoice → suspend in both systems  
5. Payment Entry → resume in both systems  
6. Grade webhook → Assessment Result in ErpGenEx  
7. Public apply `/education/apply` → Online Application → Promote → Admission  

---

## LARAVEL `.env`

```env
ERPGENEX_BASE_URL=https://your-site
ERPGENEX_WEBHOOK_URL=${ERPGENEX_BASE_URL}/api/method/omnexa_education.api.laravel_webhooks.receive
ERPGENEX_API_KEY=sk_live_...
ERPGENEX_WEBHOOK_SECRET=whsec_...
JWT_SECRET=shared-with-erpgenex-sso
```

---

## AI AGENT INSTRUCTION

Copy this entire file + `LARAVEL_TLMS_INTEGRATION_PROMPT.md` into your Laravel repo and implement:

1. Migrations for university structure  
2. `/api/v1` controllers with Bearer auth  
3. Webhook outbox with retry  
4. Admin UI for programs/courses/sections  
5. Student portal (read-only if financial hold)  
6. PHPUnit + Pest tests for all acceptance criteria  

*ErpGenEx EduSphere · Laravel University SIS Development Prompt · v1.0*
