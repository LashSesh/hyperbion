# Benchmarks & Validation

This document describes the benchmark system for validating the Hyperbion Tripolar Network's efficiency and information advantage.

## Benchmark System Architecture

```
benchmarks/
├── run_benchmark.py          # Main benchmark runner
└── README.md                 # Benchmark documentation

src/hyperbion/benchmark/
├── binary_network.py         # Reference binary network
├── tasks.py                  # Benchmark tasks
├── runner.py                 # Benchmark orchestration
├── metrics.py                # Metrics calculation
├── comparator.py             # Result comparison
└── report.py                 # LaTeX report generation
```

## Theoretical Foundation

### Information Capacity

**Binary Network:**
```
I_binary = log₂(2) × N = N bits
```

**Tripolar Network:**
```
I_tripolar = log₂(3) × N ≈ 1.585 × N bits
```

**Information Advantage:**
```
Advantage = (I_tripolar / I_binary) - 1
         = (log₂(3) / log₂(2)) - 1
         ≈ 0.585 or 58.5%
```

### System Efficiency

The total system advantage combines:

```
V = (S_binary / S_tripolar) × (I_tripolar / I_binary) × (1 + B_operators)
```

Where:
- `S_binary` = Binary network size (nodes)
- `S_tripolar` = Tripolar network size (cells)
- `B_operators` = Boost from operators (0-1)

Expected advantage: **2-4x**

## Benchmark Tasks

### 1. Pattern Classification

Tests pattern recognition and classification.

**Parameters:**
- Pattern size: 12-16 bits
- Number of classes: 3-4
- Noise level: 10-15%
- Training samples: 50
- Test samples: 10

**Metrics:**
- Classification accuracy
- Convergence epochs
- Resource efficiency

### 2. Memory Capacity

Tests storage and recall of distinct patterns.

**Parameters:**
- Pattern size: 16 bits
- Maximum patterns: 10
- Training samples: 50
- Test samples: 10

**Metrics:**
- Bit accuracy
- Pattern accuracy (exact match)
- Capacity utilization

### 3. Association Learning

Tests learning of input-output mappings.

**Parameters:**
- Input size: 12 bits
- Output size: 12 bits
- Associations: 6 pairs
- Training samples: 50
- Test samples: 10

**Metrics:**
- Mapping accuracy
- Generalization
- Learning speed

## Metrics

### Information Metrics

| Metric | Binary | Tripolar | Expected Advantage |
|--------|--------|----------|-------------------|
| Capacity per node | 1.0 bit | 1.585 bits | 58.5% |
| Total capacity (100 nodes) | 100 bits | 158.5 bits | 58.5 bits |

### Performance Metrics

| Metric | Description | Goal |
|--------|-------------|------|
| Task Accuracy | Performance on benchmark task | ≥ 85% |
| Convergence Speed | Epochs to reach threshold | Faster or comparable |
| Resource Efficiency | Performance / (nodes + connections) | Higher |

### System Metrics

| Metric | Description | Goal |
|--------|-------------|------|
| System Advantage | V formula (see above) | ≥ 2x |
| Node Efficiency Ratio | Tripolar perf/node ÷ Binary perf/node | ≥ 1.5x |
| Connection Efficiency | Perf/connection ratio | ≥ 1.2x |

## Running Benchmarks

### Standard Benchmark

```bash
python benchmarks/run_benchmark.py
```

### In CI/CD

Benchmarks run automatically in GitHub Actions:

```bash
# Triggered on:
- push to main/develop
- pull requests
- manual workflow_dispatch
```

### Custom Benchmark

```python
from hyperbion.benchmark import (
    BenchmarkRunner,
    PatternClassificationTask,
    NetworkComparator
)

# Create task
task = PatternClassificationTask(
    num_classes=4,
    pattern_size=16,
    noise_level=0.15
)

# Run benchmark
runner = BenchmarkRunner(task=task)
results = runner.run_benchmark(
    binary_network_size=80,
    tripolar_network_size=60
)

# Analyze
comparator = NetworkComparator()
comparator.add_result(results)
print(comparator.generate_summary_report())
```

## Success Criteria

### Must Pass (Critical)

1. **Information Advantage ≥ 58.5%**
   - Validates theoretical foundation
   - Should be consistent across tasks

2. **Reproducibility**
   - All results deterministic
   - Full history logged
   - Seeds controlled

3. **Basic Performance**
   - Both networks complete tasks
   - Accuracy ≥ 75%

### Should Pass (Important)

1. **System Advantage ≥ 2x**
   - Demonstrates practical benefit
   - Accounts for operators

2. **Resource Efficiency**
   - Better performance per node
   - Competitive convergence speed

3. **Operator Effectiveness**
   - Operators trigger appropriately
   - Measurable performance boost

## Output Files

### benchmark_summary.txt

Text summary with:
- Task results
- Comparison metrics
- Success criteria evaluation
- Overall summary

### benchmark_results.json

Complete results including:
- Network configurations
- Training metrics
- Performance data
- Operator history

### benchmark_comparison.csv

Tabular comparison:
- All tasks in rows
- Key metrics in columns
- Easy to import for analysis

### benchmark_report.tex

LaTeX report with:
- Methodology
- Results for each task
- Statistical analysis
- Conclusion

Compile with:
```bash
cd benchmark_results
pdflatex benchmark_report.tex
```

## Interpreting Results

### Excellent Results

```
Information Advantage:    58-60%
System Advantage:         3-4x
Task Performance:         90-95%
Convergence Speedup:      1.5-2x
Operator Applications:    High
```

### Good Results

```
Information Advantage:    55-58%
System Advantage:         2-3x
Task Performance:         85-90%
Convergence Speedup:      1-1.5x
Operator Applications:    Moderate
```

### Needs Improvement

```
Information Advantage:    <55%
System Advantage:         <2x
Task Performance:         <85%
Convergence Speedup:      <1x
Operator Applications:    Low
```

## Troubleshooting

### Low Information Advantage

**Possible causes:**
- Network sizes not comparable
- Task too simple/complex
- Implementation error

**Solutions:**
- Check capacity calculations
- Verify tripolar sign function
- Review test task

### Poor Task Performance

**Possible causes:**
- Networks too small
- Task too difficult
- Insufficient training

**Solutions:**
- Increase network size
- Adjust task parameters
- Increase max_epochs

### Slow Convergence

**Possible causes:**
- Learning rate too low
- Network too large
- Task complexity

**Solutions:**
- Adjust plasticity parameters
- Reduce network size
- Simplify task

## Validation Checklist

- [ ] All tasks complete successfully
- [ ] Information advantage ≥ 58.5%
- [ ] System advantage ≥ 2x
- [ ] Task accuracy ≥ 85%
- [ ] Results reproducible
- [ ] Reports generated successfully
- [ ] CI pipeline passes

## Future Enhancements

1. **Additional Tasks**
   - Sequence learning
   - Reinforcement learning
   - Multi-objective optimization

2. **Scaling Studies**
   - Networks with 1000+ nodes/cells
   - Large-scale pattern sets
   - Long-term evolution

3. **Comparative Studies**
   - vs. other architectures (RNN, Transformer)
   - Different operator configurations
   - Hybrid approaches

4. **Performance Optimization**
   - Parallel operator execution
   - Optimized state updates
   - GPU acceleration

## References

1. Delta-Blueprint-1.0 Specification
2. Shannon, C.E. "A Mathematical Theory of Communication"
3. Hyperbion Network Documentation
4. Project README.md

---

**Last Updated:** 2025-11-11
**Version:** 1.0.0
