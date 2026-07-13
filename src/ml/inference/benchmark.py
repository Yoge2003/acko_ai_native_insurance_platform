"""
Inference Performance Benchmarking.
Evaluates single, batch (100), and batch (1000) predictions for latency and peak memory usage.
"""

import time
import tracemalloc
import logging
import warnings
import sys
import pandas as pd

warnings.filterwarnings("ignore")

from src.ml.inference.quotation_predictor import QuotationPredictor
from src.ml.inference.claims_predictor import ClaimsPredictor
from src.ml.inference.model_loader import ModelLoader

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def run_benchmark() -> None:
    """
    Measures latency and memory footprints of the serialization pipeline in production mode.
    """
    print("======================================================================")
    print("ACKO INSURANCE PLATFORM - INFERENCE PIPELINE SPEED BENCHMARK SUMMARY")
    print("======================================================================")

    # 1. Warm-up and Component Loading
    print("[1/4] Warming up model assets and caching components in memory...")
    # Load car premium quotation
    _ = ModelLoader.load_components("car_quotation")
    car_predictor = QuotationPredictor("car")

    # Load dataset for sampling (using cached artifacts)
    _, _, artifacts = ModelLoader.load_components("car_quotation")
    # Generate 1000 sample records
    from src.ml.training.training_pipeline import TrainingPipeline
    data_pkg = TrainingPipeline.run_pipeline("car_quotation")
    # Take raw inputs from test split before preprocessor changes
    # But wait, we can just load the raw CSV or subset to feed raw inputs!
    # To get raw inputs, let's load a segment of the raw CSV file
    from src.ml.preprocessing.data_loader import DataLoader
    df_raw = DataLoader.load_csv("acko_car_quotation.csv")
    
    # Exclude target leakage columns to test raw validation
    leakage_cols = ["od_premium_before_ncb", "ncb_discount_amount", "tp_premium", "addon_premium", "gst_amount", "annual_premium"]
    df_clean_raw = df_raw.drop(columns=[col for col in leakage_cols if col in df_raw.columns])

    # Slice batches
    single_record = df_clean_raw.head(1).to_dict(orient="records")[0]
    batch_100 = df_clean_raw.head(100).to_dict(orient="records")
    batch_1000 = df_clean_raw.head(1000).to_dict(orient="records")

    print("[2/4] Executing Single Predict Benchmarks (50 iterations)...")
    # Start memory tracing
    tracemalloc.start()
    single_latencies = []
    
    # Warm up first
    _ = car_predictor.predict(single_record)

    for _ in range(50):
        t0 = time.perf_counter()
        _ = car_predictor.predict(single_record)
        t1 = time.perf_counter()
        single_latencies.append((t1 - t0) * 1000)

    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    avg_single = sum(single_latencies) / len(single_latencies)
    min_single = min(single_latencies)
    max_single = max(single_latencies)
    mem_mb = peak_mem / (1024 * 1024)

    print(f"  • Single Latency (Mean): {avg_single:.2f} ms")
    print(f"  • Single Latency (Min):  {min_single:.2f} ms")
    print(f"  • Single Latency (Max):  {max_single:.2f} ms")
    print(f"  • Peak Memory Usage:     {mem_mb:.2f} MB")
    print("----------------------------------------------------------------------")

    print("[3/4] Executing Batch (N=100) Prediction Benchmark...")
    tracemalloc.start()
    t0 = time.perf_counter()
    res_100 = car_predictor.predict_batch(batch_100)
    t1 = time.perf_counter()
    current_mem, peak_mem_100 = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    latency_100 = (t1 - t0) * 1000
    avg_per_item_100 = latency_100 / 100
    mem_mb_100 = peak_mem_100 / (1024 * 1024)

    print(f"  • Total Latency:        {latency_100:.2f} ms")
    print(f"  • Avg Time per record:  {avg_per_item_100:.2f} ms")
    print(f"  • Peak Memory Usage:    {mem_mb_100:.2f} MB")
    print("----------------------------------------------------------------------")

    print("[4/4] Executing Batch (N=1000) Prediction Benchmark...")
    tracemalloc.start()
    t0 = time.perf_counter()
    res_1000 = car_predictor.predict_batch(batch_1000)
    t1 = time.perf_counter()
    current_mem, peak_mem_1000 = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    latency_1000 = (t1 - t0) * 1000
    avg_per_item_1000 = latency_1000 / 1000
    mem_mb_1000 = peak_mem_1000 / (1024 * 1024)

    print(f"  • Total Latency:        {latency_1000:.2f} ms")
    print(f"  • Avg Time per record:  {avg_per_item_1000:.2f} ms")
    print(f"  • Peak Memory Usage:    {mem_mb_1000:.2f} MB")
    print("======================================================================")
    print("BENCHMARK COMPLETED SUCCESSFULLY.")
    print("======================================================================")


if __name__ == "__main__":
    run_benchmark()
