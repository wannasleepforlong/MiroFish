"""
OASIS Simulation Manager
Manages Twitter and Reddit dual-platform parallel simulation
Uses preset scripts + LLM intelligent configuration parameter generation
"""

import os
import json
import shutil
import uuid
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..config import Config
from ..utils.logger import get_logger
from ..utils.llm_client import LLMClient
from .zep_entity_reader import ZepEntityReader, FilteredEntities, EntityNode
from .oasis_profile_generator import OasisProfileGenerator, OasisAgentProfile
from .simulation_config_generator import SimulationConfigGenerator, SimulationParameters

logger = get_logger('mirofish.simulation')


class SimulationStatus(str, Enum):
    """Simulation status"""
    CREATED = "created"
    PREPARING = "preparing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"      # Simulation manually stopped
    COMPLETED = "completed"  # Simulation naturally completed
    FAILED = "failed"


class PlatformType(str, Enum):
    """Platform type"""
    TWITTER = "twitter"
    REDDIT = "reddit"
    LINKEDIN = "linkedin"


@dataclass
class SimulationState:
    """Simulation state"""
    simulation_id: str
    project_id: str
    graph_id: str
    
    # Platform enabled status
    enable_twitter: bool = True
    enable_reddit: bool = True
    enable_linkedin: bool = True
    discover_related_entities: bool = False
    custom_entities: List[Dict[str, str]] = field(default_factory=list)
    
    # Status
    status: SimulationStatus = SimulationStatus.CREATED
    
    # Preparation phase data
    entities_count: int = 0
    profiles_count: int = 0
    entity_types: List[str] = field(default_factory=list)
    discovered_entities_count: int = 0
    
    # Config generation info
    config_generated: bool = False
    config_reasoning: str = ""
    
    # Runtime data
    current_round: int = 0
    twitter_status: str = "not_started"
    reddit_status: str = "not_started"
    linkedin_status: str = "not_started"
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Error information
    error: Optional[str] = None
    user_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Full state dictionary (internal use)"""
        return {
            "simulation_id": self.simulation_id,
            "project_id": self.project_id,
            "graph_id": self.graph_id,
            "enable_twitter": self.enable_twitter,
            "enable_reddit": self.enable_reddit,
            "enable_linkedin": self.enable_linkedin,
            "discover_related_entities": self.discover_related_entities,
            "custom_entities": self.custom_entities,
            "status": self.status.value,
            "entities_count": self.entities_count,
            "profiles_count": self.profiles_count,
            "entity_types": self.entity_types,
            "discovered_entities_count": self.discovered_entities_count,
            "config_generated": self.config_generated,
            "config_reasoning": self.config_reasoning,
            "current_round": self.current_round,
            "twitter_status": self.twitter_status,
            "reddit_status": self.reddit_status,
            "linkedin_status": self.linkedin_status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "error": self.error,
            "user_id": self.user_id,
        }
    
    def to_simple_dict(self) -> Dict[str, Any]:
        """Simplified state dictionary (for API responses)"""
        return {
            "simulation_id": self.simulation_id,
            "project_id": self.project_id,
            "graph_id": self.graph_id,
            "status": self.status.value,
            "entities_count": self.entities_count,
            "profiles_count": self.profiles_count,
            "entity_types": self.entity_types,
            "discover_related_entities": self.discover_related_entities,
            "custom_entities": self.custom_entities,
            "discovered_entities_count": self.discovered_entities_count,
            "config_generated": self.config_generated,
            "error": self.error,
        }


class SimulationManager:
    """
    Simulation Manager
    
    Core functions:
    1. Read and filter entities from Zep graph
    2. Generate OASIS Agent Profiles
    3. Use LLM to intelligently generate simulation configuration parameters
    4. Prepare all files required by preset scripts
    """
    
    # Simulation data storage directory
    SIMULATION_DATA_DIR = os.path.join(
        os.path.dirname(__file__), 
        '../../uploads/simulations'
    )
    
    def __init__(self):
        # Ensure directory exists
        os.makedirs(self.SIMULATION_DATA_DIR, exist_ok=True)
        
        # In-memory simulation state cache
        self._simulations: Dict[str, SimulationState] = {}
    
    def _get_simulation_dir(self, simulation_id: str) -> str:
        """Get simulation data directory"""
        sim_dir = os.path.join(self.SIMULATION_DATA_DIR, simulation_id)
        os.makedirs(sim_dir, exist_ok=True)
        return sim_dir
    
    def _save_simulation_state(self, state: SimulationState):
        """Save simulation state to file"""
        sim_dir = self._get_simulation_dir(state.simulation_id)
        state_file = os.path.join(sim_dir, "state.json")
        
        state.updated_at = datetime.now().isoformat()
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)
        
        self._simulations[state.simulation_id] = state
    
    def _load_simulation_state(self, simulation_id: str) -> Optional[SimulationState]:
        """Load simulation state from file"""
        if simulation_id in self._simulations:
            return self._simulations[simulation_id]
        
        sim_dir = self._get_simulation_dir(simulation_id)
        state_file = os.path.join(sim_dir, "state.json")
        
        if not os.path.exists(state_file):
            return None
        
        with open(state_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        state = SimulationState(
            simulation_id=simulation_id,
            project_id=data.get("project_id", ""),
            graph_id=data.get("graph_id", ""),
            enable_twitter=data.get("enable_twitter", True),
            enable_reddit=data.get("enable_reddit", True),
            enable_linkedin=data.get("enable_linkedin", False),
            discover_related_entities=data.get("discover_related_entities", False),
            custom_entities=data.get("custom_entities", []),
            status=SimulationStatus(data.get("status", "created")),
            entities_count=data.get("entities_count", 0),
            profiles_count=data.get("profiles_count", 0),
            entity_types=data.get("entity_types", []),
            discovered_entities_count=data.get("discovered_entities_count", 0),
            config_generated=data.get("config_generated", False),
            config_reasoning=data.get("config_reasoning", ""),
            current_round=data.get("current_round", 0),
            twitter_status=data.get("twitter_status", "not_started"),
            reddit_status=data.get("reddit_status", "not_started"),
            linkedin_status=data.get("linkedin_status", "not_started"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            error=data.get("error"),
            user_id=data.get('user_id'),
        )
        
        self._simulations[simulation_id] = state
        return state
    
    def create_simulation(
        self,
        project_id: str,
        graph_id: str,
        enable_twitter: bool = True,
        enable_reddit: bool = True,
        enable_linkedin: bool = True,
        discover_related_entities: bool = False,
        custom_entities: Optional[List[Dict[str, str]]] = None,
        user_id: Optional[str] = None,
    ) -> SimulationState:
        """
        Create a new simulation
        
        Args:
            project_id: Project ID
            graph_id: Zep graph ID
            enable_twitter: Whether to enable Twitter simulation
            enable_reddit: Whether to enable Reddit simulation
            enable_linkedin: Whether to enable LinkedIn simulation
            discover_related_entities: Whether to ask the LLM to add relevant missing entities
            custom_entities: User-supplied entity seeds with name/description
            
        Returns:
            SimulationState
        """
        import uuid
        simulation_id = f"sim_{uuid.uuid4().hex[:12]}"
        
        state = SimulationState(
            simulation_id=simulation_id,
            project_id=project_id,
            graph_id=graph_id,
            enable_twitter=enable_twitter,
            enable_reddit=enable_reddit,
            enable_linkedin=enable_linkedin,
            discover_related_entities=discover_related_entities,
            custom_entities=custom_entities or [],
            status=SimulationStatus.CREATED,
            user_id=user_id,
        )
        
        self._save_simulation_state(state)
        logger.info(f"Created simulation: {simulation_id}, project={project_id}, graph={graph_id}")
        
        return state

    def _discover_related_entities(
        self,
        simulation_requirement: str,
        document_text: str,
        entities: List[EntityNode],
        language: str = "en",
        max_entities: int = 5,
    ) -> List[EntityNode]:
        """Use the LLM to infer a small set of relevant entities missing from the uploaded source."""
        if max_entities <= 0:
            return []

        existing_names = {entity.name.strip().lower() for entity in entities if entity.name}
        existing_name_list = [entity.name.strip() for entity in entities if entity.name]
        existing_types = sorted({
            entity.get_entity_type() or "Entity"
            for entity in entities
        })
        entity_preview = [
            {
                "name": entity.name,
                "entity_type": entity.get_entity_type() or "Entity",
                "summary": (entity.summary or "")[:220],
            }
            for entity in entities[:30]
        ]

        if language == "zh":
            system_prompt = (
                "你是社会舆情模拟设计专家。请补充最多5个虽然未在上传材料中明确出现、"
                "但对该话题传播非常相关且适合出现在社交媒体讨论中的真实或高度可信主体。"
                "下面给出的图谱实体名单是硬性排除列表，绝对不能重复、改写、换壳或近似复述。只返回 JSON。"
            )
            user_prompt = f"""请基于以下材料，补充最多 {max_entities} 个“相关但未被明确提及”的实体。

