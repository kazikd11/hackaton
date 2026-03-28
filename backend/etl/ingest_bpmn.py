"""
Ingest BPMN model -> bpmn_nodes.json (cached)

Extracts task nodes and sequence flows from the BPMN XML.
"""
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from .config import CACHE_DIR, DATASET_DIR, ensure_dirs

BPMN_NS = {
    "bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL",
}


def ingest_bpmn(force: bool = False) -> Path:
    ensure_dirs()
    out = CACHE_DIR / "bpmn_nodes.json"
    if not force and out.exists():
        return out

    bpmn_path = None
    for f in sorted(DATASET_DIR.iterdir()):
        if f.suffix == ".bpmn":
            bpmn_path = f
            break

    if bpmn_path is None:
        raise FileNotFoundError("No .bpmn file found in dataset")

    tree = ET.parse(bpmn_path)
    root = tree.getroot()

    nodes: list[dict] = []
    flows: list[dict] = []

    # Find participant names for context
    participants = {}
    for p in root.iter("{http://www.omg.org/spec/BPMN/20100524/MODEL}participant"):
        pid = p.get("id", "")
        pname = p.get("name", "")
        pref = p.get("processRef", "")
        participants[pref] = pname

    # Extract tasks from all processes
    for process in root.iter("{http://www.omg.org/spec/BPMN/20100524/MODEL}process"):
        proc_id = process.get("id", "")
        proc_name = participants.get(proc_id, proc_id)

        for task in process:
            tag = task.tag.split("}")[-1] if "}" in task.tag else task.tag
            if tag in ("userTask", "task", "serviceTask", "scriptTask", "manualTask"):
                nodes.append({
                    "id": task.get("id", ""),
                    "name": task.get("name", ""),
                    "type": tag,
                    "process": proc_name,
                })
            elif tag == "startEvent":
                nodes.append({
                    "id": task.get("id", ""),
                    "name": task.get("name", "Start"),
                    "type": "startEvent",
                    "process": proc_name,
                })
            elif tag == "endEvent":
                nodes.append({
                    "id": task.get("id", ""),
                    "name": task.get("name", "End"),
                    "type": "endEvent",
                    "process": proc_name,
                })
            elif tag == "sequenceFlow":
                flows.append({
                    "id": task.get("id", ""),
                    "source": task.get("sourceRef", ""),
                    "target": task.get("targetRef", ""),
                    "name": task.get("name", ""),
                    "process": proc_name,
                })

    result = {"nodes": nodes, "flows": flows, "participant": list(participants.values())}

    with open(out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    print(f"[ingest_bpmn] {len(nodes)} nodes, {len(flows)} flows -> {out.name}")
    return out


if __name__ == "__main__":
    ingest_bpmn(force="--force" in sys.argv)
