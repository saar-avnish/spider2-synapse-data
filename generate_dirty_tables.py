import os
import random
import pandas as pd

random.seed(42)
os.makedirs("data", exist_ok=True)

# Base entity keys
acct_ids = [1001 + i for i in range(50)]
contact_pks = [5001 + i for i in range(80)]
user_uids = [9001 + i for i in range(100)]
cookies = [f"ck_{random.randint(10000, 99999)}" for _ in range(120)]
skus = [f"SKU-{100 + i}" for i in range(30)]
item_ids = [300 + i for i in range(30)]
camp_ids = [f"CMP_{10 + i}" for i in range(15)]
rep_ids = [1 + i for i in range(12)]
order_nos = [f"ORD-{7000 + i}" for i in range(120)]
sub_ids = [f"SUB-{8000 + i}" for i in range(60)]
inv_ids = [f"INV-{40000 + i}" for i in range(150)]
txn_ids = [f"TXN-{60000 + i}" for i in range(150)]

def dirty_date():
    y, m, d = 2026, random.randint(1, 10), random.randint(1, 28)
    return random.choice([
        f"{y}-{m:02d}-{d:02d}",
        f"{d:02d}/{m:02d}/{y}",
        f"{m:02d}-{d:02d}-{y} 14:22:00",
        None
    ])

tables = {}

# Acquisition (5 tables)
tables["mkt_utm_clicks_raw"] = pd.DataFrame([{"click_uuid": f"clk_{i}", "visitor_guid": random.choice(cookies), "cmp_id": random.choice(camp_ids) + " ", "src_channel": random.choice(["google", "meta", None]), "click_ts": dirty_date()} for i in range(150)])
tables["ad_spend_daily_dump"] = pd.DataFrame([{"row_id": i, "campaign_ref": random.choice(camp_ids).replace("_", "-"), "cost_usd_str": f"${random.uniform(10, 500):.2f}", "dt": dirty_date()} for i in range(100)])
tables["web_sessions_log_v2"] = pd.DataFrame([{"sess_id": f"s_{i}", "usr_cookie": random.choice(cookies), "converted_uid": random.choice(user_uids + [None, None]), "landing_pg": "/pricing"} for i in range(150)])
tables["lead_capture_unverified"] = pd.DataFrame([{"lead_id": f"LD-{i}", "email_addr": f"user{i}@corp.com ", "acq_source_id": random.choice(camp_ids), "assigned_rep": f"REP-{random.choice(rep_ids):02d}"} for i in range(100)])
tables["affiliates_partner_payout"] = pd.DataFrame([{"payout_pk": i, "partner_id": f"PRT-{i%10}", "billed_id": f"AFF-BILL-{900 + i}", "billed to": f"Partner {i%10}", "commission_amt": round(random.uniform(50, 1000), 2)} for i in range(60)])

# Sales / CRM (6 tables)
tables["crm_accounts_master"] = pd.DataFrame([{"acct_id": a, "company_name": f"Enterprise Corp {a}", "parent_acct": random.choice(acct_ids + [None]), "billed to": f"Enterprise Corp {a} AP", "tier": random.choice(["ENT", "SMB"])} for a in acct_ids])
tables["crm_contacts_dump"] = pd.DataFrame([{"contact_pk": c, "org_id": random.choice(acct_ids + [9999]), "work_email": f"contact_{c}@corp.com", "is_billing_contact": random.choice([1, 0, "true", None])} for c in contact_pks])
tables["rep_roster_region"] = pd.DataFrame([{"emp_id": r, "rep_code": f"REP-{r:02d}", "mgr_id": random.choice(rep_ids + [None]), "territory_id": "NA-EAST"} for r in rep_ids])
tables["sales_opps_pipeline"] = pd.DataFrame([{"opp_id": f"OPP-{2000 + i}", "client_id": random.choice(acct_ids), "owner_id": random.choice(rep_ids), "est_val": random.randint(1000, 50000)} for i in range(100)])
tables["quote_headers_legacy"] = pd.DataFrame([{"q_id": f"Q-{3000 + i}", "opportunity_ref": f"OPP-{2000 + (i%50)}", "billed_to_id": random.choice(contact_pks), "billed_id": random.choice(acct_ids), "valid_until": dirty_date()} for i in range(100)])
tables["quote_line_items_tmp"] = pd.DataFrame([{"line_id": i, "quote_num": str(3000 + (i%50)), "sku_code": random.choice(skus), "net_amt": round(random.uniform(100, 3000), 2)} for i in range(150)])

