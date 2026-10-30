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
# GLOBAL BASE ENTITY POOLS
# ---------------------------------------------------------
N_ACCTS = 1500
N_CONTACTS = 3000
N_USERS = 4000
N_COOKIES = 7000
N_SKUS = 500
N_ORDERS = 9000
N_INVOICES = 11000
N_TXNS = 13000

base_acct_ids = [10000 + i for i in range(N_ACCTS)]
base_contact_ids = [50000 + i for i in range(N_CONTACTS)]
base_user_ids = [90000 + i for i in range(N_USERS)]
base_skus = [f"SKU-{1000 + i}" for i in range(N_SKUS)]
base_order_nums = [70000 + i for i in range(N_ORDERS)]
base_inv_nums = [400000 + i for i in range(N_INVOICES)]
base_txn_nums = [600000 + i for i in range(N_TXNS)]
camp_ids = [f"CMP_{100 + i}" for i in range(100)]
rep_codes = [f"REP-{10 + i:02d}" for i in range(40)]

# ---------------------------------------------------------
# CORRUPTION & KEY MUTATION UTILITIES
# ---------------------------------------------------------
DIRTY_NULLS = [None, None, np.nan, "", "   ", "NULL", "null", "N/A", "na", "--", "None", "undefined", "0", "-1"]

def dirty_val(val, null_prob=0.15):
    return random.choice(DIRTY_NULLS) if random.random() < null_prob else val

def mutate_key(val, entity_type="ACCT"):
    """Creates format fragmentation to stress-test exact hash matching."""
    if random.random() < 0.12:
        return random.choice(DIRTY_NULLS)
    roll = random.random()
    if roll < 0.25:
        return str(val)
    elif roll < 0.45:
        return f"{entity_type}-{val}"
    elif roll < 0.65:
        return f"{entity_type.lower()}_{val}"
    elif roll < 0.85:
        return f"{val:08d}"
    else:
        return f"{entity_type}-{val}-LOC"

def dirty_date_str():
    if random.random() < 0.12:
        return random.choice(DIRTY_NULLS)
    start_date = datetime(2023, 1, 1)
    d = start_date + timedelta(days=random.randint(0, 1200), seconds=random.randint(0, 86400))
    fmt = random.choice([
        "%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y %H:%M:%S",
        "%Y/%m/%d %H:%M", "%d-%b-%Y", "epoch"
    ])
    return str(int(d.timestamp())) if fmt == "epoch" else d.strftime(fmt)

def dirty_currency(val, as_cents=False):
    if random.random() < 0.08:
        return random.choice(DIRTY_NULLS)
    if as_cents:
        return int(val * 100)
    return random.choice([
        f"${val:,.2f}", f"{val:.2f}", f"{val:.4f}",
        f"${val:.2f} USD", f" {val:.2f} ", f"${int(val)}"
    ])

tables = {}
print("Generating extreme-complexity schema with Polymorphic/EAV relationships...")

# =========================================================
# DOMAIN 1: ACQUISITION & ATTRIBUTION (5 TABLES)
# =========================================================
tables["mkt_utm_clicks_raw"] = pd.DataFrame([{
    "click_uuid": f"clk_{i}_{random.randint(100, 999)}",
    "visitor_guid": f"ck_{random.randint(100000, 999999)}",
    "cmp_id": dirty_val(random.choice(camp_ids)),
    "src_channel": random.choice(["google", "organic", "meta", "direct", None]),
    "cost_per_click": dirty_currency(random.uniform(0.5, 40.0)),
    "landing_url": random.choice(["/home", "/pricing", "/features"]),
    "geo_region_cd": random.choice(["CA", "NY", "HR", "DL", "TX", None]),
    "is_bot_flag": random.choice([0, 1, "0", "1", "false", "true"]),
    "click_ts": dirty_date_str(),
    "load_batch_id": f"batch_{i // 2500}",
    "ad_grp_code": f"grp_{random.randint(10, 99)}"
} for i in range(12000)])

