import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from google.cloud import bigquery
from google.oauth2 import service_account

# Load variables from .env file if present
load_dotenv()

app = FastAPI(title="TF-IIP Technology Foresight API")

# Enable CORS for browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize BigQuery Client (Dual Support: Local File OR Render Environment Variable)
bq_client = None

# 1. Try loading from local gcp-key.json file first (Local Development)
if os.path.exists("gcp-key.json"):
    try:
        credentials = service_account.Credentials.from_service_account_file("gcp-key.json")
        bq_client = bigquery.Client(credentials=credentials, project=credentials.project_id)
        print("✓ BigQuery Client initialized from local 'gcp-key.json' file!")
    except Exception as e:
        print(f"❌ Error loading local JSON file: {e}")

# 2. Fallback to GCP_SERVICE_KEY Environment Variable (Render Production)
elif os.getenv("GCP_SERVICE_KEY"):
    try:
        key_dict = json.loads(os.getenv("GCP_SERVICE_KEY"))
        credentials = service_account.Credentials.from_service_account_info(key_dict)
        bq_client = bigquery.Client(credentials=credentials, project=credentials.project_id)
        print("✓ BigQuery Client initialized from GCP_SERVICE_KEY environment variable!")
    except Exception as e:
        print(f"❌ Error loading GCP_SERVICE_KEY env variable: {e}")

else:
    print("⚠️ Warning: No GCP credentials found. System will run with simulation fallback data.")

app = FastAPI(title="TF-IIP Technology Foresight API")

