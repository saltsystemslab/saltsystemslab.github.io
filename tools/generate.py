"""Generates projects/*.html, projects.html, and the area tiles in index.html.

Usage: python3 tools/generate.py .
"""
import html
import os
import sys

OUT = sys.argv[1]

AREAS = {
    "filters": ("Filters", "tone-filter",
                "Compact approximate-membership data structures: counting, vectorized, adaptive, and range filters with provable guarantees."),
    "hashtables": ("Hash Tables", "tone-hash",
                   "Fast, concurrent hash tables that stay stable and efficient at high load factors."),
    "gpu": ("GPU Data Management", "tone-gpu",
            "Building blocks for GPU applications: memory management, hash tables, and filters designed for thousands of concurrent threads."),
    "ai": ("AI Systems", "tone-ai",
           "GPU-native infrastructure for vector search, retrieval, and LLM serving."),
}

ORDER = {
    "filters": ["cqf", "vqf", "breadcrumb", "adaptiveqf", "skiqf", "aeris"],
    "hashtables": ["iceberg", "zombie-hashing"],
    "gpu": ["gpu-filters", "warpspeed", "gallatin", "andes"],
    "ai": ["jasper", "inferscale", "cascade"],
}

# Projects whose repo hosts its own GitHub Pages site. The SALT site links straight to it,
# and projects/<slug>.html becomes a redirect so old links keep working.
SITES = {
    "jasper": "https://saltsystemslab.github.io/Jasper/",
    "adaptiveqf": "https://saltsystemslab.github.io/adaptiveqf/",
    "cascade": "https://saltsystemslab.github.io/Cascade/",
}


# Projects that are listed but not released yet: their cards show a "Coming soon" badge
# and they get no detail page. Remove a slug from here once its page or site is ready.
COMING_SOON = {"andes", "inferscale"}


def url_for(p, prefix=""):
    if p["slug"] in COMING_SOON:
        return None
    return SITES.get(p["slug"], f'{prefix}{p["slug"]}.html')


SUMMARY = {
    "cascade": "Builds exact suffix arrays of LLM-scale corpora on a single GPU server, for corpora many times larger than GPU memory, and searches them with a batched query engine. 3.0–8.2× faster than infini-gram end to end.",
    "jasper": "A Vamana-graph ANNS index with RaBitQ quantization that runs index construction and queries entirely on the GPU, and scales to billion-vector datasets.",
    "inferscale": "An LLM inference framework that precomputes KV caches for memory chunks and injects the retrieved ones directly on the GPU. Time-to-first-token stays nearly flat as more memory is retrieved.",
    "gallatin": "Lets GPU threads malloc and free allocations of any size inside kernels, with no host calls. Built on van Emde Boas trees to keep fragmentation low.",
    "warpspeed": "A library of thread-safe GPU hash tables and the building blocks for new ones, covering chaining, cuckoo, double, iceberg, and power-of-two-choice hashing.",
    "gpu-filters": "The Two-Choice Filter and the GPU Quotient Filter: fast set membership and counting on the GPU, up to 4.4× faster than earlier GPU filters.",
    "aeris": "The first range filter that guarantees a bounded false-positive rate for any query distribution, including adversarial ones. It never forgets a false positive.",
    "skiqf": "Uses ski-rental analysis to decide when adapting to a false positive is worth the disk I/O, which makes it 2-competitive on total I/O.",
    "breadcrumb": "An AVX-512 filter benchmarked against the VQF, CQF, and prefix filter, and integrated into WiredTiger to screen negative queries.",
    "zombie-hashing": "Redistributes tombstones within small windows instead of halting for global rebuilds, so linear probing stays fast even at 95% load.",
    "cqf": "A general-purpose counting filter that is small, fast, and cache-friendly. It supports counting, deletions, resizing, merging, and concurrent access, and scales out of RAM to SSD.",
    "vqf": "Uses power-of-two-choices hashing and SIMD to deliver consistently high throughput across load factors, overcoming the classic time/space trade-off.",
    "adaptiveqf": "A quotient filter that adapts to false positives by extending fingerprints, so the same false positive never repeats, while keeping cache efficiency and mergeability.",
    "iceberg": "A fast, concurrent, resizable hash table that achieves both stability and low associativity. It runs on DRAM and persistent memory.",
}

P = []