tables["ad_spend_daily_dump"] = pd.DataFrame([{
    "row_id": i,
    "campaign_ref": random.choice(camp_ids),
    "ad_grp": f"grp_{random.randint(10, 99)}",
    "cost_usd_str": dirty_currency(random.uniform(10, 5000)),
    "impressions_cnt": random.choice([str(random.randint(100, 50000)), random.randint(100, 50000), None]),
    "clicks_cnt": random.randint(0, 3000),
    "dt": dirty_date_str(),
    "currency_code": random.choice(["USD", "usd", "INR", "EUR"]),
    "account_manager_id": random.choice(rep_codes + [None]),
    "budget_exhausted_flag": random.choice([True, False, "Y", "N", 1, 0])
} for i in range(6000)])

tables["web_sessions_log_v2"] = pd.DataFrame([{
    "sess_id": f"s_{i:06d}",
    "usr_cookie": f"ck_{random.randint(100000, 999999)}",
    "converted_uid": dirty_val(random.choice(base_user_ids)),
    "landing_pg": random.choice(["/home", "/pricing", "/features", None]),
    "duration_sec": random.choice([random.randint(1, 1800), -1, "0", None]),
    "browser_family": random.choice(["Chrome", "Safari", "Edge", "Firefox"]),
    "session_start_ts": dirty_date_str(),
    "has_cart_action": random.choice([0, 1, "true", "false"])
} for i in range(10000)])

tables["lead_capture_unverified"] = pd.DataFrame([{
    "lead_id": f"LD-{10000 + i}",
    "email_addr": f"user_{i}@domain{random.randint(1, 200)}.com",
    "company_inferred": f"Company {random.choice(base_acct_ids)} Inc",
    "acq_source_id": random.choice(camp_ids + [None]),
    "assigned_rep": random.choice(rep_codes + ["UNASSIGNED", ""]),
    "lead_status_code": random.choice(["NEW", "QUALIFIED", "JUNK", None]),
    "form_submit_ts": dirty_date_str(),
    "consent_gdpr": random.choice(["YES", "NO", 1, 0, None]),
    "enriched_score": random.choice([random.uniform(0, 100), -999, None])
} for i in range(7000)])

tables["affiliates_partner_payout"] = pd.DataFrame([{
    "payout_pk": i,
    "partner_id": f"PRT-{random.randint(100, 400)}",
    "ref_code": random.choice(camp_ids),
    "billed_id": f"CLAIM-{90000 + i}",
    "billed to": f"Partner Agency {random.randint(100, 400)}",
    "commission_amt": dirty_currency(random.uniform(50, 5000)),
    "payout_status": random.choice(["APPROVED", "PENDING_TAX", "PAID"]),
    "cleared_dt": dirty_date_str()
} for i in range(5000)])

# =========================================================
# DOMAIN 2: SALES, CRM & METADATA (6 TABLES)
# =========================================================
tables["crm_accounts_master"] = pd.DataFrame([{
    "acct_id": a_id,
    "account_number_str": mutate_key(a_id, "ACC"),
    "company_name": f"Enterprise Corp {a_id}",
    "parent_acct": random.choice(base_acct_ids + [None] * 5),
    "billed to": f"Enterprise Corp {a_id} AP",
    "billing_city": random.choice(["San Jose", "New York", "Gurugram", "London"]),
    "tier": random.choice(["Enterprise", "Mid-Market", "SMB"]),
    "account_owner_rep": random.choice(rep_codes),
    "annual_revenue_usd": dirty_currency(random.uniform(50000, 10000000)),
    "created_timestamp": dirty_date_str(),
    "is_active_flag": random.choice([1, 0, "Y", "N", "true"])
} for a_id in base_acct_ids])

