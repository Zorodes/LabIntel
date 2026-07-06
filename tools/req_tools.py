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
    if rate_constant <= 0:
        return "Error: rate constant must be positive"
    if not 0 < conversion < 1:
        return "Error: conversion must be between 0 and 1"

    # CSTR design: V = (F/k) * (Xa / (1 - Xa))
    volume = (flow_rate / rate_constant) * (conversion / (1 - conversion))
    return str(round(volume, 2))


def calculate_residence_time(volume: float, flow_rate: float) -> str:
    """
    Calculate residence time in reactor.

    Args:
        volume: Reactor volume (L)
        flow_rate: Feed flow rate (L/min)

    Returns:
        Residence time (minutes)
    """
    if flow_rate <= 0:
        return "Error: flow rate must be positive"

    residence_time = volume / flow_rate
    return str(round(residence_time, 2))


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
    limits = {
        "stainless_steel": {"max_temp": 200, "max_pressure": 20},
        "glass": {"max_temp": 150, "max_pressure": 5},
        "carbon_steel": {"max_temp": 180, "max_pressure": 30}
    }

    if material not in limits:
        return f"Unknown material: {material}"

    max_temp = limits[material]["max_temp"]
    max_pressure = limits[material]["max_pressure"]

    warnings = []

    if temperature > max_temp:
        warnings.append(f"WARNING: Temperature {temperature}C exceeds limit {max_temp}C for {material}")
    if pressure > max_pressure:
        warnings.append(f"WARNING: Pressure {pressure}atm exceeds limit {max_pressure}atm for {material}")

    if warnings:
        return " | ".join(warnings)
    else:
        return f"SAFE: {temperature}C and {pressure}atm are within limits for {material}"


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
    if order == 1:
        conversion = 1 - math.exp(-rate_constant * residence_time)
    elif order == 2:
        conversion = (rate_constant * residence_time) / (1 + rate_constant * residence_time)
    else:
        return "Error: only 1st and 2nd order supported"

    return str(round(conversion, 3))