def plan(tasks: list[str]) -> list[str]:
    # Deterministic plan: segment -> qa -> tag
    ordered: list[str] = []
    if "segment" in tasks:
        ordered.append("segment")
    if "qa" in tasks:
        ordered.append("qa")
    if "tag" in tasks:
        ordered.append("tag")
    return ordered
