"""Synthetic call sites for tool validation; not an Ascend implementation."""
class Block:
    def forward(self, x, q, ops):
        converted = ops.convert(x)
        projected = ops.project(converted)
        transformed = ops.transform(q)
        return ops.consume(projected, transformed)
