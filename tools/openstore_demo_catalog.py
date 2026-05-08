#!/usr/bin/env python3
"""
Static demo catalog for Springbrand OpenStore TG demos.

Simulates merchant-side agent payloads that would normally come from A2A.
Meowant entries include a snapshot of official product-page data verified on
2026-04-23 so TG demos can show real images and concrete specifications.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

MEOWANT_SNAPSHOT_DATE = "2026-04-23"


def _meowant_source(product_url: str, image_url: str) -> Dict[str, str]:
    return {
        "type": "official_product_page_snapshot",
        "verified_on": MEOWANT_SNAPSHOT_DATE,
        "product_url": product_url,
        "image_url": image_url,
    }

MERCHANTS: Dict[str, Dict[str, Any]] = {
    "meowant": {
        "slug": "meowant",
        "display_name": "Meowant",
        "site": "https://meowant.com",
        "category": "smart_pet_appliances",
        "tagline": "让养宠更省心：猫砂清洁、饮水、理毛与远程看护。",
        "policies": {
            "warranty_months": 24,
            "returns_days": 30,
            "support_channels": ["email", "app", "amazon_storefront"],
        },
        "differentiators": [
            "易拆洗结构，日常清洁更省心",
            "猫砂盆、饮水机和理毛设备覆盖居家高频护理场景",
            "静音水泵与防干烧逻辑，夜间场景友好",
        ],
        "products": [
            {
                "sku": "MW-LITTER-ULTRA",
                "name": "Meowant Self-Cleaning Cat Litter Box - MW-SC02 (White)",
                "name_zh": "自清洁猫砂盆 MW-SC02（白色）",
                "price_usd": 219.99,
                "compare_at_price_usd": 399.99,
                "price_display": "$219.99",
                "highlights": [
                    "75L 如厕空间，开放式大入口，适合 3.3-22 lb 猫咪",
                    "6.8 英寸低入口 + 9 组安全传感器，兼顾老年猫和短腿猫",
                    "自动清理、除味封闭仓和约 38dB 低噪运行，适合居家夜间场景",
                ],
                "keywords": [
                    "猫砂盆", "自动猫砂盆", "litter box", "铲屎", "除臭", "猫厕所",
                    "易打理", "抽拉", "静音", "声音小", "噪音小", "空间大", "大空间", "多猫",
                    "75l", "38db", "低入口", "老年猫", "传感器", "app", "健康监测",
                ],
                "image_url": "https://cdn.shopify.com/s/files/1/0697/3466/2441/files/6391ace427ade714b70fb966024ae804.jpg?v=1776417124",
                "product_url": "https://meowant.com/products/meowant-self-cleaning-cat-litter-box-mw-sc02-white",
                "specifications": [
                    {"label": "如厕空间", "value": "75L"},
                    {"label": "适用体重", "value": "3.3-22 lb"},
                    {"label": "入口高度", "value": "6.8 in"},
                    {"label": "噪音", "value": "38dB"},
                    {"label": "安全结构", "value": "9 组传感器 + anti-pinch"},
                    {"label": "猫砂兼容", "value": "结团猫砂，颗粒长度 <15mm"},
                    {"label": "App", "value": "支持最多 6 只猫的体重/活动监测"},
                ],
                "source": _meowant_source(
                    "https://meowant.com/products/meowant-self-cleaning-cat-litter-box-mw-sc02-white",
                    "https://cdn.shopify.com/s/files/1/0697/3466/2441/files/6391ace427ade714b70fb966024ae804.jpg?v=1776417124",
                ),
            },
            {
                "sku": "MW-LITTER-STEEL",
                "name": "Meowant Stainless Steel Cat Litter Box - LB02",
                "name_zh": "不锈钢猫砂盆 LB02",
                "price_usd": 79.99,
                "compare_at_price_usd": 129.99,
                "price_display": "$79.99",
                "highlights": [
                    "24 x 16 x 18 in 大尺寸盆体，81L 容量，最多可装约 20L 猫砂",
                    "3 合 1 可拆结构，可切换半封闭/全封闭形态",
                    "12 英寸高边防漏，不锈钢盆体不易挂味，标称寿命可达 5 年",
                ],
                "keywords": [
                    "猫砂盆", "不锈钢猫砂盆", "stainless", "高边", "防漏", "大猫", "多猫",
                    "81l", "20l", "半封闭", "全封闭", "易清洗", "除味", "开放式",
                ],
                "image_url": "https://cdn.shopify.com/s/files/1/0697/3466/2441/files/meowant-stainless-steel-cat-litter-box-lb02-540412.jpg?v=1748571235",
                "product_url": "https://meowant.com/products/meowant-stainless-cat-litter-box-mw-lb02",
                "specifications": [
                    {"label": "尺寸", "value": "24 x 16 x 18 in"},
                    {"label": "容量", "value": "81L"},
                    {"label": "可装猫砂", "value": "最多约 20L"},
                    {"label": "结构", "value": "3-in-1 可拆，支持半封闭/全封闭"},
                    {"label": "高边", "value": "12 in 防漏侧边"},
                    {"label": "材质", "value": "不锈钢，防刮防锈，不易残留异味"},
                    {"label": "官方说明", "value": "成人猫单猫场景最长约 30 天补砂周期"},
                ],
                "source": _meowant_source(
                    "https://meowant.com/products/meowant-stainless-cat-litter-box-mw-lb02",
                    "https://cdn.shopify.com/s/files/1/0697/3466/2441/files/meowant-stainless-steel-cat-litter-box-lb02-540412.jpg?v=1748571235",
                ),
            },
            {
                "sku": "MW-FOUNTAIN-UV",
                "name": "MeoWant Wireless Pet Water Fountain",
                "name_zh": "无线宠物饮水机",
                "price_usd": 29.99,
                "price_display": "$29.99",
                "highlights": [
                    "2.2L 容量，杯体尺寸 6.81 x 6.81 x 5.31 in",
                    "电源与水箱分离的无线结构，清洗和加水不用拔线",
                    "约 30dB 低噪运行，滤芯为离子交换树脂 + 活性炭组合",
                ],
                "keywords": [
                    "饮水机", "饮水", "滤芯", "水泵", "fountain", "静音", "易清洗", "清洗",
                    "2.2l", "30db", "无线", "bpa-free", "活性炭", "树脂滤芯",
                ],
                "image_url": "https://cdn.shopify.com/s/files/1/0697/3466/2441/files/meowant-wireless-pet-water-fountain-377853.png?v=1748571246",
                "product_url": "https://meowant.com/products/cat-water-fountain",
                "specifications": [
                    {"label": "容量", "value": "2.2L"},
                    {"label": "尺寸", "value": "6.81 x 6.81 x 5.31 in"},
                    {"label": "材质", "value": "BPA-Free"},
                    {"label": "噪音", "value": "30dB"},
                    {"label": "过滤", "value": "离子交换树脂 + 活性炭"},
                    {"label": "结构", "value": "无线泵 + 分离式供电底座"},
                ],
                "source": _meowant_source(
                    "https://meowant.com/products/cat-water-fountain",
                    "https://cdn.shopify.com/s/files/1/0697/3466/2441/files/meowant-wireless-pet-water-fountain-377853.png?v=1748571246",
                ),
            },
            {
                "sku": "MW-GROOM-AIR",
                "name": "MeoWant Pet Grooming Kit - PV01",
                "name_zh": "宠物理毛套装 PV01",
                "price_usd": 129.99,
                "compare_at_price_usd": 149.99,
                "price_display": "$129.99",
                "highlights": [
                    "5 合 1 工具组合，含梳毛刷、脱毛刷、电推剪和缝隙清洁头",
                    "3 档吸力，官方标称可带走 99% 宠物浮毛",
                    "3.2L 集尘杯 + 2.5 小时续航推剪，附 4 个长度限位梳",
                ],
                "keywords": [
                    "理毛", "吸毛", "梳毛", "groom", "掉毛", "低噪", "可水洗",
                    "5合1", "3档吸力", "3.2l", "2.5小时", "推剪", "长毛", "短毛",
                ],
                "image_url": "https://cdn.shopify.com/s/files/1/0697/3466/2441/files/meowant-pet-grooming-kit-pv01-469711.png?v=1748571245",
                "product_url": "https://meowant.com/products/dog-grooming-kit",
                "specifications": [
                    {"label": "工具数", "value": "5-in-1"},
                    {"label": "吸力", "value": "3 档"},
                    {"label": "集尘杯", "value": "3.2L"},
                    {"label": "推剪续航", "value": "满电约 2.5 小时"},
                    {"label": "限位梳", "value": "1/8, 1/4, 3/8, 1/2 in"},
                    {"label": "整机尺寸", "value": "8.7 x 7 x 13 in"},
                    {"label": "重量", "value": "10.2 lb"},
                ],
                "source": _meowant_source(
                    "https://meowant.com/products/dog-grooming-kit",
                    "https://cdn.shopify.com/s/files/1/0697/3466/2441/files/meowant-pet-grooming-kit-pv01-469711.png?v=1748571245",
                ),
            },
            {
                "sku": "MW-CAM-TREAT",
                "name": "Meowant Dog Treat Dispenser with 2K Camera",
                "name_zh": "2K 看护零食机",
                "price_usd": 139.00,
                "compare_at_price_usd": 199.00,
                "price_display": "$139.00",
                "highlights": [
                    "2K 超清实时画面 + 红外夜视，支持远程看护",
                    "零食投喂 + 双向语音，适合缓解分离焦虑",
                    "支持 2.4GHz/5GHz Wi-Fi、360° 视野和 AI 跟踪",
                ],
                "keywords": [
                    "摄像头", "监控", "camera", "零食互动", "远程", "夜视", "隐私",
                    "2k", "双向语音", "ai tracking", "360", "motion alert", "barking alert",
                ],
                "image_url": "https://cdn.shopify.com/s/files/1/0697/3466/2441/files/meowant-dog-treat-dispenser-with-2k-camera-170643.jpg?v=1748571246",
                "product_url": "https://meowant.com/products/meowant-dog-treat-dispenser-with-2k-camera",
                "specifications": [
                    {"label": "摄像头", "value": "2K Ultra HD + 夜视"},
                    {"label": "交互", "value": "零食投喂 + 双向语音"},
                    {"label": "网络", "value": "2.4GHz / 5GHz Wi-Fi"},
                    {"label": "视野", "value": "360°"},
                    {"label": "智能", "value": "AI Tracking + motion / barking alerts"},
                ],
                "source": _meowant_source(
                    "https://meowant.com/products/meowant-dog-treat-dispenser-with-2k-camera",
                    "https://cdn.shopify.com/s/files/1/0697/3466/2441/files/meowant-dog-treat-dispenser-with-2k-camera-170643.jpg?v=1748571246",
                ),
            },
            {
                "sku": "MW-WATER-STEEL",
                "name": "Meowant Stainless Steel Dog Water Fountain - DF01",
                "name_zh": "不锈钢大容量饮水机 DF01",
                "price_usd": 69.99,
                "compare_at_price_usd": 139.99,
                "price_display": "$69.99",
                "highlights": [
                    "7-13L 可调大容量，适合多宠和大型犬家庭",
                    "304 不锈钢饮水盘，支持洗碗机清洗",
                    "可视水位窗、缺水红灯提醒和防干烧保护更适合长时间使用",
                ],
                "keywords": [
                    "饮水机", "狗饮水机", "大容量", "多宠", "大型犬", "不锈钢", "304",
                    "13l", "3.4gal", "水位窗", "防干烧", "可调高度",
                ],
                "image_url": "https://cdn.shopify.com/s/files/1/0697/3466/2441/files/meowant-stainless-steel-dog-water-fountain-df01-791007.png?v=1748571232",
                "product_url": "https://meowant.com/products/meowant-stainless-steel-dog-water-fountain-df01",
                "specifications": [
                    {"label": "容量", "value": "7-13L / 1.8-3.4 gal"},
                    {"label": "适用场景", "value": "大型犬 / 多宠家庭"},
                    {"label": "材质", "value": "SUS 304 不锈钢"},
                    {"label": "过滤", "value": "多层过滤（椰壳 + 活性炭）"},
                    {"label": "提醒", "value": "可视水位窗 + 缺水红灯"},
                    {"label": "安全", "value": "防干烧保护"},
                ],
                "source": _meowant_source(
                    "https://meowant.com/products/meowant-stainless-steel-dog-water-fountain-df01",
                    "https://cdn.shopify.com/s/files/1/0697/3466/2441/files/meowant-stainless-steel-dog-water-fountain-df01-791007.png?v=1748571232",
                ),
            },
        ],
    },
    "petkit": {
        "slug": "petkit",
        "display_name": "PETKIT 小佩",
        "site": "https://www.petkit.com",
        "category": "smart_pet_appliances",
        "tagline": "宠物智能硬件品牌，覆盖清洁、喂食和饮水等场景。",
        "policies": {
            "warranty_months": 12,
            "returns_days": 15,
            "support_channels": ["app", "retail_partner"],
        },
        "differentiators": [
            "产品线完整，猫砂盆/饮水/喂食联动比较成熟",
            "App 生态和配件体系相对完善",
        ],
        "products": [
            {
                "sku": "PK-LITTER-AIR",
                "name": "PETKIT PuraMax 2",
                "price_cny": 2999,
                "highlights": ["76L 空间，适合多数成年猫", "35dB 静音运行", "三重除味 + App 状态提醒"],
                "keywords": [
                    "猫砂盆", "自动猫砂盆", "litter box", "除臭", "猫厕所", "提醒",
                    "静音", "声音小", "噪音小", "空间大", "大空间", "多猫",
                ],
                "product_url": "https://petkit.com/products/petkit-puramax-2",
            },
            {
                "sku": "PK-FEED-EVO",
                "name": "PETKIT Fresh Element Solo Automatic Feeder",
                "price_cny": 499,
                "highlights": ["3L 容量，支持 App 远程喂食", "双供电方案更稳", "粮桶和食盆拆洗方便"],
                "keywords": ["喂食", "自动喂食器", "猫粮", "feed", "定时"],
                "product_url": "https://petkit.com/products/fresh-element-solo",
            },
            {
                "sku": "PK-FOUNTAIN-3",
                "name": "PETKIT EverSweet Solo 2 Pet Water Fountain",
                "price_cny": 429,
                "highlights": ["2L 容量，适合 1-2 只猫", "无线泵结构，清洗更轻松", "≤25dB 低噪运行"],
                "keywords": ["饮水机", "饮水", "滤芯", "fountain", "入门"],
                "product_url": "https://petkit.com/products/eversweet-solo-2",
            },
        ],
    },
    "homerun": {
        "slug": "homerun",
        "display_name": "霍曼 Homerun",
        "site": "https://www.homerunsmart.com",
        "category": "smart_pet_appliances",
        "tagline": "主打大空间清洁设备和高性价比日常养宠硬件。",
        "policies": {
            "warranty_months": 12,
            "returns_days": 7,
            "support_channels": ["ecommerce_flagship"],
        },
        "differentiators": [
            "猫砂盆空间大，适合多猫家庭",
            "喂食器与饮水机价位相对友好",
        ],
        "products": [
            {
                "sku": "HM-LITTER-LITE",
                "name": "homerunPET Self-cleaning Litter Box CS106",
                "price_cny": 5099,
                "highlights": ["106L 超大空间，更适合多猫或大体型猫", "自动补砂 + 进阶除味方案", "运行噪音约 38.8dB"],
                "keywords": [
                    "猫砂盆", "自动猫砂盆", "litter box", "除味", "铲屎", "入门",
                    "静音", "声音小", "噪音小", "空间大", "大空间", "多猫",
                ],
                "product_url": "https://homerunpet.com/products/cs106-self-cleaning-litter-box",
            },
            {
                "sku": "HM-FEED-AUTO",
                "name": "homerunPET Smart Pet Feeder PF20",
                "price_cny": 699,
                "highlights": ["4L 容量，适合短途外出", "App 定时定量投喂", "防卡粮结构 + 长续航备用电源"],
                "keywords": ["喂食", "自动喂食器", "猫粮", "feed", "性价比"],
                "product_url": "https://homerunpet.com/products/homerunpet-smart-pet-feeders",
            },
            {
                "sku": "HM-WATER-2",
                "name": "homerunPET Wireless Stainless Steel Pet Water Fountain BF25M",
                "price_cny": 499,
                "highlights": ["2.5L 容量 + 不锈钢接水盘", "≤18dB 超静音", "可放洗碗机，清洁负担低"],
                "keywords": ["饮水机", "饮水", "滤芯", "fountain", "入门"],
                "product_url": "https://homerunpet.com/products/homerunpet-cube-pet-water-fountain-bf25m",
            },
        ],
    },
}

FEEDING_KEYWORDS = (
    "喂食", "feed", "定时", "猫粮", "狗粮", "出差", "自动喂", "投喂", "食盆",
)
WATER_KEYWORDS = ("饮水", "喝水", "fountain", "水泵", "滤芯", "uv", "抑菌")
GROOMING_KEYWORDS = ("理毛", "吸毛", "梳毛", "groom", "掉毛", "毛球")
CAMERA_KEYWORDS = ("摄像头", "监控", "camera", "远程看", "宠物摄像", "零食互动")
LITTER_KEYWORDS = (
    "猫砂盆", "自动猫砂盆", "猫厕所", "litter", "litter box", "铲屎", "除臭", "除味",
)
MERCHANT_ALIASES = {
    "meowant": ("meowant", "mewant", "喵万特"),
    "petkit": ("petkit", "小佩"),
    "homerun": ("homerun", "霍曼"),
}
ALL_INTENT_KEYWORDS = (
    FEEDING_KEYWORDS
    + WATER_KEYWORDS
    + GROOMING_KEYWORDS
    + CAMERA_KEYWORDS
    + LITTER_KEYWORDS
)
PRODUCT_KEYWORDS = tuple(
    dict.fromkeys(
        kw.lower()
        for merchant in MERCHANTS.values()
        for product in merchant["products"]
        for kw in product.get("keywords", [])
    )
)


def list_merchants() -> List[Dict[str, Any]]:
    out = []
    for m in MERCHANTS.values():
        out.append(
            {
                "slug": m["slug"],
                "display_name": m["display_name"],
                "site": m["site"],
                "category": m["category"],
                "product_count": len(m["products"]),
            }
        )
    return out


def get_merchant(slug: str) -> Optional[Dict[str, Any]]:
    m = MERCHANTS.get(slug.strip().lower())
    if not m:
        return None
    return {
        "slug": m["slug"],
        "display_name": m["display_name"],
        "site": m["site"],
        "category": m["category"],
        "tagline": m["tagline"],
        "policies": m["policies"],
        "differentiators": m["differentiators"],
        "products": m["products"],
    }


def list_products(slug: str) -> Optional[List[Dict[str, Any]]]:
    m = MERCHANTS.get(slug.strip().lower())
    if not m:
        return None
    return list(m["products"])


def _score_intent(text: str) -> Dict[str, float]:
    """Very small keyword router for demo — not semantic search."""
    t = text.lower()
    scores = {k: 0.0 for k in MERCHANTS}

    def bump(slug: str, w: float) -> None:
        scores[slug] += w

    for kw in FEEDING_KEYWORDS:
        if kw in t:
            bump("meowant", 0.6)
            bump("petkit", 2.4)
            bump("homerun", 2.6)
            break
    for kw in WATER_KEYWORDS:
        if kw in t:
            bump("meowant", 2.8)
            bump("petkit", 2.2)
            bump("homerun", 2.0)
            break
    for kw in GROOMING_KEYWORDS:
        if kw in t:
            bump("meowant", 3.0)
            bump("petkit", 1.2)
            bump("homerun", 1.0)
            break
    for kw in CAMERA_KEYWORDS:
        if kw in t:
            bump("meowant", 2.5)
            bump("petkit", 1.5)
            bump("homerun", 1.0)
            break
    for kw in LITTER_KEYWORDS:
        if kw in t:
            bump("meowant", 3.2)
            bump("petkit", 2.7)
            bump("homerun", 2.3)
            break

    for slug, aliases in MERCHANT_ALIASES.items():
        if any(alias in t for alias in aliases):
            bump(slug, 1.8)

    if sum(scores.values()) == 0:
        scores["meowant"] = 1.0
        scores["petkit"] = 1.0
        scores["homerun"] = 1.0
    return scores


def _product_search_blob(product: Dict[str, Any]) -> str:
    spec_bits = [
        f"{spec.get('label', '')} {spec.get('value', '')}"
        for spec in product.get("specifications", [])
    ]
    return " ".join(
        [
            str(product.get("name", "")),
            str(product.get("name_zh", "")),
            " ".join(str(h) for h in product.get("highlights", [])),
            " ".join(str(k) for k in product.get("keywords", [])),
            " ".join(spec_bits),
        ]
    ).lower()


def _extract_query_terms(text: str) -> Tuple[List[str], List[str]]:
    """Extract phrase keywords and freeform tokens for product matching."""
    t = text.lower()
    phrase_terms: List[str] = []
    for kw in ALL_INTENT_KEYWORDS + PRODUCT_KEYWORDS:
        if kw in t and kw not in phrase_terms:
            phrase_terms.append(kw)

    normalized = t
    for punct in ("，", ",", "。", ".", "？", "?", "！", "!", "/", "：", ":", "；", ";", "（", "）", "(", ")"):
        normalized = normalized.replace(punct, " ")
    token_terms: List[str] = []
    for token in normalized.split():
        if len(token) > 1 and token not in token_terms:
            token_terms.append(token)
    return phrase_terms, token_terms


def _pick_products(slug: str, text: str, limit: int = 3) -> List[Dict[str, Any]]:
    m = MERCHANTS[slug]
    phrase_terms, token_terms = _extract_query_terms(text)
    ranked: List[Tuple[float, Dict[str, Any]]] = []
    for p in m["products"]:
        score = 0.0
        blob = _product_search_blob(p)
        for term in phrase_terms:
            if term in blob:
                score += 2.5
        for token in token_terms:
            if token in blob:
                score += 1.0
        ranked.append((score, p))
    ranked.sort(key=lambda x: -x[0])
    positive = [p for score, p in ranked if score > 0]
    if positive:
        return positive[:limit]
    return [p for _, p in ranked[:limit]] or m["products"][:limit]


def _build_meowant_feature_matches(text: str) -> List[Dict[str, Any]]:
    """Return feature-guided Meowant recommendation hints for final synthesis."""
    t = (text or "").lower()
    meowant_products = {p["sku"]: p for p in MERCHANTS["meowant"]["products"]}
    rules = [
        {
            "sku": "MW-LITTER-ULTRA",
            "keywords": ("猫砂盆", "自动猫砂盆", "铲屎", "除臭", "猫厕所", "易打理", "静音", "声音小", "噪音小", "空间大", "大空间"),
            "focus": "猫砂盆、省心清理、除臭、静音和空间",
        },
        {
            "sku": "MW-LITTER-STEEL",
            "keywords": ("不锈钢", "高边", "防漏", "大猫", "多猫", "开放式", "半封闭", "全封闭"),
            "focus": "不锈钢材质、大空间、高边防漏",
        },
        {
            "sku": "MW-FOUNTAIN-UV",
            "keywords": ("饮水", "饮水机", "静音", "滤芯", "易清洗", "清洗", "水泵", "无线", "2.2l"),
            "focus": "安静饮水、清洗方便、滤芯维护",
        },
        {
            "sku": "MW-WATER-STEEL",
            "keywords": ("大容量", "大型犬", "多宠", "不锈钢", "304", "13l", "3.4gal"),
            "focus": "大容量饮水、多宠和大型犬场景",
        },
        {
            "sku": "MW-GROOM-AIR",
            "keywords": ("理毛", "吸毛", "梳毛", "掉毛", "低噪", "可水洗", "推剪"),
            "focus": "掉毛打理、低噪、边梳边吸",
        },
        {
            "sku": "MW-CAM-TREAT",
            "keywords": ("摄像头", "监控", "远程", "夜视", "隐私", "零食互动", "2k", "双向语音", "ai tracking"),
            "focus": "远程看护、互动投喂、隐私挡板",
        },
    ]

    matches: List[Dict[str, Any]] = []
    for rule in rules:
        matched_terms = [kw for kw in rule["keywords"] if kw in t]
        if not matched_terms:
            continue
        product = meowant_products[rule["sku"]]
        matches.append(
            {
                "product_sku": product["sku"],
                "product_name": product.get("name_zh") or product["name"],
                "product_url": product.get("product_url"),
                "image_url": product.get("image_url"),
                "specifications": product.get("specifications", []),
                "matched_terms": matched_terms[:4],
                "focus": rule["focus"],
                "why_it_fits": "；".join(product["highlights"]),
                "merchant_pitch": (
                    f"如果用户在意{rule['focus']}，可以优先推荐 Meowant 的 {product.get('name_zh') or product['name']}，"
                    f"因为它主打 {product['highlights'][0]}、{product['highlights'][1]}。"
                ),
            }
        )
    return matches


def simulate_sp_a2a_roundtrip(user_message: str) -> Dict[str, Any]:
    """
    Pretend to be the OpenStore SP agent coordinating merchant agents.

    Returns a single JSON-serializable object suitable for tool output.
    """
    msg = (user_message or "").strip()
    scores = _score_intent(msg)
    ordered = sorted(scores.keys(), key=lambda s: -scores[s])

    fanout: List[Dict[str, Any]] = []
    for slug in ordered:
        m = MERCHANTS[slug]
        picks = _pick_products(slug, msg, limit=3)
        fanout.append(
            {
                "a2a_channel": f"openstore://merchant-agent/{slug}",
                "merchant_slug": slug,
                "merchant_display_name": m["display_name"],
                "simulated_latency_ms": 35 + 20 * len(fanout),
                "merchant_agent_reply": {
                    "summary": f"{m['display_name']} 根据需求返回的候选商品。",
                    "candidate_products": picks,
                    "policies_echo": m["policies"],
                },
            }
        )

    me = MERCHANTS["meowant"]
    pk = MERCHANTS["petkit"]
    hm = MERCHANTS["homerun"]
    comparison_axes = [
        {
            "axis": "保修",
            "meowant": f"{me['policies']['warranty_months']} 个月",
            "petkit": f"{pk['policies']['warranty_months']} 个月",
            "homerun": f"{hm['policies']['warranty_months']} 个月",
        },
        {
            "axis": "无理由退换窗口",
            "meowant": f"{me['policies']['returns_days']} 天",
            "petkit": f"{pk['policies']['returns_days']} 天",
            "homerun": f"{hm['policies']['returns_days']} 天",
        },
        {
            "axis": "结构/清洁叙事",
            "meowant": me["differentiators"][0],
            "petkit": "配件与 App 生态相对成熟",
            "homerun": "大空间结构适合多猫家庭",
        },
    ]

    primary_merchant = ordered[0] if ordered else "meowant"
    rec_products = _pick_products(primary_merchant, msg, limit=3)
    meowant_spotlight = _pick_products("meowant", msg, limit=3)

    return {
        "demo": True,
        "disclaimer": (
            "本结果为演示：数据来自 hermes-agent 内置静态库，"
            "未发起真实 A2A / 未访问商家实时库存。"
        ),
        "sp_agent": "OpenStore Intent Matcher (Hermes demo tool)",
        "parsed_user_intent": msg[:500],
        "intent_scores": scores,
        "simulated_fanout_to_merchant_agents": fanout,
        "cross_merchant_comparison": comparison_axes,
        "recommendation": {
            "primary_merchant": primary_merchant,
            "rationale": (
                "优先选择和用户需求关键词匹配度最高的商品，再结合保修、退换窗口和清洁便利度给出推荐。"
            ),
            "recommended_products": rec_products,
            "meowant_spotlight_products": meowant_spotlight,
            "meowant_feature_matches": _build_meowant_feature_matches(msg),
        },
    }
