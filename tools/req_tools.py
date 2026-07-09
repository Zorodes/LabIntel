import math

def calculate_cstr_volume(flow_rate: float, rate_constant: float, conversion: float = 0.8) -> str:
    """
    Calculate CSTR volume using design equation.

    Args:
        flow_rate: Feed flow rate (L/min)
        rate_constant: Reaction rate constant (1/min)
        conversion: Target conversion (0.0-1.0)

    Returns:
        Volume (L) needed for the CSTR
    """
    print("=" * 60)
    print(">>> TOOL CALLED: calculate_cstr_volume")
    print("Inputs:")
    print(f"flow_rate={flow_rate}")
    print(f"rate_constant={rate_constant}")
    print(f"conversion={conversion}")
    print("=" * 60)

    if rate_constant <= 0:
        result = "Error: rate constant must be positive"
        print(f"Output: {result}")
        print("=" * 60)
        return result
    if not 0 < conversion < 1:
        result = "Error: conversion must be between 0 and 1"
        print(f"Output: {result}")
        print("=" * 60)
        return result

    # CSTR design: V = (F/k) * (Xa / (1 - Xa))
    volume = (flow_rate / rate_constant) * (conversion / (1 - conversion))
    result = str(round(volume, 2))
    print(f"Output: {result}")
    print("=" * 60)
    return result


def calculate_residence_time(volume: float, flow_rate: float) -> str:
    """
    Calculate residence time in reactor.

    Args:
        volume: Reactor volume (L)
        flow_rate: Feed flow rate (L/min)

    Returns:
        Residence time (minutes)
    """
    print("=" * 60)
    print(">>> TOOL CALLED: calculate_residence_time")
    print("Inputs:")
    print(f"volume={volume}")
    print(f"flow_rate={flow_rate}")
    print("=" * 60)

    if flow_rate <= 0:
        result = "Error: flow rate must be positive"
        print(f"Output: {result}")
        print("=" * 60)
        return result

    residence_time = volume / flow_rate
    result = str(round(residence_time, 2))
    print(f"Output: {result}")
    print("=" * 60)
    return result


def check_safety_limits(temperature: float, pressure: float, material: str = "stainless_steel") -> str:
    """
    Check if operating conditions are safe.

    Args:
        temperature: Operating temperature (Celsius)
        pressure: Operating pressure (atm)
        material: Reactor material

    Returns:
        Safety status and recommendations
    """
    print("=" * 60)
    print(">>> TOOL CALLED: check_safety_limits")
    print("Inputs:")
    print(f"temperature={temperature}")
    print(f"pressure={pressure}")
    print(f"material={material}")
    print("=" * 60)

    limits = {
        "stainless_steel": {"max_temp": 200, "max_pressure": 20},
        "glass": {"max_temp": 150, "max_pressure": 5},
        "carbon_steel": {"max_temp": 180, "max_pressure": 30}
    }

    if material not in limits:
        result = f"Unknown material: {material}"
        print(f"Output: {result}")
        print("=" * 60)
        return result

    max_temp = limits[material]["max_temp"]
    max_pressure = limits[material]["max_pressure"]

    warnings = []

    if temperature > max_temp:
        warnings.append(f"WARNING: Temperature {temperature}C exceeds limit {max_temp}C for {material}")
    if pressure > max_pressure:
        warnings.append(f"WARNING: Pressure {pressure}atm exceeds limit {max_pressure}atm for {material}")

    if warnings:
        result = " | ".join(warnings)
    else:
        result = f"SAFE: {temperature}C and {pressure}atm are within limits for {material}"

    print(f"Output: {result}")
    print("=" * 60)
    return result


def calculate_pfr_conversion(rate_constant: float, residence_time: float, order: int = 1) -> str:
    """
    Calculate conversion in PFR (Plug Flow Reactor).

    Args:
        rate_constant: Reaction rate constant (1/min)
        residence_time: Residence time (min)
        order: Reaction order (1 or 2)

    Returns:
        Conversion (0.0-1.0)
    """
    print("=" * 60)
    print(">>> TOOL CALLED: calculate_pfr_conversion")
    print("Inputs:")
    print(f"rate_constant={rate_constant}")
    print(f"residence_time={residence_time}")
    print(f"order={order}")
    print("=" * 60)

    if order == 1:
        conversion = 1 - math.exp(-rate_constant * residence_time)
    elif order == 2:
        conversion = (rate_constant * residence_time) / (1 + rate_constant * residence_time)
    else:
        result = "Error: only 1st and 2nd order supported"
        print(f"Output: {result}")
        print("=" * 60)
        return result

    result = str(round(conversion, 3))
    print(f"Output: {result}")
    print("=" * 60)
    return result

# RAG TOOL - queries documents
from tools.rag_service import configure_llama_index, load_index, storage_mtime

_rag_index = None
_rag_index_mtime = 0.0

def query_documents(query: str) -> str:
    """Query uploaded chemical engineering documents for relevant information."""
    global _rag_index, _rag_index_mtime

    print("=" * 60)
    print(">>> TOOL CALLED: query_documents")
    print(f"Query: {query}")
    print("=" * 60)

    current_mtime = storage_mtime()
    if current_mtime == 0:
        result = "No indexed documents found. Upload documents and build the index first."
        print(f"Output: {result}")
        print("=" * 60)
        return result

    if _rag_index is None or current_mtime > _rag_index_mtime:
        try:
            _rag_index = load_index()
            _rag_index_mtime = current_mtime
            index_status = "reloaded"
        except Exception as e:
            result = f"Error loading documents: {str(e)}"
            print(f"Output: {result}")
            print("=" * 60)
            return result
    else:
        index_status = "loaded"

    print(f"Index status: {index_status}")

    try:
        from llama_index.core import Settings

        configure_llama_index()

        print("=" * 60)
        print("Current LLM:", Settings.llm)
        print("Current Embed Model:", Settings.embed_model)
        print("=" * 60)

        query_engine = _rag_index.as_query_engine(
            similarity_top_k=5,
            response_mode="compact",
            llm=Settings.llm,
        )

        response = query_engine.query(query)

        source_nodes = getattr(response, "source_nodes", []) or []
        print(f"Retrieved {len(source_nodes)} source nodes")

        if not source_nodes:
            result = (
                "I could not find relevant information in the indexed documents. "
                "Please ask about content that appears in the uploaded files."
            )
            print(f"Output: {result}")
            print("=" * 60)
            return result

        source_names = []
        for node in source_nodes:
            metadata = getattr(node.node, "metadata", {}) or {}
            file_name = metadata.get("file_name")
            if file_name and file_name not in source_names:
                source_names.append(file_name)

        sources = ", ".join(source_names) if source_names else "indexed documents"
        print(f"Sources: {sources}")
        result = f"{response}\n\nSources: {sources}"
        print(f"Output: {result}")
        print("=" * 60)
        return result

    except Exception as e:
        import traceback

        traceback.print_exc()

        result = (
            f"ERROR TYPE: {type(e).__name__}\n"
            f"ERROR: {e}"
        )
        print(f"Output: {result}")
        print("=" * 60)
        return result