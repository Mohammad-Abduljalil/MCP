from mcp.server import MCPServer
import httpx

mcp = MCPServer("syp-usd-converter")

# ⚠️ سعر احتياطي (سوق موازي) - حدّثه يدويًا حسب السعر الحالي
FALLBACK_USD_TO_SYP = 13000.0
RATE_API_URL = "https://open.er-api.com/v6/latest/USD"


async def get_usd_to_syp_rate() -> tuple[float, str]:
    """جلب سعر صرف الدولار مقابل الليرة السورية."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(RATE_API_URL)
            resp.raise_for_status()
            data = resp.json()
            rate = data.get("rates", {}).get("SYP")
            if rate:
                return float(rate), "open.er-api.com (السعر الرسمي)"
    except Exception:
        pass
    return FALLBACK_USD_TO_SYP, "سعر احتياطي يدوي (سوق موازي)"


@mcp.tool()
async def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """تحويل العملات بين الليرة السورية (SYP) والدولار الأمريكي (USD).

    Args:
        amount: المبلغ المراد تحويله (رقم موجب).
        from_currency: العملة المصدر: "SYP" أو "USD".
        to_currency: العملة الهدف: "SYP" أو "USD".
    """
    f = from_currency.upper().strip()
    t = to_currency.upper().strip()
    valid = {"SYP", "USD"}

    if f not in valid or t not in valid:
        return {"error": f"عملة غير مدعومة. استخدم إحدى: {valid}"}
    if amount < 0:
        return {"error": "المبلغ يجب أن يكون رقمًا موجبًا."}

    if f == t:
        return {
            "amount": amount, "from": f, "to": t,
            "result": amount, "rate_used": 1.0,
            "rate_source": "نفس العملة",
        }

    usd_to_syp, source = await get_usd_to_syp_rate()

    if f == "USD" and t == "SYP":
        result = amount * usd_to_syp
        rate_used = usd_to_syp
    else:
        result = amount / usd_to_syp
        rate_used = 1 / usd_to_syp

    return {
        "amount": amount,
        "from": f,
        "to": t,
        "result": round(result, 2),
        "rate_used": round(rate_used, 6),
        "rate_source": source,
    }


@mcp.tool()
async def get_exchange_rate() -> dict:
    """يعيد سعر الصرف الحالي بين الدولار الأمريكي والليرة السورية."""
    usd_to_syp, source = await get_usd_to_syp_rate()
    return {
        "usd_to_syp": round(usd_to_syp, 2),
        "syp_to_usd": round(1 / usd_to_syp, 6),
        "rate_source": source,
    }


if __name__ == "__main__":
    mcp.run(transport="sse")