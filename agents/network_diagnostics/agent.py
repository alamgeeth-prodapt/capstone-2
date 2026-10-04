import sqlite3
from pathlib import Path
from google.adk.agents import Agent
from dotenv import load_dotenv
import os

load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    raise RuntimeError("GEMINI_API_KEY is not configured.")

# Project root: D:\Project_2
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "telecom_ops.db"


def check_tower_status(tower_id: str) -> dict:
    """
    Return the current status and latest performance metrics for a tower.
    """

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        tower = connection.execute(
            """
            SELECT
                tower_id,
                tower_name,
                region,
                city,
                state,
                technology,
                status,
                latitude,
                longitude
            FROM network_towers
            WHERE tower_id = ?
            """,
            (tower_id,),
        ).fetchone()

        if tower is None:
            return {
                "success": False,
                "tower_id": tower_id,
                "error": f"Tower {tower_id} was not found.",
            }

        performance = connection.execute(
            """
            SELECT
                recorded_at,
                latency_ms,
                packet_loss_pct,
                downlink_throughput_mbps,
                uplink_throughput_mbps,
                signal_strength_dbm,
                active_connections
            FROM tower_performance
            WHERE tower_id = ?
            ORDER BY recorded_at DESC
            LIMIT 1
            """,
            (tower_id,),
        ).fetchone()

        incident = connection.execute(
            """
            SELECT
                incident_id,
                severity,
                status,
                title,
                description,
                opened_at,
                classification,
                assigned_team
            FROM open_incidents
            WHERE tower_id = ?
            ORDER BY opened_at DESC
            LIMIT 1
            """,
            (tower_id,),
        ).fetchone()

        return {
            "success": True,
            "tower": dict(tower),
            "latest_performance": (
                dict(performance) if performance else None
            ),
            "open_incident": (
                dict(incident) if incident else None
            ),
        }

    finally:
        connection.close()

def run_connectivity_diagnostics(tower_id: str, symptom: str) -> dict:
    """
    Diagnose connectivity issues using the latest tower performance data.
    """

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        tower = connection.execute(
            """
            SELECT
                tower_id,
                tower_name,
                technology,
                status,
                region,
                city,
                state
            FROM network_towers
            WHERE tower_id = ?
            """,
            (tower_id,),
        ).fetchone()

        if tower is None:
            return {
                "success": False,
                "tower_id": tower_id,
                "error": f"Tower {tower_id} was not found.",
            }

        performance = connection.execute(
            """
            SELECT
                recorded_at,
                latency_ms,
                packet_loss_pct,
                downlink_throughput_mbps,
                uplink_throughput_mbps,
                signal_strength_dbm,
                active_connections
            FROM tower_performance
            WHERE tower_id = ?
            ORDER BY recorded_at DESC
            LIMIT 1
            """,
            (tower_id,),
        ).fetchone()

        if performance is None:
            return {
                "success": False,
                "tower_id": tower_id,
                "error": "No performance data found for this tower.",
            }

        p = dict(performance)
        t = dict(tower)

        findings = []
        recommendations = []

        # Site-down condition
        if t["status"] == "OFFLINE" or p["packet_loss_pct"] == 100:
            findings.append("The site is down.")
            recommendations.append(
                "Investigate the tower/site infrastructure rather than the handset."
            )

        # Signal strength
        signal = p["signal_strength_dbm"]

        if signal >= -90:
            findings.append("Signal strength is acceptable.")
        elif signal >= -110:
            findings.append("Signal strength is marginal.")
            recommendations.append(
                "Investigate radio coverage and signal conditions."
            )
        else:
            findings.append("Signal strength is poor.")
            recommendations.append(
                "Investigate radio access and coverage conditions."
            )

        # Packet loss
        packet_loss = p["packet_loss_pct"]

        if packet_loss > 5:
            findings.append("Packet loss is severe.")
            recommendations.append(
                "Investigate network connectivity and packet-loss causes."
            )
        elif packet_loss > 2:
            findings.append("Packet loss is elevated.")
            recommendations.append(
                "Investigate packet loss and backhaul connectivity."
            )
        elif packet_loss <= 1:
            findings.append("Packet loss is normal.")

        # Latency
        latency = p["latency_ms"]

        if t["technology"] == "5G":
            if latency > 50:
                findings.append("Latency is elevated for 5G.")
                recommendations.append(
                    "Investigate latency and network path performance."
                )
            elif latency <= 40:
                findings.append("Latency is normal for 5G.")
        else:
            if latency > 50:
                findings.append("Latency is elevated.")
                recommendations.append(
                    "Investigate network path performance."
                )

        # 5G throughput
        if (
            t["technology"] == "5G"
            and t["status"] == "OPERATIONAL"
            and p["downlink_throughput_mbps"] < 100
        ):
            findings.append("5G downlink throughput is degraded.")
            recommendations.append(
                "Investigate 5G radio and network throughput."
            )

        return {
            "success": True,
            "tower_id": tower_id,
            "symptom": symptom,
            "tower": t,
            "latest_performance": p,
            "findings": findings,
            "recommendations": recommendations,
        }

    finally:
        connection.close()

