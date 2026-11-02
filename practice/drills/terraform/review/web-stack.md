---
title: Review a web stack before it ships
track: terraform
topic: review
difficulty: medium
timebox_min: 20
concepts: [terraform-state, secrets-management, network-security, iac-review]
source: original
---

## Prompt

A teammate opens a PR with [`web-stack.tf`](web-stack.tf): a security group, a Postgres
RDS instance and an uploads bucket. Review it as you would in the PR. Find every problem,
rank them by severity, and give the fix for each. Narrate as you go: an interviewer grades
the order you find things in and how you justify severity, not just the list.

There are **at least eight** issues across security, state, and reproducibility.

## Starter

[`web-stack.tf`](web-stack.tf). No credentials needed; read it, don't apply it.

## Tests

Your list should cover each row below (wording free). Score one point per row; 7+ is a pass.

| # | Area |
|---|---|
| 1 | Secret in a variable default |
| 2 | Secret exposed as an output |
| 3 | Secret ends up in state |
| 4 | SSH open to the internet |
| 5 | Database reachable from the internet |
| 6 | Bucket public-access block disabled |
| 7 | No state locking |
| 8 | Provider version unpinned |
| 9 | Final snapshot skipped on a prod database |

<details>
<summary>Solution</summary>

**Critical**

1. **`db_password` default `"hunter2-prod"`** — committed to git in plain text. Remove the
   default and mark the variable `sensitive = true`. Better: `manage_master_user_password = true`
   (RDS keeps it in Secrets Manager), or read it from Secrets Manager/SSM.
2. **`output "db_password"`** prints it on every `apply` and exposes it to anyone with
   `terraform output`. Delete the output. If something really needs it, `sensitive = true`.
3. **Password in state**: even when fixed, `password` is stored in plain text in state.
   That is why the state bucket needs encryption and tight IAM, and why
   `manage_master_user_password` is the better fix.
4. **Port 22 from `0.0.0.0/0`** — SSH to the world. Remove it and use SSM Session Manager, or
   limit it to a bastion or VPN CIDR.
5. **`publicly_accessible = true`** on the database — combined with no `vpc_security_group_ids`
   (it falls back to the default SG). Make it private, in private subnets, and allow 5432
   only from `aws_security_group.web`.
6. **Public-access block all `false`** on uploads: one bad policy or ACL makes user uploads
   public. Set all four to `true`; serve files through CloudFront or presigned URLs.

**High**

7. **S3 backend with no locking** — two concurrent applies corrupt state. Add
   `use_lockfile = true` (Terraform 1.10+) or a DynamoDB `dynamodb_table`, and `encrypt = true`.
8. **No version constraints** — `hashicorp/aws` and Terraform itself are unpinned, so a new
   major version changes behaviour silently. Add `required_version` and `version = "~> 5.0"`;
   commit `.terraform.lock.hcl`.

**Medium**

9. **`skip_final_snapshot = true`** — `destroy` or a forced replacement deletes the database
   with no backup. Set it to `false` with a `final_snapshot_identifier`, plus
   `deletion_protection = true` and `backup_retention_period`.

Also worth a mention: no `storage_encrypted = true` on the database, no tags, region
hardcoded twice, and the security group has no `vpc_id` (it lands in the default VPC).

</details>

## Notes

- **Order matters in the room**: lead with secrets and public exposure, then state and
  reproducibility, then hygiene. Say *why* each is that severity (blast radius × likelihood).
- **"Fixed in code" ≠ fixed**: a leaked password needs rotating, and it stays in git
  history and old state versions.
- **Tools that would have caught this**: `tflint`, `checkov` / `trivy config`, and
  `terraform plan` review in CI. Naming them shows how you'd stop it recurring.
- **Follow-ups**: move the database to private subnets with a module; refactor the inline
  `ingress` blocks into `aws_vpc_security_group_ingress_rule` resources without destroying
  the SG (`moved` blocks / `terraform state mv`).