P.append(dict(
    slug="jasper", name="Jasper", area="ai",
    tagline="GPU-native approximate nearest neighbor search",
    tags=["CUDA", "Python", "VLDB 2026"],
    overview=[
        "Jasper is a GPU-native approximate nearest neighbor search (ANNS) index built for speed and scale. It combines the Vamana graph index with RaBitQ quantization, and it runs both index construction and queries entirely on the GPU.",
        "Its build throughput matches or beats state-of-the-art GPU ANNS libraries, and it scales out to billion-vector datasets. The index supports inserts, updates, and deletes without a full rebuild, so it fits workloads where the corpus keeps changing.",
    ],
    features=[
        ("Fast construction", "Build throughput that matches or beats state-of-the-art GPU ANNS libraries, and scales out to billion-vector datasets."),
        ("Directional beam search", "A faster search algorithm and index layout for both device-memory and host-memory search."),
        ("Dynamic updates", "Insert, update, and delete vectors without rebuilding the index. Deleted vectors are excluded from search immediately."),
        ("RaBitQ quantization", "Higher performance than traditional product quantization, and it maps naturally to GPU computation."),
    ],
    usage=("Build an index and search (Python)", "python", """import torch, jasper

vectors = torch.randn(1_000_000, 128, dtype=torch.float16, device="cuda")
g = jasper.Graph.build(vectors, n_neighbors=64, distance="l2", alpha=1.2)

queries = torch.randn(100, 128, dtype=torch.float16, device="cuda")
indices, distances = g.search(queries, k=10, beam_width=64)"""),
    links=[("Project website", "https://saltsystemslab.github.io/Jasper/"),
           ("Source code", "https://github.com/saltsystemslab/Jasper"),
           ("System paper (arXiv)", "https://arxiv.org/abs/2601.07048"),
           ("Directional beam search (VecDB 2026)", "https://prashantpandey.github.io/assets/pdf/uploads/vecdb26_dbs.pdf")],
    citation="""@misc{mccoy2026gpuacceleratedanns,
  title  = {GPU-Accelerated ANNS: Quantized for Speed, Built for Change},
  author = {Hunter McCoy and Zikun Wang and Prashant Pandey},
  year   = {2026},
  eprint = {2601.07048},
  archivePrefix = {arXiv},
  url    = {https://arxiv.org/abs/2601.07048}
}""",
))

P.append(dict(
    slug="inferscale", name="InferScale", area="ai",
    tagline="GPU-native KV injection for personalized LLM serving",
    tags=["Python", "CUDA", "arXiv 2026"],
    overview=[
        "InferScale is an inference framework for personalized LLM serving. It does not re-prefill retrieved memories into the prompt. Instead, it precomputes KV caches for memory chunks and injects the retrieved ones directly on the GPU.",
        "As a result, time-to-first-token stays nearly flat as more memory is retrieved, and throughput scales near-linearly with the number of concurrent users. Retrieval is powered by Jasper.",
    ],
    features=[
        ("Flat TTFT", "Latency stays nearly constant as retrieved memory grows, while prefill-based systems such as Mem0 slow down with k."),
        ("Throughput scaling", "Serving throughput scales near-linearly with concurrent users. Mem0 saturates early."),
        ("Accuracy", "Within a few points of Mem0 on LoCoMo memory QA, and often ahead of it at small k."),
        ("Built on Jasper", "Vector retrieval uses the Jasper GPU index through the jasperpy bindings."),
    ],
    usage=("Quick start (Python)", "python", """from inferscale.v1 import Chunk, InferScale, InferScaleConfig

config = InferScaleConfig(model="meta-llama/Llama-3.1-8B-Instruct",
                          top_k=2, context_window=2, vector_backend="exact")
chunks = [Chunk(id="c1", text="Alice moved to Berlin in March 2021."),
          Chunk(id="c2", text="Alice adopted a grey cat named Miso in 2023.")]

with InferScale(config) as engine:
    engine.precompute(chunks)
    engine.start()
    print(engine.query("What is the name of Alice's cat?").text)"""),
    links=[("Source code", "https://github.com/saltsystemslab/InferScale"),
           ("Paper (arXiv)", "https://arxiv.org/abs/2607.27090")],
    citation="""@article{li2026inferscale,
  title   = {InferScale: GPU-Native KV Injection for Personalized LLM Serving},
  author  = {Li, Peter and Pandey, Prashant},
  journal = {arXiv preprint arXiv:2607.27090},
  year    = {2026}
}""",
))

P.append(dict(
    slug="andes", name="Andes", area="gpu",
    tagline="",
    tags=[],
    links=[("SALT on GitHub", "https://github.com/saltsystemslab")],
))