# E-Commerce (7 tables)
tables["ecom_users_auth"] = pd.DataFrame([{"uid": u, "login_email": f"user{u}@example.com", "ext_crm_id": f"ACCT#{random.choice(acct_ids)}" if u % 2 == 0 else None, "created_ts": dirty_date()} for u in user_uids])
tables["shop_cart_abandon"] = pd.DataFrame([{"cart_uuid": f"crt_{i}", "user_id": str(random.choice(user_uids)) if i % 2 == 0 else random.choice(cookies), "session_ref": f"s_{i%150}"} for i in range(100)])
tables["ord_header_main"] = pd.DataFrame([{"order_no": o, "buyer_id": random.choice(user_uids), "billed_to_id": random.choice([f"CUS-{a}" for a in acct_ids] + [None]), "ord_status": random.choice(["COMPLETED", "Pending"])} for o in order_nos])
tables["ord_items_detail"] = pd.DataFrame([{"id": i, "ord_id": random.choice(order_nos), "prod_id": random.choice(item_ids), "qty": random.choice([1, 2, 5, -1]), "unit_prc": round(random.uniform(15, 300), 2)} for i in range(200)])
tables["prod_catalog_v1"] = pd.DataFrame([{"item_id": item_ids[i], "sku": skus[i], "base_price": round(random.uniform(15, 300), 2)} for i in range(len(skus))])
tables["inv_warehouse_stock"] = pd.DataFrame([{"stock_row_id": i, "wh_id": "WH-01", "product_code": random.choice(skus).replace("-", "") if i % 2 == 0 else random.choice(skus), "on_hand_qty": random.randint(0, 500)} for i in range(80)])
tables["shipments_dispatch"] = pd.DataFrame([{"ship_id": f"SHP-{i}", "order_ref": random.choice(order_nos).replace("ORD-", ""), "carrier_cd": "FEDEX"} for i in range(100)])

# Billing & Finance (6 tables)
tables["bill_invoices_issued"] = pd.DataFrame([{"inv_id": inv_ids[i], "billed_id": random.choice(order_nos) if i % 2 == 0 else random.choice(sub_ids), "billed_to_id": random.choice(acct_ids), "billed to": f"Enterprise Corp {random.choice(acct_ids)}", "gross_total": round(random.uniform(50, 5000), 2), "inv_date": dirty_date()} for i in range(len(inv_ids))])
tables["bill_invoice_lines"] = pd.DataFrame([{"inv_line_pk": i, "invoice_num": random.choice(inv_ids), "sku_ref": random.choice(skus), "line_amt": round(random.uniform(10, 1000), 2)} for i in range(250)])
tables["pay_transactions_gateway"] = pd.DataFrame([{"txn_id": txn_ids[i], "inv_ref": random.choice(inv_ids), "payer_id": random.choice(acct_ids), "settled_amt_cents": random.randint(5000, 500000)} for i in range(len(txn_ids))])
tables["sub_plans_recurring"] = pd.DataFrame([{"sub_id": sub_ids[i], "acct_ref": random.choice(acct_ids), "billed_to_id": random.choice(contact_pks), "mrr_val": random.choice([99.0, 499.0])} for i in range(len(sub_ids))])
tables["credit_notes_refunds"] = pd.DataFrame([{"cn_id": f"CN-{i}", "orig_billed_id": random.choice(inv_ids), "refund_amt": round(random.uniform(10, 500), 2)} for i in range(50)])
tables["tax_ledger_recon"] = pd.DataFrame([{"tax_entry_id": i, "doc_id": random.choice(inv_ids), "billed_id": f"TAX-REG-{1000 + i}", "tax_rate_pct": random.choice([0.18, 18.0])} for i in range(100)])

for name, df in tables.items():
    df.to_csv(f"data/{name}.csv", index=False)

print(f"Generated {len(tables)} tables inside spider2-synapse-data/data/")