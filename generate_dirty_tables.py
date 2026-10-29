import os
import random
import string
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)
os.makedirs("data", exist_ok=True)

# ---------------------------------------------------------
# GLOBAL ENTITY POOLS (Heavy scaling)
# ---------------------------------------------------------
N_ACCTS = 1200
N_CONTACTS = 2500
N_USERS = 3500
N_COOKIES = 6000
N_SKUS = 400
N_ORDERS = 8000
N_INVOICES = 10000
N_TXNS = 12000

acct_ids = [10000 + i for i in range(N_ACCTS)]
contact_ids = [50000 + i for i in range(N_CONTACTS)]
user_ids = [90000 + i for i in range(N_USERS)]
cookies = [f"ck_{''.join(random.choices(string.ascii_lowercase + string.digits, k=16))}" for _ in range(N_COOKIES)]
skus = [f"SKU-{1000 + i}" for i in range(N_SKUS)]
camp_ids = [f"CMP_{100 + i}" for i in range(80)]
rep_codes = [f"REP-{10 + i:02d}" for i in range(35)]
order_nos = [f"ORD-{70000 + i}" for i in range(N_ORDERS)]
sub_ids = [f"SUB-{80000 + i}" for i in range(4000)]
inv_ids = [f"INV-{400000 + i}" for i in range(N_INVOICES)]
txn_ids = [f"TXN-{600000 + i}" for i in range(N_TXNS)]

# ---------------------------------------------------------
# CORRUPTION UTILITIES
# ---------------------------------------------------------
DIRTY_NULLS = [None, None, np.nan, "", "   ", "NULL", "null", "N/A", "na", "--", "None", "undefined"]

def dirty_val(val, null_prob=0.15):
    return random.choice(DIRTY_NULLS) if random.random() < null_prob else val

def dirty_date_str():
    if random.random() < 0.12:
        return random.choice(DIRTY_NULLS)
    start_date = datetime(2024, 1, 1)
    d = start_date + timedelta(days=random.randint(0, 950), seconds=random.randint(0, 86400))
    fmt = random.choice([
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m-%d-%Y %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%d-%b-%Y",
        "epoch"
    ])
    if fmt == "epoch":
        return str(int(d.timestamp()))
    return d.strftime(fmt)

def dirty_currency(val, as_cents=False):
    if random.random() < 0.08:
        return random.choice(DIRTY_NULLS)
    if as_cents:
        return int(val * 100)
    fmt = random.choice([
        f"${val:,.2f}",
        f"{val:.2f}",
        f"{val:.4f}",
        f"${val:.2f} USD",
        f" {val:.2f} ",
        f"${int(val)}"
    ])
    return fmt

def dirty_phone():
    if random.random() < 0.2:
        return random.choice(DIRTY_NULLS)
    num = "".join([str(random.randint(0, 9)) for _ in range(10)])
    return random.choice([
        f"+1-{num[:3]}-{num[3:6]}-{num[6:]}",
        f"({num[:3]}) {num[3:6]}-{num[6:]}",
        num,
        f"+91 {num[:5]} {num[5:]}",
        f"001.{num[:3]}.{num[3:6]}.{num[6:]}"
    ])

tables = {}
print("Generating high-scale dirty tables across 4 enterprise domains...")

# =========================================================
# DOMAIN 1: ACQUISITION & WEB TRAFFIC
# =========================================================
print("Building Acquisition domain (5 tables)...")