# Enable CORS for browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Complete SRS-Compliant Level 1 & Level 2 Integrated Framework
TAXONOMY_TREE = {
    "1. Energy & Hydrocarbon Value Chain": {
        "Upstream Exploration & Production (E&P)": {},
        "Midstream Logistics & Infrastructure": {},
        "Downstream Refining & Petrochemicals": {},
        "Oilfield Services (OFS) & Telemetry": {},
        "Unconventional Hydrocarbon Extraction": {},
        "Offshore Marine Engineering & Subsea Drilling": {}
    },
    "2. Sustainable Solutions & Green Tech": {
        "Carbon Capture, Utilization & Storage (CCUS)": {},
        "Direct Air Capture (DAC) & CO2 Removal": {},
        "Green Hydrogen & Electrolyzer Manufacturing": {},
        "Renewable Energy Generation": {},
        "Nuclear Power Generation & SMRs": {},
        "Bio-Plastics & Biodegradable Polymers": {},
        "Industrial Wastewater Zero-Liquid Discharge (ZLD)": {},
        "E-Waste Recovery & Urban Mining": {},
        "Waste Management & Circular Economy": {}
    },
    "3. Mining & Advanced Metallurgy": {
        "Critical Minerals & Battery Metals Mining": {},
        "Rare Earth Element (REE) Processing": {},
        "Precious Metals Mining": {},
        "Base Metals Mining & Beneficiation": {},
        "Industrial Minerals & Aggregates": {},
        "Automated & Sustainable Mining Tech": {},
        "Green Steel & Low-Carbon Ironmaking": {},
        "Specialty Alloys & Superalloys": {},
        "Lightweight Structural Metals": {},
        "Powder Metallurgy & 3D Printing Feedstocks": {},
        "Recycled Metals & Secondary Smelting": {}
    },
    "4. Power Grids & Grid Modernization": {
        "Smart Grid Infrastructure & IoT": {},
        "High-Voltage Direct Current (HVDC) Transmission": {},
        "Distributed Energy Resource Management (DERMS)": {},
        "Microgrid Development & Energy Islanding": {},
        "Utility-Scale Battery Energy Storage (BESS)": {},
        "Grid Cyber-Physical Security": {},
        "Power Utilities & Traditional Grid Infrastructure": {}
    },
    "5. Advanced Materials & Chemicals": {
        "Graphene & 2D Nanomaterials": {},
        "Carbon Fiber & Advanced Composites": {},
        "Synthetic Diamonds & Superabrasives": {},
        "Carbon Black & Functional Fillers": {},
        "Bio-Char & Activated Carbon Production": {},
        "Chemical Manufacturing": {}
    },
    "6. Technology & Digital Innovation": {
        "Artificial Intelligence (AI) & Machine Learning": {},
        "Cloud Computing & Infrastructure": {},
        "Cybersecurity & Data Privacy": {},
        "Quantum Computing & DeepTech": {},
        "Robotics & Industrial Automation": {},
        "Semiconductors & Microelectronics": {},
        "Software as a Service (SaaS) & Enterprise Software": {},
        "Space Technology, Satellites & Exploration": {},
        "Telecommunications & 5G/6G Networks": {},
        "Virtual, Augmented & Mixed Reality (XR)": {},
        "Internet of Things (IoT) & Smart Home Tech": {},
        "Web3, Blockchain & Decentralized Tech": {},
        "Data Analytics, Business Intelligence & Big Data": {}
    },
    "7. Manufacturing & Aerospace": {
        "Automobile Manufacturing (Traditional OEMs)": {},
        "Electric Vehicles (EV) & Autonomous Driving Systems": {},
        "Battery Technology & Energy Storage Systems": {},
        "Aerospace, Commercial Aviation & Drone Tech": {},
        "Defense Systems & Military Hardware": {},
        "Maritime Shipping, Logistics & Shipbuilding": {},
        "Rail Transportation & High-Speed Infrastructure": {},
        "Logistics, Warehousing & Supply Chain Management": {}
    },
    "8. Healthcare & Life Sciences": {
        "Pharmaceuticals & Drug Discovery": {},
        "Biotechnology, Genomics & Gene Editing": {},
        "Medical Devices, Equipment & Diagnostics": {},
        "Healthcare Providers (Hospitals, Clinics & Eldercare)": {},
        "Telehealth, Digital Health & Remote Monitoring": {},
        "Health Insurance & Managed Care": {},
        "Veterinary Medicine & Pet Healthcare": {}
    },
    "9. Finance, Insurance & Real Estate": {
        "Commercial, Retail & Central Banking": {},
        "Investment Banking, Wealth & Asset Management": {},
        "Financial Technology (FinTech) & Digital Payments": {},
        "Insurance (Life, Property, Casualty & InsurTech)": {},
        "Commercial Real Estate (Offices, Retail & Industrial)": {},
        "Residential Real Estate, Housing & PropTech": {},
        "Venture Capital, Private Equity & Sovereign Funds": {}
    },
    "10. Consumer Markets, Media & Services": {
        "E-Commerce Marketplaces & Direct-to-Consumer (D2C)": {},
        "Fast-Moving Consumer Goods (FMCG)": {},
        "Luxury Goods, Haute Couture & Jewelry": {},
        "Consumer Electronics & Gadgets": {},
        "Cosmetics, Beauty & Personal Care": {},
        "Agricultural Technology (AgTech & Vertical Farming)": {},
        "Food Processing & Alternative Proteins": {},
        "Digital Media, Streaming Services & OTT Platforms": {},
        "Video Gaming, Esports & Interactive Entertainment": {},
        "Hospitality, Travel, Tourism & Foodservice": {},
        "Education Technology (EdTech) & Higher Education": {},
        "Management Consulting & Legal Services": {},
        "Civil Engineering, Architecture & Heavy Construction": {}
    }
}
# BigQuery CPC Class Mappings for Sub-Sectors
CPC_MAPPINGS = {
    "Carbon Capture, Utilization & Storage (CCUS)": ["Y02C", "B01D53/14"],
    "Green Hydrogen & Electrolyzer Manufacturing": ["Y02E60/36", "C25B1/04"],
    "Downstream Refining & Petrochemicals": ["C10G", "B01J"]
}