tables["crm_contacts_dump"] = pd.DataFrame([{
    "contact_pk": c_pk,
    "org_id": mutate_key(random.choice(base_acct_ids + [99999, 88888]), "ACC"),
    "first_name": f"Contact_{c_pk}",
    "work_email": f"c_{c_pk}@domain{random.randint(1, 200)}.com",
    "job_title_raw": random.choice(["VP", "Director", "Engineer", "Manager"]),
    "is_billing_contact": random.choice([1, 0, "true", "Y", "N", None]),
    "created_at_dt": dirty_date_str()
} for c_pk in base_contact_ids])

tables["rep_roster_region"] = pd.DataFrame([{
    "emp_id": r_idx + 1,
    "rep_code": f"REP-{r_idx + 1:02d}",
    "full_name": f"Representative {r_idx + 1}",
    "territory_id": random.choice(["NA-EAST", "NA-WEST", "EMEA", "APAC"]),
    "quota_curr_qtr": dirty_currency(random.uniform(150000, 800000)),
    "commission_rate_pct": random.choice([0.05, 0.08, "5%", "8%"]),
    "hire_date": dirty_date_str(),
    "is_active_staff": random.choice([1, 0, True, False])
} for r_idx in range(len(rep_codes))])

tables["sales_opps_pipeline"] = pd.DataFrame([{
    "opp_id": f"OPP-{20000 + i}",
    "client_id": mutate_key(random.choice(base_acct_ids), "ACC"),
    "primary_contact_ref": random.choice(base_contact_ids),
    "owner_id": random.randint(1, len(rep_codes)),
    "stage_cd": random.choice(["Closed Won", "Negotiation", "Lost", "Discovery"]),
    "est_val": dirty_currency(random.uniform(5000, 250000)),
    "close_target_date": dirty_date_str()
} for i in range(7000)])

tables["quote_headers_legacy"] = pd.DataFrame([{
    "q_id": f"Q-{30000 + i}",
    "quote_version": random.choice([1, 2, "v1", "v2"]),
    "opportunity_ref": f"OPP-{20000 + random.randint(0, 6999)}",
    "billed_to_id": random.choice(base_contact_ids),
    "billed_id": mutate_key(random.choice(base_acct_ids), "ACC"),
    "quote_status": random.choice(["DRAFT", "ISSUED", "ACCEPTED", "EXPIRED"]),
    "gross_quote_val": dirty_currency(random.uniform(5000, 180000)),
    "valid_until": dirty_date_str()
} for i in range(5000)])

tables["quote_line_items_tmp"] = pd.DataFrame([{
    "line_id": i,
    "quote_num": str(30000 + random.randint(0, 4999)),
    "line_item_seq": (i % 6) + 1,
    "sku_code": random.choice(base_skus),
    "order_qty": random.randint(1, 100),
    "unit_list_price": dirty_currency(random.uniform(50, 1200)),
    "net_amt": dirty_currency(random.uniform(100, 15000)),
    "audit_ts": dirty_date_str()
} for i in range(11000)])

# =========================================================
# DOMAIN 3: COMMERCE & SUPPLY (7 TABLES)
# =========================================================
tables["ecom_users_auth"] = pd.DataFrame([{
    "uid": u_id,
    "login_email": f"user{u_id}@domain{random.randint(1, 200)}.com",
    "ext_crm_id": mutate_key(random.choice(base_acct_ids), "ACC"),
    "user_role": random.choice(["ADMIN", "BUYER", "AUDITOR"]),
    "is_mfa_enabled": random.choice([1, 0, "true", "false"]),
    "account_status": random.choice(["ACTIVE", "LOCKED", "SUSPENDED"]),
    "last_login_ts": dirty_date_str()
} for u_id in base_user_ids])

tables["shop_cart_abandon"] = pd.DataFrame([{
    "cart_uuid": f"crt_{i}_{random.randint(100, 999)}",
    "user_id": str(random.choice(base_user_ids)) if i % 2 == 0 else f"ck_{random.randint(100000, 999999)}",
    "session_ref": f"s_{random.randint(0, 9999):06d}",
    "total_cart_estimate": dirty_currency(random.uniform(20, 2500)),
    "abandoned_timestamp": dirty_date_str(),
    "coupon_applied_code": random.choice(["SAVE10", "WELCOME20", None])
} for i in range(6000)])

