"""
Entity deduplication service
Identifies and merges duplicate nodes pointing to the same real-world entity after graph building

Typical scenarios:
  - "Trump" and "US President Trump" are recognized by Zep as two different nodes
  - This service uses LLM to determine if they point to the same entity and automatically merges them
"""

import json
import time
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field

import httpx
from zep_cloud.client import Zep

from ..config import Config
from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger
from ..utils.zep_paging import fetch_all_nodes, fetch_all_edges

ZEP_API_BASE = "https://api.getzep.com/api/v2"

logger = get_logger('mirofish.entity_deduplicator')


DEDUP_SYSTEM_PROMPT = """You are an entity disambiguation expert. Your task is to identify duplicate nodes in a knowledge graph that point to the same real-world entity.

**Important: You must output valid JSON format data, do not output anything else.**

## Judgment Criteria

Two nodes should be considered "the same entity" if and only if:
- They refer to exactly the same person, organization, or thing in the real world
- They are merely different ways of referring to it (e.g., full name vs. nickname, with title vs. without title)
- For example: "Trump" and "US President Trump" are the same person

## Hard Rules (Must Be Strictly Followed)

1. **Types must match**: Person can only merge with person, organization with organization, location with location. Never merge across types.
2. **Do not merge hierarchical relationships**: State Department ≠ Consulate, headquarters ≠ branch office, department ≠ subsidiary. They are different entities.
3. **Do not merge associated relationships**: A person working at an organization doesn't mean the person and organization are the same entity.
4. **Information sources are not entities**: News media, data platforms, etc. are not the same as the entities they report on.
5. **When in doubt, don't merge**: If you're not sure whether two nodes are the same entity, don't merge them.

## Negative Examples (Should NEVER Merge)

- "General Dan Knutes" vs "Joint Chiefs of Staff" → Don't merge (person vs organization)
- "US State Department" vs "US Consulate in Adana, Turkey" → Don't merge (parent organization vs sub-organization)
- "Iranian Ambassador to China Fazli" vs "Golddata" → Don't merge (diplomat vs financial platform)
- "Strait of Hormuz" vs "USA" → Don't merge (geographic location vs country)
- "Xinhua News" vs "Xinhua News Agency" → Don't merge (website vs news agency, though related, different entities)

## Positive Examples (Should Merge)

- "Trump" vs "US President Trump" → Merge (same person, nickname vs with title)
- "Alaghi" vs "Iranian Foreign Minister Alaghi" → Merge (same person, nickname vs full name + title), canonical_name should be "Alaghi"
- "IRGC" vs "Islamic Revolutionary Guard Corps" → Merge (same organization, acronym vs full name)

## Output Format

```json
{
    "duplicate_groups": [
        {
            "canonical_name": "The standard name to keep (choose the most concise and commonly used)",
            "members": [
                {"uuid": "node uuid", "name": "node name"}
            ],
            "reason": "Merge reason (brief)"
        }
    ]
}
```

Rules:
- Each duplicate_group must contain at least 2 members
- canonical_name should be the most commonly used, concise, and recognizable name (e.g., "Trump" is better than "US President Trump")
- If no duplicates are found, return `{"duplicate_groups": []}`
"""

DEDUP_BATCH_SIZE = 80
NAME_JACCARD_THRESHOLD = 0.5


@dataclass
class MergeAction:
    """Record of a single merge operation"""
    group_canonical_name: str
    keep_node_uuid: str
    keep_node_name: str
    removed_nodes: List[Dict[str, str]]
    edges_migrated: int
    reason: str


@dataclass
class DeduplicationReport:
    """Deduplication execution report"""
    total_nodes_before: int = 0
    total_nodes_after: int = 0
    groups_found: int = 0
    nodes_removed: int = 0
    edges_migrated: int = 0
    merge_actions: List[MergeAction] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_nodes_before": self.total_nodes_before,
            "total_nodes_after": self.total_nodes_after,
            "groups_found": self.groups_found,
            "nodes_removed": self.nodes_removed,
            "edges_migrated": self.edges_migrated,
            "merge_actions": [
                {
                    "group_canonical_name": a.group_canonical_name,
                    "keep_node_uuid": a.keep_node_uuid,
                    "keep_node_name": a.keep_node_name,
                    "removed_nodes": a.removed_nodes,
                    "edges_migrated": a.edges_migrated,
                    "reason": a.reason,
                }
                for a in self.merge_actions
            ],
            "errors": self.errors,
        }