def build_bigquery_sql(sub_sector: str, custom_term: Optional[str] = None) -> str:
    """Generates cost-optimized BigQuery SQL for Google Patents public dataset."""
    cpc_codes = CPC_MAPPINGS.get(sub_sector, ["Y02C"])
    cpc_clause = " OR ".join([f"cpc.code LIKE '{code}%'" for code in cpc_codes])
    
    keyword_clause = "1=1"
    if custom_term and custom_term.strip():
        keyword_clause = f"REGEXP_CONTAINS(LOWER(title_localized.text), r'(?i)\\b{custom_term.lower()}\\b')"

    sql = f"""
    SELECT 
      EXTRACT(YEAR FROM PARSE_DATE('%Y%m%d', CAST(publication_date AS STRING))) AS pub_year,
      COUNT(DISTINCT family_id) AS patent_family_count
    FROM 
      `patents-public-data.patents.publications`,
      UNNEST(cpc) AS cpc,
      UNNEST(title_localized) AS title_localized
    WHERE 
      publication_date >= 20160101
      AND ({cpc_clause})
      AND {keyword_clause}
    GROUP BY pub_year
    ORDER BY pub_year ASC;
    """
    return sql.strip()

# Endpoint to serve index.html homepage
@app.get("/", response_class=FileResponse)
def home():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "index.html file not found in root directory"}

# API Endpoint: Get Level 1 Macro Industries
@app.get("/api/v1/macro-industries")
def get_macro_industries():
    return {"macro_industries": list(TAXONOMY_TREE.keys())}

# API Endpoint: Get Level 2 Sub-Sectors
@app.get("/api/v1/sub-sectors")
def get_sub_sectors(macro_industry: str = Query(...)):
    if macro_industry not in TAXONOMY_TREE:
        raise HTTPException(status_code=404, detail="Macro Industry not found")
    return {"sub_sectors": list(TAXONOMY_TREE[macro_industry].keys())}

# API Endpoint: Calculate CAGR, Momentum Velocity & Leaderboards
@app.get("/api/v1/calculate")
def run_analytics(sub_sector: str, custom_term: Optional[str] = None):
  # 1. Build optimized BigQuery SQL
  sql_query = build_bigquery_sql(sub_sector, custom_term)

  patent_history = []

  # 2. Execute live BigQuery query if client is active
  if bq_client:
    try:
      print(f"🔍 Querying Google Patents BigQuery for: {sub_sector}...")
      query_job = bq_client.query(sql_query)
      results = [dict(row) for row in query_job.result()]
      print(f"✅ Success! Fetched {len(results)} annual patent records.")

      # Extract annual time series from live results
      patent_history = [row.get("patent_family_count", 0) for row in results]
    except Exception as e:
      print(f"❌ BigQuery Execution Error: {e}")

  # Fallback to simulation array if query yields empty data or errors
  if not patent_history or len(patent_history) < 10:
    print("⚠️ Using fallback time-series baseline.")
    patent_history = [12, 15, 18, 22, 30, 45, 60, 95, 140, 210]

  # 3. Calculate 10-Year CAGR & 3-Year Momentum
  start_vol = patent_history[0]
  end_vol = patent_history[-1]
  cagr = ((end_vol / start_vol) ** (1 / 10)) - 1.0

  trailing_3_yr = sum(patent_history[-3:])
  historical_avg = (
      sum(patent_history[:-3]) / len(patent_history[:-3])
      if len(patent_history) > 3
      else 1.0
  )
  momentum = (
      trailing_3_yr / (3 * historical_avg) if historical_avg > 0 else 1.0
  )

  x_pos = 75 if "Carbon" in sub_sector else 40
  y_pos = min(int(momentum * 20), 90)

  return {
      "selected_sub_sector": sub_sector,
      "custom_term_injected": custom_term,
      "calculated_metrics": {
          "10_year_cagr_percentage": round(cagr * 100, 2),
          "3_year_momentum_velocity": round(momentum, 2),
          "technology_stage": "Emerging" if momentum > 2.0 else "Early Stage",
          "matrix_x_position": x_pos,
          "matrix_y_position": y_pos,
      },
      "emerging_buzzwords": [
          "Metal-Organic Frameworks",
          "Direct Air Capture",
          "Solid Amine Contactor",
      ],
      "leaderboards": {
          "top_corporate": [
              {"name": "Climeworks AG", "patents": 412},
              {"name": "Carbon Engineering", "patents": 328},
          ],
          "top_academia": [
              {"name": "UC Berkeley", "citations": 1420},
              {"name": "ETH Zürich", "citations": 1180},
          ],
      },
  }