import httpx
import os
import traceback

async def analyze_web_vitals(url:str):
    api_key = os.getenv("GOOGLE_PAGESPEED_API_KEY","")
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&category=PERFORMANCE"
    if api_key:
        api_url += f"&key={api_key}"
    try:
        async with httpx.AsyncClient(timeout = 90) as client:
            response = await client.get(api_url)
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", {}).get("message", f"Unknown API error")
                except Exception:
                    error_message = response.text
                return{
                    "status": "error",
                    "message": f"Google Api returned status code {response.status_code} {error_message}"
                }
            data = response.json()
            loading_experience = data.get("loadingExperience",{})
            metrics = loading_experience.get("metrics",{})
            field_lcp = metrics.get("LARGEST_CONTENTFUL_PAINT_MS",{}).get("percentile")
            field_cls = metrics.get("CUMULATIVE_LAYOUT_SHIFT_SCORE",{}).get("percentile")
            field_inp = metrics.get("INTERACTION_TO_NEXT_PAINT",{}).get("percentile")

            lighthouse_result = data.get("lighthouseResult",{})
            audits = lighthouse_result.get("audits",{})
            categories = lighthouse_result.get("categories",{})

            performance_score = categories.get("performance", {}).get("score", 0) * 100
            return{
                "status":"success",
                "performance_score": int(performance_score),
                "field_data":{
                    "lcp_ms":field_lcp,
                    "cls": float(field_cls) / 100 if field_cls else None,
                    "inp_ms": field_inp 
                },
                "lab_data":{
                    "lcp_ms":audits.get("largest-contentful-paint",{}).get("numericValue"),
                    "cls":audits.get("cumulative-layout-shift",{}).get("numericValue"),
                    "tbt_ms": audits.get("total-blocking-time",{}).get("numericValue")
                }
            }
    except Exception as e:
        print(f"WEB VITALS ERROR: {type(e).__name__} - {str(e)}")
        traceback.print_exc()
        return {"status":"error","message":f"{type(e).__name__}: {str(e)}"}