P.append(dict(
    slug="gallatin", name="Gallatin", area="gpu",
    tagline="General-purpose GPU memory manager",
    tags=["CUDA", "Header-only", "PPoPP 2024"],
    overview=[
        "Gallatin is a general-purpose GPU allocator. GPU threads can malloc and free device-side allocations inside kernels with no host calls and no synchronization with the host. It scales to GPUs of any size and supports allocations of any size, up to all of GPU DRAM.",
        "GPU memory is split into segments. Segments can be formatted into smaller blocks, which are further divided into slices, or several contiguous segments can be combined into one large allocation. Van Emde Boas trees give fast successor search over segments, so Gallatin always picks the lowest-ID segment, which keeps fragmentation low and maximizes memory reuse.",
    ],
    features=[
        ("In-kernel malloc/free", "Device-side allocation from any thread, with no host round-trips."),
        ("Any size", "Allocations range from a few bytes up to all of device memory."),
        ("Tunable", "Template parameters for segment, minimum, and maximum sizes. Tuning can more than double peak throughput for fixed-size workloads."),
        ("Header-only", "Depends only on CUDA and Cooperative Groups. Add it with CPM in one snippet."),
    ],
    usage=("Add to CMake and allocate in a kernel", "cpp", """# CMakeLists.txt
CPMAddPackage(NAME gallatin GITHUB_REPOSITORY saltsystemslab/gallatin GIT_TAG origin/main)
target_link_libraries(${EXE_NAME} PRIVATE gallatin)

// main.cu
#include <gallatin/allocators/global_allocator.cuh>
using namespace gallatin::allocators;

__global__ void kernel() {
  void* p = global_malloc(256);
  /* ... */
  global_free(p);
}

init_global_allocator(16ULL << 30, /*seed=*/42);   // host
kernel<<<blocks, threads>>>();
free_global_allocator();"""),
    links=[("Source code", "https://github.com/saltsystemslab/gallatin"),
           ("GPU allocator benchmark suite", "https://github.com/saltsystemslab/memmansurvey")],
))

P.append(dict(
    slug="warpspeed", name="warpSpeed", area="gpu",
    tagline="Concurrent GPU hash tables",
    tags=["CUDA"],
    overview=[
        "warpSpeed is a library of concurrent, thread-safe GPU hash tables, together with the building blocks for writing new ones. Every table has a similar API, and the repository includes a benchmark suite that compares the tables against existing state-of-the-art designs.",
        "Tables are initialized with a fixed number of keys, support key-value pairs up to 16 bytes, and are tiled for performance.",
    ],
    features=[
        ("Eight table designs", "Chaining, cuckoo, double hashing, iceberg hashing, and power-of-two-choice hashing, several with metadata variants."),
        ("Uniform API", "upsert_replace, upsert_function, find_with_reference, find_pair, and remove."),
        ("Lock-free compound ops", "Every operation has a _no_lock variant for building compound operations inside a critical section."),
        ("Thorough benchmarks", "Load, scaling, aging, caching, sparse-tensor, and adversarial-race benchmarks."),
    ],
    usage=("Core device API", "cpp", """__device__ bool upsert_replace(const tile_type& tile, const Key& key, const Val& val);
__device__ bool find_with_reference(tile_type tile, Key key, Val& val);
__device__ bool remove(tile_type tile, Key key);

// Lock-free variants for compound operations:
uint64_t b = get_lock_bucket(tile, key);
stall_lock(tile, b);
upsert_replace_no_lock(tile, key, val);
unlock(tile, b);"""),
    links=[("Source code", "https://github.com/saltsystemslab/warpSpeed")],
))

P.append(dict(
    slug="gpu-filters", name="GPU Filters", area="gpu",
    tagline="High-performance filters for GPUs",
    tags=["CUDA", "PPoPP 2023"],
    overview=[
        "Filters store a set approximately, giving up a little accuracy for a lot of space efficiency. That trade-off matters on accelerators like GPUs, where memory is limited. Most filter research has focused on CPUs, though, so there were few fast, full-featured GPU filters.",
        "This project explores the design space of GPU filters and introduces two new ones. The Two-Choice Filter (TCF) provides fast set membership. The GPU Quotient Filter (GQF) adds counting at some performance cost. Both have point and bulk APIs, and they are up to 4.4× and 1.4× faster than earlier GPU filters.",
    ],
    features=[
        ("Two-Choice Filter (TCF)", "Template components for point key-value structures, with configurable layout, access pattern, and false-positive rate."),
        ("Bulk TCF", "A TCF optimized for bulk data that groups keys with Thrust."),
        ("GPU Quotient Filter (GQF)", "Inserts, queries, deletes, counting, and key-value association, with a reduction scheme for Zipfian workloads."),
        ("Easy integration", "Add the library with CPM in one CMake snippet."),
    ],
    usage=("Add to CMake", "cmake", """include(cmake/CPM.cmake)

CPMAddPackage(
  NAME gpu-filters
  GITHUB_REPOSITORY saltsystemslab/gpu-filters
  GIT_TAG origin/main
)"""),
    links=[("Source code", "https://github.com/saltsystemslab/gpu-filters"),
           ("Paper (PPoPP 2023)", "https://doi.org/10.1145/3572848.3577507")],
    citation="""@inproceedings{mccoy2023gpufilters,
  author    = {McCoy, Hunter and Hofmeyr, Steven and Yelick, Katherine and Pandey, Prashant},
  title     = {High-Performance Filters for GPUs},
  booktitle = {Proceedings of the 28th ACM SIGPLAN Symposium on Principles and Practice of Parallel Programming (PPoPP)},
  year      = {2023},
  doi       = {10.1145/3572848.3577507}
}""",
))

