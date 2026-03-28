"""Process family endpoints."""

from fastapi import APIRouter, HTTPException

from backend.api.data_loader import (
    load_processes,
    load_process_by_id,
    load_variants,
    load_graph,
    load_steps,
)

router = APIRouter()


@router.get("/processes")
async def get_processes():
    """Return list of all process families with summary metrics."""
    data = load_processes()
    if data is None:
        raise HTTPException(status_code=503, detail="Process data not available")
    return data


@router.get("/processes/{process_id}/variants")
async def get_process_variants(process_id: str):
    """Return variant summary for a specific process family.

    Shows all observed execution paths with frequencies and durations.
    """
    # Verify process exists
    process = load_process_by_id(process_id)
    if process is None:
        raise HTTPException(status_code=404, detail=f"Process '{process_id}' not found")

    data = load_variants(process_id)
    if data is None:
        # Return a minimal response if no variant data exists yet
        return {
            "process_id": process_id,
            "process_name": process.get("name", process_id),
            "total_cases": process.get("total_cases", 0),
            "variant_count": process.get("variant_count", 0),
            "variants": [],
            "happy_path": None,
        }
    return data


@router.get("/processes/{process_id}/graph")
async def get_process_graph(process_id: str):
    """Return the process graph (nodes and edges) for visualization.

    Nodes represent process steps; edges represent transitions with frequencies.
    """
    process = load_process_by_id(process_id)
    if process is None:
        raise HTTPException(status_code=404, detail=f"Process '{process_id}' not found")

    data = load_graph(process_id)
    if data is None:
        return {
            "process_id": process_id,
            "process_name": process.get("name", process_id),
            "nodes": [],
            "edges": [],
        }
    return data


@router.get("/processes/{process_id}/steps")
async def get_process_steps(process_id: str):
    """Return step-level insights for a process family.

    Each step includes metrics and automation signals.
    """
    process = load_process_by_id(process_id)
    if process is None:
        raise HTTPException(status_code=404, detail=f"Process '{process_id}' not found")

    data = load_steps(process_id)
    if data is None:
        return []
    return data
