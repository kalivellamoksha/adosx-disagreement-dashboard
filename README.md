# ADOSX Disagreement Dashboard

## 1. Project Overview

The ADOSX Disagreement Dashboard is a full-stack application that compares event records from two different systems and identifies disagreements between them.

The application imports CSV files into a database, compares corresponding records, and displays disagreements in a React dashboard.

The main goal is to identify data inconsistencies while keeping organization data separated.

## 2. Technologies Used

**Backend:** Python, Django, Django REST Framework

**Frontend:** React.js, Vite, JavaScript, CSS

**Database:** SQLite

**Testing:** Django TestCase

**Version Control:** Git and GitHub

## 3. Features Implemented

- Import records from three CSV files into SQLite.
- Preserve original CSV values, including invalid or blank amounts.
- Normalize inconsistent record references.
- Detect records missing from System B.
- Detect System B entries referencing nonexistent records.
- Detect duplicate System B entries.
- Detect different values between corresponding records.
- Identify invalid numeric values.
- Detect location disagreements.
- Display disagreements in a React dashboard.
- Filter disagreements by reason.
- Sort disagreements by numeric value.
- Restrict API results to the server-configured organization.
- Test comparison logic and tenant isolation.

## 4. Project Structure

```text
adosx-disagreement-dashboard/
├── backend/
│   ├── config/
│   ├── reconciliation/
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── import_csv.py
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   └── package.json
├── data/
│   ├── locations.csv
│   ├── system_a.csv
│   └── system_b.csv
├── README.md
├── DECISIONS.md
└── .gitignore
```

## 5. How to Run the Project

### Prerequisites

Install Python, Node.js, and npm.

### Backend Setup

Open a terminal in the project root.

Create a Python virtual environment:

```powershell
py -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Navigate to the backend:

```powershell
cd backend
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Apply database migrations:

```powershell
python manage.py migrate
```

Import the CSV files:

```powershell
python manage.py import_csv
```

Start Django:

```powershell
python manage.py runserver 8001
```

Backend API:

`http://127.0.0.1:8001/api/disagreements/`

### Frontend Setup

Open another terminal from the project root.

```powershell
cd frontend
```

Install frontend dependencies:

```powershell
npm install
```

Start React:

```powershell
npm run dev
```

Open:

`http://localhost:5173/`

## 6. Dataset

The supplied dataset contains:

| File | Records |
|---|---:|
| system_a.csv | 120 |
| system_b.csv | 121 |
| locations.csv | 5 |

All records are imported into SQLite.

Original values are preserved in the database so that malformed numeric values can be investigated instead of silently discarded.

## 7. Comparison Logic

The application compares System A records with System B entries using normalized record references.

The comparison identifies the following disagreement categories:

**MISSING_IN_B:** A record exists in System A but has no corresponding entry in System B.

**ORPHAN_IN_B:** A System B entry references a record that does not exist in System A.

**DUPLICATE_IN_B:** Multiple System B entries reference the same System A record.

**VALUE_MISMATCH:** Corresponding records contain different numeric values.

**INVALID_VALUE:** A value cannot be interpreted as a valid number.

**LOCATION_MISMATCH:** Corresponding records are associated with different locations.

Numeric comparisons use Python's Decimal type to avoid floating-point precision issues.

Differences in number formatting are normalized before comparison.

Date differences alone are not treated as amount disagreements.

## 8. Tenant Isolation

Locations are mapped to organizations through `locations.csv`.

For the take-home demonstration, Django uses a server-configured organization:

`ADOSX_TENANT_ID`

By default, it is set to `ORG-A`.

The API rejects requests that attempt to access a different organization.

The comparison function also restricts returned disagreement information to the relevant organization.

This demonstrates server-side tenant restriction without implementing authentication.

**Limitation:** The deployment serves one configured organization at a time. A production system would require authenticated tenant identity, authorization checks, and stronger database-level tenant boundaries.

## 9. API Endpoint

### Get Disagreements

**GET** `/api/disagreements/`

Optional parameters:

| Parameter | Description |
|---|---|
| org_id | Must match the server-configured organization |
| reason | Filter by disagreement reason |
| sort | `asc` or `desc` |

Example:

`/api/disagreements/?reason=VALUE_MISMATCH&sort=desc`

The response contains the organization ID, number of disagreements, and disagreement records.

## 10. Testing

Run:

```powershell
cd backend
python manage.py test reconciliation -v 2
```

The test suite covers missing records, orphan references, duplicates, value mismatches, matching values, tenant isolation, and API access restrictions.

Additional tests cover invalid amounts, numeric formatting, and date differences if included in the final version.

## 11. What I Deliberately Did Not Build

To stay within the assignment's one-day time box, I deliberately excluded:

- User authentication and login.
- Advanced visual design.
- CSV uploads through the frontend.
- Background processing.
- Deployment infrastructure.
- Advanced performance optimization.
- Multi-user tenant administration.

I prioritized correct data import, disagreement detection, tenant restriction, and automated tests.

## 12. How I Worked With the AI Agent

I used ChatGPT as a development assistant during the assignment.

The agent helped with project structure, Django models, CSV parsing, comparison logic, React integration, testing, and documentation.

I ran the generated commands and code locally, reviewed terminal errors, checked API responses, and made corrections during implementation.

I also verified that the imported record counts matched the supplied CSV files.

The agent supported development, but I remained responsible for checking the implementation and understanding its behavior.

## 13. Required Questions

### a. Name one thing the AI agent got wrong. How did you notice?

The AI agent initially assumed that the backend and frontend were communicating through port 8000.

However, Django was running on port 8001, and the React dashboard displayed a "Failed to fetch" error.

I inspected the browser developer console and found requests being sent to the wrong port.

I corrected the API URL in the React application and verified that the dashboard displayed the disagreement records.

### b. Which part of your submission are you least confident about, and why?

I am least confident about handling unusual reconciliation edge cases in much larger datasets.

The supplied dataset is relatively small, and the implementation focuses on the required disagreement categories.

In a production system, additional cases such as ambiguous references, malformed locations, and complicated duplicate relationships would require more extensive validation.

### c. If you had a second day, what would you fix first?

I would first improve tenant isolation and expand the reconciliation tests.

I would introduce authenticated organization context and ensure that access restrictions are consistently enforced at the API and data-access layers.

I would also add more tests for malformed records, cross-tenant references, and uncommon duplicate scenarios.

## 14. Summary

The project demonstrates an end-to-end data reconciliation workflow using Django, SQLite, and React.

It prioritizes accurate disagreement detection, preservation of dirty data, tenant separation, and clear implementation choices over unnecessary features.