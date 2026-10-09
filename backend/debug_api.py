import asyncio
import httpx
from httpx import ASGITransport
import sys

async def main():
    from app.main import app
    from app.db.init_db import init_db
    await init_db()
    
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Login clinician
        res = await client.post(
            "/api/v1/auth/login",
            json={"username": "clinician", "password": "ClinovaDemo2026!"},
        )
        if res.status_code != 200:
            print(f"Login clinician failed: {res.status_code}")
            sys.exit(1)
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Translate standalone
        res2 = await client.post("/api/v1/translation/translate", json={
            "text": "छाती में दर्द",
            "source_lang": "hi",
            "target_lang": "en"
        }, headers=headers)
        
        if res2.status_code != 200:
            print(f"Translate failed: {res2.status_code}")
            sys.exit(1)
        print("Translate success")
        
        # Login patient
        res3 = await client.post(
            "/api/v1/auth/login",
            json={"username": "patient", "password": "ClinovaDemo2026!"},
        )
        if res3.status_code != 200:
            print(f"Login patient failed: {res3.status_code}")
            sys.exit(1)
        patient_token = res3.json()["access_token"]
        patient_headers = {"Authorization": f"Bearer {patient_token}"}
        
        # Intake submit
        intake_res = await client.post("/api/v1/intake/submit", json={
            "chief_complaint": "chest pain",
            "symptoms": ["pain"],
            "facility_id": "FAC-DH-04",
            "pathway": "REGULAR",
            "consent_status": "GRANTED"
        }, headers=patient_headers)
        
        if intake_res.status_code != 200:
            print(f"Intake submit failed: {intake_res.status_code} {intake_res.text}")
            sys.exit(1)
        case_id = intake_res.json()["case_id"]
        print("Intake success, case_id:", case_id)
        
        # Translate case entity
        res4 = await client.post(f"/api/v1/translation/cases/{case_id}/translations", json={
            "text": "सांस लेने में तकलीफ",
            "source_lang": "hi",
            "target_lang": "en",
            "entity_type": "Case",
            "entity_id": case_id
        }, headers=headers)
        if res4.status_code != 200:
            print(f"Translate case entity failed: {res4.status_code} {res4.text}")
            sys.exit(1)
        print("Translate case entity success")

        res5 = await client.get(f"/api/v1/translation/cases/{case_id}/translations", headers=headers)
        if res5.status_code != 200:
            print(f"List translations failed: {res5.status_code}")
            sys.exit(1)
        list_data = res5.json()
        print("List translations success")
        if not list_data:
            print("List translations empty")
            sys.exit(1)
        translation_id = list_data[0]["id"]
        
        # Verify translation
        res6 = await client.post(f"/api/v1/translation/cases/{case_id}/translations/{translation_id}/verify", json={
            "is_correct": True
        }, headers=headers)
        if res6.status_code != 200:
            print(f"Verify failed: {res6.status_code} {res6.text}")
            sys.exit(1)
        print("Verify success")
        
        # Correct translation
        res7 = await client.post(f"/api/v1/translation/cases/{case_id}/translations/{translation_id}/correct", json={
            "corrected_text": "severe shortness of breath"
        }, headers=headers)
        if res7.status_code != 200:
            print(f"Correct failed: {res7.status_code} {res7.text}")
            sys.exit(1)
        print("Correct success")

if __name__ == "__main__":
    asyncio.run(main())
