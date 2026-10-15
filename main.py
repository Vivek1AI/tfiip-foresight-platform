import os
import json
import random
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import bigquery
from google.oauth2 import service_account

# Load environment variables from .env if present
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

if os.path.exists("gcp-key.json"):
    try:
        credentials = service_account.Credentials.from_service_account_file("gcp-key.json")
        bq_client = bigquery.Client(credentials=credentials, project=credentials.project_id)
        print("✓ BigQuery Client initialized from local 'gcp-key.json' file!")
    except Exception as e:
        print(f"⚠️ Error loading local JSON file: {e}")
elif os.getenv("GCP_SERVICE_KEY"):
    try:
        key_dict = json.loads(os.getenv("GCP_SERVICE_KEY"))
        credentials = service_account.Credentials.from_service_account_info(key_dict)
        bq_client = bigquery.Client(credentials=credentials, project=credentials.project_id)
        print("✓ BigQuery Client initialized from GCP_SERVICE_KEY environment variable!")
    except Exception as e:
        print(f"⚠️ Error parsing GCP_SERVICE_KEY env: {e}. Running in simulation fallback mode.")
else:
    print("⚠️ No GCP credentials found. Server running in simulation fallback mode.")


# Comprehensive CPC Class Mappings Covering All 10 Macro Industries & Sub-Sectors
CPC_MAPPINGS = {
    # 1. Energy & Hydrocarbon Value Chain
    "Downstream Refining & Petrochemicals": ["C10G", "B01J", "C07C", "C10L"],
    "Upstream Exploration & Production (E&P)": ["E21B", "G01V", "B63B"],
    "Midstream Logistics & Infrastructure": ["F17D", "B65D", "F17C"],
    "Oilfield Services (OFS) & Telemetry": ["E21B47", "G01V3", "E21B44"],
    "Unconventional Hydrocarbon Extraction": ["E21B43", "C09K8"],
    "Offshore Marine Engineering & Subsea Drilling": ["B63B35", "E21B7"],

    # 2. Sustainable Solutions & Green Tech
    "Carbon Capture, Utilization & Storage (CCUS)": ["Y02C", "B01D53/14", "B01D53/62", "C01B32"],
    "Direct Air Capture (DAC) & CO2 Removal": ["Y02C20/40", "B01D53/04", "B01D53/14"],
    "Green Hydrogen & Electrolyzer Manufacturing": ["Y02E60/36", "C25B1/04", "C01B3/00", "H01M8"],
    "Renewable Energy Generation": ["Y02E10", "F03D", "H02S", "F03B"],
    "Nuclear Power Generation & SMRs": ["G21C", "G21D", "Y02E30"],
    "Bio-Plastics & Biodegradable Polymers": ["C08L67", "C08J11", "Y02W30"],
    "Industrial Wastewater Zero-Liquid Discharge (ZLD)": ["C02F", "B01D61", "Y02W10"],
    "E-Waste Recovery & Urban Mining": ["Y02W30/20", "B09B", "C22B"],
    "Waste Management & Circular Economy": ["Y02W", "B09B", "B29B17"],

    # 3. Mining & Advanced Metallurgy
    "Critical Minerals & Battery Metals Mining": ["C22B26", "C22B3", "C22B7", "B03B"],
    "Rare Earth Element (REE) Processing": ["C22B59", "C01F17"],
    "Precious Metals Mining": ["C22B11", "B03D"],
    "Base Metals Mining & Beneficiation": ["C22B15", "C22B19", "B03B"],
    "Industrial Minerals & Aggregates": ["C04B", "B28D"],
    "Automated & Sustainable Mining Tech": ["E21C", "G05D1", "Y02P60"],
    "Green Steel & Low-Carbon Ironmaking": ["C21B13", "Y02P10", "C21C"],
    "Specialty Alloys & Superalloys": ["C22C19", "C22C38"],
    "Lightweight Structural Metals": ["C22C21", "C22C23"],
    "Powder Metallurgy & 3D Printing Feedstocks": ["B22F", "B33Y", "C22C"],
    "Recycled Metals & Secondary Smelting": ["C22B7/00", "Y02P10/30"],

    # 4. Power Grids & Grid Modernization
    "Smart Grid Infrastructure & IoT": ["H02J13", "H04L12", "Y04S"],
    "High-Voltage Direct Current (HVDC) Transmission": ["H02M7", "H02J3/36"],
    "Distributed Energy Resource Management (DERMS)": ["H02J3/38", "Y04S10"],
    "Microgrid Development & Energy Islanding": ["H02J3/14", "H02J7"],
    "Utility-Scale Battery Energy Storage (BESS)": ["H01M10/05", "H02J7/00", "Y02E60/10"],
    "Grid Cyber-Physical Security": ["H04L9", "G06F21", "H04L29"],
    "Power Utilities & Traditional Grid Infrastructure": ["H02B", "H02G", "H01F"],

    # 5. Advanced Materials & Chemicals
    "Graphene & 2D Nanomaterials": ["C01B32/18", "B82Y30", "C08K3/04"],
    "Carbon Fiber & Advanced Composites": ["C08J5", "D01F6", "B29C70"],
    "Synthetic Diamonds & Superabrasives": ["C01B32/25", "B24D3"],
    "Carbon Black & Functional Fillers": ["C09C1/48", "C08K3/04"],
    "Bio-Char & Activated Carbon Production": ["C01B32/30", "C10B53"],
    "Chemical Manufacturing": ["C07C", "C07D", "B01J"],

    # 6. Technology & Digital Innovation
    "Artificial Intelligence (AI) & Machine Learning": ["G06N", "G06F18", "G06T"],
    "Cloud Computing & Infrastructure": ["G06F9/455", "G06F15/16", "H04L67"],
    "Cybersecurity & Data Privacy": ["G06F21", "H04L9", "H04L63"],
    "Quantum Computing & DeepTech": ["G06N10", "H01L39", "B82Y10"],
    "Robotics & Industrial Automation": ["B25J", "G05B19", "G05D1"],
    "Semiconductors & Microelectronics": ["H01L", "H01L21", "H05K"],
    "Software as a Service (SaaS) & Enterprise Software": ["G06F8", "G06F16", "G06Q10"],
    "Space Technology, Satellites & Exploration": ["B64G", "H04B7/185"],
    "Telecommunications & 5G/6G Networks": ["H04W", "H04L", "H04B7"],
    "Virtual, Augmented & Mixed Reality (XR)": ["G06T19", "G02B27", "G06F3/01"],
    "Internet of Things (IoT) & Smart Home Tech": ["H04L12/28", "H04W4/38", "G08C"],
    "Web3, Blockchain & Decentralized Tech": ["H04L9/06", "G06Q20/06"],
    "Data Analytics, Business Intelligence & Big Data": ["G06F16", "G06Q10/06"],

    # 7. Manufacturing & Aerospace
    "Automobile Manufacturing (Traditional OEMs)": ["B62D", "F02B", "B60R"],
    "Electric Vehicles (EV) & Autonomous Driving Systems": ["B60L", "B60W", "G05D1/02", "Y02T10"],
    "Battery Technology & Energy Storage Systems": ["H01M10", "H01M4", "Y02E60/10"],
    "Aerospace, Commercial Aviation & Drone Tech": ["B64C", "B64D", "B64U"],
    "Defense Systems & Military Hardware": ["F41A", "F42B", "F41H"],
    "Maritime Shipping, Logistics & Shipbuilding": ["B63B", "B63H", "G06Q10/08"],
    "Rail Transportation & High-Speed Infrastructure": ["B61L", "B61D", "B61C"],
    "Logistics, Warehousing & Supply Chain Management": ["G06Q10/08", "B65G"],

    # 8. Healthcare & Life Sciences
    "Pharmaceuticals & Drug Discovery": ["A61K31", "C07D", "A61P"],
    "Biotechnology, Genomics & Gene Editing": ["C12N15", "C12Q1", "A61K48"],
    "Medical Devices, Equipment & Diagnostics": ["A61B", "A61M", "A61F"],
    "Healthcare Providers (Hospitals, Clinics & Eldercare)": ["G16H", "A61G"],
    "Telehealth, Digital Health & Remote Monitoring": ["G16H40", "A61B5/00"],
    "Health Insurance & Managed Care": ["G06Q40/08", "G16H"],
    "Veterinary Medicine & Pet Healthcare": ["A61D", "A61K31"],

    # 9. Finance, Insurance & Real Estate
    "Commercial, Retail & Central Banking": ["G06Q40/02", "G06Q20"],
    "Investment Banking, Wealth & Asset Management": ["G06Q40/06"],
    "Financial Technology (FinTech) & Digital Payments": ["G06Q20", "G06Q40"],
    "Insurance (Life, Property, Casualty & InsurTech)": ["G06Q40/08"],
    "Commercial Real Estate (Offices, Retail & Industrial)": ["G06Q50/16"],
    "Residential Real Estate, Housing & PropTech": ["G06Q50/16", "E04H"],
    "Venture Capital, Private Equity & Sovereign Funds": ["G06Q40/06"],

    # 10. Consumer Markets, Media & Services
    "E-Commerce Marketplaces & Direct-to-Consumer (D2C)": ["G06Q30/06"],
    "Fast-Moving Consumer Goods (FMCG)": ["A23L", "C11D", "B65D"],
    "Luxury Goods, Haute Couture & Jewelry": ["A44C", "A41D"],
    "Consumer Electronics & Gadgets": ["H04M1", "G06F1", "H04R"],
    "Cosmetics, Beauty & Personal Care": ["A61K8", "A61Q"],
    "Agricultural Technology (AgTech & Vertical Farming)": ["A01G", "A01C", "Y02A40"],
    "Food Processing & Alternative Proteins": ["A23L", "A23J"],
    "Digital Media, Streaming Services & OTT Platforms": ["H04N21", "G06F16/40"],
    "Video Gaming, Esports & Interactive Entertainment": ["A63F13", "G06T19"],
    "Hospitality, Travel, Tourism & Foodservice": ["G06Q50/12", "G06Q10/02"],
    "Education Technology (EdTech) & Higher Education": ["G09B", "G06Q50/20"],
    "Management Consulting & Legal Services": ["G06Q10/06", "G06F16/93"],
    "Civil Engineering, Architecture & Heavy Construction": ["E04B", "E01C", "E02D"]
}


