# Hyperbion Benchmark Suite

Comprehensive benchmark comparing Hyperbion Tripolar Network with classical Binary Network.

## Overview

This benchmark suite empirically evaluates:

1. **Information Capacity**: Theoretical vs. actual capacity advantage
2. **System Efficiency**: Resource utilization and performance per node
3. **Task Performance**: Accuracy on standardized tasks
4. **Convergence Speed**: Training efficiency
5. **Operator Effectiveness**: Impact of autonomous operators

## Running Benchmarks

### Quick Start

```bash
# From project root
python benchmarks/run_benchmark.py
```

### Output

Benchmarks generate the following outputs in `benchmark_results/`:

- `benchmark_summary.txt` - Text summary report
- `benchmark_results.json` - Complete results in JSON
- `benchmark_comparison.csv` - CSV for analysis
- `benchmark_report.tex` - LaTeX report (compile with pdflatex)

## Benchmark Tasks

### 1. Pattern Classification

Tests ability to classify noisy input patterns into categories.

- **Easy**: 3 classes, 12-bit patterns, 10% noise
- **Medium**: 4 classes, 16-bit patterns, 15% noise

### 2. Memory Capacity

Tests how many distinct patterns can be stored and retrieved.

- Pattern size: 16 bits
- Maximum patterns: 10

### 3. Association Learning

Tests learning of input-output associations.

- Input size: 12 bits
- Output size: 12 bits
- Associations: 6 pairs

## Success Criteria

The benchmark evaluates against these criteria:

1. ✅ **Information Advantage ≥ 58.5%**
   - Theoretical: log₂(3) / log₂(2) - 1 ≈ 58.5%
   - Empirical measurement across all tasks

2. ✅ **System Advantage ≥ 2x**
   - V = (S_bin / S_tri) × (I_tri / I_bin) × (1 + operator_boost)
   - Should demonstrate 2-4x advantage

3. ✅ **Reproducibility**
   - All results deterministic and logged
   - Full history available for replay

## Metrics Explained

### Information Capacity

```
I_binary = log₂(2) × N = N bits
I_tripolar = log₂(3) × N ≈ 1.585 × N bits
```

### System Efficiency

```
V = (Size_Ratio) × (Capacity_Ratio) × (1 + Operator_Boost)
```

Where:
- **Size_Ratio**: Binary nodes / Tripolar cells
- **Capacity_Ratio**: Tripolar capacity / Binary capacity
- **Operator_Boost**: Performance gain from operators

### Resource Efficiency

- **Performance per Node**: Task accuracy / Network size
- **Performance per Connection**: Task accuracy / Total connections
- **Connection Density**: Actual connections / Maximum possible

## Customizing Benchmarks

### Adding New Tasks

```python
from hyperbion.benchmark import BenchmarkTask

class MyTask(BenchmarkTask):
    def generate_training_data(self, num_samples):
        # Your implementation
        pass

    def generate_test_data(self, num_samples):
        # Your implementation
        pass

    def evaluate_performance(self, predictions, targets):
        # Your metrics
        pass
```

### Adjusting Parameters

Edit `run_benchmark.py`:

```python
runner = BenchmarkRunner(
    task=task,
    num_training_samples=100,  # More samples
    num_test_samples=20,
    max_epochs=100,            # More epochs
    convergence_threshold=0.90  # Higher threshold
)
```

## CI/CD Integration

Benchmarks run automatically in CI pipeline:

- On every push to main/develop branches
- On pull requests
- Results uploaded as artifacts
- Success criteria checked

See `.github/workflows/ci.yml` for details.

## Interpreting Results

### Good Results

- Information advantage: 55-60%
- System advantage: 2-4x
- Task performance: ≥ 85% accuracy
- Convergence: Faster or comparable to binary

### Red Flags

- Information advantage < 50%
- System advantage < 1.5x
- Task performance < 75% accuracy
- Convergence: Much slower than binary

## Troubleshooting

### "Benchmark failed to converge"

- Increase `max_epochs`
- Reduce `convergence_threshold`
- Check network sizes (may be too small)

### "Low information advantage"

- Verify network sizes are comparable
- Check that operators are triggering
- Review task complexity

### "Poor task performance"

- May need larger networks
- Adjust learning rates
- Check task difficulty settings

## Advanced Usage

### Running Single Task

```python
from hyperbion.benchmark import BenchmarkRunner, PatternClassificationTask

task = PatternClassificationTask(num_classes=4, pattern_size=16)
runner = BenchmarkRunner(task=task)
results = runner.run_benchmark(binary_network_size=80, tripolar_network_size=60)
```

### Generating LaTeX Report

```python
from hyperbion.benchmark.report import ReportGenerator

ReportGenerator.generate_latex_report(
    results=[result1, result2, result3],
    output_path="my_report.tex"
)
```

### Exporting Data

```python
from hyperbion.benchmark import NetworkComparator

comparator = NetworkComparator()
comparator.add_result(result1)
comparator.add_result(result2)

# Export
comparator.export_to_json("results.json")
comparator.export_to_csv("comparison.csv")
summary = comparator.generate_summary_report()
```

## References

- Delta-Blueprint-1.0 Specification
- Hyperbion Network Documentation
- Project README.md

## License

MIT License - See project LICENSE file
