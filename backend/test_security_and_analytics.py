import sys
from datetime import datetime, timedelta

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from fastapi.testclient import TestClient

from auth import ADMIN_MASTER_PIN, FAILED_ATTEMPTS
from database import Base, SessionLocal, engine
from main import app, expire_ended_campaigns
from models import Billboard, ClickLog, SpotlightCard, StoreOffer
from seed import seed_database


def run_milestone3_tests():
    print("==================================================")
    print("STEP 1: PREPARING DATABASE TABLES & SEED")
    print("==================================================")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)

    client = TestClient(app)

    print("\n==================================================")
    print("STEP 2: ROUTE GUARD & 401 UNAUTHORIZED TEST")
    print("==================================================")
    # Calling admin overview without any auth header or cookie
    res_unauth = client.get("/api/v1/admin/overview")
    print(f"GET /api/v1/admin/overview without token: status {res_unauth.status_code}")
    assert res_unauth.status_code == 401, f"Expected 401, got {res_unauth.status_code}"
    print("✓ 401 Unauthorized successfully enforced on admin routes!")

    print("\n==================================================")
    print("STEP 3: BRUTE-FORCE LOCKOUT & LOGIN TEST")
    print("==================================================")
    # Clear test client IP in tracking dict
    test_ip = "testclient"
    FAILED_ATTEMPTS.pop(test_ip, None)

    # 1. First 4 failed attempts return 401
    for attempt in range(1, 5):
        res_fail = client.post("/api/v1/admin/login", json={"pin": f"wrong_{attempt}"})
        print(f"Attempt {attempt}/5 with wrong PIN: status {res_fail.status_code}")
        assert res_fail.status_code == 401

    # 2. 5th failed attempt activates 429 lockout
    res_lock = client.post("/api/v1/admin/login", json={"pin": "wrong_5"})
    print(f"Attempt 5/5 with wrong PIN: status {res_lock.status_code}")
    assert res_lock.status_code == 429
    assert "locked for 30 minutes" in res_lock.json()["detail"].lower()
    print("✓ 5-Attempt brute-force lockout (429) verified!")

    # Reset IP lockout for valid login test
    FAILED_ATTEMPTS.pop(test_ip, None)

    # 3. Successful login with Master PIN 2026
    res_login = client.post("/api/v1/admin/login", json={"pin": ADMIN_MASTER_PIN})
    print(f"POST /api/v1/admin/login with '{ADMIN_MASTER_PIN}': status {res_login.status_code}")
    assert res_login.status_code == 200
    token_data = res_login.json()
    assert "access_token" in token_data
    token = token_data["access_token"]
    print(f"✓ Valid JWT Token issued: {token[:20]}...")

    # 4. Access admin overview using Authorization: Bearer <token>
    auth_headers = {"Authorization": f"Bearer {token}"}
    res_auth = client.get("/api/v1/admin/overview", headers=auth_headers)
    print(f"GET /api/v1/admin/overview with Bearer token: status {res_auth.status_code}")
    assert res_auth.status_code == 200
    assert len(res_auth.json()["billboards"]) > 0
    print("✓ Authorized access verified!")

    # 5. Access admin overview using dev X-Admin-Pin header
    res_pin_header = client.get("/api/v1/admin/overview", headers={"X-Admin-Pin": ADMIN_MASTER_PIN})
    print(f"GET /api/v1/admin/overview with X-Admin-Pin: status {res_pin_header.status_code}")
    assert res_pin_header.status_code == 200
    print("✓ Dev X-Admin-Pin header bypass verified!")

    print("\n==================================================")
    print("STEP 4: OUTBOUND /go/ REDIRECT & CLICK TRACKING")
    print("==================================================")
    offer = db.query(StoreOffer).first()
    initial_offer_clicks = offer.clicks

    # Outbound click on offer
    res_go_offer = client.get(f"/go/offer/{offer.id}?format=json", headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0)"})
    print(f"GET /go/offer/{offer.id}?format=json: status {res_go_offer.status_code}")
    assert res_go_offer.status_code == 200
    db.refresh(offer)
    print(f"  - Offer clicks: {initial_offer_clicks} -> {offer.clicks}")
    assert offer.clicks == initial_offer_clicks + 1

    # Outbound click on billboard
    billboard = db.query(Billboard).first()
    initial_bb_clicks = billboard.clicks
    res_go_bb = client.get(f"/go/billboard/{billboard.id}?format=json")
    print(f"GET /go/billboard/{billboard.id}?format=json: status {res_go_bb.status_code}")
    assert res_go_bb.status_code == 200
    db.refresh(billboard)
    print(f"  - Billboard clicks: {initial_bb_clicks} -> {billboard.clicks}")
    assert billboard.clicks == initial_bb_clicks + 1

    # Verify ClickLog rows created
    recent_logs = db.query(ClickLog).order_by(ClickLog.id.desc()).limit(2).all()
    print(f"  - Logged entries in click_logs: {len(recent_logs)}")
    assert len(recent_logs) >= 2
    assert recent_logs[1].device_type == "mobile"  # Mobile iPhone user agent test
    print("✓ Click logging and device detection verified!")

    print("\n==================================================")
    print("STEP 5: SPONSOR ROI & 1-CLICK WHATSAPP REPORT API")
    print("==================================================")
    res_sponsors = client.get("/api/v1/admin/analytics/sponsors", headers=auth_headers)
    print(f"GET /api/v1/admin/analytics/sponsors: status {res_sponsors.status_code}")
    assert res_sponsors.status_code == 200
    sponsor_data = res_sponsors.json()
    assert len(sponsor_data["campaigns"]) > 0
    first_camp = sponsor_data["campaigns"][0]
    print(f"  - Brand: {first_camp['brand_name']} | Slot: {first_camp['tier']} | CTR: {first_camp['ctr_percent']}%")
    print(f"  - WhatsApp Report:\n    {first_camp['whatsapp_report_text']}")
    assert "JaChai Ad Performance" in first_camp["whatsapp_report_text"]
    assert "Direct Store Clicks" in first_camp["whatsapp_report_text"]
    print("✓ 1-Click WhatsApp report formatting verified!")

    print("\n==================================================")
    print("STEP 6: CAMPAIGN AUTO-EXPIRY GUARD")
    print("==================================================")
    # Create an expired billboard campaign
    yesterday = (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d")
    expired_bb = Billboard(
        sponsor_en="EXPIRED BRAND CAMPAIGN",
        sponsor_bn="মেয়াদোত্তীর্ণ ক্যাম্পেইন",
        headline_en="FLASH SALE ENDED",
        headline_bn="ফ্ল্যাশ সেল শেষ",
        category_badge="Test",
        starting_price=500,
        image_url="/images/old-money-shirt.jpg",
        target_url="/",
        campaign_start="2026-09-01",
        campaign_end=yesterday,
        is_active=True,
        impressions=1000,
        clicks=50,
        display_order=99
    )
    db.add(expired_bb)
    db.commit()
    db.refresh(expired_bb)
    print(f"Created test billboard #{expired_bb.id} with campaign_end={expired_bb.campaign_end}, is_active={expired_bb.is_active}")

    # Run auto-expiry guard
    deactivated = expire_ended_campaigns(db)
    print(f"expire_ended_campaigns() deactivated {deactivated} campaign(s)")
    db.refresh(expired_bb)
    print(f"Test billboard #{expired_bb.id} is_active is now: {expired_bb.is_active}")
    assert expired_bb.is_active is False
    print("✓ Campaign auto-expiry guard verified!")

    db.close()
    print("\n==================================================")
    print("ALL MILESTONE 3 TESTS PASSED SUCCESSFULLY! (100% OK)")
    print("==================================================")


if __name__ == "__main__":
    run_milestone3_tests()