P.append(dict(
    slug="cascade", name="Cascade", area="ai",
    tagline="GPU-accelerated out-of-core suffix array construction",
    tags=["CUDA", "C++", "arXiv 2026"],
    links=[("Project website", "https://saltsystemslab.github.io/Cascade/"),
           ("Source code", "https://github.com/saltsystemslab/Cascade"),
           ("Paper (arXiv)", "https://arxiv.org/abs/2610.15254")],
))

P.append(dict(
    slug="aeris", name="Aeris Filter", area="filters",
    tagline="Adaptive, expandable range filter",
    tags=["C", "C++", "SplinterDB"],
    overview=[
        "Aeris (Adaptive Expandable Range filter) is a range filter that resolves false positives as it encounters them. It is the first range filter to guarantee a bounded false-positive rate for any query distribution, including skewed and adversarial ones, where existing range filters' false-positive rates are unbounded.",
        "Aeris builds on the Memento filter, a fingerprint-based dynamic range filter, and inherits its dynamic updates, constant-time operations, and false-positive guarantees. It also expands efficiently and is monotonically adaptive, so it never forgets a false positive.",
    ],
    features=[
        ("Bounded FPR", "Guaranteed for any query distribution, including adversarial workloads."),
        ("Monotonic adaptivity", "Once a false positive is fixed, it stays fixed."),
        ("Expandable", "Grows efficiently as the dataset grows."),
        ("Point and range queries", "Constant-time operations, inherited from the Memento filter."),
    ],
    usage=("API", "cpp", """ARQF* arqf = (ARQF*)malloc(sizeof(ARQF));
arqf_init_with_rhm(arqf, db, n_slots, key_size, memento_bits, seed);

qf_insert_memento(arqf->qf, value, 0, &fingerprint);       // insert

result = qf_point_query(arqf->qf, left, QF_NO_LOCK);       // query
result = qf_range_query(arqf->qf, left, right, QF_NO_LOCK);

arqf_adapt_range(arqf, left, right, 0);                     // fix a false positive"""),
    links=[("Source code", "https://github.com/saltsystemslab/AerisFilter")],
))

P.append(dict(
    slug="skiqf", name="SkiQF", area="filters",
    tagline="Online adaptive quotient filters",
    tags=["C", "C++", "SplinterDB", "WiredTiger"],
    overview=[
        "Adaptive filters keep the observed false-positive rate low on skewed workloads by learning from repeated false positives. However, each adaptation adds disk I/O, which hurts throughput on workloads where false positives do not repeat.",
        "Existing adaptive filters adapt on every detected false positive. Online adaptive filters instead decide, as queries arrive, whether adapting is worth the cost. SkiQF applies ski-rental analysis to this adapt-or-tolerate decision and is 2-competitive on total I/O.",
    ],
    features=[
        ("SkiQF", "Ski-rental-based adaptation that is 2-competitive on total I/O."),
        ("HybridSkiQF", "Combines SkiQF with additional heuristics."),
        ("Common interface", "All variants extend BaseAdaptiveFilter and share one query/adapt API."),
        ("Reproducible", "One script runs the paper's full experiment suite on SplinterDB and WiredTiger."),
    ],
    usage=("Run the experiments", "bash", """./setup.sh      # builds external dependencies (SplinterDB, WiredTiger)
./run_tests     # results are written to ./paper/<experiment-name>/"""),
    links=[("Source code", "https://github.com/saltsystemslab/SkiRentalAdaptiveQF")],
))

