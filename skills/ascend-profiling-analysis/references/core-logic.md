# Trace analysis logic

The included `scripts/ascend_profile/` package contains the core parser, classifier, cross-rank alignment, diagnostic and report algorithms. Its `knowledge/` directory supplies the taxonomy and semantic contract. A target environment supplies one or more profiler roots with `kernel_details.csv`, trace and communication data.

The processing sequence is normalize → segment → classify → summarize → cross-rank alignment → diagnose → report. Preserve raw-row IDs through every stage. Classify attention and MoE from combinations of kernel signatures rather than model names alone. Distinguish kernel-duration totals from critical-path step time; long communication kernels can overlap compute. Findings must carry evidence links and limitations, especially when ranks or shapes are incomplete.