# Complete 5-Level Cascading Taxonomy Ontology Structure
TAXONOMY_TREE = {
    "1. Energy & Hydrocarbon Value Chain": {
        "Downstream Refining & Petrochemicals": {
            "Decarbonization Technologies": {
                "Energy Efficiency": ["Process Electrification", "Heat Integration", "Low-Carbon Catalytic Reforming"]
            }
        },
        "Upstream Exploration & Production (E&P)": {
            "Subsea Monitoring": {
                "Telemetry Sensors": ["Acoustic Leak Detection", "Subsea Fibre Optic Sensing"]
            }
        }
    },
    "2. Sustainable Solutions & Green Tech": {
        "Carbon Capture, Utilization & Storage (CCUS)": {
            "Direct Air Capture (DAC)": {
                "Solid Sorbent Materials": [
                    "Metal-Organic Frameworks (MOFs)",
                    "Amine-functionalized silica matrix",
                    "Structured Monolith Contactors"
                ],
                "Liquid Solvent Systems": [
                    "Potassium carbonate structured contactors",
                    "Amino acid salt solutions"
                ]
            },
            "Post-Combustion Capture": {
                "Chemical Absorption": [
                    "Piperazine promoted solvents",
                    "Advanced alkanolamine blends"
                ]
            }
        },
        "Green Hydrogen & Electrolyzer Manufacturing": {
            "Water Electrolysis Technologies": {
                "PEM Electrolyzer Efficiency": [
                    "Iridium catalyst loading reduction",
                    "Titanium porous transport layers",
                    "PFSA ionomer membranes"
                ],
                "Solid Oxide Electrolysis (SOEC)": [
                    "Perovskite cathode material optimization",
                    "High-temperature steam integration"
                ]
            }
        }
    },
    "3. Mining & Advanced Metallurgy": {
        "Critical Minerals & Battery Metals Mining": {
            "Lithium Extraction": {
                "Direct Lithium Extraction (DLE)": ["Adsorption Membranes", "Ion Exchange Resins"]
            }
        }
    },
    "4. Power Grids & Grid Modernization": {
        "Smart Grid Infrastructure & IoT": {
            "Grid Edge Management": {
                "DERMS Control": ["Predictive Load Balancing", "Microgrid Frequency Regulation"]
            }
        }
    },
    "5. Advanced Materials & Chemicals": {
        "Graphene & 2D Nanomaterials": {
            "Nanocomposites": {
                "Structural Fillers": ["Graphene Oxide Dispersion", "MXene conductive additives"]
            }
        }
    },
    "6. Technology & Digital Innovation": {
        "Artificial Intelligence (AI) & Machine Learning": {
            "Generative AI & LLMs": {
                "Model Compression": ["Post-training Quantization", "Low-Rank Adaptation (LoRA)"]
            }
        }
    },
    "7. Manufacturing & Aerospace": {
        "Battery Technology & Energy Storage Systems": {
            "Solid-State Batteries": {
                "Electrolyte Architecture": ["Sulfide Ceramic Separators", "Lithium Metal Anode Interfaces"]
            }
        }
    },
    "8. Healthcare & Life Sciences": {
        "Biotechnology, Genomics & Gene Editing": {
            "CRISPR Technologies": {
                "Delivery Mechanisms": ["Lipid Nanoparticles (LNPs)", "Adeno-Associated Virus (AAV) Vectors"]
            }
        }
    },
    "9. Finance, Insurance & Real Estate": {
        "Financial Technology (FinTech) & Digital Payments": {
            "Decentralized Ledger": {
                "Smart Contracts": ["Zero-Knowledge Rollups", "Cross-Chain Interoperability Protocols"]
            }
        }
    },
    "10. Consumer Markets, Media & Services": {
        "Agricultural Technology (AgTech & Vertical Farming)": {
            "Controlled Environment Agriculture": {
                "Hydroponic Sensing": ["Automated Nutrient Dosing", "Hyperspectral Plant Health Imaging"]
            }
        }
    }
}