P.append(dict(
    slug="breadcrumb", name="Breadcrumb Filter", area="filters",
    tagline="SIMD-accelerated filter",
    tags=["C++", "AVX-512"],
    overview=[
        "Breadcrumb Filter is an AVX-512 filter. The repository includes a benchmark harness that compares it with the VQF, the CQF, and the prefix filter on single-threaded, multithreaded, mixed, insert/delete, and load-factor workloads.",
        "The filter is also integrated into WiredTiger, where it screens negative queries before they reach the database. This measures end-to-end query performance under a fixed memory budget.",
    ],
    features=[
        ("AVX-512 and AVX2", "Builds for both instruction sets."),
        ("Benchmark suite", "Standard, mixed, insert/delete, and load-factor benchmarks, single- and multithreaded."),
        ("WiredTiger integration", "Filters negative lookups under a configurable memory budget."),
    ],
    usage=("Build and run", "bash", """git submodule update --init
cd build && mkdir avx512 && cd avx512 && cmake ../.. && make && cd ..
numactl -N 0 -m 0 ./avx512/Tester configs/ST_Config.txt outST.txt analysis"""),
    links=[("Source code", "https://github.com/saltsystemslab/BreadcrumbFilter")],
))

P.append(dict(
    slug="zombie-hashing", name="Zombie Hashing", area="hashtables",
    tagline="Linear probing with consistent performance at high load",
    tags=["C", "C++"],
    overview=[
        "Zombie Hashing is a linear probing scheme that keeps performance consistent and data locality high, even at high load factors. Linear probing tables use tombstones (deletion markers) to speed up operations and reduce primary clustering. Those tombstones must be redistributed periodically, which halts all operations and makes performance uneven.",
        "Zombie Hashing redistributes tombstones within small windows instead, so the table never needs to stop. It comes in two variants: an ordered compact table and an unordered vectorized table based on Abseil.",
    ],
    features=[
        ("No global rebuilds", "Tombstones are redistributed locally, so operations never stop."),
        ("Two variants", "An ordered compact linear probing table and an unordered vectorized table built on Abseil."),
        ("High load factors", "Evaluated at 75%, 85%, and 95% load under churn."),
        ("Churn benchmarks", "Measures both throughput and latency against RobinHood, Graveyard, Iceberg, CLHT, and Abseil."),
    ],
    usage=("Quick start", "bash", """git clone https://github.com/saltsystemslab/ZombieHT && cd ZombieHT
./setup.sh
./run_throughput.sh   # churn throughput experiments
./run_latency.sh      # churn latency experiments
./plot_data.sh        # report at ./bench/report/main.pdf"""),
    links=[("Source code", "https://github.com/saltsystemslab/ZombieHT")],
))

P.append(dict(
    slug="cqf", name="Counting Quotient Filter", short="CQF", area="filters",
    tagline="A general-purpose counting filter",
    tags=["C", "SIGMOD 2017"],
    overview=[
        "The Counting Quotient Filter (CQF) supports approximate membership testing and counts how often each item occurs in a dataset. Like a Bloom filter it can return false positives, but it is a general-purpose approximate membership query (AMQ) structure designed so that every bit counts.",
        "The CQF is small and fast, has good locality of reference, and scales out of RAM to SSD. It supports deletions, counting (even on skewed datasets), resizing, merging, and highly concurrent access.",
    ],
    features=[
        ("Counting", "Space-efficient counts that adapt to skewed datasets."),
        ("Full feature set", "Insertions, deletions, resizing, and merging."),
        ("Cache-friendly", "Good locality of reference, and it scales out of RAM to SSD."),
        ("Concurrent", "Supports highly concurrent access."),
    ],
    usage=("API and build", "c", """qf_insert(item, count);          // insert an item
qf_count_key_value(item);        // count (may over-count, like a Bloom filter)
qf_remove(item, count);          // decrement; count = 0 removes the item

$ make test && ./test 24 8       # Haswell or newer
$ make NH=1 test                 # older CPUs"""),
    links=[("Source code", "https://github.com/saltsystemslab/cqf"),
           ("Paper (SIGMOD 2017)", "https://doi.org/10.1145/3035918.3035963")],
    citation="""@inproceedings{PandeyBJP17,
  author    = {Prashant Pandey and Michael A. Bender and Rob Johnson and Rob Patro},
  title     = {A General-Purpose Counting Filter: Making Every Bit Count},
  booktitle = {Proceedings of the 2017 ACM International Conference on Management of Data (SIGMOD)},
  pages     = {775--787},
  year      = {2017},
  doi       = {10.1145/3035918.3035963}
}""",
))