要求：
1. 不要重复已有实体，也不要输出泛泛而谈的抽象概念。
2. 下方“图谱中已找到的实体名称”是严格排除名单。你输出的实体必须与这些名称明显不同，不能是同一实体的改写、别名、上级机构、下级机构、同一人的头衔变体或轻微措辞变化。
2. 实体必须是适合在社交媒体上发声或被讨论的主体，如人物、组织、机构、媒体、社群、公司、政府部门等。
3. 若已有实体类型可复用，优先复用；否则给出最贴切的新类型。
4. 如果没有足够可靠的补充对象，返回空数组。
5. 每个实体 summary 控制在 1-2 句，说明其身份与相关性。

模拟需求：
{simulation_requirement[:3000]}

文档内容摘要：
{document_text[:6000]}

已有实体类型：
{json.dumps(existing_types, ensure_ascii=False)}

图谱中已找到的实体名称（严格排除，不可重复）：
{json.dumps(existing_name_list[:80], ensure_ascii=False, indent=2)}

已有实体示例：
{json.dumps(entity_preview, ensure_ascii=False, indent=2)}

返回格式：
{{
  "discovered_entities": [
    {{
      "name": "实体名称",
      "entity_type": "实体类型",
      "summary": "实体简介",
      "why_relevant": "为何与该事件高度相关"
    }}
  ],
  "reasoning": "简短说明"
}}"""
        else:
            system_prompt = (
                "You are a social simulation design expert. Your task is to infer stakeholder groups "
                "and influential actors that are NOT explicitly mentioned in the materials but would "
                "naturally participate in discussions around this topic. Think like a PR strategist: "
                "who else matters? Who would react? Who has power? Return diverse entity types, not just generic 'Person' or 'Organization'. "
                "The provided entity names are strictly forbidden—never return them or close variants. Return JSON only."
            )
            user_prompt = f"""Based on the scenario below, discover up to {max_entities} STRATEGIC stakeholders or influential groups missing from the source material.

