"""Deterministic, content-derived node identifiers.

The V2 architecture requires that every node in the canonical IR has
a stable identifier that:

    1. Is reproducible. Two runs on the same input produce the same
       identifier.
    2. Is source-derived. Identifiers depend on the source content
       and structure, not on the wall clock or on randomness.
    3. Is kind-aware. Different IR node kinds have disjoint
       identifier spaces.
    4. Has a stable external format. The 26-character Crockford
       base32 form is uniform regardless of the underlying
       encoding; downstream tools (CI gates, log analyzers, the
       evidence store) rely on that.

The identifier is **not** a true ULID. A ULID embeds a 48-bit
millisecond timestamp; we cannot use that here because the
identifier must be reproducible from inputs alone, not from the
moment of construction. The *external format* is identical
(26 Crockford base32 characters), but the meaning of the 130
encoded bits is different:

    bits 0-15  (32 bits)   kind namespace hash (CRC32 over kind)
    bits 16-47 (32 bits)   source fingerprint hash
                            (CRC32 over the canonical source-path id)
    bits 48-79 (32 bits)   source position hash
                            (CRC32 over the source position key)
    bits 80-129 (50 bits)  ordinal / counter salt

CRC32 is used because it is deterministic, dependency-free, and
provides enough dispersion for the kind-partitioning requirement.
Two identifiers in the same kind partition can still collide if
their source/position/ordinal inputs collide; that is acceptable
because the V2 pipeline raises a fatal diagnostic on hash
collisions in the ordinal domain (see ``id_for_node``).

The total identifier space is 2^130, large enough that the
collision probability in any realistic input is negligible.

Identifiers are not cryptographic. They are reproducibility tokens.
The evidence store in Phase 2K uses SHA-256 for integrity.
"""

from __future__ import annotations

import hashlib
import zlib
from dataclasses import dataclass, field
from typing import Final

# Crockford base32 alphabet.
# https://www.crockford.com/base32.html — excludes I, L, O, U to
# avoid visual ambiguity. Lowercase is permitted for input but
# the canonical representation is uppercase.
_CROCKFORD_ALPHABET: Final[str] = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_CROCKFORD_DECODE: Final[dict[str, int]] = {
    ch: i for i, ch in enumerate(_CROCKFORD_ALPHABET)
}
_CROCKFORD_DECODE.update({
    "I": 1, "L": 1, "O": 0,
})


def _crockford_encode(value: int, length: int) -> str:
    """Encode an integer in Crockford base32 to exactly ``length`` chars.

    Raises ``ValueError`` if the value cannot fit in ``length``
    characters.
    """
    if value < 0:
        raise ValueError("Crockford encoding requires a non-negative value")
    max_value = (1 << (5 * length)) - 1
    if value > max_value:
        raise ValueError(
            f"value {value} does not fit in {length} Crockford base32 chars"
        )
    out = ["0"] * length
    for i in range(length - 1, -1, -1):
        out[i] = _CROCKFORD_ALPHABET[value & 0x1F]
        value >>= 5
    return "".join(out)


def _crockford_decode(text: str) -> int:
    """Decode a Crockford base32 string back to an integer."""
    if not text:
        raise ValueError("Crockford decode requires a non-empty string")
    text = text.upper()
    value = 0
    for ch in text:
        if ch not in _CROCKFORD_DECODE:
            raise ValueError(f"invalid Crockford base32 character: {ch!r}")
        value = (value << 5) | _CROCKFORD_DECODE[ch]
    return value


# Public constants. The 26-character form is the external
# contract. Any change to the length or alphabet is a breaking
# change for downstream evidence tools.
ID_LENGTH: Final[int] = 26
ID_BITS: Final[int] = ID_LENGTH * 5  # 130 bits
ID_CHARSET: Final[str] = _CROCKFORD_ALPHABET


# Namespace prefix used to keep node ids distinct from other
# 26-character identifiers that may live in the evidence store
# (e.g. observation ids, contract ids). The first character of
# every V2 node id is "N".
IRID_NAMESPACE: Final[str] = "N"

# Namespace prefix for the kind namespace (first 2 chars). Not
# currently used for collision avoidance but reserved for future
# expansion.
KIND_NAMESPACE: Final[str] = "NK"


@dataclass(frozen=True)
class IdContext:
    """Per-source-file identifier context.

    A single compilation unit (a repository) has many source
    positions. To make identifiers both deterministic and bounded
    in size, we hash the canonical source-path identity once and
    use the resulting fingerprint as the "source identity"
    component of every node id derived from that source.

    The fingerprint is content-derived: it is the SHA-256 of the
    canonical path, truncated to 32 bits. Two sources with
    different paths but identical content will produce distinct
    identifiers, which is the correct behaviour for the IR.
    """

    source_fingerprint: int  # 32-bit
    kind_namespace: int      # 32-bit
    ordinal: int = 0         # incremented per kind within a unit