P.append(dict(
    slug="vqf", name="Vector Quotient Filter", short="VQF", area="filters",
    tagline="Overcoming the time/space trade-off in filter design",
    tags=["C", "AVX-512", "SIGMOD 2021"],
    overview=[
        "The Vector Quotient Filter (VQF) supports approximate membership testing. Like the quotient filter, it is based on Robin Hood hashing. Unlike the quotient filter, it uses power-of-two-choices hashing to reduce the variance of runs.",
        "As a result, the VQF delivers consistent, high throughput across load factors, and power-of-two-choices hashing also makes it more amenable to concurrent updates. It uses AVX-512 instructions, with an AVX2 fallback.",
    ],
    features=[
        ("Consistent throughput", "Power-of-two-choices hashing keeps performance steady across load factors."),
        ("SIMD", "AVX-512 operations, with an AVX2 implementation as a fallback."),
        ("Concurrent inserts", "A thread-safe build is available."),
        ("Simple API", "vqf_insert, vqf_is_present, and vqf_remove."),
    ],
    usage=("API and build", "c", """vqf_insert(item);        // insert an item
vqf_is_present(item);    // membership (may return false positives)
vqf_remove(item);        // remove an item

$ make main && ./main 24
$ make THREAD=1 main_tx && ./main_tx 24 4    # thread-safe inserts"""),
    links=[("Source code", "https://github.com/saltsystemslab/vqf"),
           ("Paper (SIGMOD 2021)", "https://doi.org/10.1145/3448016.3452841")],
    citation="""@inproceedings{PandeyCDB21,
  author    = {Prashant Pandey and Alex Conway and Joe Durie and Michael A. Bender
               and Martin Farach-Colton and Rob Johnson},
  title     = {Vector Quotient Filters: Overcoming the Time/Space Trade-Off in Filter Design},
  booktitle = {Proceedings of the 2021 ACM International Conference on Management of Data (SIGMOD)},
  year      = {2021}
}""",
))

P.append(dict(
    slug="adaptiveqf", name="Adaptive Quotient Filter", short="AdaptiveQF", area="filters",
    tagline="A quotient filter that adapts to false positives",
    tags=["C", "C++", "SIGMOD 2025"],
    overview=[
        "The Adaptive Quotient Filter (AQF) is an approximate membership filter that learns from its mistakes. It compactly stores fingerprints for keys, and when a false positive is identified it extends the matching fingerprint so the same false positive does not happen again. Like other filters, it never returns false negatives.",
        "To adapt, the AQF uses a reverse map, configured when the filter is created, to recover the original key behind a fingerprint. It is built on the quotient filter and keeps that design's cache efficiency and mergeability.",
    ],
    features=[
        ("Adaptivity", "Extends fingerprints to eliminate repeated false positives."),
        ("Reverse maps", "Uses the built-in LocalMap or SplinterDB maps, or a custom one."),
        ("C and C++ APIs", "A C API in aqf.h and a C++ AdaptiveQF<ReverseMap> wrapper."),
        ("Quotient-filter design", "Keeps cache efficiency and mergeability."),
    ],
    usage=("Quick start", "bash", """make
make -C examples
./examples/adapt_demo        # insert, query, detect a false positive, adapt

make -C tests test_e2e && ./tests/test_e2e"""),
    links=[("Source code", "https://github.com/saltsystemslab/adaptiveqf"),
           ("Paper (arXiv)", "https://arxiv.org/abs/2405.10253"),
           ("Paper (ACM DL)", "https://doi.org/10.1145/3677128")],
    citation="""@article{wen2024aqf,
  author  = {Richard Wen and Hunter McCoy and David Tench and Guido Tagliavini and Michael A. Bender
             and Alex Conway and Martin Farach-Colton and Rob Johnson and Prashant Pandey},
  title   = {Adaptive Quotient Filters},
  journal = {Proceedings of the ACM on Management of Data},
  volume  = {2},
  number  = {4},
  articleno = {192},
  year    = {2024},
  doi     = {10.1145/3677128}
}""",
))

P.append(dict(
    slug="iceberg", name="IcebergHT", area="hashtables",
    tagline="High-performance hash tables through stability and low associativity",
    tags=["C", "PMEM", "SIGMOD 2023"],
    overview=[
        "IcebergHT is a fast, concurrent, and resizable hash table for 64-bit keys and values. It supports insertions, deletions, and queries.",
        "Iceberg hashing is the first hash-table design to be both stable (items stay where they are first placed) and low-associativity (each item can live in only a few places). That combination keeps operations cache- and I/O-efficient, both in DRAM and on persistent memory.",
    ],
    features=[
        ("Stable and low associativity", "The first hash-table design with both properties."),
        ("Concurrent and resizable", "Scales across threads and grows in place."),
        ("Persistent memory", "Optional PMEM build."),
        ("Vectorized", "Uses vector instructions to speed up operations."),
    ],
    usage=("API and build", "c", """iceberg_insert(key, value);     // insert a key-value pair
iceberg_get_value(key);         // look up a value
iceberg_remove(key);            // remove a key

$ make main && ./main -s 24 -t 4                        # 2^24 slots, 4 threads
$ PMEM=1 make main && ./main -p /path/to/pmem -s 24 -t 4"""),
    links=[("Source code", "https://github.com/saltsystemslab/iceberghashtable"),
           ("Paper (ACM DL)", "https://doi.org/10.1145/3588727"),
           ("Paper (arXiv)", "https://arxiv.org/abs/2210.04068")],
    citation="""@article{pandey2023iceberght,
  author  = {Prashant Pandey and Michael A. Bender and Alex Conway and Mart{\\'\\i}n Farach-Colton
             and William Kuszmaul and Guido Tagliavini and Rob Johnson},
  title   = {IcebergHT: High Performance Hash Tables Through Stability and Low Associativity},
  journal = {Proceedings of the ACM on Management of Data},
  volume  = {1},
  number  = {1},
  year    = {2023},
  doi     = {10.1145/3588727}
}""",
))