tables["ord_header_main"] = pd.DataFrame([{
    "order_no": f"ORD-{o_no}",
    "raw_order_id": o_no,
    "buyer_id": random.choice(base_user_ids),
    "billed_to_id": mutate_key(random.choice(base_acct_ids), "ACC"),
    "order_placed_ts": dirty_date_str(),
    "ord_status": random.choice(["COMPLETED", "PENDING", "CANCELLED"]),
    "grand_total_amt": dirty_currency(random.uniform(55, 9000)),
    "currency_code": random.choice(["USD", "INR", "EUR"]),
    "parent_quote_id": f"Q-{random.randint(30000, 34999)}" if random.random() < 0.4 else None
} for o_no in base_order_nums])

tables["ord_items_detail"] = pd.DataFrame([{
    "id": i,
    "ord_id": f"ORD-{random.choice(base_order_nums)}",
    "order_line_no": (i % 8) + 1,
    "item_sku_str": random.choice(base_skus),
    "qty": random.choice([1, 2, 5, 10, -1, 0]),
    "unit_prc": dirty_currency(random.uniform(15, 600)),
    "extended_price": dirty_currency(random.uniform(15, 6000)),
    "shipped_date": dirty_date_str()
} for i in range(13000)])

tables["prod_catalog_v1"] = pd.DataFrame([{
    "item_id": 3000 + i,
    "sku": base_skus[i],
    "product_name": f"Module {base_skus[i]}",
    "base_price": dirty_currency(random.uniform(50, 1500)),
    "lifecycle_status": random.choice(["GA", "BETA", "SUNSET"]),
    "release_date": dirty_date_str()
} for i in range(N_SKUS)])

tables["inv_warehouse_stock"] = pd.DataFrame([{
    "stock_row_id": i,
    "wh_id": random.choice(["WH-NORTH", "WH-SOUTH", "WH-CENTRAL"]),
    "product_code": random.choice(base_skus).replace("-", "") if i % 3 == 0 else random.choice(base_skus),
    "on_hand_qty": random.randint(-5, 1200),
    "safety_stock_level": random.randint(20, 150),
    "last_counted_audit_dt": dirty_date_str(),
    "wh_manager_emp_id": random.choice(rep_codes)
} for i in range(6000)])

tables["shipments_dispatch"] = pd.DataFrame([{
    "ship_id": f"SHP-{100000 + i}",
    "order_ref": str(random.choice(base_order_nums)),
    "carrier_cd": random.choice(["FEDEX", "UPS", "DHL", "BLUEDART"]),
    "shipment_status": random.choice(["DISPATCHED", "DELIVERED", "RETURNED"]),
    "freight_cost_actual": dirty_currency(random.uniform(10, 250)),
    "delivered_dt": dirty_date_str()
} for i in range(8000)])

# =========================================================
# DOMAIN 4: BILLING & PAYMENTS (4 TABLES)
# =========================================================
tables["bill_invoices_issued"] = pd.DataFrame([{
    "inv_id": f"INV-{inv_num}",
    "raw_inv_num": inv_num,
    "billed_id": f"ORD-{random.choice(base_order_nums)}" if i % 2 == 0 else f"SUB-{random.randint(80000, 84000)}",
    "billed_to_id": mutate_key(random.choice(base_acct_ids), "ACC"),
    "billed to": f"Enterprise Corp {random.choice(base_acct_ids)} AP",
    "gross_total": dirty_currency(random.uniform(55, 17000)),
    "inv_date": dirty_date_str(),
    "invoice_status": random.choice(["PAID", "OPEN", "VOID", "OVERDUE"])
} for i, inv_num in enumerate(base_inv_nums)])

