"""
FastAPI Server
==============

REST API for interacting with the Hyperbion Tripolar Network.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import tempfile
import os

from ..core.network import HyperbionNetwork
from ..core.gabriel_cell import PlasticityParams
from ..persistence.persistence import NetworkPersistence
from ..persistence.exporters import (
    JSONExporter,
    GraphMLExporter,
    LaTeXExporter,
    CSVExporter
)


# ============================================================================
# Pydantic Models
# ============================================================================

class CreateNetworkRequest(BaseModel):
    name: str = "HyperbionNetwork"


class AddCellRequest(BaseModel):
    state: int = Field(default=0, ge=-1, le=1)
    bias: float = 0.0


class ConnectCellsRequest(BaseModel):
    source_id: int
    target_id: int
    weight: float


class ApplyOperatorRequest(BaseModel):
    operator: str
    targets: List[int]
    parameters: Optional[Dict[str, Any]] = None


class StepRequest(BaseModel):
    inputs: Optional[Dict[int, int]] = None
    noise_level: float = 0.0
    apply_plasticity: bool = True
    auto_trigger_operators: bool = True


class CreateClusterRequest(BaseModel):
    cell_ids: List[int]
    metadata: Optional[Dict[str, Any]] = None


class ExportRequest(BaseModel):
    format: str = Field(default="json", pattern="^(json|graphml|latex|csv)$")


# ============================================================================
# Global Network Storage
# ============================================================================

# In production, use proper database or session management
_networks: Dict[str, HyperbionNetwork] = {}
_active_network_id: Optional[str] = None


def create_network(name: str = "HyperbionNetwork") -> str:
    """Create a new network and return its ID."""
    global _active_network_id

    network = HyperbionNetwork(name=name)
    network_id = f"{name}_{id(network)}"

    _networks[network_id] = network
    _active_network_id = network_id

    return network_id


def get_network(network_id: Optional[str] = None) -> HyperbionNetwork:
    """Get network by ID or return active network."""
    if network_id is None:
        network_id = _active_network_id

    if network_id is None or network_id not in _networks:
        raise HTTPException(status_code=404, detail="Network not found")

    return _networks[network_id]


# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="Hyperbion Tripolar Network API",
    description="REST API for the Hyperbion self-organizing neural network",
    version="1.0.0"
)


@app.get("/")
def root():
    """API root endpoint."""
    return {
        "name": "Hyperbion Tripolar Network API",
        "version": "1.0.0",
        "active_networks": len(_networks),
        "documentation": "/docs"
    }


# ============================================================================
# Network Management
# ============================================================================

@app.post("/network/create")
def api_create_network(request: CreateNetworkRequest):
    """Create a new network."""
    network_id = create_network(request.name)
    network = get_network(network_id)

    return {
        "network_id": network_id,
        "name": network.name,
        "status": "created"
    }


@app.get("/network/list")
def api_list_networks():
    """List all networks."""
    return {
        "networks": [
            {
                "id": nid,
                "name": net.name,
                "size": len(net.cells),
                "steps": net.step_count
            }
            for nid, net in _networks.items()
        ]
    }


@app.get("/network/state")
def api_get_network_state(network_id: Optional[str] = None):
    """Get complete network state."""
    network = get_network(network_id)
    return network.get_state()


@app.delete("/network/delete")
def api_delete_network(network_id: str):
    """Delete a network."""
    global _active_network_id

    if network_id not in _networks:
        raise HTTPException(status_code=404, detail="Network not found")

    del _networks[network_id]

    if _active_network_id == network_id:
        _active_network_id = None

    return {"status": "deleted", "network_id": network_id}


# ============================================================================
# Cell Management
# ============================================================================

@app.post("/network/add_cell")
def api_add_cell(
    request: AddCellRequest,
    network_id: Optional[str] = None
):
    """Add a new cell to the network."""
    network = get_network(network_id)
    cell_id = network.add_cell(state=request.state, bias=request.bias)

    return {
        "cell_id": cell_id,
        "state": request.state,
        "bias": request.bias
    }


@app.post("/network/connect")
def api_connect_cells(
    request: ConnectCellsRequest,
    network_id: Optional[str] = None
):
    """Create a connection between cells."""
    network = get_network(network_id)

    success = network.connect_cells(
        request.source_id,
        request.target_id,
        request.weight
    )

    if not success:
        raise HTTPException(status_code=400, detail="Failed to create connection")

    return {
        "source": request.source_id,
        "target": request.target_id,
        "weight": request.weight,
        "status": "connected"
    }


@app.get("/network/cells")
def api_get_cells(network_id: Optional[str] = None):
    """Get all cells in the network."""
    network = get_network(network_id)

    return {
        "cells": [
            {
                "id": cell.id,
                "state": cell.state,
                "bias": cell.bias,
                "connections": len(cell.connections),
                "age": cell.age
            }
            for cell in network.cells.values()
        ]
    }


@app.get("/network/cells/{cell_id}")
def api_get_cell(cell_id: int, network_id: Optional[str] = None):
    """Get detailed information about a specific cell."""
    network = get_network(network_id)

    if cell_id not in network.cells:
        raise HTTPException(status_code=404, detail="Cell not found")

    return network.cells[cell_id].to_dict()


# ============================================================================
# Simulation
# ============================================================================

@app.post("/network/step")
def api_step(
    request: StepRequest,
    network_id: Optional[str] = None
):
    """Execute one simulation step."""
    network = get_network(network_id)

    result = network.step(
        inputs=request.inputs,
        noise_level=request.noise_level,
        apply_plasticity=request.apply_plasticity,
        auto_trigger_operators=request.auto_trigger_operators
    )

    return result


@app.post("/network/run")
def api_run(
    steps: int = 10,
    network_id: Optional[str] = None
):
    """Run multiple simulation steps."""
    network = get_network(network_id)

    results = []
    for _ in range(steps):
        result = network.step()
        results.append(result)

    return {
        "steps_executed": steps,
        "final_step": network.step_count,
        "final_network_size": len(network.cells)
    }


# ============================================================================
# Operators
# ============================================================================

@app.post("/network/apply_operator")
def api_apply_operator(
    request: ApplyOperatorRequest,
    network_id: Optional[str] = None
):
    """Apply an operator to the network."""
    network = get_network(network_id)

    try:
        params = request.parameters or {}
        result = network.apply_operator(
            request.operator,
            request.targets,
            **params
        )

        return {
            "operator": result.operator_type,
            "success": result.success,
            "affected_cells": result.affected_cells,
            "metrics": result.metrics,
            "message": result.message
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/network/operators")
def api_get_operators(network_id: Optional[str] = None):
    """Get information about all operators."""
    network = get_network(network_id)

    return {
        "operators": {
            name: op.get_statistics()
            for name, op in network.operators.items()
        }
    }


@app.get("/network/operator_history")
def api_get_operator_history(network_id: Optional[str] = None):
    """Get operator application history."""
    network = get_network(network_id)

    return {
        "history": [
            {
                "operator": result.operator_type,
                "timestamp": result.timestamp,
                "affected_cells": result.affected_cells,
                "success": result.success
            }
            for result in network.operator_history
        ]
    }


# ============================================================================
# Clusters
# ============================================================================

@app.post("/network/create_cluster")
def api_create_cluster(
    request: CreateClusterRequest,
    network_id: Optional[str] = None
):
    """Create a cluster from cells."""
    network = get_network(network_id)

    cluster_id = network.create_cluster(request.cell_ids, request.metadata)

    return {
        "cluster_id": cluster_id,
        "size": len(request.cell_ids)
    }


@app.post("/network/auto_detect_clusters")
def api_auto_detect_clusters(
    min_size: int = 3,
    network_id: Optional[str] = None
):
    """Automatically detect clusters."""
    network = get_network(network_id)

    cluster_ids = network.auto_detect_clusters(min_cluster_size=min_size)

    return {
        "detected_clusters": len(cluster_ids),
        "cluster_ids": cluster_ids
    }


@app.get("/network/clusters")
def api_get_clusters(network_id: Optional[str] = None):
    """Get all clusters."""
    network = get_network(network_id)

    return {"clusters": network.clusters}


# ============================================================================
# Export
# ============================================================================

@app.post("/network/export")
def api_export(
    request: ExportRequest,
    network_id: Optional[str] = None
):
    """Export network to various formats."""
    network = get_network(network_id)

    # Create temporary file
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix=f'.{request.format}',
        delete=False
    ) as tmp:
        tmp_path = tmp.name

    try:
        # Export based on format
        if request.format == "json":
            JSONExporter.export(network, tmp_path)
            media_type = "application/json"

        elif request.format == "graphml":
            GraphMLExporter.export(network, tmp_path)
            media_type = "application/xml"

        elif request.format == "latex":
            LaTeXExporter.export(network, tmp_path)
            media_type = "application/x-latex"

        elif request.format == "csv":
            CSVExporter.export_cells(network, tmp_path)
            media_type = "text/csv"

        else:
            raise HTTPException(status_code=400, detail="Invalid format")

        # Return file
        return FileResponse(
            tmp_path,
            media_type=media_type,
            filename=f"{network.name}.{request.format}"
        )

    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Metrics & History
# ============================================================================

@app.get("/network/metrics")
def api_get_metrics(network_id: Optional[str] = None):
    """Get network metrics."""
    network = get_network(network_id)

    return {"metrics": dict(network.metrics)}


@app.get("/network/history")
def api_get_history(
    event_type: Optional[str] = None,
    network_id: Optional[str] = None
):
    """Get event history."""
    network = get_network(network_id)

    if event_type:
        history = NetworkPersistence.replay_history(network, [event_type])
    else:
        history = network.event_history

    return {"history": history}


# ============================================================================
# Server Startup
# ============================================================================

@app.on_event("startup")
def startup_event():
    """Create default network on startup."""
    create_network("DefaultNetwork")
    print("Hyperbion API started with default network")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
