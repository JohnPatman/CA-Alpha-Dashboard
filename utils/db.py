"""
utils/db.py
-----------
Shared database helpers for the CA Alpha Dashboard.
"""
import sqlite3
import pandas as pd
from datetime import date

DB = "data/events.db"

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def days_to(date_str):
    """Days from today to a date string. Negative = past."""
    if not date_str:
        return None
    try:
        return int((date.fromisoformat(date_str) - date.today()).days)
    except:
        return None

def traffic_light(days):
    """Return emoji + label based on days to deadline."""
    if days is None:
        return "⚪", "No deadline"
    if days < 0:
        return "⚫", "Passed"
    if days <= 3:
        return "🔴", f"{days}d"
    if days <= 7:
        return "🟠", f"{days}d"
    if days <= 14:
        return "🟡", f"{days}d"
    return "🟢", f"{days}d"

def get_live_events(filters=None):
    """
    Return all LIVE + UPCOMING events joined with any available detail.
    Optional filters dict: {status, event_type, event_category, country}
    """
    conn = get_conn()

    where = ["e.status IN ('LIVE','UPCOMING')"]
    params = []

    if filters:
        if filters.get("status") and filters["status"] != "All":
            where.append("e.status = ?")
            params.append(filters["status"])
        if filters.get("event_type") and filters["event_type"] != "All":
            where.append("e.event_type = ?")
            params.append(filters["event_type"])
        if filters.get("event_category") and filters["event_category"] != "All":
            where.append("e.event_category = ?")
            params.append(filters["event_category"])
        if filters.get("country") and filters["country"] != "All":
            where.append("e.country = ?")
            params.append(filters["country"])

    sql = f"""
        SELECT
            e.event_id,
            e.ticker,
            e.company_name,
            e.country,
            e.currency,
            e.event_type,
            e.event_category,
            e.status,
            e.announcement_date,
            e.ex_date,
            e.record_date,
            e.election_deadline,
            e.payment_date,
            e.notes,
            e.source_url,
            -- scrip / fx fields
            s.cash_amount,
            s.cash_currency,
            s.scrip_issue_price,
            s.dividend_currency_opts,
            s.company_fx_rate,
            s.market_fx_rate,
            s.fx_arbitrage_pct,
            s.election_default,
            s.optimal_election,
            s.scrip_discount_pct,
            s.withholding_tax_pct,
            -- rights fields
            r.rights_ratio,
            r.subscription_price,
            r.current_price,
            r.terp,
            r.nil_paid_value,
            r.discount_to_terp_pct,
            r.underwriter,
            r.gross_proceeds_mn,
            -- tender fields
            t.tender_type,
            t.tender_price,
            t.tender_price_low,
            t.tender_price_high,
            t.premium_to_mkt_pct,
            t.max_value_mn,
            t.proration_expected,
            t.estimated_proration_pct,
            t.odd_lot_threshold,
            t.odd_lot_guaranteed,
            -- merger fields
            m.acquirer,
            m.consideration_type,
            m.cash_per_share,
            m.spread_to_terms_pct,
            m.break_risk,
            m.regulatory_status,
            m.court_sanction_date,
            -- split fields
            sp.split_ratio,
            sp.split_type,
            -- spinoff fields
            so.spinoff_name,
            so.spinoff_ticker,
            so.distribution_ratio
        FROM events e
        LEFT JOIN scrip_details s  ON e.event_id = s.event_id
        LEFT JOIN rights_details r ON e.event_id = r.event_id
        LEFT JOIN tender_details t ON e.event_id = t.event_id
        LEFT JOIN merger_details m ON e.event_id = m.event_id
        LEFT JOIN split_details sp ON e.event_id = sp.event_id
        LEFT JOIN spinoff_details so ON e.event_id = so.event_id
        WHERE {" AND ".join(where)}
        ORDER BY
            CASE e.status WHEN 'LIVE' THEN 0 ELSE 1 END,
            e.election_deadline ASC NULLS LAST,
            e.ex_date ASC NULLS LAST
    """

    df = pd.read_sql(sql, conn, params=params)
    conn.close()

    # Compute days columns
    df["days_to_deadline"] = df["election_deadline"].apply(days_to)
    df["days_to_ex"]       = df["ex_date"].apply(days_to)
    df["days_to_payment"]  = df["payment_date"].apply(days_to)

    return df

def get_filter_options():
    """Return unique values for filter dropdowns."""
    conn = get_conn()
    c = conn.cursor()
    types      = [r[0] for r in c.execute("SELECT DISTINCT event_type FROM events ORDER BY event_type")]
    categories = [r[0] for r in c.execute("SELECT DISTINCT event_category FROM events ORDER BY event_category")]
    countries  = [r[0] for r in c.execute("SELECT DISTINCT country FROM events ORDER BY country")]
    statuses   = ["LIVE", "UPCOMING", "CLOSED"]
    conn.close()
    return types, categories, countries, statuses