Think across these dimensions:
- Direct participants: who's directly affected but not mentioned?
- Influencers & amplifiers: who shapes opinion? (media, influencers, thought leaders, critics)
- Regulators & gatekeepers: who has power to regulate or block? (agencies, standards bodies, NGOs)
- Competitors & alternatives: who benefits from a different outcome?
- Communities & constituencies: organized groups with shared interests?

Rules:
1. DIVERSITY: Return a mix of entity types—aim for different roles/perspectives, not multiple instances of the same type.
2. EXCLUSION: The "entity names already in graph" is a hard block. Absolutely no repeats, aliases, or rephrases.
3. RELEVANCE: Each must be a real, plausible actor in public discourse (person, organization, media outlet, movement, agency, etc.)
4. SPECIFICITY: "Influencers" > "People". "Environmental NGOs" > "Organizations". Be concrete.
5. No abstract concepts: only entities that could post, react, or be discussed on social platforms.
6. If you find < 2 unique additions, return empty array rather than forcing weak matches.

Simulation topic:
{simulation_requirement[:3000]}

Background:
{document_text[:6000]}

Existing types already in use:
{json.dumps(existing_types, ensure_ascii=False)}

FORBIDDEN—these names are already in the graph, never use them:
{json.dumps(existing_name_list, ensure_ascii=False, indent=2)}

