# Security Policy

This document describes the security protocols, encryption benchmarks, and reporting channels of the ACKO AI Native Insurance Platform.

---

## 🛡️ 1. Security Safeguards & Controls

The application implements three primary security lines:

1. **Information Encrypting Standards**:
   * All passwords are encrypted before storage using **bcrypt** with a work factor of 12. Plaintext passwords are never saved.
2. **Dynamic SQL Injection Blocking**:
   * Database updates utilize SQLAlchemy parameterized queries.
   * The **Manager AI Assistant** employs validation parser regexes and LangGraph checking nodes that block DML/DDL mutation keywords (`DELETE`, `DROP`, `UPDATE`, `ALTER`, `TRUNCATE`) from executing.
3. **Session Guards**:
   * Automatic session logouts occur after 15 minutes of idle time.
   * Account lockouts trigger for 15 minutes after 5 consecutive incorrect login attempts to protect against brute-force attacks.

---

## 📬 2. Reporting a Vulnerability

If you discover a security issue, **do not open a public GitHub issue**. Instead, report it privately to our security team:
* **Email**: `security@acko.com`
* **Response bounds**: We will acknowledge reports within 48 hours and provide a resolution timeframe within 7 days.
