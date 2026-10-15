"""Family-resolution tests for MoE / FFN.

Same approach as ``test_attention_families.py``: bags of kernel names
captured from real DSV / Qwen-MoE traces, resolved through the
cheat-sheet in ``moe_families.yaml`` (mirrored as
``_resolve_moe_family`` below).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SKILL_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS = _SKILL_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from ascend_profile import common  # noqa: E402


def _categories_from_kernels(names: list[str]) -> set[str]:
    cats: set[str] = set()
    for n in names:
        c, _ = common.categories_and_roles(n, "", "")
        cats.update(c)
    return cats


def _resolve_moe_family(names: list[str]) -> str:
    """Apply the cheat-sheet from moe_families.yaml."""
    cats = _categories_from_kernels(names)
    has_fused = "moe.dispatch_expert_compute" in cats
    has_dispatch = "moe.dispatch" in cats
    has_combine = "moe.combine" in cats
    has_gating = "moe.gating" in cats
    has_compute = "compute.matmul" in cats

    if has_fused and has_gating:
        return "fused_mc2"
    if has_dispatch and has_combine and has_gating:
        return "mc2"
    if has_compute and not (has_dispatch or has_combine or has_gating or has_fused):
        return "dense"
    return "other"


_FIXTURES: list[tuple[str, list[str], str]] = [
    # ---------- Dense FFN (Llama / Qwen / Mistral) ----------
    (
        "Llama_dense_ffn",
        # gate/up/down projection BMM only.
        ["MatMulV2", "SwiGlu", "AddRmsNorm"],
        "dense",
    ),
    # ---------- MC2 expert-parallel MoE ----------
    (
        "Qwen3MoE_mc2",
        [
            "MoeGatingTopK",
            "MoeDistributeDispatchV2",
            "GroupedMatmul",
            "MoeDistributeCombineV2",
        ],
        "mc2",
    ),
    (
        "DSV3_mc2_with_HC_prefix_around_it",
        # HC* prefix kernels (HCPreSinkhorn / HCPreInvRMS / HCPost) are
        # structural block-head helpers that appear before BOTH attention
        # and MoE blocks. They MUST NOT be filed under moe.gating. The
        # actual moe.gating signal here comes from MoeGatingTopKHash + the
        # dispatch / combine pair, not from the HC* prefix.
        [
            "MoeGatingTopKHash",
            "HCPreSinkhorn",
            "HCPreInvRMS",
            "HCPost",
            "MoeDistributeDispatchV2",
            "GroupedMatmul",
            "MoeDistributeCombineV2",
        ],
        "mc2",
    ),
    # ---------- Fused MC2 (dispatch_ffn_combine) ----------
    (
        "DSV3_fused_mc2_prefill",
        [
            "MoeGatingTopKHash",
            "DispatchFFNCombine",
        ],
        "fused_mc2",
    ),
    (
        "DSV3_fused_mc2_decode",
        [
            "MoeGatingTopKHash",
            "DispatchGmmCombineDecode",
        ],
        "fused_mc2",
    ),
]


@pytest.mark.parametrize("label,kernels,expected_family", _FIXTURES, ids=[c[0] for c in _FIXTURES])
def test_moe_family_resolution(label, kernels, expected_family):
    got = _resolve_moe_family(kernels)
    assert got == expected_family, (
        f"fixture {label}: kernels {kernels} resolved to family {got!r}, "
        f"expected {expected_family!r}"
    )


def test_hc_mhc_prefix_kernels_are_block_head_not_moe_gating():
    """Regression guard for the V3.2/V4 hand-off:

    The HC* / MHC* prefix kernels (HCPreSinkhorn, HCPreInvRMS, HCPost,
    MhcRmsNorm) are structural block-head helpers that appear before
    BOTH attention layers and MoE routing blocks in real DSV4 prefill
    traces. They MUST be tagged ``block_head.mhc_prefix`` and MUST NOT
    be conflated with ``moe.gating``.

    An earlier revision of this skill assumed they were internal to
    ``moe_gating_top_k`` and routed them through ``moe.gating``; that
    broke layers where the same prefix precedes attention. The user
    flagged it as "把正确的改错了" — guard the correct classification
    explicitly here.
    """
    for name in ("HCPreSinkhorn", "HCPreInvRMS", "HCPost", "MhcRmsNorm"):
        cats, roles = common.categories_and_roles(name, "", "")
        cat_set, role_set = set(cats), set(roles)
        assert "block_head.mhc_prefix" in cat_set, (
            f"{name}: expected block_head.mhc_prefix, got {sorted(cat_set)}"
        )
        assert "moe.gating" not in cat_set, (
            f"{name}: must NOT be tagged moe.gating (this would mis-attribute "
            f"a structural prefix to MoE; same kernels also appear before attention)."
        )
        assert "block_head" in role_set, (
            f"{name}: expected role 'block_head', got {sorted(role_set)}"
        )
        assert "moe" not in role_set, (
            f"{name}: must NOT carry the 'moe' role"
        )