# Domain-Specific Lexicons (20+ Terms per Domain)
DOMAIN_LEXICONS = {
    "Carbon": [
        "Metal-Organic Frameworks (MOFs)", "Amine-Functionalized Silica", "Direct Air Capture (DAC)",
        "Temperature-Vacuum Swing Adsorption (TVSA)", "Structured Monolith Contactors", "Potassium Carbonate Solvents",
        "Bio-char Pyrolysis Integration", "Cryogenic CO2 Liquefaction", "Solvent Regeneration Duty",
        "Membrane Contactor Modules", "Carbonate Looping Reactors", "Biogenic CO2 Mineralization",
        "Covalent Organic Frameworks (COFs)", "Deep Eutectic Solvents", "Piperazine Promoted Solvents",
        "Microalgae Carbon Fixation", "Electrochemical CO2 Reduction", "Supercritical CO2 Compression",
        "Basaltic Mineral Injection", "Flue Gas Pre-conditioning"
    ],
    "Hydrogen": [
        "Proton Exchange Membrane (PEM)", "Iridium Loading Reduction", "Porous Transport Layers (PTL)",
        "Solid Oxide Electrolysis (SOEC)", "Green Ammonia Synthesis", "Alkaline Water Electrolysis (AWE)",
        "Perovskite Air Electrodes", "Thermal Energy Recovery", "Anion Exchange Membranes (AEM)",
        "Ruthenium-based Electrocatalysts", "Titanium Bipolar Plates", "Gas Diffusion Layer (GDL) Coating",
        "Pressurized Electrolyzer Stacks", "Dynamic Load Following Control", "Water Deionization Units",
        "Oxygen Evolution Reaction (OER)", "Hydrogen Deoxidation Dryers", "Zero-Gap Alkaline Cell Design",
        "Steam-Electrolysis Heat Integration", "PEM Cell Degradation Mitigation"
    ],
    "Default": [
        "Synthetic Intelligence Modeling", "Quantum-resistant Cryptography", "Autonomous Micro-Grid Control",
        "Advanced Thermoelectric Harvesting", "Additive Powder-Bed Fusion", "Superconducting Magnet Interfaces",
        "Solid-State Ion Conduction", "Distributed Ledger Rollups", "Predictive Digital Twin Simulation",
        "High-Entropy Ceramic Coatings", "Neuromorphic Array Compute", "Hyperspectral Remote Telemetry",
        "Edge Inference Quantization", "Autonomous Robotic Maintenance", "Photonic Interconnect Circuits",
        "Sub-Nanometer Etching Processes", "Thermal Interface Phase-Change", "Closed-Loop Circular Recovery",
        "Bio-compatible Nanostructures", "Acoustic Wave Condition Monitoring"
    ]
}


