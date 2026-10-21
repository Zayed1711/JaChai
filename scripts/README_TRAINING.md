# JaChai Universal Linguistic & Query Disambiguation Router 🧠

An end-to-end, low-latency Neural Linguistic Router specifically tailored for Bangladeshi e-commerce search traffic. It analyzes messy, polysemous, or Banglish queries (mixing Bengali script, phonetic English/Banglish slang, and noisy brand spellings), normalizes them into clean canonical search terms, and maps them directly to JaChai's **15 Core Platform Categories**.

---

## 🏗 System Architecture & 15 Core Categories

| Category Slug | Display Name (EN) | Core Domains & Edge Cases |
|---|---|---|
| `mobile-gadgets` | Mobile & Gadgets | Smartphones, AirPods, smart bands, chargers, power banks |
| `laptops-pc` | Laptops & PC | Laptops, CPUs, GPUs (RTX), NVMe SSDs (Samsung 980 Pro 1TB), RAM |
| `fashion-apparel` | Fashion & Apparel | Panjabi, polo shirts, jeans, hoodies, underwear/boxers, lungi |
| `saree-boutiques` | Saree & Boutiques | Jamdani, katan silk, tant, georgette, bridal sarees |
| `grocery-snacks` | Grocery & Snacks | Khati gawa ghee, mustard oil, organic honey, rice, dal, dry fruits |
| `sportswear-gym` | Sportswear & Gym | Football kits (Barca Home kit, Madrid), resistance bands, gym wear |
| `cameras-photography` | Cameras & Photography | DSLRs (Canon 200D kit lens), mirrorless, lenses, gimbals |
| `bicycles-mtb` | Bicycles & MTB | Mountain bikes (MTB), gear cycles, Duranta, Veloce, Phoenix |
| `cycles-evs` | Cycles & EVs | Electric bikes, e-scooters, Walton Takyon, battery cycles |
| `home-appliances` | Home Appliances | Refrigerators (WFC-3F5), inverter ACs, microwaves, blenders, air fryers |
| `fine-jewelry` | Fine Jewelry & Gold | 22K/24K hallmark gold chains, diamond rings, gold nose pins |
| `fashion-jewelry` | Fashion Jewelry | Oxidised choker sets, jhumka earrings, crystal charm bracelets |
| `sneakers-footwear` | Sneakers & Footwear | Leather formal shoes, running sneakers (Bata, Apex, Nike Air Max) |
| `watches-horology` | Watches & Horology | Chronograph watches, Casio Edifice, Seiko automatic, smartwatches |
| `beauty-skincare` | Beauty & Skincare | Skincare sets, sunscreen SPF50, snail mucin, facewash, makeup |

---

## 📁 Pipeline File Tree

```text
e:/JaChai/
├── data/
│   ├── cleaned_catalog_corpus.json      # 75,311 catalog products & 341 merchant registries
│   ├── cleaned_bangla_reviews.json      # 10,657 real Bengali & Banglish customer reviews
│   ├── cleaned_category_vocab.json      # 15 category keyword matrices
│   └── train_router.jsonl               # 2,052 instruction-tuning pairs in target schema
├── scripts/
│   ├── preprocess_data.py               # Phase 1: Ingestion, exploration & cleaning
│   ├── generate_training_pairs.py       # Phase 2: Instruction-tuning pair synthesizer
│   └── test_inference.py                # Phase 4: Validation test suite & latency benchmark
├── train_qlora.py                       # Phase 3: 4-bit QLoRA fine-tuning script
└── models/
    └── jachai-router-qwen2.5-lora/      # Target adapter destination
```

---

## 🚀 Execution Guide

### Phase 1: Preprocess Raw Data
```powershell
python scripts/preprocess_data.py
```
*Parses `Training/` zip archives and CSVs, cleans text, and outputs standardized data files into `data/`.*

### Phase 2: Generate Instruction-Tuning Pairs (2,000+ Records)
```powershell
python scripts/generate_training_pairs.py
```
*Creates `data/train_router.jsonl` with 2,052 high-quality prompt-response pairs addressing polysemy, slang, and SKUs.*

### Phase 3: Fine-Tune with QLoRA (Google Colab / Cloud GPU / Local GPU)
To train the adapter on a GPU (e.g., free Google Colab T4, RunPod, or local NVIDIA card):
```bash
# 1. Install fine-tuning dependencies
pip install transformers peft trl bitsandbytes accelerate datasets

# 2. Run QLoRA training
python train_qlora.py \
    --model_id Qwen/Qwen2.5-1.5B-Instruct \
    --data_path data/train_router.jsonl \
    --output_dir models/jachai-router-qwen2.5-lora \
    --epochs 3 \
    --batch_size 4 \
    --grad_accum 4 \
    --lr 2e-4
```
*Weights will be saved to `models/jachai-router-qwen2.5-lora`.*

### Phase 4: Test & Validate Inference
```powershell
# 1. Fast Sub-Millisecond Benchmark:
python scripts/test_inference.py --engine fast

# 2. Ollama Local Model Benchmark:
python scripts/test_inference.py --engine ollama

# 3. Fine-Tuned LoRA Adapter Benchmark:
python scripts/test_inference.py --engine lora
```

---

## 🎯 Target Schema Example
Input: `"Barca Home kit"`
Output:
```json
{
  "clean_query": "fc barcelona home football jersey",
  "category_hint": "sportswear-gym",
  "attributes": {
    "brand": "fc barcelona",
    "item": "jersey"
  }
}
```
Input: `"Samsung 980 Pro 1TB"`
Output:
```json
{
  "clean_query": "samsung 980 pro 1tb nvme pcie 4.0 m.2 ssd",
  "category_hint": "laptops-pc",
  "attributes": {
    "brand": "samsung",
    "model": "980 pro",
    "capacity": "1tb",
    "item": "nvme ssd"
  }
}
```