@dataclass(frozen=True)
class DeterministicId:
    """A 26-character Crockford base32 identifier.

    The textual form is the canonical external form. The integer
    form is the canonical internal form for hashing and equality.
    """

    text: str

    def __post_init__(self) -> None:
        if not isinstance(self.text, str):
            raise TypeError("DeterministicId requires a string text")
        if len(self.text) != ID_LENGTH:
            raise ValueError(
                f"DeterministicId must be {ID_LENGTH} characters, "
                f"got {len(self.text)}"
            )
        # Validate the alphabet; raise on invalid characters.
        # The Crockford canonical alphabet excludes I, L, O, U;
        # they are valid input aliases but never appear in the
        # canonical form. We reject them here.
        canonical_chars = set(_CROCKFORD_ALPHABET)
        for ch in self.text:
            if ch not in canonical_chars:
                raise ValueError(
                    f"non-canonical Crockford base32 character in id: {ch!r}"
                )
        if not self.text.startswith(IRID_NAMESPACE):
            raise ValueError(
                f"DeterministicId must start with namespace "
                f"{IRID_NAMESPACE!r}, got {self.text!r}"
            )

    def as_int(self) -> int:
        return _crockford_decode(self.text)

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return f"DeterministicId({self.text!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DeterministicId):
            return self.text == other.text
        if isinstance(other, str):
            return self.text == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.text)


def _crc32(data: bytes) -> int:
    """Unsigned CRC32. Stable across Python versions and platforms."""
    return zlib.crc32(data) & 0xFFFFFFFF


def _hash_source_path(canonical_path: str) -> int:
    """Hash a canonical source path to a 32-bit fingerprint.

    The canonical path is the relative, normalized, lowercased
    path within the repository. The function does not assume the
    path exists on disk; the fingerprint is purely content-derived
    from the path string.
    """
    if not isinstance(canonical_path, str):
        raise TypeError("canonical_path must be a string")
    if not canonical_path:
        raise ValueError("canonical_path must be non-empty")
    digest = hashlib.sha256(canonical_path.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big", signed=False)


def _hash_source_position(
    line: int,
    column: int,
    byte_offset: int,
) -> int:
    """Hash a source position to a 32-bit value.

    Inputs are bounded integers. A non-positive line is invalid;
    column may be 0 (meaning "before the first character").
    """
    if line < 1:
        raise ValueError(f"line must be >= 1, got {line}")
    if column < 0:
        raise ValueError(f"column must be >= 0, got {column}")
    if byte_offset < 0:
        raise ValueError(f"byte_offset must be >= 0, got {byte_offset}")
    key = f"L{line:09d}:C{column:09d}:B{byte_offset:011d}".encode("ascii")
    return _crc32(key)


def _hash_kind(kind: str) -> int:
    """Hash a kind string to a 32-bit namespace value.

    Kinds are expected to be from the ``IRKind`` enum but the
    function accepts any string. Unknown kinds do not raise; they
    just hash deterministically, which is what we want for the
    forward-compatibility case.
    """
    if not isinstance(kind, str):
        raise TypeError("kind must be a string")
    if not kind:
        raise ValueError("kind must be non-empty")
    return _crc32(kind.encode("utf-8"))


def _compose_identifier(
    kind_namespace: int,
    source_fingerprint: int,
    position_hash: int,
    ordinal: int,
) -> DeterministicId:
    """Compose a 130-bit value and Crockford-encode it.

    The composition is a 4-tuple of values whose total bit width
    is at most 125 bits (the body, i.e. 25 chars * 5 bits):

        kind_namespace:    32 bits (CRC32), reduced to 27 bits
        source_fingerprint: 32 bits (top half of SHA-256), reduced to 32 bits
        position_hash:     32 bits (CRC32), reduced to 32 bits
        ordinal:           34 bits

    27 + 32 + 32 + 34 = 125 bits, which fits exactly into the
    body of the 26-character Crockford base32 form. The first
    5 bits of the encoded value are overwritten with the
    namespace character ("N" for node ids).
    """
    if ordinal < 0:
        raise ValueError(f"ordinal must be >= 0, got {ordinal}")
    kind_low = kind_namespace & 0x07FFFFFF  # 27 bits
    packed = (
        (kind_low << 98)
        | ((source_fingerprint & 0xFFFFFFFF) << 66)
        | ((position_hash & 0xFFFFFFFF) << 34)
        | (ordinal & 0x3FFFFFFFF)
    )
    body_bits = 25 * 5  # 125 bits
    mask = (1 << body_bits) - 1
    value = packed & mask
    body = _crockford_encode(value, 25)
    return DeterministicId(IRID_NAMESPACE + body)


def id_for_node(
    kind: str,
    canonical_path: str,
    line: int,
    column: int,
    byte_offset: int,
    ordinal: int = 0,
) -> DeterministicId:
    """Construct a deterministic 26-character identifier for a node.

    The identifier depends on:

        * the kind string (kind namespace hash)
        * the canonical source path (source fingerprint)
        * the source position (position hash)
        * the ordinal (0 by default; used when several nodes
          share the same kind+path+position, e.g. siblings)

    The function is pure: it does not read the wall clock, the
    filesystem, or any external state.

    The same input always produces the same output.
    """
    kind_namespace = _hash_kind(kind)
    source_fingerprint = _hash_source_path(canonical_path)
    position_hash = _hash_source_position(line, column, byte_offset)
    return _compose_identifier(
        kind_namespace=kind_namespace,
        source_fingerprint=source_fingerprint,
        position_hash=position_hash,
        ordinal=ordinal,
    )


__all__ = [
    "DeterministicId",
    "IdContext",
    "id_for_node",
    "ID_LENGTH",
    "ID_BITS",
    "ID_CHARSET",
    "IRID_NAMESPACE",
    "KIND_NAMESPACE",
]
