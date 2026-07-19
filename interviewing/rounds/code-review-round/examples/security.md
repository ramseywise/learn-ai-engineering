# Security & Trust Boundaries

## Example 1: Over-permissioned MCP tool config

**The diff**
```python
# mcp_servers/data_agent.py
+ tools = [
+     {
+         "name": "query_database",
+         "description": "Run queries against the analytics database",
+         "allowed_operations": ["read", "write"],
+         "connection": os.environ["DATABASE_URL"],
+     },
+     {
+         "name": "execute_shell",
+         "description": "Execute shell commands for data processing",
+         "allowed_commands": "*",
+     },
+ ]
```

**Surface read**: New MCP server config. Two tools for a data agent. Looks standard.

**Model review**

> **[Blocker]** `data_agent.py:5` — An analytics agent has `write` access to the database. Analytics queries should be read-only. Write access means a prompt injection in retrieved data could trigger `DROP TABLE` or data exfiltration via `INSERT INTO external_table SELECT * FROM users`.
>
> **[Blocker]** `data_agent.py:10` — `allowed_commands: "*"` gives unrestricted shell access. This is the canonical over-permissioning anti-pattern from the OWASP Agent Security cheat sheet. An agent that can run arbitrary shell commands can exfiltrate data, install packages, or modify the host. Allowlist specific commands: `["python", "head", "wc", "csvtool"]`.
>
> **[Warning]** `data_agent.py:6` — `DATABASE_URL` is passed directly into tool config. If this includes credentials (postgres://user:pass@host), they'll be visible in tool metadata and potentially in logs/traces. Use a connection alias or secrets reference.

**What this teaches**: Agent tool permissions are the #1 security review target for AI engineering. Least privilege means read-only when reads suffice, specific command allowlists instead of wildcards, and credentials never in tool metadata. See [OWASP Agent Security](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html) §1; [security guide §3](../../../guides/7-security-safety/interview-guide.md) on least privilege.

---

## Example 2: Trust boundary violation — untrusted content in system message

**The diff**
```python
# agents/support_agent.py
  async def handle_ticket(ticket: SupportTicket):
      # Retrieve relevant docs for context
      docs = await retriever.search(ticket.customer_message)

-     response = await llm.generate(
-         system="You are a helpful support agent. Answer based on the docs provided.",
-         messages=[
-             {"role": "user", "content": f"Customer says: {ticket.customer_message}\n\nDocs:\n{docs}"}
-         ],
-     )
+     response = await llm.generate(
+         system=f"""You are a helpful support agent. Answer based on the docs provided.
+
+ Customer context: {ticket.customer_message}
+ Relevant documentation: {docs}""",
+         messages=[
+             {"role": "user", "content": "Please respond to the customer's issue."}
+         ],
+     )
```

**Surface read**: Refactored to put context in system message instead of user message. Cleaner separation of concerns?

**Model review**

> **[Blocker]** `support_agent.py:10-12` — Both `ticket.customer_message` (untrusted user input) and `docs` (retrieved content — potentially poisoned) are now interpolated into the **system message**. System messages have highest instruction authority — an injection payload in the customer message or a poisoned doc can now override the agent's behavior at the system level.
>
> The previous version was safer: untrusted content was in the user message, where the model treats it as data rather than instructions. Move it back:
> ```python
> system="You are a helpful support agent. Answer based on the docs provided.",
> messages=[
>     {"role": "user", "content": (
>         f"<customer_message>{ticket.customer_message}</customer_message>\n\n"
>         f"<retrieved_docs>{docs}</retrieved_docs>\n\n"
>         "Please respond to the customer's issue."
>     )}
> ]
> ```
>
> Wrapping in explicit tags further helps the model distinguish data from instructions.

**What this teaches**: Trust separation is the core defense against prompt injection. The "refactor" looks like a cleanup but is a security regression — it elevates untrusted content from user-role to system-role authority. See [security guide §2](../../../guides/7-security-safety/interview-guide.md) on source-sink analysis; [security notes](../../../notes/security.md) §2.

---

## Example 3: Missing auth check on new endpoint

**The diff**
```python
# api/routes/admin.py
@router.get("/admin/users")
- @require_role("admin")
  async def list_users(db: Database = Depends(get_db)):
      return await db.fetch_all("SELECT * FROM users")

+ @router.get("/admin/users/{user_id}/export")
+ async def export_user_data(user_id: int, db: Database = Depends(get_db)):
+     user = await db.fetch_one("SELECT * FROM users WHERE id = :id", {"id": user_id})
+     return {"data": user, "exported_at": datetime.now().isoformat()}
```

**Surface read**: New endpoint added, existing endpoint modified.

**Model review**

> **[Blocker]** `admin.py:2-3` — `@require_role("admin")` decorator removed from `list_users`. One-line deletion that drops an auth boundary on all user records.
>
> **[Blocker]** `admin.py:6-9` — New `export_user_data` under `/admin/` has no `@require_role`. Needs the same auth check.
>
> **[Warning]** `admin.py:8` — `SELECT *` returns all columns including sensitive fields.

**What this teaches**: Classic but still catches people — decorator removal is a one-line deletion with outsized consequence. The new endpoint not inheriting auth from its neighbor is the second catch. Relevant everywhere, including agent API endpoints.
