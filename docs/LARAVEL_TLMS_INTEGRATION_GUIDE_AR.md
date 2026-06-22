# دليل ربط EduSphere مع Laravel TLMS

> **التطبيق:** `omnexa_education` (EduSphere)  
> **بوابة الربط:** `/app/education-laravel-integration`  
> **الإعدادات:** Education Settings → تبويب **Laravel TLMS Integration**

---

## 1. نظرة عامة

| النظام | المسؤولية |
|--------|-----------|
| **ErpGenEx / EduSphere** | SIS، القبول، الرسوم، حسابات الطلاب، Frappe User، الحجز المالي |
| **Laravel TLMS** | الجداول، الحصص (مباشر/مسجّل)، التقييمات الإلكترونية، ملفات المعلّمين |

**ErpGenEx يتحكم في دورة حياة الحساب** — Laravel لا ينشئ طلاباً من واجهته.

حالات الحساب (`Education Student.account_access_status`):

`Not Provisioned` → `Provisioning` → `Active` ↔ `Financial Hold` / `Suspended` → `Withdrawn`

---

## 2. إعداد ErpGenEx (خطوة بخطوة)

### 2.1 تفعيل الربط

1. افتح **Education Settings**
2. فعّل **Enable Laravel TLMS**
3. أدخل:
   - **Laravel Base URL** — مثال: `https://tlms.school.edu`
   - **Laravel API Key** — مفتاح يتحقق منه Laravel عند استقبال طلبات ErpGenEx
   - **Laravel Webhook Secret** — سر مشترك لتوقيع Webhooks القادمة من Laravel
   - **Laravel JWT Secret** (اختياري) — لتسجيل الدخول الموحّد SSO
4. اضغط **Test Laravel Connection** — يجب أن يرد Laravel على `GET /api/v1/health`

### 2.2 نسخ رابط Webhook إلى Laravel

من بوابة **Laravel TLMS Integration** (`/app/education-laravel-integration`) انسخ:

```
https://{your-site}/api/method/omnexa_education.api.laravel_webhooks.receive
```

ضعه في `.env` لـ Laravel:

```env
ERPGENEX_BASE_URL=https://erp.school.edu
ERPGENEX_WEBHOOK_URL=${ERPGENEX_BASE_URL}/api/method/omnexa_education.api.laravel_webhooks.receive
ERPGENEX_WEBHOOK_SECRET=نفس_قيمة_Education_Settings
ERPGENEX_API_KEY=نفس_مفتاح_Laravel_API_Key
JWT_SECRET=نفس_laravel_jwt_secret
```

### 2.3 ربط المقررات

1. أنشئ سجلات **Education Lms Course Link**
2. اختر Provider: **Laravel TLMS**
3. املأ **External Course ID** ليطابق معرّف المقرر في Laravel

### 2.4 الحجز المالي التلقائي (اختياري)

في Education Settings:

- **Auto Suspend on Overdue** — إيقاف الوصول عند تأخر الفواتير
- **Grace Days** — أيام السماح قبل الإيقاف

عند التأخر: `financial_hold` + تعطيل User + إرسال `suspend` إلى Laravel  
عند السداد (Payment Entry): رفع الحجز + `resume` في Laravel

---

## 3. واجهات ErpGenEx API

| الوظيفة | Method (Frappe) |
|---------|-----------------|
| اختبار الاتصال | `omnexa_education.api.laravel_client.ping` |
| تفعيل حساب طالب | `omnexa_education.api.student_account_lifecycle.provision_student` |
| إيقاف | `omnexa_education.api.student_account_lifecycle.suspend_student` |
| استئناف | `omnexa_education.api.student_account_lifecycle.resume_student` |
| إيقاف المتأخرين دفعة | `omnexa_education.api.student_account_lifecycle.bulk_suspend_overdue` |
| مزامنة تسجيل LMS | `omnexa_education.api.education_lms.sync_lms_enrollment` |
| معالجة طابور المزامنة | `omnexa_education.api.laravel_client.process_sync_queue` |

**Webhook وارد (Laravel → ErpGenEx):**

```
POST /api/method/omnexa_education.api.laravel_webhooks.receive
Header: X-ErpGenEx-Signature: sha256=<HMAC-SHA256(raw_body, webhook_secret)>
```

**أحداث Webhook المدعومة:**