def get_regional_network_summary(region: str) -> dict:
    """
    Return a health summary for towers in a region.
    """

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        towers = connection.execute(
            """
            SELECT
                tower_id,
                tower_name,
                technology,
                status,
                city,
                state
            FROM network_towers
            WHERE region = ?
            ORDER BY tower_id
            """,
            (region,),
        ).fetchall()

        if not towers:
            return {
                "success": False,
                "region": region,
                "error": f"No towers found in region: {region}",
            }

        tower_ids = [tower["tower_id"] for tower in towers]

        # Get the latest performance record for every tower.
        performance = {}

        for tower_id in tower_ids:
            row = connection.execute(
                """
                SELECT
                    recorded_at,
                    latency_ms,
                    packet_loss_pct,
                    downlink_throughput_mbps,
                    uplink_throughput_mbps,
                    signal_strength_dbm,
                    active_connections
                FROM tower_performance
                WHERE tower_id = ?
                ORDER BY recorded_at DESC
                LIMIT 1
                """,
                (tower_id,),
            ).fetchone()

            if row:
                performance[tower_id] = dict(row)

        total_towers = len(towers)

        operational = sum(
            1 for tower in towers
            if tower["status"] == "OPERATIONAL"
        )

        degraded = sum(
            1 for tower in towers
            if tower["status"] == "DEGRADED"
        )

        offline = sum(
            1 for tower in towers
            if tower["status"] == "OFFLINE"
        )

        maintenance = sum(
            1 for tower in towers
            if tower["status"] == "MAINTENANCE"
        )

        return {
            "success": True,
            "region": region,
            "summary": {
                "total_towers": total_towers,
                "operational": operational,
                "degraded": degraded,
                "offline": offline,
                "maintenance": maintenance,
            },
            "tower_performance": performance,
            "towers": [dict(tower) for tower in towers],
        }

    finally:
        connection.close()

# if __name__ == "__main__":
#     print("=== CHECK TOWER STATUS ===")
#     result = check_tower_status("TX-512")
#     print(result)

#     print("\n=== CONNECTIVITY DIAGNOSTICS ===")
#     result = run_connectivity_diagnostics(
#         "TX-512",
#         "Customers reporting slow connectivity"
#     )
#     print(result)

#     print("\n=== REGIONAL NETWORK SUMMARY ===")
#     result = get_regional_network_summary("Midwest")
#     print(result)

root_agent = Agent(
    name="network_diagnostics_agent",
    model="gemini-3.8-flash",
    description=(
        "A network diagnostics specialist that investigates "
        "telecom tower health, connectivity problems, and "
        "regional network conditions."
    ),
    instruction="""
You are a Network Diagnostics specialist.

Your job is to investigate telecom network problems using the
SQL-backed tools provided to you.

Available tools:

1. check_tower_status
   - Use this when you need the current status, latest performance
     metrics, or open incident for a specific tower.

2. run_connectivity_diagnostics
   - Use this when a user reports a connectivity symptom for a
     specific tower.
   - Analyze the latest network performance data and return findings
     and recommendations.

3. get_regional_network_summary
   - Use this when the user asks about the health of a region.
   - Summarize tower operational, degraded, offline, and maintenance
     states.

Rules:
- Always use the tools to obtain network data.
- Do not invent tower information or network metrics.
- If a tower or region is not found, clearly report that.
- Base your diagnosis on the returned SQL data.
- Give concise, operationally useful conclusions.
""",
    tools=[
        check_tower_status,
        run_connectivity_diagnostics,
        get_regional_network_summary,
    ],
)