import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect("backend/jachai.db")
c = conn.cursor()

# Remove existing gold/oil if any
c.execute("DELETE FROM ticker_ads WHERE text_en LIKE '%GOLD%' OR text_en LIKE '%OIL%'")

# Ensure other items have higher priority order
c.execute("UPDATE ticker_ads SET priority_order = priority_order + 5")

# Insert 1. Live Gold Index
c.execute("""
INSERT INTO ticker_ads (text_en, text_bn, is_active, glide_speed_sec, priority_order)
VALUES (?, ?, 1, 55, 1)
""", (
    "BAJUS LIVE GOLD INDEX: 22K Hallmarked Gold: ৳1,18,450 / Bhori (11.664g) · 24K: ৳1,29,200 · Live Rate Tracked Across Verified Jewellers",
    "বাজুস লাইভ গোল্ড ইনডেক্স: ২২ ক্যারেট হলমার্কযুক্ত স্বর্ণের রেট: ৳১,১৮,৪৫০ / ভরি (১১.৬৬৪ গ্রাম) · ২৪ ক্যারেট: ৳১,২৯,২০০ · ভেরিফাইড জুয়েলার্স লাইভ রেট ট্র্যাকড"
))

# Insert 2. Live Oil Price Index (Right alongside Gold Price)
c.execute("""
INSERT INTO ticker_ads (text_en, text_bn, is_active, glide_speed_sec, priority_order)
VALUES (?, ?, 1, 55, 2)
""", (
    "LIVE OIL PRICE INDEX: Bottled Soybean Oil: ৳175 / Litre (5L Jar ৳850) · Pure Mustard Oil: ৳260 / L · Fuel Octane: ৳125 / L · Diesel: ৳105 / L",
    "লাইভ তেল বাজার দর: বোতলজাত সয়াবিন তেল: ৳১৭৫ / লিটার (৫ লিটার ৳৮৫০) · খাঁটি সরিষার তেল: ৳২৬০ / লিটার · অকটেন: ৳১২৫ · ডিজেল: ৳১০৫ / লিটার"
))

conn.commit()
print("[✓] Successfully inserted Gold & Oil tickers into database:")
for r in conn.execute("SELECT id, priority_order, text_en FROM ticker_ads ORDER BY priority_order ASC").fetchall():
    print(f"  ID: {r[0]} | Priority: {r[1]} | {r[2][:70]}...")