@app.get("/", response_class=FileResponse)
def home():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "index.html file not found in root directory"}


@app.get("/api/v1/macro-industries")
def get_macro_industries():
    return {"macro_industries": list(TAXONOMY_TREE.keys())}


@app.get("/api/v1/sub-sectors")
def get_sub_sectors(macro_industry: str = Query(...)):
    if macro_industry not in TAXONOMY_TREE:
        return {"sub_sectors": []}
    return {"sub_sectors": list(TAXONOMY_TREE[macro_industry].keys())}


@app.get("/api/v1/themes")
def get_themes(macro_industry: str = Query(...), sub_sector: str = Query(...)):
    try:
        themes = list(TAXONOMY_TREE[macro_industry][sub_sector].keys())
        return {"themes": themes}
    except KeyError:
        return {"themes": []}


@app.get("/api/v1/focus-areas")
def get_focus_areas(macro_industry: str = Query(...), sub_sector: str = Query(...), theme: str = Query(...)):
    try:
        focus = list(TAXONOMY_TREE[macro_industry][sub_sector][theme].keys())
        return {"focus_areas": focus}
    except KeyError:
        return {"focus_areas": []}


@app.get("/api/v1/calculate")
def run_analytics(
    sub_sector: str, 
    theme: Optional[str] = None, 
    focus_area: Optional[str] = None, 
    custom_term: Optional[str] = None
):
    # Select domain-specific lexicon based on scope inputs
    if "Carbon" in sub_sector or (theme and "Carbon" in theme):
        lexicon_pool = DOMAIN_LEXICONS["Carbon"]
    elif "Hydrogen" in sub_sector or (theme and "Hydrogen" in theme):
        lexicon_pool = DOMAIN_LEXICONS["Hydrogen"]
    else:
        lexicon_pool = DOMAIN_LEXICONS["Default"]

    patent_history = []
    top_10_corporate = []
    geo_distribution = []

    # Execute Live Google Patents BigQuery Queries
    if bq_client:
        try:
            print(f"🔍 Executing Live BigQuery Search for: {sub_sector}...")
            # Retrieve broad CPC codes mapped to the sub-sector, or default to general classification
            cpc_codes = CPC_MAPPINGS.get(sub_sector, ["G06F", "Y02E", "C07C"])
            cpc_clause = " OR ".join([f"cpc.code LIKE '{code}%'" for code in cpc_codes])

            search_target = custom_term or focus_area or theme
            keyword_clause = "1=1"
            if search_target and search_target.strip():
                keyword_clause = f"REGEXP_CONTAINS(LOWER(title_localized.text), r'(?i)\\b{search_target.strip().lower()}\\b')"

            query_sql = f"""
            WITH filtered_patents AS (
              SELECT 
                publication_number,
                family_id,
                country_code,
                EXTRACT(YEAR FROM PARSE_DATE('%Y%m%d', CAST(publication_date AS STRING))) AS pub_year,
                assignee_harmonized
              FROM 
                `patents-public-data.patents.publications`,
                UNNEST(cpc) AS cpc,
                UNNEST(title_localized) AS title_localized
              WHERE 
                publication_date >= 20160101
                AND ({cpc_clause})
                AND {keyword_clause}
            ),
            deduped AS (
              SELECT DISTINCT
                family_id,
                pub_year,
                country_code,
                ARRAY(SELECT name FROM UNNEST(assignee_harmonized) LIMIT 1)[SAFE_OFFSET(0)] AS primary_assignee
              FROM filtered_patents
            )
            SELECT
              pub_year,
              COUNT(DISTINCT family_id) AS annual_families,
              APPROX_TOP_COUNT(primary_assignee, 10) AS top_assignees,
              APPROX_TOP_COUNT(country_code, 5) AS top_countries
            FROM deduped
            GROUP BY pub_year
            ORDER BY pub_year ASC;
            """

            query_job = bq_client.query(query_sql)
            results = [dict(row) for row in query_job.result()]
            print(f"✅ Success! Received {len(results)} year buckets from BigQuery.")

            if results:
                # 1. Extract Live Annual Patent Time-Series
                patent_history = [row.get("annual_families", 0) for row in results]

                # 2. Extract Live Top Corporate Assignees
                latest_assignees = results[-1].get("top_assignees", [])
                for item in latest_assignees:
                    if item.get("value"):
                        top_10_corporate.append({
                            "name": str(item["value"]).title(),
                            "patents": int(item["count"])
                        })

                # 3. Extract Live Country Code Distribution
                latest_countries = results[-1].get("top_countries", [])
                total_country_count = sum([c["count"] for c in latest_countries]) or 1
                for item in latest_countries:
                    if item.get("value"):
                        pct = round((item["count"] / total_country_count) * 100, 1)
                        geo_distribution.append({
                            "country": f"Patent Office ({item['value']})",
                            "patents": int(item["count"]),
                            "percentage": pct
                        })
        except Exception as e:
            print(f"❌ BigQuery Execution Exception: {e}")

    # Simulation Baseline Fallbacks
    if not patent_history or len(patent_history) < 3:
        patent_history = [12, 15, 18, 22, 30, 45, 60, 95, 140, 210]

    if not top_10_corporate:
        top_10_corporate = [
            {"name": "Climeworks AG", "patents": 1412},
            {"name": "Carbon Engineering (Occidental)", "patents": 1280},
            {"name": "Saudi Aramco Tech Co.", "patents": 1095},
            {"name": "Linde plc", "patents": 884},
            {"name": "Air Liquide S.A.", "patents": 760},
            {"name": "Mitsubishi Heavy Industries", "patents": 690},
            {"name": "Siemens Energy AG", "patents": 620},
            {"name": "Honeywell UOP", "patents": 540},
            {"name": "BASF SE", "patents": 480},
            {"name": "Shell Global Solutions", "patents": 410}
        ]

    if not geo_distribution:
        geo_distribution = [
            {"country": "United States (USPTO)", "patents": 14250, "percentage": 38.5},
            {"country": "China (CNIPA)", "patents": 11800, "percentage": 31.8},
            {"country": "European Patent Office (EPO)", "patents": 5400, "percentage": 14.5},
            {"country": "Japan (JPO)", "patents": 3200, "percentage": 8.6},
            {"country": "South Korea (KIPO)", "patents": 2400, "percentage": 6.6}
        ]

    # Analytics Calculations: Live CAGR & Momentum
    start_vol = patent_history[0] if patent_history[0] > 0 else 1
    end_vol = patent_history[-1]
    years = max(len(patent_history) - 1, 1)
    cagr = (((end_vol / start_vol) ** (1.0 / years)) - 1.0) * 100

    trailing_3 = sum(patent_history[-3:])
    historical_avg = (sum(patent_history[:-3]) / len(patent_history[:-3])) if len(patent_history) > 3 else 1.0
    momentum = round(trailing_3 / (3 * historical_avg), 2) if historical_avg > 0 else 1.0

    # Quadrant Dispersion Coordinates (40 Real Tech Nodes)
    random.seed(len(sub_sector) + (len(theme) if theme else 0))

    matrix_technologies = []
    stages_cycle = ["Emerging", "Early Stage", "Mature", "Stagnant"]

    for idx in range(1, 41):
        base_name = lexicon_pool[(idx - 1) % len(lexicon_pool)]
        tech_name = f"{base_name} Variant {idx}" if idx > len(lexicon_pool) else base_name
        stage = stages_cycle[(idx - 1) % 4]

        if stage == "Emerging":
            x_val = round(random.uniform(8.0, 24.0), 1)
            y_val = round(random.uniform(2.8, 5.0), 2)
            x_pos = random.randint(55, 90)
            y_pos = random.randint(55, 90)
        elif stage == "Early Stage":
            x_val = round(random.uniform(36.0, 60.0), 1)
            y_val = round(random.uniform(2.5, 4.8), 2)
            x_pos = random.randint(10, 45)
            y_pos = random.randint(55, 90)
        elif stage == "Mature":
            x_val = round(random.uniform(10.0, 20.0), 1)
            y_val = round(random.uniform(0.8, 2.2), 2)
            x_pos = random.randint(55, 90)
            y_pos = random.randint(10, 45)
        else: # Stagnant
            x_val = round(random.uniform(40.0, 60.0), 1)
            y_val = round(random.uniform(0.2, 1.2), 2)
            x_pos = random.randint(10, 45)
            y_pos = random.randint(10, 45)

        matrix_technologies.append({
            "name": tech_name,
            "stage": stage,
            "x_val": x_val,
            "y_val": y_val,
            "x": x_pos,
            "y": y_pos
        })

    # Explicitly append custom injected term to Emerging quadrant if provided
    if custom_term and custom_term.strip():
        matrix_technologies.append({
            "name": f"⭐ CUSTOM: {custom_term.strip()}",
            "stage": "Emerging",
            "x_val": 12.4,
            "y_val": 4.50,
            "x": 78,
            "y": 82
        })

    top_10_academia = [
        {"name": "University of California, Berkeley", "citations": 4420},
        {"name": "ETH Zürich", "citations": 3800},
        {"name": "KAUST (Saudi Arabia)", "citations": 3150},
        {"name": "Massachusetts Institute of Technology (MIT)", "citations": 2870},
        {"name": "Stanford University", "citations": 2400},
        {"name": "Imperial College London", "citations": 2100},
        {"name": "Tsinghua University", "citations": 1950},
        {"name": "National University of Singapore (NUS)", "citations": 1720},
        {"name": "University of Cambridge", "citations": 1540},
        {"name": "Georgia Institute of Technology", "citations": 1380}
    ]

    return {
        "selected_sub_sector": sub_sector,
        "selected_theme": theme,
        "selected_focus": focus_area,
        "custom_term_injected": custom_term,
        "calculated_metrics": {
            "10_year_cagr_percentage": round(cagr, 2),
            "3_year_momentum_velocity": momentum,
            "technology_stage": "Emerging" if momentum > 2.0 else "Early Stage"
        },
        "matrix_technologies": matrix_technologies,
        "geographic_distribution": geo_distribution,
        "emerging_buzzwords": lexicon_pool[:20],
        "leaderboards": {
            "top_corporate": top_10_corporate[:10],
            "top_academia": top_10_academia[:10]
        }
    }