class EntityDeduplicator:
    """
    Entity deduplication service for knowledge graphs.
    
    Uses LLM to identify duplicate entities and merges them while preserving edges.
    """

    def __init__(self):
        """Initialize the deduplicator with LLM and Zep clients."""
        self.llm_client = LLMClient()
        self.zep_client = Zep(api_key=Config.ZEP_API_KEY)
        # Use Bearer token auth for Zep Cloud API
        self._http = httpx.Client(
            base_url=ZEP_API_BASE,
            headers={
                "Authorization": f"Bearer {Config.ZEP_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=30.0,
        )

    def __del__(self):
        """Cleanup HTTP client."""
        if hasattr(self, '_http'):
            self._http.close()

    def deduplicate(
        self,
        graph_id: str,
        progress_callback: Optional[Callable[[str, float], None]] = None,
        dry_run: bool = False,
    ) -> DeduplicationReport:
        """
        Execute entity deduplication on a knowledge graph.
        
        Args:
            graph_id: The Zep graph ID
            progress_callback: Optional callback for progress updates (message, progress 0-1)
            dry_run: If True, only detect duplicates without merging
            
        Returns:
            DeduplicationReport with results
        """
        def _progress(msg: str, pct: float = 0.0):
            logger.info(f"[dedup] {msg}")
            if progress_callback:
                progress_callback(msg, pct)

        _progress(f"Starting entity deduplication for graph: {graph_id}")

        # Fetch all nodes
        _progress("Fetching all nodes from graph...")
        raw_nodes = fetch_all_nodes(self.zep_client, graph_id)
        
        # Convert Zep objects to dictionaries
        node_list = []
        for node in raw_nodes:
            if hasattr(node, '__dict__'):
                # It's a Zep object, convert to dict
                node_dict = {
                    "uuid": getattr(node, 'uuid_', None) or getattr(node, 'uuid', ''),
                    "name": getattr(node, 'name', '') or '',
                    "labels": getattr(node, 'labels', []) or [],
                    "summary": getattr(node, 'summary', '') or '',
                    "attributes": getattr(node, 'attributes', {}) or {},
                }
                node_list.append(node_dict)
            else:
                # It's already a dict
                node_list.append(node)
        
        if not node_list:
            _progress("No nodes found in graph, skipping deduplication")
            return DeduplicationReport()

        total_before = len(node_list)
        _progress(f"Found {total_before} nodes in graph")

        report = DeduplicationReport()
        report.total_nodes_before = total_before

        # Build node map for quick lookup
        node_map: Dict[str, Dict[str, Any]] = {
            n["uuid"]: n for n in node_list
        }

        # Find duplicate groups using LLM
        _progress("Analyzing entities for duplicates...")
        duplicate_groups = self._find_duplicates(node_list)

        if not duplicate_groups:
            _progress("No duplicate entities found")
            report.total_nodes_after = total_before
            return report

        report.groups_found = len(duplicate_groups)
        _progress(f"Found {report.groups_found} groups of potential duplicates")

        if dry_run:
            _progress("Dry run mode - skipping actual merge")
            return report

        # Execute merges
        for idx, group in enumerate(duplicate_groups):
            canonical = group.get("canonical_name", "")
            members = group.get("members", [])
            reason = group.get("reason", "")

            group_progress = (idx + 1) / len(duplicate_groups)

            valid_members = [m for m in members if m["uuid"] in node_map]
            if len(valid_members) < 2:
                continue

            keep_node = self._pick_primary_node(valid_members, node_map, canonical)
            dup_nodes = [m for m in valid_members if m["uuid"] != keep_node["uuid"]]

            _progress(
                f"Merging group [{canonical}]: keeping '{keep_node['name']}', "
                f"removing {len(dup_nodes)} duplicate nodes",
                group_progress,
            )

            edges_migrated = 0
            removed = []

            for dup in dup_nodes:
                try:
                    migrated = self._merge_node_into(
                        graph_id, keep_node["uuid"], dup["uuid"], node_map
                    )
                    edges_migrated += migrated
                    removed.append({"uuid": dup["uuid"], "name": dup["name"]})
                except Exception as e:
                    err_msg = f"Failed to merge node '{dup['name']}': {str(e)}"
                    logger.error(err_msg)
                    report.errors.append(err_msg)

            self._update_primary_node(keep_node["uuid"], canonical, valid_members, node_map)

            report.merge_actions.append(MergeAction(
                group_canonical_name=canonical,
                keep_node_uuid=keep_node["uuid"],
                keep_node_name=keep_node["name"],
                removed_nodes=removed,
                edges_migrated=edges_migrated,
                reason=reason,
            ))
            report.nodes_removed += len(removed)
            report.edges_migrated += edges_migrated

            for r in removed:
                node_map.pop(r["uuid"], None)

        report.total_nodes_after = total_before - report.nodes_removed
        _progress(
            f"Deduplication complete: merged {report.groups_found} groups, "
            f"removed {report.nodes_removed} nodes, "
            f"migrated {report.edges_migrated} edges",
            1.0,
        )
        return report

    # ------------------------------------------------------------------
    # Name similarity & type compatibility pre-filtering
    # ------------------------------------------------------------------

    @staticmethod
    def _labels_compatible(labels_a: List[str], labels_b: List[str]) -> bool:
        """Check if two nodes' type labels are compatible (at least one common label)"""
        if not labels_a or not labels_b:
            return True
        return bool(set(labels_a) & set(labels_b))

    @staticmethod
    def _name_similar(name_a: str, name_b: str) -> bool:
        """Check if two names are similar enough to be candidate duplicates"""
        a = name_a.strip()
        b = name_b.strip()
        if not a or not b:
            return False
        if a == b:
            return True
        if a in b or b in a:
            return True
        chars_a = set(a)
        chars_b = set(b)
        union = chars_a | chars_b
        if not union:
            return False
        jaccard = len(chars_a & chars_b) / len(union)
        return jaccard >= NAME_JACCARD_THRESHOLD

    def _build_candidate_clusters(
        self, node_list: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """
        Pre-filtering: cluster nodes by name similarity + type compatibility.
        Only nodes with similar names AND compatible types are placed in the same candidate cluster.
        Uses union-find algorithm to build connected components.
        """
        n = len(node_list)
        parent = list(range(n))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x: int, y: int):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py

        for i in range(n):
            for j in range(i + 1, n):
                if not self._labels_compatible(
                    node_list[i]["labels"], node_list[j]["labels"]
                ):
                    continue
                if self._name_similar(node_list[i]["name"], node_list[j]["name"]):
                    union(i, j)

        clusters: Dict[int, List[Dict[str, Any]]] = {}
        for i in range(n):
            root = find(i)
            clusters.setdefault(root, []).append(node_list[i])

        return [c for c in clusters.values() if len(c) >= 2]

    # ------------------------------------------------------------------
    # LLM duplicate detection
    # ------------------------------------------------------------------

    def _find_duplicates(
        self, node_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        First use name similarity + type compatibility pre-filtering, 
        then use LLM to confirm each cluster.
        This way LLM only processes pre-filtered candidate nodes, avoiding false positives.
        """
        clusters = self._build_candidate_clusters(node_list)
        if not clusters:
            logger.info("[dedup] Name similarity pre-filtering: no candidate duplicate nodes found")
            return []

        candidate_count = sum(len(c) for c in clusters)
        logger.info(
            f"[dedup] Name similarity pre-filtering: "
            f"{len(clusters)} candidate groups ({candidate_count} nodes, "
            f"from {len(node_list)} total nodes)"
        )

        all_groups: List[Dict[str, Any]] = []
        for cluster in clusters:
            groups = self._find_duplicates_single_batch(cluster)
            all_groups.extend(groups)

        return all_groups

    def _find_duplicates_single_batch(
        self, node_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Use LLM to confirm if a group of candidate nodes are duplicates"""
        nodes_desc = "\n".join(
            f"- uuid: {n['uuid']}  |  name: {n['name']}  "
            f"|  labels: {', '.join(n['labels'])}  "
            f"|  summary: {(n.get('summary') or '')[:100]}"
            for n in node_list
        )

        user_message = (
            f"Below is a group of similar-named entity nodes in a knowledge graph. "
            f"Please determine if any of them point to the same real-world entity:\n\n"
            f"{nodes_desc}\n\n"
            f"Please return results in the required JSON format strictly."
            f"Note: Similar names don't necessarily mean the same entity. Please carefully analyze labels and summary."
            f"If none of these nodes are duplicates, return {{\"duplicate_groups\": []}}"
        )

        messages = [
            {"role": "system", "content": DEDUP_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        try:
            result = self.llm_client.chat_json(
                messages=messages, temperature=0.1, max_tokens=4096
            )
            groups = result.get("duplicate_groups", [])
            return self._validate_groups(groups, node_list)
        except Exception as e:
            logger.error(f"LLM duplicate detection failed: {e}")
            return []

    def _validate_groups(
        self,
        groups: List[Dict[str, Any]],
        node_list: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Validate LLM-returned groups: filter invalid data + type consistency check"""
        valid_uuids = {n["uuid"] for n in node_list}
        uuid_to_labels = {n["uuid"]: n.get("labels", []) for n in node_list}
        validated = []

        for g in groups:
            if not isinstance(g, dict):
                continue
            members = g.get("members", [])
            if not isinstance(members, list) or len(members) < 2:
                continue

            valid_members = []
            for m in members:
                if isinstance(m, dict) and m.get("uuid") in valid_uuids:
                    valid_members.append(m)

            if len(valid_members) < 2:
                continue

            # Type consistency check: use first member's type as baseline, filter incompatible members
            base_labels = set(uuid_to_labels.get(valid_members[0]["uuid"], []))
            if base_labels:
                type_checked = [valid_members[0]]
                for m in valid_members[1:]:
                    m_labels = set(uuid_to_labels.get(m["uuid"], []))
                    if not m_labels or (m_labels & base_labels):
                        type_checked.append(m)
                    else:
                        logger.warning(
                            f"[dedup] Type mismatch, refusing to merge: "
                            f"'{m.get('name')}' ({list(m_labels)}) vs "
                            f"'{valid_members[0].get('name')}' ({list(base_labels)})"
                        )
                valid_members = type_checked

            if len(valid_members) < 2:
                continue

            seen_uuids: set = set()
            unique_members = []
            for m in valid_members:
                if m["uuid"] not in seen_uuids:
                    seen_uuids.add(m["uuid"])
                    unique_members.append(m)

            if len(unique_members) >= 2:
                validated.append({
                    "canonical_name": g.get("canonical_name", unique_members[0]["name"]),
                    "members": unique_members,
                    "reason": g.get("reason", ""),
                })

        return validated

    # ------------------------------------------------------------------
    # Node merge operations
    # ------------------------------------------------------------------

    def _pick_primary_node(
        self,
        members: List[Dict[str, str]],
        node_map: Dict[str, Dict[str, Any]],
        canonical_name: str,
    ) -> Dict[str, str]:
        """
        Select the primary node (the one to keep)
        
        Priority:
        1. Node whose name exactly matches canonical_name
        2. Node with longest summary (most informative)
        3. First in the list
        """
        for m in members:
            if m["name"] == canonical_name:
                return m

        best = members[0]
        best_len = len(node_map.get(best["uuid"], {}).get("summary", ""))
        for m in members[1:]:
            s_len = len(node_map.get(m["uuid"], {}).get("summary", ""))
            if s_len > best_len:
                best = m
                best_len = s_len
        return best

    def _merge_node_into(
        self,
        graph_id: str,
        keep_uuid: str,
        remove_uuid: str,
        node_map: Dict[str, Dict[str, Any]],
    ) -> int:
        """
        Migrate edges from remove_uuid node to keep_uuid, then delete remove_uuid
        
        Returns:
            Number of edges migrated
        """
        try:
            edges = self.zep_client.graph.node.get_edges(node_uuid=remove_uuid)
        except Exception as e:
            logger.warning(f"Failed to get edges for node {remove_uuid}: {e}")
            edges = []

        migrated = 0
        keep_name = node_map.get(keep_uuid, {}).get("name", "")
        old_edge_uuids: List[str] = []

        for edge in edges:
            # Handle both dict and object formats
            if hasattr(edge, 'source_node_uuid'):
                source_uuid = edge.source_node_uuid
                target_uuid = edge.target_node_uuid
                fact = getattr(edge, 'fact', '') or ""
                edge_name = getattr(edge, 'name', '') or ""
                edge_uuid = getattr(edge, 'uuid_', None) or getattr(edge, 'uuid', '')
            else:
                source_uuid = edge.get('source_node_uuid')
                target_uuid = edge.get('target_node_uuid')
                fact = edge.get('fact', '')
                edge_name = edge.get('name', '')
                edge_uuid = edge.get('uuid_') or edge.get('uuid', '')
            
            old_edge_uuids.append(edge_uuid)

            if source_uuid == remove_uuid:
                other_uuid = target_uuid
            else:
                other_uuid = source_uuid

            if other_uuid == keep_uuid:
                continue

            other_name = node_map.get(other_uuid, {}).get("name", "")
            if not other_name:
                continue

            if source_uuid == remove_uuid:
                src_name, tgt_name = keep_name, other_name
            else:
                src_name, tgt_name = other_name, keep_name

            try:
                self.zep_client.graph.add_fact_triple(
                    graph_id=graph_id,
                    fact=fact if fact else f"{src_name} {edge_name} {tgt_name}",
                    fact_name=edge_name,
                    source_node_name=src_name,
                    target_node_name=tgt_name,
                )
                migrated += 1
                time.sleep(0.3)
            except Exception as e:
                logger.warning(f"Failed to migrate edge '{edge_name}': {e}")

        self._remove_node(remove_uuid, old_edge_uuids)
        return migrated

    def _remove_node(self, node_uuid: str, edge_uuids: List[str]):
        """
        Delete node: try HTTP DELETE with proper auth, fall back to deleting all associated edges
        """
        try:
            # Use Bearer token auth
            resp = self._http.delete(f"graph/node/{node_uuid}")
            resp.raise_for_status()
            logger.info(f"Successfully deleted node {node_uuid} via HTTP API")
            return
        except Exception as e:
            logger.warning(f"Failed to delete node {node_uuid} via HTTP ({e}), falling back to deleting associated edges")

        deleted_edges = 0
        for eu in edge_uuids:
            try:
                self.zep_client.graph.edge.delete(uuid_=eu)
                deleted_edges += 1
                time.sleep(0.2)
            except Exception as e:
                logger.warning(f"Failed to delete edge {eu}: {e}")

        logger.info(f"Deleted {deleted_edges}/{len(edge_uuids)} edges for node {node_uuid} (node becomes isolated)")

    def _update_primary_node(
        self,
        keep_uuid: str,
        canonical_name: str,
        all_members: List[Dict[str, str]],
        node_map: Dict[str, Dict[str, Any]],
    ):
        """Update primary node: merge all members' summaries, unify name"""
        summaries = []
        for m in all_members:
            s = node_map.get(m["uuid"], {}).get("summary", "")
            if s:
                summaries.append(s)

        merged_summary = "\n\n".join(dict.fromkeys(summaries))

        update_body: Dict[str, Any] = {}
        current_name = node_map.get(keep_uuid, {}).get("name", "")
        if current_name != canonical_name:
            update_body["name"] = canonical_name
        if merged_summary:
            update_body["summary"] = merged_summary

        if not update_body:
            return

        try:
            resp = self._http.patch(
                f"graph/node/{keep_uuid}",
                json=update_body,
            )
            resp.raise_for_status()
            logger.info(f"Successfully updated primary node {keep_uuid} name/summary")
        except Exception as e:
            logger.warning(f"Failed to update primary node {keep_uuid}: {e}, skipping name/summary update")
