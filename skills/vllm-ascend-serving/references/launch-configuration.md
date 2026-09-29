# Deriving a serving configuration

Use the checked-out `vllm-ascend/` revision that was selected for the vLLM source pair. Keep a user-provided launch script or explicit topology as the starting point. Fill only unspecified choices from project evidence.

## No launch script or command

Read these sources in order for the requested model, quantization, hardware and features:

1. `vllm-ascend/docs/source/user_guide/support_matrix/supported_models.md` and `supported_features.md` for model and feature support.
2. `vllm-ascend/docs/source/tutorials/models/` for model-specific weights, environment and launch examples.
3. `vllm-ascend/docs/source/user_guide/feature_guide/` for options and interaction limits of requested features such as graph mode, quantization, speculative decoding, context parallelism or expert parallelism.
4. `vllm-ascend/tests/e2e/nightly/single_node/models/configs/` or `tests/e2e/nightly/multi_node/` for a tested case with a similar model, hardware and topology.

Extract the model path, dtype and quantization, context length, execution mode, environment variables and serving flags. Nightly cases may contain test-only paths, ports, request settings or hardware assumptions; adapt them to the actual host and verify flags against the selected code version. When no matching evidence exists, start from the smallest feasible documented configuration, mark unsupported combinations as unknown and validate with a controlled startup and representative request.

## No parallel strategy

Record the request pattern (latency, throughput, long context, MoE or prefill/decode separation), model and KV-cache memory needs, hardware type, available servers and free NPUs on each server. Then choose a topology supported by the model and feature guides:

- Choose the smallest TP degree that fits one model replica and the expected KV cache. Keep TP within a node when practical to reduce cross-node communication.
- Use DP replicas when one replica fits and the goal is more independent request throughput. Map each replica to actual available devices; do not assign all cards merely because they exist.
- Consider PP when one replica must span more devices or nodes and the model's support matrix permits PP. Check layer partitioning and cross-node networking requirements.
- Use EP for a supported MoE configuration, and PCP/DCP for a supported long-context configuration, only after checking the relevant feature compatibility and rank layout. These dimensions do not follow from card count alone.
- For separate prefill and decode services, plan each role's topology and connector with `vllm-ascend-pd-serving`.

Write the final TP/DP/PP/EP/CP values that apply, server-to-rank and rank-to-device mapping, expected world size, model/KV memory budget and source for each nondefault choice. Verify that the available devices and network satisfy the plan before launch. After startup, check health, model listing and one representative request; use performance measurements if the topology was chosen for a performance target.
