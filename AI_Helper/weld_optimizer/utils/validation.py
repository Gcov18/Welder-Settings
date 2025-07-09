"""
Validation utilities for welding parameters
"""

from config import PARAMETER_LIMITS, MATERIAL_COMPATIBILITY


def validate_parameter_ranges(parameters):
    """Validate that parameters are within acceptable ranges."""
    errors = []
    warnings = []

    for param, value in parameters.items():
        if param in PARAMETER_LIMITS and value is not None:
            limits = PARAMETER_LIMITS[param]

            if value < limits["min"]:
                errors.append(f"{param} ({value}) is below minimum ({limits['min']})")
            elif value > limits["max"]:
                errors.append(f"{param} ({value}) is above maximum ({limits['max']})")

            # Add warnings for values near limits
            range_size = limits["max"] - limits["min"]
            if value < limits["min"] + 0.1 * range_size:
                warnings.append(f"{param} ({value}) is near minimum recommended value")
            elif value > limits["max"] - 0.1 * range_size:
                warnings.append(f"{param} ({value}) is near maximum recommended value")

    return errors, warnings


def validate_material_compatibility(base_material, filler_material):
    """Check if base and filler materials are compatible."""
    if base_material in MATERIAL_COMPATIBILITY:
        compatible_fillers = MATERIAL_COMPATIBILITY[base_material]
        if filler_material not in compatible_fillers:
            return False, f"{filler_material} may not be suitable for {base_material}"

    return True, "Material combination appears compatible"


def validate_process_parameters(process, parameters):
    """Validate parameters specific to welding process."""
    errors = []
    warnings = []

    voltage = parameters.get("voltage", 0)
    amperage = parameters.get("amperage", 0)
    wire_speed = parameters.get("wire_feed_speed", 0)

    if process == "GMAW":  # MIG
        # Voltage to amperage ratio check
        if voltage > 0 and amperage > 0:
            ratio = voltage / amperage * 100  # V/A * 100
            if ratio < 4:
                warnings.append("Voltage may be too low for amperage (cold weld risk)")
            elif ratio > 12:
                warnings.append("Voltage may be too high for amperage (excessive spatter risk)")

        # Wire feed speed check
        if wire_speed == 0:
            errors.append("Wire feed speed is required for MIG welding")

    elif process == "GTAW":  # TIG
        # TIG typically uses lower voltage
        if voltage > 25:
            warnings.append("High voltage for TIG welding may cause arc instability")

        # Wire feed speed should be 0 for manual TIG
        if wire_speed > 0:
            warnings.append("Wire feed speed not typically used in manual TIG welding")

    elif process == "SMAW":  # Stick
        # Stick welding voltage range
        if voltage < 18:
            warnings.append("Low voltage for stick welding may cause poor arc starting")
        elif voltage > 35:
            warnings.append("High voltage for stick welding may cause excessive spatter")

        # Wire feed speed not applicable
        if wire_speed > 0:
            warnings.append("Wire feed speed not applicable for stick welding")

    elif process == "FCAW":  # Flux Core
        # Similar to MIG but typically higher voltage
        if voltage < 20:
            warnings.append("Voltage may be low for flux core welding")

        if wire_speed == 0:
            errors.append("Wire feed speed is required for flux core welding")

    return errors, warnings


def validate_thickness_parameters(thickness, parameters):
    """Validate parameters against material thickness."""
    warnings = []

    voltage = parameters.get("voltage", 0)
    amperage = parameters.get("amperage", 0)

    if thickness > 0:
        # Rule of thumb: ~30-40A per mm for steel
        expected_amperage = thickness * 35

        if amperage > 0:
            if amperage < expected_amperage * 0.6:
                warnings.append(f"Amperage may be low for {thickness}mm thickness")
            elif amperage > expected_amperage * 1.5:
                warnings.append(f"Amperage may be high for {thickness}mm thickness")

        # Voltage relationship with thickness
        if thickness > 10 and voltage < 20:
            warnings.append("Consider higher voltage for thick material")
        elif thickness < 3 and voltage > 25:
            warnings.append("Consider lower voltage for thin material")

    return warnings


def comprehensive_validation(parameters, material_info=None):
    """Perform comprehensive validation of all parameters."""
    all_errors = []
    all_warnings = []

    # Basic parameter range validation
    errors, warnings = validate_parameter_ranges(parameters)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # Material compatibility
    if material_info:
        is_compatible, message = validate_material_compatibility(
            material_info.get("base_material"), material_info.get("filler_material")
        )
        if not is_compatible:
            all_warnings.append(message)

    # Process-specific validation
    process = parameters.get("process")
    if process:
        errors, warnings = validate_process_parameters(process, parameters)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    # Thickness validation
    thickness = parameters.get("thickness")
    if thickness:
        warnings = validate_thickness_parameters(thickness, parameters)
        all_warnings.extend(warnings)

    return {
        "valid": len(all_errors) == 0,
        "errors": all_errors,
        "warnings": all_warnings,
        "severity": "error" if all_errors else "warning" if all_warnings else "ok",
    }


def suggest_parameter_adjustments(parameters, validation_result):
    """Suggest parameter adjustments based on validation results."""
    suggestions = []

    if not validation_result["valid"]:
        return ["Please fix validation errors before proceeding"]

    voltage = parameters.get("voltage", 0)
    amperage = parameters.get("amperage", 0)
    thickness = parameters.get("thickness", 0)

    # Suggest optimizations
    if voltage > 0 and amperage > 0:
        # Power calculation
        power = voltage * amperage

        if thickness > 0:
            power_per_mm = power / thickness

            if power_per_mm < 500:
                suggestions.append("Consider increasing power for better penetration")
            elif power_per_mm > 2000:
                suggestions.append("Consider reducing power to prevent burn-through")

    # Travel speed suggestions
    travel_speed = parameters.get("travel_speed", 0)
    if travel_speed > 0 and thickness > 0:
        if travel_speed > 15 and thickness > 5:
            suggestions.append("Reduce travel speed for thick material to ensure penetration")
        elif travel_speed < 5 and thickness < 3:
            suggestions.append("Increase travel speed for thin material to prevent burn-through")

    return suggestions if suggestions else ["Parameters look good!"]
