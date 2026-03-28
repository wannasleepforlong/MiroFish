"""
LLM Cost Tracker - Tracks token usage for all LLM API calls
Stores data in Supabase for later analysis
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from supabase import create_client, Client
from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('mirofish.llm_cost_tracker')


class LLMCostTracker:
    """Track LLM API calls and token usage per project and simulation"""
    
    _instance: Optional['LLMCostTracker'] = None
    _supabase: Optional[Client] = None
    
    def __new__(cls):
        """Singleton pattern - one instance per app"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize Supabase connection"""
        if self._initialized:
            return
        
        try:
            supabase_url = Config.SUPABASE_URL
            supabase_key = Config.SUPABASE_KEY
            
            if not supabase_url or not supabase_key:
                logger.warning("Supabase credentials not configured, LLM cost tracking disabled")
                self._supabase = None
                self._initialized = True
                return
            
            self._supabase = create_client(supabase_url, supabase_key)
            logger.info("✓ LLMCostTracker initialized with Supabase")
            self._initialized = True
        except Exception as e:
            logger.error(f"✗ Failed to initialize Supabase: {e}")
            self._supabase = None
            self._initialized = True
    
    def track_llm_call(
        self,
        operation_name: str,
        model: str,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        project_id: Optional[str] = None,
        simulation_id: Optional[str] = None,
        user_id: Optional[str] = None       
    ) -> Dict[str, Any]:
        """
        Track an LLM API call
        
        Args:
            operation_name: Operation name (ontology_generation, entity_deduplication, etc.)
            model: Model name (gpt-4, mistral-large, etc.)
            provider: Provider (openai, mistral, etc.)
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            project_id: Project ID (for project-level operations like ontology generation)
            simulation_id: Simulation ID (for simulation-level operations like agent generation)
            
        Returns:
            Dict with 'success' bool and optional 'error' message
            Example: {"success": True} or {"success": False, "error": "..."}
        """
        if not self._supabase:
            error_msg = "Supabase not configured"
            logger.debug(error_msg)
            return {"success": False, "error": error_msg}
        
        # Must have at least one ID
        if not project_id and not simulation_id:
            error_msg = "Must provide either project_id or simulation_id"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        try:
            record = {
                "operation_name": operation_name,
                "model": model,
                "provider": provider,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "project_id": project_id,
                "simulation_id": simulation_id,
                "user_id": user_id  
            }
            
            response = self._supabase.table("llm_usage").insert(record).execute()
            
            # Log with context
            id_str = f"sim={simulation_id}" if simulation_id else f"proj={project_id}"
            logger.info(
                f"✓ LLM call tracked: {operation_name} [{id_str}] | "
                f"input={input_tokens} | output={output_tokens} | model={model}"
            )
            return {"success": True}
        except Exception as e:
            error_msg = f"Failed to track LLM call: {str(e)}"
            logger.error(f"✗ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def get_project_costs(self, project_id: str) -> Dict[str, Any]:
        """
        Get all LLM usage for a project (includes all prep work before simulation)
        
        Args:
            project_id: Project ID
            
        Returns:
            Dict with total tokens and breakdown by operation
        """
        if not self._supabase:
            logger.debug("Supabase not configured, cannot fetch costs")
            return {}
        
        try:
            response = self._supabase.table("llm_usage").select("*").eq("project_id", project_id).execute()
            records = response.data
            
            if not records:
                logger.info(f"No LLM usage records found for project {project_id}")
                return {
                    "project_id": project_id,
                    "total_input_tokens": 0,
                    "total_output_tokens": 0,
                    "total_tokens": 0,
                    "breakdown_by_operation": {},
                    "total_calls": 0
                }
            
            # Calculate totals
            total_input = sum(r["input_tokens"] for r in records)
            total_output = sum(r["output_tokens"] for r in records)
            
            # Breakdown by operation
            breakdown = {}
            for record in records:
                op = record["operation_name"]
                if op not in breakdown:
                    breakdown[op] = {"input_tokens": 0, "output_tokens": 0, "calls": 0}
                breakdown[op]["input_tokens"] += record["input_tokens"]
                breakdown[op]["output_tokens"] += record["output_tokens"]
                breakdown[op]["calls"] += 1
            
            result = {
                "project_id": project_id,
                "total_input_tokens": total_input,
                "total_output_tokens": total_output,
                "total_tokens": total_input + total_output,
                "breakdown_by_operation": breakdown,
                "total_calls": len(records)
            }
            
            logger.info(f"✓ Retrieved costs for project {project_id}: {result['total_tokens']} total tokens")
            return result
        except Exception as e:
            error_msg = f"Failed to get project costs: {str(e)}"
            logger.error(f"✗ {error_msg}")
            return {}
    
    def get_simulation_costs(self, simulation_id: str) -> Dict[str, Any]:
        """
        Get all LLM usage for a simulation
        
        Args:
            simulation_id: Simulation ID
            
        Returns:
            Dict with total tokens and breakdown by operation
        """
        if not self._supabase:
            logger.debug("Supabase not configured, cannot fetch costs")
            return {}
        
        try:
            response = self._supabase.table("llm_usage").select("*").eq("simulation_id", simulation_id).execute()
            records = response.data
            
            if not records:
                logger.info(f"No LLM usage records found for simulation {simulation_id}")
                return {
                    "simulation_id": simulation_id,
                    "total_input_tokens": 0,
                    "total_output_tokens": 0,
                    "total_tokens": 0,
                    "breakdown_by_operation": {},
                    "total_calls": 0
                }
            
            # Calculate totals
            total_input = sum(r["input_tokens"] for r in records)
            total_output = sum(r["output_tokens"] for r in records)
            
            # Breakdown by operation
            breakdown = {}
            for record in records:
                op = record["operation_name"]
                if op not in breakdown:
                    breakdown[op] = {"input_tokens": 0, "output_tokens": 0, "calls": 0}
                breakdown[op]["input_tokens"] += record["input_tokens"]
                breakdown[op]["output_tokens"] += record["output_tokens"]
                breakdown[op]["calls"] += 1
            
            result = {
                "simulation_id": simulation_id,
                "total_input_tokens": total_input,
                "total_output_tokens": total_output,
                "total_tokens": total_input + total_output,
                "breakdown_by_operation": breakdown,
                "total_calls": len(records)
            }
            
            logger.info(f"✓ Retrieved costs for simulation {simulation_id}: {result['total_tokens']} total tokens")
            return result
        except Exception as e:
            error_msg = f"Failed to get simulation costs: {str(e)}"
            logger.error(f"✗ {error_msg}")
            return {}