Return format:
{{
  "discovered_entities": [
    {{
      "name": "Specific entity name (not generic)",
      "entity_type": "Specific type (e.g. 'EnvironmentalNGO', 'MediaOutlet', 'CompetitorCompany')",
      "summary": "Who they are and why they matter to this scenario",
      "why_relevant": "What stake/power do they have here?"
    }}
  ],
  "reasoning": "Why these specific actors matter; brief diversity analysis"
}}"""
        try:
            llm = LLMClient()
            response = llm.chat_json(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=1800,
            )
        except Exception as exc:
            logger.warning(f"LLM related entity discovery failed: {exc}")
            return []

        discovered_entities = response.get("discovered_entities", [])
        normalized: List[EntityNode] = []
        seen_names = set(existing_names)

        def normalize_name(value: str) -> str:
            return re.sub(r'[^a-z0-9]+', '', value.lower())

        for idx, item in enumerate(discovered_entities[:max_entities]):
            name = str(item.get("name", "")).strip()
            entity_type = str(item.get("entity_type", "")).strip() or "Entity"
            summary = str(item.get("summary", "")).strip()
            why_relevant = str(item.get("why_relevant", "")).strip()

            if not name:
                continue
            lowered = name.lower()
            normalized_name = normalize_name(name)
            if lowered in seen_names:
                continue
            if any(
                normalized_name == normalize_name(existing_name)
                or normalized_name in normalize_name(existing_name)
                or normalize_name(existing_name) in normalized_name
                for existing_name in existing_name_list
            ):
                continue

            normalized.append(EntityNode(
                uuid=f"llm_discovered_{uuid.uuid4().hex[:12]}_{idx}",
                name=name,
                labels=["Entity", entity_type],
                summary=summary or why_relevant or f"{name} is relevant to this simulation topic.",
                attributes={
                    "discovered_by_llm": True,
                    "why_relevant": why_relevant,
                    "source": "llm_related_entity_discovery",
                },
            ))
            seen_names.add(lowered)

        logger.info(f"LLM discovered {len(normalized)} additional relevant entities")
        return normalized

    def _expand_custom_entities(
        self,
        custom_entities: List[Dict[str, str]],
        language: str = "en",
    ) -> List[EntityNode]:
        """Use the LLM to turn user-entered name/description seeds into structured entities."""
        cleaned = []
        for item in custom_entities:
            name = str(item.get("name", "")).strip()
            description = str(item.get("description", "")).strip()
            if name and description:
                cleaned.append({"name": name, "description": description})

        if not cleaned:
            return []

        if language == "zh":
            system_prompt = "你是社会模拟设计专家。请将用户手动添加的实体线索扩展为结构化社交实体。只返回 JSON。"
            user_prompt = f"""用户手动添加了一些实体线索。请基于每个实体的 name 和 description，补全适合模拟配置使用的结构化字段。

要求：
1. 必须保留用户给定的 name，不要改名。
2. 推断一个最合适的 entity_type（人物用Person，记者用Person:Journalist，影响者用Person:Influencer，组织用Organization:公司/政府/媒体等）。
3. 生成 2-3 句的详细 summary，包含身份背景和行为特征。
4. 提供详细的 attributes，帮助后续人格生成。
5. **多样化原则**：当描述attributes时，为每个实体赋予独特、多样化的特征。避免所有实体都使用相似的风格或立场。即使是小角色也可以有独特的背景、观点或行为模式。

输入：
{json.dumps(cleaned, ensure_ascii=False, indent=2)}

返回格式：
{{
  "entities": [
    {{
      "name": "原始名称",
      "entity_type": "实体类型",
      "summary": "详细摘要（2-3句，包含身份、背景、行为特征）",
      "attributes": {{
        "seed_description": "原始描述",
        "expertise_areas": ["专业领域1", "专业领域2"],
        "communication_style": "沟通风格（如：分析型、激进型、幽默型）",
        "influence_level": "High/Medium/Low",
        "target_audience": ["目标受众1", "目标受众2"],
        "stance": "可能立场",
        "role": "角色（如：影响者、专家、记者、普通用户）"
      }}
    }}
  ]
}}"""
        else:
            system_prompt = "You are a social simulation design expert. Expand user-added entity seeds into structured social entities. Return JSON only."
            user_prompt = f"""The user manually added some entity seeds. For each item, use its name and description to fill in the structured fields needed for simulation setup.