| الحدث | النتيجة في ErpGenEx |
|-------|---------------------|
| `grade.posted` | سجل في Education Assessment Result |
| `timetable.approved` | صفوف في Education Timetable Entry |
| `attendance.recorded` | تسجيل في السجل |
| `lesson.completed` | تسجيل في السجل |

---

## 4. ما يجب أن يوفّره Laravel

**Base URL:** `{laravel_base_url}/api/v1`

### Endpoints مطلوبة (ErpGenEx → Laravel)

| Method | Path | الغرض |
|--------|------|-------|
| GET | `/health` | اختبار الاتصال |
| POST | `/users/provision` | إنشاء/تحديث مستخدم |
| POST | `/users/{id}/suspend` | إيقاف الوصول |
| POST | `/users/{id}/resume` | استئناف الوصول |
| POST | `/classes/sync` | مزامنة الفصول |
| POST | `/enrollments/sync` | مزامنة تسجيل الطلاب |

**Headers على كل طلب:**

```
Authorization: Bearer {laravel_api_key}
X-ErpGenEx-School: {Education Institution name}
Content-Type: application/json
```

### مثال Provision (ErpGenEx يرسل)

```json
{
  "external_id": "MH-STU00001",
  "student_code": "STU00001",
  "email": "stu001@school.local",
  "first_name": "Ahmed",
  "last_name": "Hassan",
  "role": "student",
  "institution_id": "Al-Noor International",
  "grade_level": "Grade 11",
  "section": "11-A",
  "account_status": "active",
  "enrollments": [
    {"course_external_id": "MATH-G11", "section_external_id": "11-A", "role": "student"}
  ]
}
```

**الرد المطلوب:**

```json
{
  "id": "uuid-or-int",
  "laravel_user_id": "uuid-or-int",
  "external_id": "MH-STU00001",
  "account_status": "active"
}
```

### مثال Webhook grade.posted (Laravel يرسل)

```json
{
  "event": "grade.posted",
  "timestamp": "2026-06-06T12:00:00Z",
  "school_id": "Al-Noor International",
  "data": {
    "student_external_id": "MH-STU00001",
    "course_external_id": "MATH-G11",
    "assessment_external_id": "EXAM-MID-2026",
    "score": 87,
    "max_score": 100,
    "term": "2025-2026-T2"
  }
}
```

---

## 5. أوامر Bench للاختبار

```bash
# اختبار Ping
bench --site {site} execute omnexa_education.api.laravel_client.ping

# معالجة طابور المزامنة يدوياً
bench --site {site} execute omnexa_education.api.laravel_client.process_sync_queue

# إيقاف المتأخرين
bench --site {site} execute omnexa_education.api.student_account_lifecycle.bulk_suspend_overdue
```

---

## 6. DocTypes ذات الصلة

| DocType | الغرض |
|---------|-------|
| Education Settings | إعدادات الربط |
| Education Student | الطالب + `laravel_user_id` + حالة الحساب |
| Education Lms Course Link | ربط مقرر ErpGenEx ↔ Laravel |
| Education Laravel Sync Queue | طابور إعادة المحاولة (Scheduler كل ساعة) |
| Education Account Access Log | سجل تدقيق (provision / suspend / resume) |

---

## 7. سيناريوهات قبول

| # | السيناريو | معيار النجاح |
|---|-----------|--------------|
| 1 | تفعيل طالب من ErpGenEx | User في Frappe + مستخدم في Laravel خلال 30 ث |
| 2 | فاتورة متأخرة | financial_hold + User معطّل + Laravel suspend |
| 3 | Payment Entry | رفع الحجز + User مفعّل + Laravel resume |
| 4 | Webhook grade.posted | صف في Education Assessment Result |
| 5 | Webhook timetable.approved | صفوف في Education Timetable Entry |
| 6 | توقيع Webhook خاطئ | رفض 401/403 |
| 7 | بوابة الطالب | رسالة منع عند financial hold |

---

## 8. مراجع إضافية

- [LARAVEL_TLMS_INTEGRATION_PROMPT.md](LARAVEL_TLMS_INTEGRATION_PROMPT.md) — مواصفات كاملة لمطوّر Laravel / AI Agent (إنجليزي)
- [ISMS_MASTER_PLAN_AR.md](ISMS_MASTER_PLAN_AR.md) — خطة ISMS بالعربية

---

*ErpGenEx EduSphere · دليل ربط Laravel TLMS · v1.0*
