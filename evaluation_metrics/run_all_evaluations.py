"""
run_all_evaluations.py - Run all evaluation scripts

This script runs all evaluation scripts in sequence to generate
all metrics, charts, and analysis as defined in EVALUATION_STRATEGY.md
"""

import subprocess
import sys
from pathlib import Path


def run_script(script_name):
    """Run a Python script and print its output."""
    script_path = Path(__file__).parent / script_name
    print(f"\n{'='*70}")
    print(f"RUNNING: {script_name}")
    print(f"{'='*70}\n")
    
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=False,
        text=True,
        cwd=str(Path(__file__).parent)
    )
    
    return result.returncode == 0


def main():
    print("="*70)
    print("CROP RECOMMENDATION SYSTEM - COMPLETE EVALUATION")
    print("="*70)
    print("\nThis will run all evaluation scripts and generate:")
    print("  - 25 evaluation charts")
    print("  - Statistical analysis")
    print("  - CSV summaries")
    print()
    
    scripts = [
        ('02_ensemble_metrics.py', 'Ensemble Model Metrics (Charts 1-7)'),
        ('03_xgboost_vs_ensemble.py', 'XGBoost vs Ensemble Proof (Charts 8-14)'),
        ('04_rindm_validation.py', 'RINDM Validation (Charts 15-17)'),
        ('05_rindm_soil_analysis.py', 'RINDM Soil Analysis (Charts 18-19, 23)'),
        ('06_rindm_cumulative.py', 'RINDM Cumulative Analysis (Charts 20-22)'),
        ('07_integration_test.py', 'End-to-End Integration (Charts 24-25)'),
    ]
    
    results = []
    
    for script, description in scripts:
        print(f"\n>>> {description}")
        success = run_script(script)
        results.append((script, success))
        
        if not success:
            print(f"\n⚠ Warning: {script} had errors")
    
    # Summary
    print("\n" + "="*70)
    print("EVALUATION COMPLETE - SUMMARY")
    print("="*70)
    
    for script, success in results:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"  {script}: {status}")
    
    successful = sum(1 for _, s in results if s)
    print(f"\nCompleted: {successful}/{len(results)} scripts successfully")
    
    output_dir = Path(__file__).parent / "plots"
    print(f"\nAll outputs saved to: {output_dir}")
    print("\nGenerated files:")
    if output_dir.exists():
        for f in sorted(output_dir.iterdir()):
            print(f"  - {f.name}")


if __name__ == "__main__":
    main()
