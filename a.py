import base64
import struct
import json

def parse_raw_xdr_envelope(xdr_str):
    """
    Partially parse a Soroban/Testnet TransactionEnvelope XDR.
    Outputs a Lab-like dict with available fields.
    """
    xdr_bytes = base64.b64decode(xdr_str)
    length = len(xdr_bytes)

    result = {
        "type": "TransactionEnvelope",
        "data": {
            "raw_length": length,
            "base64": xdr_str,
            "hex": xdr_bytes.hex(),
            "fee": None,
            "seq_num": None,
            "operation_count": None,
            "signatures": [],
            "source_account": None,
            "memo": None,
            "operations": []
        }
    }

    # --- Minimal heuristic parsing ---
    try:
        # Fee: first 8 bytes after type (big-endian uint32)
        if length >= 12:
            fee = struct.unpack(">I", xdr_bytes[4:8])[0]
            result["data"]["fee"] = fee

        # Sequence number: next 8 bytes
        if length >= 16:
            seq_num = struct.unpack(">Q", xdr_bytes[8:16])[0]
            result["data"]["seq_num"] = seq_num

        # Operation count: next 4 bytes after seq_num (simplified)
        if length >= 20:
            op_count = struct.unpack(">I", xdr_bytes[16:20])[0]
            result["data"]["operation_count"] = op_count

        # Signatures: naive approach - last 64 bytes for single signature
        if length >= 84:
            sig_bytes = xdr_bytes[-64:]
            result["data"]["signatures"].append(base64.b64encode(sig_bytes).decode())

        # Operations: only store placeholders
        ops = []
        for i in range(op_count or 0):
            ops.append({"type": "UnknownOp"})
        result["data"]["operations"] = ops

    except Exception as e:
        result["data"]["parse_error"] = str(e)

    return result


# ===== Example usage =====
if __name__ == "__main__":
    xdr_str = "AAAAAgAAAAA5Pg9hOoocs1tB+EVcyj89cvBofVcAoT9qhbYg2ix4XwADDUABQOaKAAAADgAAAAEAAAAAAAAAAAAAAABo3SVjAAAAAAAAAAIAAAAAAAAABgAAAAMAAAAAAAAAAAAAAAJBcmNoaW1lZGVzAAAAAAAAX//PfHIXWrIVIpH//ceRtxw6FBYKA0WuliaOL395PK2hkAAAAef//////////////////8AAAAAAAAAFhg44p42o1uC8d++nR0ARxYW61oI//fFLKJmxWQYdUhK0AAAteYg9IAAAAC15iD0gAAAAAGMAAABkAAAAZQAAAGQAAAAAAAAAAdoseF8AAABASpVmHxUUruTwy58byrPQZihMFFZrbejaOUjj92nzAlJ0XK6rvq2Lp0rJyi2mJCZOgaRobpbIMHK+WAJ3Rj5QAA=="
    parsed = parse_raw_xdr_envelope(xdr_str)
    print(json.dumps(parsed, indent=2))
