from mcp.server.fastmcp import FastMCP
from tools.req_tools import (
    calculate_cstr_volume,
    calculate_residence_time,
    check_safety_limits,
    calculate_pfr_conversion
)

mcp = FastMCP("ChemEngTools")

mcp.tool()(calculate_cstr_volume)
mcp.tool()(calculate_residence_time)
mcp.tool()(check_safety_limits)
mcp.tool()(calculate_pfr_conversion)

if __name__ == "__main__":
    mcp.run()