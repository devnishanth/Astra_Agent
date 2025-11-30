from asyncio.subprocess import Process
from mcp.server.fastmcp import FastMCP
import subprocess
import shlex
import asyncio


mcp = FastMCP("WP-server")

@mcp.tool()
async def wp_user_enum_authorid(target: str, range: str = "1-20") -> str:
    """This tool Enumerates Wordpress users via author ID's."""
    cmd = f"python3 Wp_Enum_ID.py -u {target} -r {range}"
    try:
        proc: Process = await asyncio.create_subprocess_exec(
            *shlex.split(cmd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Wait max 120s (can be tuned)
        out, err = await asyncio.wait_for(proc.communicate(), timeout=1000)
        return (out.decode() + err.decode()).strip()

    except asyncio.TimeoutError:
        proc.kill()
        return f"[ERROR] Scan timed out after 120s: {cmd}"
    except Exception as e:
        return f"[ERROR] Failed to run command {cmd}: {str(e)}"

@mcp.tool()
async def wp_user_enum_json(target: str) -> str:
    """This tool Enumerates Wordpress users via exposed JSON endpoint"""
    cmd = f"python3 Wp_Enum_Json.py -u {target}"
    try:
        proc: Process = await asyncio.create_subprocess_exec(
            *shlex.split(cmd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Wait max 120s (can be tuned)
        out, err = await asyncio.wait_for(proc.communicate(), timeout=1000)
        return (out.decode() + err.decode()).strip()

    except asyncio.TimeoutError:
        proc.kill()
        return f"[ERROR] Scan timed out after 120s: {cmd}"
    except Exception as e:
        return f"[ERROR] Failed to run command {cmd}: {str(e)}"

@mcp.tool()
async def wp_brute(target: str) -> str:
    """This brute forces the discovered usernames with default passwords"""
    cmd = f"python3 Brute_user.py --username username --password password --url {target}"
    try:
        proc: Process = await asyncio.create_subprocess_exec(
            *shlex.split(cmd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Wait max 120s (can be tuned)
        out, err = await asyncio.wait_for(proc.communicate(), timeout=1000)
        return (out.decode() + err.decode()).strip()

    except asyncio.TimeoutError:
        proc.kill()
        return f"[ERROR] Scan timed out after 120s: {cmd}"
    except Exception as e:
        return f"[ERROR] Failed to run command {cmd}: {str(e)}"

if __name__ == "__main__":
    # Run MCP server (stdio transport by default)
    mcp.run(transport="stdio")