# Application Tracker Schema

The tracker is a CSV file that records every job application. Keep it in `outputs/job_application_tracker.csv` (domestic) or `outputs/job_application_tracker_international.csv`.

## CSV columns

| Column | Type | Example | Notes |
|--------|------|---------|-------|
| `date` | YYYY-MM-DD | 2026-07-14 | Date of application submission |
| `company` | string | COMPANY_X | Company name |
| `role` | string | Senior Backend Engineer | Job title as posted |
| `location` | string | Remote / Beijing | Remote, hybrid, or city |
| `variant_used` | string | resume_jd_company_x_cn | Which resume variant was sent (filename without `.pdf`) |
| `jd_source` | string | https://... or "referral" | URL of the job posting or referral source |
| `status` | enum | `submitted` / `screening` / `interview` / `offer` / `rejected` / `withdrawn` | Current stage |
| `applied_via` | string | LinkedIn / Boss / referral | Channel used to apply |
| `response_date` | YYYY-MM-DD or empty | 2026-07-16 | First response from employer (empty if no response yet) |
| `notes` | string | "Recruiter: NAME" | Free-text notes (recruiter contact, interview schedule, etc.) |

## Example row

```csv
date,company,role,location,variant_used,jd_source,status,applied_via,response_date,notes
2026-07-14,COMPANY_X,Senior Backend Engineer,Remote,resume_jd_company_x_cn,https://example.com/jobs/123,submitted,LinkedIn,,Recruiter: Jane Doe
```

## Status flow

```
submitted → screening → interview → offer
                  ↘ rejected
                  ↘ withdrawn (by candidate)
```

## Privacy

The tracker CSV contains real company names, dates, and recruiter contacts. **Never commit it to a public repo.** The `.gitignore` excludes `outputs/*` except `outputs/README.md`.
