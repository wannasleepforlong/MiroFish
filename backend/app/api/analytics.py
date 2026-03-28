"""
Analytics API - Aggregated token usage dashboard data
"""

from flask import jsonify, request
from ..api import analytics_bp
from ..services.llm_cost_tracker import LLMCostTracker
from ..utils.logger import get_logger

logger = get_logger('mirofish.analytics')


@analytics_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """
    Return aggregated token usage across all projects and simulations.

    Response shape:
    {
      "success": true,
      "data": {
        "totals": {
          "input_tokens": 123456,
          "output_tokens": 78900,
          "total_tokens": 202356,
          "total_calls": 42
        },
        "by_operation": {
          "ontology_generation": { "input_tokens": .., "output_tokens": .., "calls": .. },
          ...
        },
        "by_project": [
          { "project_id": "..", "input_tokens": .., "output_tokens": .., "total_tokens": .., "calls": .. },
          ...
        ],
        "by_simulation": [
          { "simulation_id": "..", "input_tokens": .., "output_tokens": .., "total_tokens": .., "calls": .. },
          ...
        ]
      }
    }
    """
    try:
        tracker = LLMCostTracker()

        if not tracker._supabase:
            return jsonify({
                "success": False,
                "error": "Token tracking not configured"
            }), 503

        # Fetch all records
        user_id = request.headers.get("X-User-Id")
        query = tracker._supabase.table("llm_usage").select("*")
        if user_id:
            query = query.eq("user_id", user_id)
        response = query.execute()
        records = response.data or []

        if not records:
            return jsonify({
                "success": True,
                "data": {
                    "totals": {
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0,
                        "total_calls": 0
                    },
                    "by_operation": {},
                    "by_project": [],
                    "by_simulation": []
                }
            })

        # ── Totals ──────────────────────────────────────────────
        total_input  = sum(r["input_tokens"]  for r in records)
        total_output = sum(r["output_tokens"] for r in records)

        # ── By operation ────────────────────────────────────────
        by_operation = {}
        for r in records:
            op = r["operation_name"]
            if op not in by_operation:
                by_operation[op] = {"input_tokens": 0, "output_tokens": 0, "calls": 0}
            by_operation[op]["input_tokens"]  += r["input_tokens"]
            by_operation[op]["output_tokens"] += r["output_tokens"]
            by_operation[op]["calls"]         += 1

        # ── By project ──────────────────────────────────────────
        project_map = {}
        for r in records:
            pid = r.get("project_id")
            if not pid:
                continue
            if pid not in project_map:
                project_map[pid] = {"project_id": pid, "input_tokens": 0, "output_tokens": 0, "calls": 0}
            project_map[pid]["input_tokens"]  += r["input_tokens"]
            project_map[pid]["output_tokens"] += r["output_tokens"]
            project_map[pid]["calls"]         += 1

        by_project = sorted(
            [
                {**v, "total_tokens": v["input_tokens"] + v["output_tokens"]}
                for v in project_map.values()
            ],
            key=lambda x: x["total_tokens"],
            reverse=True
        )

        # ── By simulation ────────────────────────────────────────
        sim_map = {}
        for r in records:
            sid = r.get("simulation_id")
            if not sid:
                continue
            if sid not in sim_map:
                sim_map[sid] = {"simulation_id": sid, "input_tokens": 0, "output_tokens": 0, "calls": 0}
            sim_map[sid]["input_tokens"]  += r["input_tokens"]
            sim_map[sid]["output_tokens"] += r["output_tokens"]
            sim_map[sid]["calls"]         += 1

        by_simulation = sorted(
            [
                {**v, "total_tokens": v["input_tokens"] + v["output_tokens"]}
                for v in sim_map.values()
            ],
            key=lambda x: x["total_tokens"],
            reverse=True
        )

        logger.info(
            f"✓ Dashboard data fetched: {len(records)} records, "
            f"{total_input + total_output} total tokens"
        )

        return jsonify({
            "success": True,
            "data": {
                "totals": {
                    "input_tokens":  total_input,
                    "output_tokens": total_output,
                    "total_tokens":  total_input + total_output,
                    "total_calls":   len(records)
                },
                "by_operation": by_operation,
                "by_project":    by_project,
                "by_simulation": by_simulation
            }
        })

    except Exception as e:
        logger.error(f"✗ Dashboard fetch failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500