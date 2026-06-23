### Omnexa Education

Education vertical — ISMS (Integrated School Management System) on ErpGenEx, with **Laravel TLMS** for Teaching & Learning (§5).

**Planning docs (ISMS Specification AR):**

| Document | Purpose |
|----------|---------|
| [docs/ISMS_MASTER_PLAN_AR.md](docs/ISMS_MASTER_PLAN_AR.md) | Architecture, finance-controlled account lifecycle, roadmap |
| [docs/LARAVEL_TLMS_INTEGRATION_GUIDE_AR.md](docs/LARAVEL_TLMS_INTEGRATION_GUIDE_AR.md) | **دليل ربط Laravel TLMS (عربي)** — إعداد ErpGenEx + Webhooks + API |
| [docs/ERPGENEX_education_demo.md](docs/ERPGENEX_education_demo.md) | **ديمو متعدد المؤسسات** — 5 أنواع + أكاديمية + KPIs |
| [docs/LARAVEL_TLMS_INTEGRATION_PROMPT.md](docs/LARAVEL_TLMS_INTEGRATION_PROMPT.md) | Copy-paste prompt for Laravel team / AI agent |
| [docs/LARAVEL_UNIVERSITY_SIS_DEVELOPMENT_PROMPT.md](docs/LARAVEL_UNIVERSITY_SIS_DEVELOPMENT_PROMPT.md) | **University SIS + program sync prompt** (Banner/Workday parity) |
| [docs/EDUCATION_PORTALS_CATALOG_AR.md](docs/EDUCATION_PORTALS_CATALOG_AR.md) | **دليل البوابات والمسارات والأدوار** (→ `Docs/NewEducationIN/`) |
| [docs/ISMS_GLOBAL_DEVELOPMENT_CHECKLIST.md](docs/ISMS_GLOBAL_DEVELOPMENT_CHECKLIST.md) | 80-item checklist vs global standards (PowerSchool, Banner, Workday) |

License model: Paid app. Access is gated through `license_gate.before_request` when `omnexa_license_enforce` is enabled.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app omnexa_education
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/omnexa_education
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
