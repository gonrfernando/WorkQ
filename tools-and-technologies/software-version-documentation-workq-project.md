---
icon: file-lines
---

# Software Version Documentation - WorkQ Project

**Last updated:** 2025-06-17\
**Documented by:** Axel Orquiz

***

### ⚙️ Base Language and Environment

* **Python:** 3.12.4
* **WSGI Server:** waitress 3.0.2
* **Operating System:** Windows

***

### 📦 Main Project Dependencies

| Library          | Version    | Purpose                 |
| ---------------- | ---------- | ----------------------- |
| pyramid          | 2.0.2      | Main web framework      |
| pyramid\_jinja2  | 2.10.1     | Template engine support |
| SQLAlchemy       | 1.4.54     | ORM for database access |
| psycopg2         | 2.9.10     | PostgreSQL connector    |
| alembic          | 1.16.1     | Database migrations     |
| boto3            | 1.38.36    | AWS S3 integration      |
| bcrypt           | 4.3.0      | Password hashing        |
| werkzeug         | 3.1.3      | Security and utilities  |
| jinja2           | 3.1.5      | HTML templates          |
| smtplib          | built-in   | Email sending           |
| waitress         | 3.0.2      | WSGI server             |
| WebTest          | 3.0.4      | Functional testing      |
| pytest           | 8.3.5      | Testing framework       |
| webtest-sessions | (editable) | Session testing         |

***

### 🧰 External Tools Used

| Tool       | Version          | Purpose                        |
| ---------- | ---------------- | ------------------------------ |
| Git        | 2.49.0.windows.1 | Version control                |
| PostgreSQL | 13.18            | Relational database management |

***

### 🔎 Notes

* Some libraries such as Flask, zope.\*, or BeautifulSoup are present in the environment but **are not used directly** in this project.