BY_SLUG = {p["slug"]: p for p in P}
assert sorted(BY_SLUG) == sorted(s for v in ORDER.values() for s in v)

e = html.escape


def page(p):
    area_name, tone, _ = AREAS[p["area"]]
    tags = "".join(f'<span class="chip">{e(t)}</span>' for t in p.get("tags", []))
    body = []
    if p.get("todo"):
        body.append(f'<div class="todo">{e(p["todo"])}</div>')
    if p.get("overview"):
        body.append("<h2>Overview</h2>" + "".join(f"<p>{e(x)}</p>" for x in p["overview"]))
    if p.get("features"):
        items = "".join(f'<div class="feature"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in p["features"])
        body.append(f'<h2>Key features</h2><div class="features">{items}</div>')
    if p.get("usage"):
        title, lang, code = p["usage"]
        body.append(f'<h2>{e(title)}</h2><pre><code class="lang-{lang}">{e(code)}</code></pre>')
    if p.get("citation"):
        body.append(f'<h2>Citation</h2><pre><code>{e(p["citation"])}</code></pre>')

    links = "".join(f'<li><a href="{e(u)}">{e(t)} →</a></li>' for t, u in p["links"])
    related = [BY_SLUG[x] for x in ORDER[p["area"]] if x != p["slug"]]
    rel = "".join(f'<li><a href="{e(url_for(q))}">{e(q["name"])}</a><span>{e(q["tagline"])}</span></li>'
                  if url_for(q) else f'<li><strong>{e(q["name"])}</strong><span>Coming soon</span></li>'
                  for q in related)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(p["name"])} · SALT Systems Lab</title>
  <meta name="description" content="{e(p["name"])}: {e(p["tagline"])}. An open-source project from SALT Systems Lab.">
  <link rel="icon" type="image/svg+xml" href="../assets/logo-mark.svg">
  <link rel="stylesheet" href="../assets/style.css">
</head>
<body class="{tone}">

<header class="site">
  <div class="wrap">
    <a class="brand" href="../"><img class="mark" src="../assets/logo-mark.svg" alt=""> SALT Systems Lab</a>
    <nav class="main">
      <a href="../">Home</a>
      <a href="../projects.html" aria-current="page">Projects</a>
      <a href="https://github.com/saltsystemslab">GitHub</a>
    </nav>
  </div>
</header>

<main>
  <div class="wrap hero detail-hero">
    <p class="crumbs"><a href="../projects.html">Projects</a> / <a href="../projects.html#{p["area"]}">{e(area_name)}</a></p>
    <h1>{e(p["name"])}</h1>
    <p class="lede">{e(p["tagline"])}</p>
    <div class="meta">{tags}</div>
  </div>

  <div class="wrap detail">
    <article class="prose">
      {"".join(body)}
    </article>
    <aside class="side">
      <div class="side-box">
        <h3>Links</h3>
        <ul class="side-links">{links}</ul>
      </div>
      <div class="side-box">
        <h3>More in {e(area_name)}</h3>
        <ul class="related">{rel}</ul>
      </div>
    </aside>
  </div>
</main>

<footer class="site">
  <div class="wrap">
    <span>© SALT Systems Lab, Northeastern University</span>
    <span><a href="https://github.com/saltsystemslab">GitHub</a> · <a href="https://prashantpandey.github.io/">Prashant Pandey</a></span>
  </div>
</footer>

</body>
</html>
"""



def redirect(p):
    url = e(SITES[p["slug"]])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{e(p["name"])} · SALT Systems Lab</title>
  <link rel="canonical" href="{url}">
  <meta http-equiv="refresh" content="0; url={url}">
</head>
<body>
  <p>{e(p["name"])} has moved to <a href="{url}">{url}</a>.</p>
</body>
</html>
"""