Rules:
1. Preserve the exact user-provided name.
2. Infer the best-fit entity_type (use format: Person, Person:Journalist, Person:Influencer, Organization:Company, Organization:Government, etc.)
3. Write a 2-3 sentence detailed summary with identity, background, and behavior traits.
4. Provide detailed attributes to help with persona generation.
5. **Diversity Rule**: When inventing attributes, make each entity unique and diverse. Avoid giving all entities similar styles or stances. Even minor characters should have distinct backgrounds, viewpoints, or behavioral patterns.

Input:
{json.dumps(cleaned, ensure_ascii=False, indent=2)}

Return format:
{{
  "entities": [
    {{
      "name": "Original name",
      "entity_type": "Entity type (e.g., Person:Influencer, Organization:Company)",
      "summary": "Detailed 2-3 sentence summary with identity, background, and behavior traits",
      "attributes": {{
        "seed_description": "Original description",
        "expertise_areas": ["Area of expertise 1", "Area of expertise 2"],
        "communication_style": "Communication style (e.g., Analytical, Aggressive, Humorous)",
        "influence_level": "High/Medium/Low",
        "target_audience": ["Audience 1", "Audience 2"],
        "stance": "Likely stance",
        "role": "Role (e.g., Influencer, Expert, Journalist, Regular User)"
      }}
    }}
  ]
}}"""

        try:
            llm = LLMClient()
            response = llm.chat_json(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=1800,
            )
            results = response.get("entities", [])
        except Exception as exc:
            logger.warning(f"LLM custom entity expansion failed: {exc}")
            results = []

        expanded: List[EntityNode] = []
        seen = set()

        def fallback_type(name: str) -> str:
            org_markers = ("foundation", "institute", "board", "alliance", "agency", "company", "group", "collective")
            lowered = name.lower()
            return "Organization" if any(marker in lowered for marker in org_markers) else "Person"

        source_by_name = {item["name"]: item["description"] for item in cleaned}

        for idx, item in enumerate(results):
            name = str(item.get("name", "")).strip()
            if not name or name in seen or name not in source_by_name:
                continue
            entity_type = str(item.get("entity_type", "")).strip() or fallback_type(name)
            summary = str(item.get("summary", "")).strip() or source_by_name[name]
            attributes = item.get("attributes") if isinstance(item.get("attributes"), dict) else {}
            attributes["seed_description"] = source_by_name[name]
            expanded.append(EntityNode(
                uuid=f"custom_entity_{uuid.uuid4().hex[:12]}_{idx}",
                name=name,
                labels=["Entity", entity_type],
                summary=summary,
                attributes=attributes,
            ))
            seen.add(name)

        for idx, item in enumerate(cleaned):
            if item["name"] in seen:
                continue
            expanded.append(EntityNode(
                uuid=f"custom_entity_fallback_{uuid.uuid4().hex[:12]}_{idx}",
                name=item["name"],
                labels=["Entity", fallback_type(item["name"])],
                summary=item["description"],
                attributes={"seed_description": item["description"], "source": "user_custom_entity"},
            ))

        logger.info(f"Expanded {len(expanded)} custom user entities")
        return expanded
    
    def prepare_simulation(
        self,
        simulation_id: str,
        simulation_requirement: str,
        document_text: str,
        defined_entity_types: Optional[List[str]] = None,
        use_llm_for_profiles: bool = True,
        discover_related_entities: Optional[bool] = None,
        custom_entities: Optional[List[Dict[str, str]]] = None,
        progress_callback: Optional[callable] = None,
        parallel_profile_count: int = 3,
        language: str = "zh",
        user_id: Optional[str] = None
    ) -> SimulationState:
        """
        Prepare simulation environment (fully automated)
        
        Steps:
        1. Read and filter entities from Zep graph
        2. Generate OASIS Agent Profiles for each entity (optional LLM enhancement, supports parallel)
        3. Use LLM to intelligently generate simulation config parameters (time, activity levels, posting frequency, etc.)
        4. Save config files and Profile files
        5. Copy preset scripts to simulation directory
        
        Args:
            simulation_id: Simulation ID
            simulation_requirement: Simulation requirement description (used by LLM to generate config)
            document_text: Original document content (used by LLM to understand background)
            defined_entity_types: Predefined entity types (optional)
            use_llm_for_profiles: Whether to use LLM to generate detailed personas
            progress_callback: Progress callback function (stage, progress, message)
            parallel_profile_count: Number of parallel persona generations, default 3
            
        Returns:
            SimulationState
        """
        state = self._load_simulation_state(simulation_id)
        if not state:
            raise ValueError(f"Simulation does not exist: {simulation_id}")
        
        try:
            state.status = SimulationStatus.PREPARING
            self._save_simulation_state(state)
            
            sim_dir = self._get_simulation_dir(simulation_id)
            
            # ========== Phase 1: Read and filter entities ==========
            if progress_callback:
                progress_callback("reading", 0, "Connecting to Zep graph...")
            
            reader = ZepEntityReader()
            
            if progress_callback:
                progress_callback("reading", 30, "Reading node data...")
            
            filtered = reader.filter_defined_entities(
                graph_id=state.graph_id,
                defined_entity_types=defined_entity_types,
                enrich_with_edges=True
            )

            if discover_related_entities is None:
                discover_related_entities = state.discover_related_entities
            else:
                state.discover_related_entities = discover_related_entities

            if custom_entities is None:
                custom_entities = state.custom_entities
            else:
                state.custom_entities = custom_entities

            discovered_entities: List[EntityNode] = []
            if discover_related_entities:
                if progress_callback:
                    progress_callback("reading", 65, "Discovering additional relevant entities with LLM...")
                discovered_entities = self._discover_related_entities(
                    simulation_requirement=simulation_requirement,
                    document_text=document_text,
                    entities=filtered.entities,
                    language=language,
                    max_entities=5,
                )
                if discovered_entities:
                    print("\n=== DISCOVERED ENTITIES ===")
                    for e in discovered_entities:
                        print(f"Name: {e.name},Type: {e.get_entity_type()}")
                    
                    filtered.entities.extend(discovered_entities)
                    filtered.entity_types.update(
                        entity.get_entity_type() or "Entity"
                        for entity in discovered_entities
                    )
                state.discovered_entities_count = len(discovered_entities)
            else:
                state.discovered_entities_count = 0

            state.entities_count = len(filtered.entities)
            state.entity_types = list(filtered.entity_types)

            custom_entity_nodes: List[EntityNode] = []
            if custom_entities:
                if progress_callback:
                    progress_callback("reading", 82, "Expanding custom entities with LLM...")
                custom_entity_nodes = self._expand_custom_entities(
                    custom_entities=custom_entities,
                    language=language,
                )
                if custom_entity_nodes:
                    filtered.entities.extend(custom_entity_nodes)
                    filtered.entity_types.update(
                        entity.get_entity_type() or "Entity"
                        for entity in custom_entity_nodes
                    )
                    state.entities_count = len(filtered.entities)
                    state.entity_types = list(filtered.entity_types)

            if progress_callback:
                progress_callback(
                    "reading", 100, 
                    f"Complete, {state.entities_count} entities found",
                    current=state.entities_count,
                    total=state.entities_count
                )
            
            if state.entities_count == 0:
                state.status = SimulationStatus.FAILED
                state.error = "No matching entities found, please check that the graph was built correctly"
                self._save_simulation_state(state)
                return state

            if discovered_entities:
                discovered_path = os.path.join(sim_dir, "discovered_entities.json")
                with open(discovered_path, 'w', encoding='utf-8') as f:
                    json.dump([entity.to_dict() for entity in discovered_entities], f, ensure_ascii=False, indent=2)
                logger.info(f"Saved {len(discovered_entities)} discovered entities to {discovered_path}")
            if custom_entity_nodes:
                custom_path = os.path.join(sim_dir, "custom_entities_expanded.json")
                with open(custom_path, 'w', encoding='utf-8') as f:
                    json.dump([entity.to_dict() for entity in custom_entity_nodes], f, ensure_ascii=False, indent=2)
                logger.info(f"Saved {len(custom_entity_nodes)} expanded custom entities to {custom_path}")
            
            # ========== Phase 2: Generate Agent Profiles ==========
            total_entities = len(filtered.entities)
            
            if progress_callback:
                progress_callback(
                    "generating_profiles", 0, 
                    "Starting generation...",
                    current=0,
                    total=total_entities
                )
            
            # Pass graph_id to enable Zep retrieval for richer context
            generator = OasisProfileGenerator(graph_id=state.graph_id, language=language, supabase_user_id=user_id)            
            
            def profile_progress(current, total, msg):
                if progress_callback:
                    progress_callback(
                        "generating_profiles", 
                        int(current / total * 100), 
                        msg,
                        current=current,
                        total=total,
                        item_name=msg
                    )
            
            # Set real-time save file path (prefer Reddit JSON format)
            realtime_output_path = None
            realtime_platform = "reddit"
            if state.enable_reddit:
                realtime_output_path = os.path.join(sim_dir, "reddit_profiles.json")
                realtime_platform = "reddit"
            elif state.enable_linkedin:
                realtime_output_path = os.path.join(sim_dir, "linkedin_profiles.csv")
                realtime_platform = "twitter"
            elif state.enable_twitter:
                realtime_output_path = os.path.join(sim_dir, "twitter_profiles.csv")
                realtime_platform = "twitter"
            
            profiles = generator.generate_profiles_from_entities(
                entities=filtered.entities,
                use_llm=use_llm_for_profiles,
                progress_callback=profile_progress,
                graph_id=state.graph_id,  # Pass graph_id for Zep retrieval
                parallel_count=parallel_profile_count,  # Parallel generation count
                realtime_output_path=realtime_output_path,  # Real-time save path
                output_platform=realtime_platform  # Output format
            )
            
            state.profiles_count = len(profiles)
            
            # Save Profile files (note: Twitter uses CSV format, Reddit uses JSON format)
            # Reddit was already saved in real-time during generation, save again here for completeness
            if progress_callback:
                progress_callback(
                    "generating_profiles", 95, 
                    "Saving Profile files...",
                    current=total_entities,
                    total=total_entities
                )
            
            if state.enable_reddit:
                generator.save_profiles(
                    profiles=profiles,
                    file_path=os.path.join(sim_dir, "reddit_profiles.json"),
                    platform="reddit"
                )
            
            if state.enable_twitter:
                # Twitter uses CSV format! This is an OASIS requirement
                generator.save_profiles(
                    profiles=profiles,
                    file_path=os.path.join(sim_dir, "twitter_profiles.csv"),
                    platform="twitter"
                )

            if state.enable_linkedin:
                # LinkedIn reuses the Twitter-style CSV profile schema.
                generator.save_profiles(
                    profiles=profiles,
                    file_path=os.path.join(sim_dir, "linkedin_profiles.csv"),
                    platform="twitter"
                )
            
            if progress_callback:
                progress_callback(
                    "generating_profiles", 100, 
                    f"Complete, {len(profiles)} profiles generated",
                    current=len(profiles),
                    total=len(profiles)
                )
            
            # ========== Phase 3: LLM intelligent simulation config generation ==========
            if progress_callback:
                progress_callback(
                    "generating_config", 0, 
                    "Analyzing simulation requirements...",
                    current=0,
                    total=3
                )
            
            config_generator = SimulationConfigGenerator(language=language, user_id=user_id)
            
            if progress_callback:
                progress_callback(
                    "generating_config", 30, 
                    "Calling LLM to generate config...",
                    current=1,
                    total=3
                )
            
            sim_params = config_generator.generate_config(
                simulation_id=simulation_id,
                project_id=state.project_id,
                graph_id=state.graph_id,
                simulation_requirement=simulation_requirement,
                document_text=document_text,
                entities=filtered.entities,
                enable_twitter=state.enable_twitter,
                enable_reddit=state.enable_reddit,
                enable_linkedin=state.enable_linkedin
            )
            
            if progress_callback:
                progress_callback(
                    "generating_config", 70, 
                    "Saving config files...",
                    current=2,
                    total=3
                )
            
            # Save config file
            config_path = os.path.join(sim_dir, "simulation_config.json")
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(sim_params.to_json())
            
            state.config_generated = True
            state.config_reasoning = sim_params.generation_reasoning
            
            if progress_callback:
                progress_callback(
                    "generating_config", 100, 
                    "Config generation complete",
                    current=3,
                    total=3
                )
            
            # Note: Run scripts remain in backend/scripts/ directory, no longer copied to simulation directory
            # When starting simulation, simulation_runner runs scripts from scripts/ directory
            
            # Update status
            state.status = SimulationStatus.READY
            self._save_simulation_state(state)
            
            logger.info(f"Simulation preparation complete: {simulation_id}, "
                       f"entities={state.entities_count}, profiles={state.profiles_count}")
            
            return state
            
        except Exception as e:
            logger.error(f"Simulation preparation failed: {simulation_id}, error={str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            state.status = SimulationStatus.FAILED
            state.error = str(e)
            self._save_simulation_state(state)
            raise
    
    def get_simulation(self, simulation_id: str) -> Optional[SimulationState]:
        """Get simulation state"""
        return self._load_simulation_state(simulation_id)
    
    def list_simulations(self, project_id: Optional[str] = None) -> List[SimulationState]:
        """List all simulations"""
        simulations = []
        
        if os.path.exists(self.SIMULATION_DATA_DIR):
            for sim_id in os.listdir(self.SIMULATION_DATA_DIR):
                # Skip hidden files (e.g. .DS_Store) and non-directory files
                sim_path = os.path.join(self.SIMULATION_DATA_DIR, sim_id)
                if sim_id.startswith('.') or not os.path.isdir(sim_path):
                    continue
                
                state = self._load_simulation_state(sim_id)
                if state:
                    if project_id is None or state.project_id == project_id:
                        simulations.append(state)
        
        return simulations
    
    def get_profiles(self, simulation_id: str, platform: str = "reddit") -> List[Dict[str, Any]]:
        """Get Agent Profiles for simulation"""
        state = self._load_simulation_state(simulation_id)
        if not state:
            raise ValueError(f"Simulation does not exist: {simulation_id}")
        
        sim_dir = self._get_simulation_dir(simulation_id)
        profile_path = os.path.join(sim_dir, f"{platform}_profiles.json")
        
        if not os.path.exists(profile_path):
            return []
        
        with open(profile_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_simulation_config(self, simulation_id: str) -> Optional[Dict[str, Any]]:
        """Get simulation configuration"""
        sim_dir = self._get_simulation_dir(simulation_id)
        config_path = os.path.join(sim_dir, "simulation_config.json")
        
        if not os.path.exists(config_path):
            return None
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_run_instructions(self, simulation_id: str) -> Dict[str, str]:
        """Get run instructions"""
        sim_dir = self._get_simulation_dir(simulation_id)
        config_path = os.path.join(sim_dir, "simulation_config.json")
        scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts'))
        
        return {
            "simulation_dir": sim_dir,
            "scripts_dir": scripts_dir,
            "config_file": config_path,
            "commands": {
                "twitter": f"python {scripts_dir}/run_twitter_simulation.py --config {config_path}",
                "reddit": f"python {scripts_dir}/run_reddit_simulation.py --config {config_path}",
                "linkedin": f"python {scripts_dir}/run_linkedin_sumulation.py --config {config_path}",
                "parallel": f"python {scripts_dir}/run_parallel_simulation.py --config {config_path}",
            },
            "instructions": (
                f"1. Activate conda environment: conda activate MiroFish\n"
                f"2. Run simulation (scripts located at {scripts_dir}):\n"
                f"   - Run Twitter only: python {scripts_dir}/run_twitter_simulation.py --config {config_path}\n"
                f"   - Run Reddit only: python {scripts_dir}/run_reddit_simulation.py --config {config_path}\n"
                f"   - Run LinkedIn only: python {scripts_dir}/run_linkedin_sumulation.py --config {config_path}\n"
                f"   - Run both platforms in parallel: python {scripts_dir}/run_parallel_simulation.py --config {config_path}"
            )
        }