# 1. mkt_utm_clicks_raw (12,000 rows, 17 cols)
tables["mkt_utm_clicks_raw"] = pd.DataFrame([{
    "click_uuid": f"clk_{i}_{random.randint(100, 999)}",
    "visitor_guid": random.choice(cookies),
    "cmp_id": dirty_val(random.choice(camp_ids) + random.choice(["", " ", "  ", "_v1"])),
    "src_channel": random.choice(["google_ads", "GSearch", "google", "meta_paid", "FB_Ads", "organic", "direct", None]),
    "medium": random.choice(["cpc", "cpm", "display", "social", "email", "", None]),
    "ad_grp_code": f"grp_{random.randint(10, 99)}",
    "keyword_raw": random.choice(["enterprise erp", "cloud billing software", "b2b crm", "pricing tier", "login portal", None]),
    "cost_per_click": dirty_currency(random.uniform(0.5, 35.0)),
    "landing_url": random.choice(["/home", "/landing-v1", "/pricing?utm_source=ad", "/contact-sales", "/product/demo"]),
    "user_agent_str": random.choice(["Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "AppleWebKit/537.36", "Mobile/Safari", None]),
    "ip_address_v4": f"{random.randint(10, 220)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
    "geo_country": random.choice(["US", "USA", "IN", "India", "GB", "United Kingdom", "DE", None]),
    "geo_region_cd": random.choice(["CA", "NY", "HR", "DL", "TX", "LON", "BY", None]),
    "is_bot_flag": random.choice([0, 1, "0", "1", "false", "true", "Y", None]),
    "click_ts": dirty_date_str(),
    "load_batch_id": f"batch_{i // 2000}",
    "raw_payload_json": f'{{"screen":"{random.choice(["1920x1080","1366x768","414x896"])}", "ref":"{random.choice(["bing","google","fb"])}"}}'
} for i in range(12000)])

# 2. ad_spend_daily_dump (5,000 rows, 15 cols)
tables["ad_spend_daily_dump"] = pd.DataFrame([{
    "row_id": i,
    "campaign_ref": random.choice(camp_ids).replace("_", "-") if random.random() < 0.4 else random.choice(camp_ids),
    "ad_grp": f"grp_{random.randint(10, 99)}",
    "cost_usd_str": dirty_currency(random.uniform(10, 4500)),
    "impressions_cnt": random.choice([str(random.randint(100, 50000)), random.randint(100, 50000), "-1", None]),
    "clicks_cnt": random.randint(0, 2500),
    "conversions_qty": random.choice([random.randint(0, 80), "0", None]),
    "cpa_target": dirty_currency(random.uniform(5, 120)),
    "dt": dirty_date_str(),
    "currency_code": random.choice(["USD", "usd", "INR", "EUR", "USD "]),
    "dsp_platform": random.choice(["Google Ads", "DV360", "Meta Business", "LinkedIn Campaign Mgr"]),
    "account_manager_id": random.choice(rep_codes + [None]),
    "budget_exhausted_flag": random.choice([True, False, "Y", "N", 1, 0]),
    "synced_at": dirty_date_str(),
    "audit_hash": f"h_{random.randint(100000, 999999)}"
} for i in range(5000)])

# 3. web_sessions_log_v2 (10,000 rows, 16 cols)
tables["web_sessions_log_v2"] = pd.DataFrame([{
    "sess_id": f"s_{i:06d}",
    "usr_cookie": random.choice(cookies),
    "converted_uid": random.choice(user_ids + [None] * 5 + ["guest", "anon"]),
    "landing_pg": random.choice(["/home", "/pricing", "/features", "/signup", "/checkout", None]),
    "exit_pg": random.choice(["/pricing", "/checkout", "/confirmation", "/docs", "/blog"]),
    "pageviews_cnt": random.choice([random.randint(1, 35), "1", None]),
    "duration_sec": random.choice([random.randint(1, 1800), -1, "0", None]),
    "referrer_domain": random.choice(["google.com", "t.co", "linkedin.com", "direct", "None", None]),
    "browser_family": random.choice(["Chrome", "Safari", "Edge", "Firefox", "Opera"]),
    "os_version": random.choice(["Win11", "Win10", "macOS 14", "iOS 17", "Android 14"]),
    "device_type": random.choice(["Desktop", "desktop", "Mobile", "mobile", "Tablet", None]),
    "session_start_ts": dirty_date_str(),
    "session_end_ts": dirty_date_str(),
    "has_cart_action": random.choice([0, 1, "true", "false", None]),
    "locale_code": random.choice(["en-US", "en-GB", "en-IN", "de-DE", "fr-FR"]),
    "utm_source_stitch": random.choice(["google", "newsletter", "affiliate", None])
} for i in range(10000)])

# 4. lead_capture_unverified (6,000 rows, 16 cols)
tables["lead_capture_unverified"] = pd.DataFrame([{
    "lead_id": f"LD-{10000 + i}",
    "email_addr": f"  User{i}@CorpDomain{random.randint(1, 200)}.COM " if i % 3 == 0 else f"user{i}@corpdomain{random.randint(1, 200)}.com",
    "full_name_raw": f"FirstName_{i} LastName_{i}",
    "contact_phone_str": dirty_phone(),
    "company_inferred": f"Company {random.choice(acct_ids)} Inc",
    "acq_source_id": random.choice(camp_ids + [None]),
    "assigned_rep": random.choice(rep_codes + ["UNASSIGNED", ""]),
    "lead_status_code": random.choice(["NEW", "CONTACTED", "QUALIFIED", "JUNK", "IN_REVIEW", None]),
    "est_employee_band": random.choice(["1-10", "11-50", "51-200", "201-500", "500+", None]),
    "territory_tag": random.choice(["NORTH_AMERICA", "APAC_SOUTH", "EMEA_CENTRAL", None]),
    "form_submit_ts": dirty_date_str(),
    "ip_captured": f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}",
    "consent_gdpr": random.choice(["YES", "NO", "OPT_IN", 1, 0, None]),
    "enriched_score": random.choice([random.uniform(0, 100), -999, None]),
    "notes_txt": random.choice(["Interested in enterprise tier", "Urgent pricing request", "Follow up Q3", None]),
    "legacy_crm_link": f"CRM-SYNC-{i // 10}"
} for i in range(6000)])

# 5. affiliates_partner_payout (5,000 rows, 15 cols)
# TRAP: 'billed_id' here represents Affiliate Self-Billing Claim ID
tables["affiliates_partner_payout"] = pd.DataFrame([{
    "payout_pk": i,
    "partner_id": f"PRT-{random.randint(100, 300)}",
    "partner_legal_name": f"Affiliate Partner Entity {random.randint(100, 300)} LLC",
    "ref_code": random.choice(camp_ids),
    "billed_id": f"AFF-CLAIM-{90000 + i}",
    "billed to": f"Partner Agency {random.randint(100, 300)}",
    "billed_to_tax_num": f"TAX-AP-{random.randint(10000, 99999)}",
    "commission_amt": dirty_currency(random.uniform(50, 4500)),
    "payout_currency": random.choice(["USD", "EUR", "GBP"]),
    "payout_status": random.choice(["APPROVED", "PENDING_TAX", "PAID", "REJECTED", "HELD"]),
    "cleared_dt": dirty_date_str(),
    "routing_transit_num": f"021{random.randint(100000, 999999)}",
    "disbursement_batch": f"DISB-B{i // 500}",
    "partner_tier": random.choice(["PLATINUM", "GOLD", "SILVER", "BRONZE"]),
    "contract_expiry_dt": dirty_date_str()
} for i in range(5000)])

# =========================================================
# DOMAIN 2: SALES & CRM
# =========================================================
print("Building Sales & CRM domain (6 tables)...")

# 6. crm_accounts_master (N_ACCTS rows, 16 cols)
# TRAP: 'billed to' free text, mixed account hierarchies
tables["crm_accounts_master"] = pd.DataFrame([{
    "acct_id": a_id,
    "account_number_str": f"ACCT-{a_id}",
    "company_name": f"Enterprise Corp {a_id}",
    "parent_acct": random.choice(acct_ids + [None] * 4),
    "billed to": random.choice([f"Enterprise Corp {a_id} Accounts Payable", f"ap-finance@{a_id}.com", f"Dept {a_id}", None]),
    "billing_address_line": f"Suite {random.randint(100, 999)}, Tech Boulevard",
    "billing_city": random.choice(["San Jose", "New York", "Gurugram", "London", "Bengaluru", "Berlin"]),
    "billing_state_code": random.choice(["CA", "NY", "HR", "LON", "KA", "TX", None]),
    "tier": random.choice(["Enterprise", "ENT", "Mid-Market", "SMB", "SMB-Tier1", ""]),
    "industry_vertical": random.choice(["SaaS", "Fintech", "HealthTech", "Retail", "Manufacturing", None]),
    "account_owner_rep": random.choice(rep_codes),
    "annual_revenue_usd": dirty_currency(random.uniform(50000, 10000000)),
    "created_timestamp": dirty_date_str(),
    "is_active_flag": random.choice([1, 0, "Y", "N", "true", "active"]),
    "tax_exemption_cert": random.choice([f"CERT-TX-{random.randint(1000, 9999)}", None, "PENDING"]),
    "credit_limit_amt": dirty_currency(random.uniform(10000, 500000))
} for a_id in acct_ids])

# 7. crm_contacts_dump (N_CONTACTS rows, 16 cols)
# TRAP: orphan org_id values
tables["crm_contacts_dump"] = pd.DataFrame([{
    "contact_pk": c_pk,
    "org_id": random.choice(acct_ids + [99999, 88888, 77777] * 2),
    "first_name": f"ContactFirstName_{c_pk}",
    "last_name": f"LastName_{c_pk}",
    "work_email": f"contact_{c_pk}@corpdomain{random.randint(1, 200)}.com",
    "direct_phone_str": dirty_phone(),
    "job_title_raw": random.choice(["Director of Procurement", "VP Engineering", "Billing Specialist", "Lead Architect", "CFO", "AP Associate"]),
    "is_billing_contact": random.choice([1, 0, "true", "Y", "N", "False", None]),
    "is_primary_signatory": random.choice([1, 0, None]),
    "department_name": random.choice(["Finance", "Procurement", "Information Technology", "Executive", None]),
    "crm_contact_stage": random.choice(["ACTIVE", "INACTIVE", "BOUNCED", "LEFT_COMPANY"]),
    "created_at_dt": dirty_date_str(),
    "last_activity_date": dirty_date_str(),
    "external_auth_link": f"AUTH-ID-{c_pk}",
    "opt_out_all_emails": random.choice([0, 1, "0", None]),
    "sync_hash_md5": f"md5_{c_pk}_{random.randint(1000, 9999)}"
} for c_pk in contact_ids])

# 8. rep_roster_region (100 rows, 15 cols)
tables["rep_roster_region"] = pd.DataFrame([{
    "emp_id": r_idx + 1,
    "rep_code": f"REP-{r_idx + 1:02d}",
    "full_name": f"Sales Representative {r_idx + 1}",
    "email_work": f"rep_{r_idx + 1}@salesorg.com",
    "mgr_id": random.choice(list(range(1, 10)) + [None]),
    "territory_id": random.choice(["NA-EAST", "NA_EAST", "NA-WEST", "EMEA-CENTRAL", "APAC-SOUTH"]),
    "quota_curr_qtr": dirty_currency(random.uniform(150000, 800000)),
    "commission_rate_pct": random.choice([0.05, 0.08, 0.10, "5%", "8%", "10%"]),
    "hire_date": dirty_date_str(),
    "termination_date": dirty_date_str() if random.random() < 0.15 else None,
    "is_active_staff": random.choice([1, 0, True, False]),
    "cost_center_code": f"CC-SLS-{random.randint(10, 40)}",
    "base_salary_band": random.choice(["TIER_1", "TIER_2", "TIER_3"]),
    "mobile_work_phone": dirty_phone(),
    "license_level": random.choice(["Standard", "Executive", "Admin"])
} for r_idx in range(len(rep_codes))])

# 9. sales_opps_pipeline (6,000 rows, 16 cols)
tables["sales_opps_pipeline"] = pd.DataFrame([{
    "opp_id": f"OPP-{20000 + i}",
    "opportunity_title": f"Expansion Contract {i}",
    "client_id": random.choice(acct_ids),
    "primary_contact_ref": random.choice(contact_ids),
    "owner_id": random.choice(list(range(1, 35))),
    "stage_cd": random.choice(["Closed Won", "CW", "Negotiation", "Lost", "04_Won", "Discovery", "Proposal Sent"]),
    "est_val": dirty_currency(random.uniform(5000, 250000)),
    "probable_val_weighted": dirty_currency(random.uniform(2000, 200000)),
    "close_target_date": dirty_date_str(),
    "actual_closed_ts": dirty_date_str(),
    "deal_type": random.choice(["NEW_BUSINESS", "UPSELL", "RENEWAL", "MIGRATION"]),
    "lead_origin_id": random.choice(camp_ids + [None]),
    "competitor_named": random.choice(["Competitor A", "Competitor B", "None", "Incumbent", None]),
    "forecast_category": random.choice(["PIPELINE", "BEST_CASE", "COMMIT", "CLOSED"]),
    "lost_reason_code": random.choice(["PRICE", "COMPETITOR", "FEATURE_GAP", "BUDGET_CUT", None]),
    "last_updated_time": dirty_date_str()
} for i in range(6000)])

# 10. quote_headers_legacy (5,000 rows, 16 cols)
# TRAP: 'billed_to_id' maps to contact_pk, while 'billed_id' maps to acct_id
tables["quote_headers_legacy"] = pd.DataFrame([{
    "q_id": f"Q-{30000 + i}",
    "quote_version": random.choice([1, 2, 3, "v1", "v2"]),
    "opportunity_ref": f"OPP-{20000 + random.randint(0, 5999)}",
    "billed_to_id": random.choice(contact_ids),
    "billed_id": random.choice(acct_ids),
    "quote_status": random.choice(["DRAFT", "ISSUED", "ACCEPTED", "EXPIRED", "SUPERSEDED"]),
    "gross_quote_val": dirty_currency(random.uniform(5000, 180000)),
    "discount_applied_pct": random.choice([0, 5, 10, 15, 20, "10%", "15.0%"]),
    "net_quote_val": dirty_currency(random.uniform(4000, 160000)),
    "payment_terms": random.choice(["Net 30", "Net 45", "Net 60", "Due on Receipt", "NET30"]),
    "valid_until": dirty_date_str(),
    "created_by_rep": random.choice(rep_codes),
    "authorized_by_mgr": random.choice([1, 0, None]),
    "currency_symbol": random.choice(["USD", "$", "EUR", "INR"]),
    "pricing_tier_locked": random.choice(["TIER_2024", "TIER_2025", "CUSTOM"]),
    "special_clauses_txt": random.choice(["Custom SLA attached", "Multi-year price lock", "Standard T&C", None])
} for i in range(5000)])

# 11. quote_line_items_tmp (10,000 rows, 15 cols)
# TRAP: quote_num strips the 'Q-' prefix
tables["quote_line_items_tmp"] = pd.DataFrame([{
    "line_id": i,
    "quote_num": str(30000 + random.randint(0, 4999)),
    "line_item_seq": (i % 5) + 1,
    "sku_code": random.choice(skus),
    "item_description_raw": f"Product SKU component {random.choice(skus)}",
    "order_qty": random.randint(1, 100),
    "unit_list_price": dirty_currency(random.uniform(50, 1200)),
    "disc_pct": random.choice([0, 5, 10, 0.15, "10%", "0.0"]),
    "net_amt": dirty_currency(random.uniform(100, 15000)),
    "is_recurring_line": random.choice([1, 0, "Y", "N"]),
    "billing_cycle_code": random.choice(["ANNUAL", "MONTHLY", "ONE_OFF"]),
    "provisioning_status": random.choice(["READY", "WAITING_APPROVAL", "CUSTOM"]),
    "tax_code_ref": random.choice(["TAX_EXEMPT", "STD_SERVICE", "SW_TAX"]),
    "config_options_json": f'{{"users":{random.randint(5, 500)}, "env":"prod"}}',
    "audit_ts": dirty_date_str()
} for i in range(10000)])

# =========================================================
# DOMAIN 3: E-COMMERCE & FULFILLMENT
# =========================================================
print("Building E-Commerce domain (7 tables)...")

# 12. ecom_users_auth (N_USERS rows, 16 cols)
tables["ecom_users_auth"] = pd.DataFrame([{
    "uid": u_id,
    "login_email": f"user{u_id}@corpdomain{random.randint(1, 200)}.com",
    "password_hash_raw": f"hash_salt_{u_id}_{random.randint(1000, 9999)}",
    "ext_crm_id": f"ACCT#{random.choice(acct_ids)}" if u_id % 2 == 0 else f"CUST-{random.choice(acct_ids)}" if u_id % 3 == 0 else None,
    "user_role": random.choice(["CUSTOMER_ADMIN", "BUYER", "AUDITOR", "STANDARD_USER"]),
    "sso_provider": random.choice(["Okta", "Google Auth", "Azure AD", "None", None]),
    "is_mfa_enabled": random.choice([1, 0, "true", "false", None]),
    "account_status": random.choice(["ACTIVE", "LOCKED", "SUSPENDED", "PENDING_VERIFICATION"]),
    "failed_logins_cnt": random.randint(0, 5),
    "last_login_ts": dirty_date_str(),
    "created_ts": dirty_date_str(),
    "registration_ip": f"10.0.{random.randint(0, 255)}.{random.randint(1, 254)}",
    "preferred_lang": random.choice(["en", "es", "fr", "de", "hi"]),
    "time_zone_str": random.choice(["America/Los_Angeles", "America/New_York", "Asia/Kolkata", "Europe/London"]),
    "marketing_opt_in": random.choice([True, False, 1, 0, None]),
    "profile_completion_pct": random.choice([100, 80, 50, "100%", None])
} for u_id in user_ids])

# 13. shop_cart_abandon (6,000 rows, 15 cols)
# TRAP: 'user_id' mixes integer uid and string cookie
tables["shop_cart_abandon"] = pd.DataFrame([{
    "cart_uuid": f"crt_{i}_{random.randint(100, 999)}",
    "user_id": str(random.choice(user_ids)) if i % 2 == 0 else random.choice(cookies),
    "session_ref": f"s_{random.randint(0, 9999):06d}",
    "item_json": f'{{"sku": "{random.choice(skus)}", "qty": {random.randint(1, 10)}, "added_at": "{dirty_date_str()}"}}',
    "total_cart_estimate": dirty_currency(random.uniform(20, 2500)),
    "items_count": random.randint(1, 8),
    "checkout_step_reached": random.choice(["CART", "ADDRESS", "PAYMENT_METHOD", "REVIEW"]),
    "abandoned_timestamp": dirty_date_str(),
    "device_fingerprint": f"fp_{random.randint(100000, 999999)}",
    "recovery_email_sent_flag": random.choice([1, 0, "Y", "N", None]),
    "recovery_email_opened": random.choice([1, 0, None]),
    "coupon_applied_code": random.choice(["SAVE10", "WELCOME20", "ENTERPRISE", None, ""]),
    "store_region": random.choice(["US_EAST", "US_WEST", "APAC", "EU"]),
    "cart_currency": random.choice(["USD", "EUR", "INR"]),
    "is_converted_subsequent": random.choice([0, 1, False, True, None])
} for i in range(6000)])

# 14. ord_header_main (N_ORDERS rows, 17 cols)
# TRAP: 'billed_to_id' has prefixed strings, unpadded numbers, and nulls
tables["ord_header_main"] = pd.DataFrame([{
    "order_no": o_no,
    "buyer_id": random.choice(user_ids),
    "billed_to_id": random.choice([f"CUS-{a}" for a in acct_ids] + [str(a) for a in acct_ids] + [None, ""]),
    "ship_to_addr_id": f"ADDR-{random.randint(1000, 5000)}",
    "order_placed_ts": dirty_date_str(),
    "ord_status": random.choice(["COMPLETED", "comp", "Pending", "CANCELLED", "PROCESSING", "1", "0"]),
    "subtotal_amount": dirty_currency(random.uniform(50, 8000)),
    "tax_total_amt": dirty_currency(random.uniform(5, 500)),
    "shipping_freight_fee": dirty_currency(random.uniform(0, 150)),
    "grand_total_amt": dirty_currency(random.uniform(55, 8650)),
    "currency_code": random.choice(["USD", "USD ", "usd", "INR", "EUR"]),
    "payment_method_code": random.choice(["CREDIT_CARD", "ACH_WIRE", "NET_TERMS", "PAYPAL"]),
    "order_channel": random.choice(["WEB_PORTAL", "EDI", "DIRECT_SALES", "MOBILE_APP"]),
    "is_expedited_delivery": random.choice([1, 0, "true", "false", None]),
    "parent_quote_id": f"Q-{random.randint(30000, 34999)}" if random.random() < 0.4 else None,
    "cancellation_reason": random.choice(["BUYER_REGRET", "PAYMENT_FAILED", "FRAUD_SUSPECTED", None]),
    "integration_sync_status": random.choice(["SYNCED", "PENDING", "ERROR"])
} for o_no in order_nos])

# 15. ord_items_detail (12,000 rows, 16 cols)
tables["ord_items_detail"] = pd.DataFrame([{
    "id": i,
    "ord_id": random.choice(order_nos),
    "order_line_no": (i % 8) + 1,
    "prod_id": random.randint(3000, 3000 + N_SKUS - 1),
    "item_sku_str": random.choice(skus),
    "qty": random.choice([1, 2, 3, 5, 10, -1, 0]),
    "unit_prc": dirty_currency(random.uniform(15, 600)),
    "extended_price": dirty_currency(random.uniform(15, 6000)),
    "discount_line_amt": dirty_currency(random.uniform(0, 100)),
    "item_tax_rate": random.choice([0.08, 0.18, 0.05, "8%", "18%", 0]),
    "fulfillment_status": random.choice(["FULFILLED", "PENDING_STOCK", "BACKORDERED", "RETURNED"]),
    "warehouse_source_id": f"WH-{random.randint(1, 5):02d}",
    "is_gift_wrapped": random.choice([0, 1, None]),
    "return_request_id": f"RET-{random.randint(100, 999)}" if random.random() < 0.05 else None,
    "shipped_date": dirty_date_str(),
    "record_created_at": dirty_date_str()
} for i in range(12000)])

# 16. prod_catalog_v1 (N_SKUS rows, 16 cols)
tables["prod_catalog_v1"] = pd.DataFrame([{
    "item_id": 3000 + i,
    "sku": skus[i],
    "parent_sku": random.choice(skus[:30] + [None] * 5),
    "product_name": f"Enterprise Solution Module {skus[i]}",
    "cat_id": random.choice([10, 20, 30, "10", "ELEC", "SW_LIC", "SVC"]),
    "category_hierarchy": f"Software > B2B > Subscriptions > {skus[i]}",
    "base_price": dirty_currency(random.uniform(50, 1500)),
    "unit_cost_raw": dirty_currency(random.uniform(10, 600)),
    "weight_kg_str": f"{random.uniform(0.1, 5.0):.2f} kg",
    "is_tangible_good": random.choice([0, 1, "Y", "N", False, True]),
    "inventory_tracked": random.choice([1, 0, "true", "false"]),
    "lifecycle_status": random.choice(["GA", "BETA", "SUNSET", "END_OF_LIFE"]),
    "release_date": dirty_date_str(),
    "ean_upc_barcode": f"890123{random.randint(100000, 999999)}",
    "tax_classification_code": random.choice(["TAX_STD", "TAX_ZERO", "TAX_REDUCED"]),
    "last_price_update_ts": dirty_date_str()
} for i in range(N_SKUS)])

# 17. inv_warehouse_stock (6,000 rows, 15 cols)
# TRAP: product_code drops hyphens randomly
tables["inv_warehouse_stock"] = pd.DataFrame([{
    "stock_row_id": i,
    "wh_id": random.choice(["WH-NORTH", "WH-SOUTH", "WH_01", "WH_CENTRAL", "WH-APAC-01"]),
    "product_code": random.choice(skus).replace("-", "") if i % 3 == 0 else random.choice(skus),
    "on_hand_qty": random.randint(-5, 1200),
    "reserved_qty": random.randint(0, 150),
    "available_to_promise": random.randint(0, 1000),
    "reorder_threshold": random.choice([50, 100, 200, "100", None]),
    "safety_stock_level": random.randint(20, 150),
    "last_counted_audit_dt": dirty_date_str(),
    "unit_storage_cost_monthly": dirty_currency(random.uniform(0.2, 5.0)),
    "aisle_bin_locator": f"Aisle_{random.randint(1, 20)}-Bin_{random.randint(10, 99)}",
    "is_damaged_stock": random.choice([0, 1, None]),
    "wh_manager_emp_id": random.choice(rep_codes),
    "restock_po_pending": f"PO-{random.randint(10000, 99999)}" if random.random() < 0.25 else None,
    "last_modified_ts": dirty_date_str()
} for i in range(6000)])

# 18. shipments_dispatch (8,000 rows, 16 cols)
# TRAP: order_ref strips 'ORD-' prefix
tables["shipments_dispatch"] = pd.DataFrame([{
    "ship_id": f"SHP-{100000 + i}",
    "order_ref": random.choice(order_nos).replace("ORD-", ""),
    "carrier_cd": random.choice(["FEDEX", "FDX", "UPS", "DHL_EXP", "BLUEDART", "USPS"]),
    "tracking_num": f"1Z{random.randint(10000000, 99999999)}",
    "shipment_status": random.choice(["DISPATCHED", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED", "FAILED_ATTEMPT", "RETURNED"]),
    "freight_cost_actual": dirty_currency(random.uniform(10, 250)),
    "weight_billed_lbs": f"{random.uniform(1, 40):.1f} lbs",
    "dispatched_ts": dirty_date_str(),
    "delivered_dt": dirty_date_str(),
    "signature_recipient_name": f"Recipient_{i}" if random.random() < 0.6 else None,
    "destination_country": random.choice(["US", "IN", "GB", "DE", "CA"]),
    "destination_postal_code": f"{random.randint(10000, 99999)}",
    "delivery_exception_reason": random.choice(["INCORRECT_ADDRESS", "CUSTOMER_UNAVAILABLE", "DAMAGED", None]),
    "warehouse_dispatched_from": random.choice(["WH-01", "WH-NORTH", "WH-SOUTH"]),
    "customs_declaration_no": f"CUST-DEC-{random.randint(1000, 9999)}" if random.random() < 0.3 else None,
    "audit_sync_flag": random.choice([1, 0, True, False])
} for i in range(8000)])

# =========================================================
# DOMAIN 4: BILLING, PAYMENTS & REVENUE
# =========================================================
print("Building Billing & Finance domain (6 tables)...")

# 19. bill_invoices_issued (N_INVOICES rows, 18 cols)
# TRAP: 'billed_id' holds Order/Sub ID, 'billed_to_id' holds Account ID, 'billed to' holds Display String
tables["bill_invoices_issued"] = pd.DataFrame([{
    "inv_id": inv_ids[i],
    "invoice_number_display": f"INV/{2025 + (i % 2)}/{10000 + i}",
    "billed_id": random.choice(order_nos) if i % 2 == 0 else random.choice(sub_ids),
    "billed_to_id": random.choice(acct_ids),
    "billed to": f"Enterprise Corp {random.choice(acct_ids)} Accounts Payable",
    "billing_contact_pk": random.choice(contact_ids),
    "subtotal_amount": dirty_currency(random.uniform(50, 15000)),
    "tax_amount": dirty_currency(random.uniform(5, 2000)),
    "gross_total": dirty_currency(random.uniform(55, 17000)),
    "currency_iso": random.choice(["USD", "usd", "USD ", "INR", "EUR", "GBP"]),
    "inv_date": dirty_date_str(),
    "payment_due_date": dirty_date_str(),
    "invoice_status": random.choice(["PAID", "paid", "OPEN", "PARTIALLY_PAID", "VOID", "UNPAID", "OVERDUE"]),
    "payment_terms_code": random.choice(["NET_30", "NET_45", "NET_60", "DUE_ON_RECEIPT"]),
    "is_disputed_flag": random.choice([0, 1, "Y", "N", None]),
    "dunning_level": random.choice([0, 1, 2, 3, "0", None]),
    "external_tax_engine_id": f"AVALARA-DOC-{random.randint(100000, 999999)}",
    "pdf_archive_path": f"/billing/archive/2025/inv_{i}.pdf"
} for i in range(N_INVOICES)])

# 20. bill_invoice_lines (12,000 rows, 16 cols)
# TRAP: sku_ref mixes product SKUs and subscription plan codes
tables["bill_invoice_lines"] = pd.DataFrame([{
    "inv_line_pk": i,
    "invoice_num": random.choice(inv_ids),
    "line_item_order": (i % 6) + 1,
    "charge_type": random.choice(["ONE_TIME", "RECURRING", "TAX", "usage_fee", "OVERAGE", "DISCOUNT"]),
    "sku_ref": random.choice(skus + ["PLAN-PRO", "PLAN-ENT", "PLAN-STARTER", "TIER-API-USAGE"]),
    "item_narrative": f"Service charge for reference {random.choice(skus)}",
    "billed_units": random.randint(1, 100),
    "rate_per_unit": dirty_currency(random.uniform(10, 500)),
    "line_amt": dirty_currency(random.uniform(10, 5000)),
    "taxable_amount": dirty_currency(random.uniform(10, 5000)),
    "tax_jurisdiction_code": random.choice(["US_CA", "US_NY", "IN_HR", "UK_VAT", "DE_VAT", None]),
    "service_period_start": dirty_date_str(),
    "service_period_end": dirty_date_str(),
    "gl_revenue_account": f"GL-REV-{random.randint(4000, 4999)}",
    "cost_center_allocated": f"CC-PROD-{random.randint(10, 99)}",
    "created_audit_ts": dirty_date_str()
} for i in range(12000)])

# 21. pay_transactions_gateway (N_TXNS rows, 17 cols)
# TRAP: settled_amt_cents is stored in integer cents (100x scale mismatch with invoices)
tables["pay_transactions_gateway"] = pd.DataFrame([{
    "txn_id": txn_ids[i],
    "gateway_reference_id": f"ch_{''.join(random.choices(string.ascii_letters + string.digits, k=24))}",
    "inv_ref": random.choice(inv_ids).replace("INV-", "") if i % 4 == 0 else random.choice(inv_ids),
    "payer_id": random.choice(acct_ids + contact_ids),
    "payment_gateway_vendor": random.choice(["Stripe", "Adyen", "Razorpay", "AuthorizeNet", "Cybersource"]),
    "pay_status": random.choice(["succeeded", "PAID", "failed", "00_OK", "DECLINED", "PROCESSING", "REFUNDED"]),
    "settled_amt_cents": dirty_currency(random.uniform(50, 18000), as_cents=True),
    "fee_amt_deducted_cents": dirty_currency(random.uniform(1, 50), as_cents=True),
    "currency_code": random.choice(["USD", "usd", "INR", "EUR"]),
    "payment_method_subclass": random.choice(["VISA_CREDIT", "MASTERCARD_DEBIT", "ACH_CHECK", "UPI", "AMEX"]),
    "auth_code_network": f"AUTH{random.randint(100000, 999999)}",
    "failure_error_code": random.choice(["insufficient_funds", "card_expired", "do_not_honor", "fraud_suspected", None]),
    "ip_address_geo": f"{random.randint(10, 220)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
    "avs_check_result": random.choice(["PASS", "FAIL", "UNAVAILABLE", "PARTIAL"]),
    "cvv_result_code": random.choice(["M", "N", "P", "S", None]),
    "transaction_completed_ts": dirty_date_str(),
    "reconciliation_status": random.choice(["MATCHED", "UNRECONCILED", "DISCREPANCY"])
} for i in range(N_TXNS)])

# 22. sub_plans_recurring (6,000 rows, 16 cols)
# TRAP: billed_to_id points to contact_pk rather than acct_id
tables["sub_plans_recurring"] = pd.DataFrame([{
    "sub_id": sub_ids[i % len(sub_ids)],
    "acct_ref": random.choice(acct_ids),
    "billed_to_id": random.choice(contact_ids),
    "plan_tier_id": random.choice(["PLAN-PRO", "PLAN-ENT", "PLAN-STARTER", "TIER-CUSTOM-CORP"]),
    "contract_duration_months": random.choice([1, 12, 24, 36, "12", "36"]),
    "mrr_val": dirty_currency(random.uniform(99.0, 4500.0)),
    "arr_computed_val": dirty_currency(random.uniform(1188.0, 54000.0)),
    "auto_renew_flag": random.choice([1, 0, True, False, "Y", "N", None]),
    "sub_status": random.choice(["ACTIVE", "active", "TRIALING", "PAST_DUE", "CANCELED", "UNPAID"]),
    "started_date": dirty_date_str(),
    "next_bill_date": dirty_date_str(),
    "cancellation_effective_dt": dirty_date_str() if random.random() < 0.15 else None,
    "discount_contract_token": f"DISC-{random.randint(10, 99)}" if random.random() < 0.25 else None,
    "seat_quantity_licensed": random.choice([5, 10, 25, 50, 100, 500, "50"]),
    "churn_risk_score": random.choice([random.uniform(0.0, 1.0), "LOW", "MEDIUM", "HIGH", None]),
    "assigned_csm_rep": random.choice(rep_codes)
} for i in range(6000)])

# 23. credit_notes_refunds (5,000 rows, 15 cols)
# TRAP: orig_billed_id points to inv_id 60% of the time, txn_id 40%
tables["credit_notes_refunds"] = pd.DataFrame([{
    "cn_id": f"CN-{50000 + i}",
    "credit_note_display": f"CRN-2025-{1000 + i}",
    "orig_billed_id": random.choice(inv_ids) if i % 2 == 0 else random.choice(txn_ids),
    "billed_to": random.choice(acct_ids),
    "refund_amt": dirty_currency(random.uniform(10, 3500)),
    "tax_refund_portion": dirty_currency(random.uniform(1, 400)),
    "currency_code": random.choice(["USD", "EUR", "INR"]),
    "issue_dt": dirty_date_str(),
    "refund_reason_txt": random.choice(["duplicate charge", "service outage credits", "sla breach refund", "customer churn courtesy", "wrong tier charged", None]),
    "approver_emp_id": random.choice(rep_codes),
    "refund_execution_status": random.choice(["COMPLETED", "PENDING_APPROVAL", "REJECTED", "VOID"]),
    "gl_adjustment_code": f"GL-CREDIT-{random.randint(100, 999)}",
    "ledger_applied_date": dirty_date_str(),
    "external_audit_ref": f"AUDIT-CN-{i // 200}",
    "comments_history": random.choice(["Manager approved override", "Standard SLA credit", None])
} for i in range(5000)])

# 24. tax_ledger_recon (6,000 rows, 16 cols)
# TRAP: billed_id represents State Tax Authority Registration Number
tables["tax_ledger_recon"] = pd.DataFrame([{
    "tax_entry_id": i,
    "doc_id": random.choice(inv_ids),
    "billed_id": f"TAX-REG-{random.randint(10000, 99999)}",
    "billed_to_state": random.choice(["CA", "NY", "HR", "TX", "KA", "LON", "DL", None]),
    "jurisdiction": random.choice(["US-CA", "CA", "NY", "IND-HR", "UK-VAT", "DE-MWST", "US-TX"]),
    "taxable_basis_amt": dirty_currency(random.uniform(50, 15000)),
    "tax_rate_pct": random.choice([0.08, 8.0, 18.0, 0.18, 20.0, 0.20, "18%", "8%"]),
    "calculated_tax_liability": dirty_currency(random.uniform(5, 2700)),
    "tax_collected_flag": random.choice([1, 0, "Y", "N", "true"]),
    "remitted_to_authority_date": dirty_date_str() if random.random() < 0.7 else None,
    "tax_filing_period": random.choice(["2025-Q1", "2025-Q2", "2025-Q3", "2025-M01", "2025-M02"]),
    "remittance_reference_no": f"GOV-TX-{random.randint(100000, 999999)}",
    "exemption_claimed_flag": random.choice([0, 1, None]),
    "auditor_signoff": random.choice(["TAX_AGENT_1", "TAX_AGENT_2", "UNREVIEWED", None]),
    "reconciliation_delta_cents": random.choice([0, 1, -1, 5, -5, None]),
    "created_at_audit": dirty_date_str()
} for i in range(6000)])

# ---------------------------------------------------------
# WRITE TABLES TO DISK
# ---------------------------------------------------------
for name, df in tables.items():
    csv_path = f"data/{name}.csv"
    df.to_csv(csv_path, index=False)
    print(f"-> Generated {name}.csv: {len(df):,} rows x {len(df.columns)} columns")

print("\nAll 24 tables successfully generated in ./data/ with enterprise scale and deep ambiguity.")