def card(p):
    tags = "".join(f'<span class="chip">{e(t)}</span>' for t in p.get("tags", []))
    body = f'<p>{e(SUMMARY[p["slug"]])}</p>' if p["slug"] in SUMMARY else ""
    href = url_for(p, "projects/")
    code = next((u for t, u in p["links"] if t == "Source code"), None)
    paper = next((u for t, u in p["links"] if t.startswith("Paper")), None)
    site = next((u for t, u in p["links"] if t == "Project website"), None)
    if p["slug"] in COMING_SOON:
        links = []
    elif p["slug"] in SITES:
        links = [f'<a href="{e(href)}">Project site ↗</a>']
    else:
        links = [f'<a href="{href}">Details</a>']
        if site: links.append(f'<a href="{e(site)}">Website</a>')
    if code: links.append(f'<a href="{e(code)}">Code</a>')
    if paper: links.append(f'<a href="{e(paper)}">Paper</a>')
    return f"""
        <article class="project" id="{p["slug"]}">
          <h3>{f'<a href="{e(href)}">{e(p["name"])}</a>' if href else e(p["name"])}{' <span class="soon">Coming soon</span>' if not href else ""}</h3>
          {f'<p class="tagline">{e(p["tagline"])}</p>' if p["tagline"] else ""}
          {body}
          <div class="meta">{tags}</div>
          {f'<div class="links">{" ".join(links)}</div>' if links else ""}
        </article>"""


def projects_page():
    toc = "\n".join(f'      <a class="{tone}" href="#{k}">{e(name)}</a>' for k, (name, tone, _) in AREAS.items())
    sections = []
    for k, (name, tone, sub) in AREAS.items():
        cards = "".join(card(BY_SLUG[s]) for s in ORDER[k])
        sections.append(f"""
  <section id="{k}" class="{tone}">
    <div class="wrap">
      <div class="group-head"><span class="dot"></span><h2>{e(name)}</h2></div>
      <p class="sub">{e(sub)}</p>
      <div class="projects">{cards}
      </div>
    </div>
  </section>""")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Projects · SALT Systems Lab</title>
  <meta name="description" content="Open-source projects from SALT Systems Lab: filters, hash tables, GPU data management, and AI systems.">
  <link rel="icon" type="image/svg+xml" href="assets/logo-mark.svg">
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>

<header class="site">
  <div class="wrap">
    <a class="brand" href="./"><img class="mark" src="assets/logo-mark.svg" alt=""> SALT Systems Lab</a>
    <nav class="main">
      <a href="./">Home</a>
      <a href="projects.html" aria-current="page">Projects</a>
      <a href="https://github.com/saltsystemslab">GitHub</a>
    </nav>
  </div>
</header>

<main>
  <div class="wrap hero" style="padding-bottom: 40px">
    <p class="eyebrow">Projects</p>
    <h1>Open-source systems from SALT.</h1>
    <p class="lede">{len(P)} projects in {len(AREAS)} areas, released with code, benchmarks, and the papers behind them.</p>
    <div class="toc">
{toc}
    </div>
  </div>
{"".join(sections)}
</main>

<footer class="site">
  <div class="wrap">
    <span>© SALT Systems Lab, Northeastern University</span>
    <span><a href="https://github.com/saltsystemslab">GitHub</a> · <a href="https://prashantpandey.github.io/">Prashant Pandey</a></span>
  </div>
</footer>

</body>
</html>
"""


def area_tiles():
    out = []
    for k, (name, tone, sub) in AREAS.items():
        chips = "".join(f'<span class="chip">{e(BY_SLUG[s].get("short", BY_SLUG[s]["name"]))}</span>' for s in ORDER[k])
        out.append(f"""        <a class="area {tone}" href="projects.html#{k}">
          <h3>{e(name)}</h3>
          <p>{e(sub)}</p>
          <div class="names">{chips}</div>
        </a>""")
    return "\n".join(out)


os.makedirs(os.path.join(OUT, "projects"), exist_ok=True)
for p in P:
    path = os.path.join(OUT, "projects", p["slug"] + ".html")
    if p["slug"] in COMING_SOON:
        if os.path.exists(path):
            os.remove(path)
        continue
    with open(path, "w") as f:
        f.write(redirect(p) if p["slug"] in SITES else page(p))
with open(os.path.join(OUT, "projects.html"), "w") as f:
    f.write(projects_page())
with open(os.path.join(OUT, "index.html")) as f:
    idx = f.read()
start = idx.index('<div class="areas">') + len('<div class="areas">')
end = idx.index("      </div>\n    </div>\n  </section>", start)
idx = idx[:start] + "\n" + area_tiles() + "\n" + idx[end:]
with open(os.path.join(OUT, "index.html"), "w") as f:
    f.write(idx)
print(len(P), "pages")
