TRIPOLAR DATABASE INDEX
**Projekt:** `tripolar-index`  
**Ziel:** 35-40% schnellere Suche als binäre Indizes  
**Priorität:** ⭐⭐⭐⭐⭐⭐

## Delta-Spezifikation

### Projektstruktur
```
tripolar-index/
├── Cargo.toml
├── src/
│   ├── lib.rs              # Public API
│   ├── triindex.rs         # Tripolar B-Tree
│   ├── node.rs             # Node structure
│   ├── metadata.rs         # Hot/cold tracking
│   └── query.rs            # Query optimization
├── benches/
│   └── search_bench.rs
├── examples/
│   └── compare_btree.rs    # vs std::collections::BTreeMap
└── tests/
    └── correctness.rs
```

### Cargo.toml
```toml
[package]
name = "tripolar-index"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1.0", features = ["derive"] }

[dev-dependencies]
criterion = "0.5"
rand = "0.8"
```

### Core API (lib.rs)
```rust
/// Tripolare Index-Struktur
pub struct TriPolarIndex 
where
    K: Ord + Clone,
    V: Clone,
{
    root: Option<Box<TriNode>>,
    size: usize,
    access_tracker: AccessTracker,
}

pub struct TriNode {
    pub threshold_low: K,
    pub threshold_high: K,
    pub entries: Vec,
    pub left: Option<Box<TriNode>>,    // < threshold_low
    pub middle: Option<Box<TriNode>>,  // between thresholds
    pub right: Option<Box<TriNode>>,   // > threshold_high
    pub metadata: NodeMetadata,
}

#[derive(Debug, Clone)]
pub struct NodeMetadata {
    pub access_count: usize,
    pub is_hot: bool,
    pub cached_result: Option,  // Cached index für häufige Keys
}

impl TriPolarIndex 
where
    K: Ord + Clone,
    V: Clone,
{
    pub fn new() -> Self;
    pub fn insert(&mut self, key: K, value: V);
    pub fn get(&mut self, key: &K) -> Option;
    pub fn remove(&mut self, key: &K) -> Option;
    pub fn len(&self) -> usize;
    pub fn optimize(&mut self);  // Re-balance based on access patterns
}
```

### TriNode Implementation (node.rs)
```rust
impl TriNode
where
    K: Ord + Clone,
    V: Clone,
{
    pub fn new(entries: Vec) -> Self {
        let n = entries.len();
        let idx_low = n / 3;
        let idx_high = 2 * n / 3;
        
        let threshold_low = entries[idx_low].0.clone();
        let threshold_high = entries[idx_high].0.clone();
        
        Self {
            threshold_low,
            threshold_high,
            entries,
            left: None,
            middle: None,
            right: None,
            metadata: NodeMetadata {
                access_count: 0,
                is_hot: false,
                cached_result: None,
            },
        }
    }
    
    pub fn search(&mut self, key: &K) -> Option {
        self.metadata.access_count += 1;
        
        // Check cache
        if let Some(cached_idx) = self.metadata.cached_result {
            if &self.entries[cached_idx].0 == key {
                return Some(&self.entries[cached_idx].1);
            }
        }
        
        // Tripolare Suche
        if key < &self.threshold_low {
            // L0 branch
            if let Some(ref mut left) = self.left {
                left.search(key)
            } else {
                self.linear_search(key)
            }
        } else if key > &self.threshold_high {
            // L1 branch
            if let Some(ref mut right) = self.right {
                right.search(key)
            } else {
                self.linear_search(key)
            }
        } else {
            // LD branch (middle)
            if let Some(ref mut middle) = self.middle {
                middle.search(key)
            } else {
                self.linear_search(key)
            }
        }
    }
    
    fn linear_search(&mut self, key: &K) -> Option {
        for (i, (k, v)) in self.entries.iter().enumerate() {
            if k == key {
                // Cache result if hot
                if self.metadata.is_hot {
                    self.metadata.cached_result = Some(i);
                }
                return Some(v);
            }
        }
        None
    }
    
    pub fn update_hot_status(&mut self, threshold: usize) {
        self.metadata.is_hot = self.metadata.access_count > threshold;
    }
}
```

### Benchmarks (benches/search_bench.rs)
```rust
use criterion::*;
use tripolar_index::TriPolarIndex;
use std::collections::BTreeMap;

fn benchmark_search(c: &mut Criterion) {
    let mut group = c.benchmark_group("index_search");
    
    for size in [1_000, 10_000, 100_000, 1_000_000].iter() {
        // Prepare data
        let data: Vec = (0..*size)
            .map(|i| (i, format!("value_{}", i)))
            .collect();
        
        // Build TriPolar Index
        let mut tri_index = TriPolarIndex::new();
        for (k, v) in &data {
            tri_index.insert(*k, v.clone());
        }
        
        // Build BTreeMap
        let btree: BTreeMap = data.iter().cloned().collect();
        
        // Benchmark TriPolar
        group.bench_with_input(
            BenchmarkId::new("tripolar", size),
            size,
            |b, &size| {
                b.iter(|| {
                    for _ in 0..1000 {
                        let key = rand::random::().abs() % size;
                        black_box(tri_index.get(&key));
                    }
                })
            },
        );
        
        // Benchmark BTree
        group.bench_with_input(
            BenchmarkId::new("btree", size),
            size,
            |b, &size| {
                b.iter(|| {
                    for _ in 0..1000 {
                        let key = rand::random::().abs() % size;
                        black_box(btree.get(&key));
                    }
                })
            },
        );
    }
    
    group.finish();
}

criterion_group!(benches, benchmark_search);
criterion_main!(benches);
```