tables["bill_invoice_lines"] = pd.DataFrame([{
    "inv_line_pk": i,
    "invoice_num": f"INV-{random.choice(base_inv_nums)}",
    "line_item_order": (i % 6) + 1,
    "sku_ref": random.choice(base_skus + ["PLAN-PRO", "PLAN-ENT"]),
    "line_amt": dirty_currency(random.uniform(10, 5000)),
    "created_audit_ts": dirty_date_str()
} for i in range(12000)])

tables["pay_transactions_gateway"] = pd.DataFrame([{
    "txn_id": f"TXN-{t_num}",
    "inv_ref": str(random.choice(base_inv_nums)) if i % 3 == 0 else f"INV-{random.choice(base_inv_nums)}",
    "payer_id": mutate_key(random.choice(base_acct_ids), "ACC"),
    "pay_status": random.choice(["succeeded", "PAID", "failed", "REFUNDED"]),
    "settled_amt_cents": dirty_currency(random.uniform(50, 18000), as_cents=True),
    "transaction_completed_ts": dirty_date_str()
} for i, t_num in enumerate(base_txn_nums)])

tables["credit_notes_refunds"] = pd.DataFrame([{
    "cn_id": f"CN-{50000 + i}",
    "orig_billed_id": f"INV-{random.choice(base_inv_nums)}" if i % 2 == 0 else f"TXN-{random.choice(base_txn_nums)}",
    "billed_to": mutate_key(random.choice(base_acct_ids), "ACC"),
    "refund_amt": dirty_currency(random.uniform(10, 3500)),
    "issue_dt": dirty_date_str(),
    "approver_emp_id": random.choice(rep_codes)
} for i in range(5000)])

# =========================================================
# DOMAIN 5: GENERIC / EAV / POLYMORPHIC ARCHITECTURE (2 TABLES)
# =========================================================
# Generic EAV Table: entity_fk points to DIFFERENT entities depending on entity_type
eav_rows = []
entity_choices = [
    ("ACCOUNT", base_acct_ids, "ACC"),
    ("CONTACT", base_contact_ids, "CON"),
    ("ORDER", base_order_nums, "ORD"),
    ("INVOICE", base_inv_nums, "INV")
]
for i in range(10000):
    etype, id_list, prefix = random.choice(entity_choices)
    chosen_id = random.choice(id_list)
    eav_rows.append({
        "registry_id": i + 1,
        "entity_type": etype,
        "entity_fk": mutate_key(chosen_id, prefix),
        "attribute_key": random.choice(["KYC_STATUS", "CREDIT_TIER", "LEGACY_MIGRATION_FLAG", "RISK_RATING"]),
        "attribute_value": random.choice(["VERIFIED", "TIER_A", "HIGH", "PASSED", "FLAGGED", "1", "0"]),
        "updated_at": dirty_date_str(),
        "modified_by_emp": random.choice(rep_codes)
    })
tables["core_entity_registry"] = pd.DataFrame(eav_rows)

# Audit Ledger Table: Polymorphic event sink
audit_rows = []
for i in range(12000):
    etype, id_list, prefix = random.choice(entity_choices)
    chosen_id = random.choice(id_list)
    audit_rows.append({
        "event_id": f"EVT-{100000 + i}",
        "parent_domain": etype,
        "record_ref_id": mutate_key(chosen_id, prefix),
        "action_name": random.choice(["INSERT", "UPDATE", "SOFT_DELETE", "STATE_TRANSITION"]),
        "payload_checksum": f"sha_{random.randint(10000000, 99999999)}",
        "logged_timestamp": dirty_date_str()
    })
tables["audit_event_ledger"] = pd.DataFrame(audit_rows)

# ---------------------------------------------------------
# EXPORT
# ---------------------------------------------------------
for name, df in tables.items():
    df.to_csv(f"data/{name}.csv", index=False)
    print(f"-> Generated {name}.csv ({len(df):,} rows x {len(df.columns)} cols)")

print("\nExtreme complexity dataset generated in ./data/.")