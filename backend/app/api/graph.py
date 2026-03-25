"""
Graph-related API routes.

Project context is persisted on the server so the frontend does not have to
send the full working state between requests.
"""

import os
import tempfile
import traceback
import threading
from flask import request, jsonify

from . import graph_bp
from ..config import Config
from ..services.ontology_generator import OntologyGenerator
from ..services.graph_builder import GraphBuilderService
from ..services.text_processor import TextProcessor
from ..utils.llm_client import LLMClient
from ..utils.file_parser import FileParser
from ..utils.logger import get_logger
from ..models.task import TaskManager, TaskStatus
from ..models.project import ProjectManager, ProjectStatus

# Logger instance.
logger = get_logger('mirofish.api')


def allowed_file(filename: str) -> bool:
    """Check whether the uploaded file extension is allowed."""
    if not filename or '.' not in filename:
        return False
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    return ext in Config.ALLOWED_EXTENSIONS


@graph_bp.route('/simulation/assess', methods=['POST'])
def assess_simulation_fit():
    """
    Quickly assess whether running a simulation is likely to be useful.

    Request type: multipart/form-data
    Parameters:
        files: uploaded files (PDF/MD/TXT), multiple allowed
        simulation_requirement: simulation prompt / goal
        language: optional language hint
    """
    try:
        simulation_requirement = request.form.get('simulation_requirement', '').strip()
        language = request.form.get('language', Config.LANGUAGE)
        uploaded_files = request.files.getlist('files')

        if not simulation_requirement:
            return jsonify({
                "success": False,
                "error": "Please provide simulation_requirement"
            }), 400

        if not uploaded_files or all(not f.filename for f in uploaded_files):
            return jsonify({
                "success": False,
                "error": "Please upload at least one document"
            }), 400

        document_texts = []
        file_names = []
        for file in uploaded_files:
            if file and file.filename and allowed_file(file.filename):
                suffix = os.path.splitext(file.filename)[1]
                temp_path = None
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                        temp_file.write(file.read())
                        temp_path = temp_file.name
                    text = FileParser.extract_text(temp_path)
                    text = TextProcessor.preprocess_text(text)
                    if text:
                        document_texts.append(text)
                        file_names.append(file.filename)
                finally:
                    if temp_path and os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except OSError:
                            pass

        if not document_texts:
            return jsonify({
                "success": False,
                "error": "No documents were processed successfully. Check the file formats."
            }), 400

        combined_text = "\n\n".join(document_texts)
        context_excerpt = combined_text[:12000]

        if language == 'zh':
            system_prompt = "你是社会仿真项目评估专家。请判断给定材料是否值得做社交仿真，并返回 JSON。"
            user_prompt = f"""请评估下面这组“文档 + 模拟目标”是否适合进行社交媒体仿真，以及仿真是否有望得到较好的结果。

评估维度：
1. 是否真的有必要做 simulation，而不是简单总结/抽取即可。
2. 文档信息是否足够支撑一个可信的仿真。
3. 该 prompt 是否足够明确，能让仿真产出有价值的观察。
4. 如果不适合，请明确指出原因。

模拟目标：
{simulation_requirement[:3000]}

文档内容摘录：
{context_excerpt}

返回 JSON：
{{
  "should_run_simulation": true,
  "confidence": 78,
  "summary": "一句话结论",
  "simulation_value": "为什么值得做或不值得做",
  "document_sufficiency": "文档充分性判断",
  "likely_limitations": ["限制1", "限制2"],
  "recommended_next_step": "建议下一步"
}}"""
        else:
            system_prompt = "You are a social simulation planning expert. Judge whether the provided documents and prompt are a good fit for running a social simulation. Return JSON only."
            user_prompt = f"""Assess whether this document + simulation-goal pair is a good candidate for a social media simulation, and whether the simulation is likely to produce useful results.

Evaluate:
1. Whether simulation is actually necessary versus simpler analysis.
2. Whether the documents contain enough grounded context for a credible simulation.
3. Whether the prompt is specific enough to produce useful outcomes.
4. If it is not a good fit, explain why clearly.

Simulation goal:
{simulation_requirement[:3000]}

Document excerpt:
{context_excerpt}

Return JSON:
{{
  "should_run_simulation": true,
  "confidence": 78,
  "summary": "One-line conclusion",
  "simulation_value": "Why simulation is or is not worth running here",
  "document_sufficiency": "Assessment of document adequacy",
  "likely_limitations": ["limitation 1", "limitation 2"],
  "recommended_next_step": "Best next step"
}}"""

        llm = LLMClient()
        result = llm.chat_json(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=1200,
        )

        return jsonify({
            "success": True,
            "data": {
                "should_run_simulation": bool(result.get("should_run_simulation", False)),
                "confidence": int(result.get("confidence", 0) or 0),
                "summary": str(result.get("summary", "")).strip(),
                "simulation_value": str(result.get("simulation_value", "")).strip(),
                "document_sufficiency": str(result.get("document_sufficiency", "")).strip(),
                "likely_limitations": result.get("likely_limitations", []) or [],
                "recommended_next_step": str(result.get("recommended_next_step", "")).strip(),
                "files_analyzed": file_names,
                "document_length": len(combined_text),
            }
        })
    except Exception as e:
        logger.error(f"Simulation fit assessment failed: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


# ============== Project management endpoints ==============

@graph_bp.route('/project/<project_id>', methods=['GET'])
def get_project(project_id: str):
    """
    Get project details.
    """
    project = ProjectManager.get_project(project_id)

    if not project:
        return jsonify({
            "success": False,
            "error": f"Project not found: {project_id}"
        }), 404

    return jsonify({
        "success": True,
        "data": project.to_dict()
    })


@graph_bp.route('/project/list', methods=['GET'])
def list_projects():
    """
    List all projects.
    """
    limit = request.args.get('limit', 50, type=int)
    projects = ProjectManager.list_projects(limit=limit)

    return jsonify({
        "success": True,
        "data": [p.to_dict() for p in projects],
        "count": len(projects)
    })


@graph_bp.route('/project/<project_id>', methods=['DELETE'])
def delete_project(project_id: str):
    """
    Delete a project.
    """
    success = ProjectManager.delete_project(project_id)

    if not success:
        return jsonify({
            "success": False,
            "error": f"Project not found or deletion failed: {project_id}"
        }), 404

    return jsonify({
        "success": True,
        "message": f"Project deleted: {project_id}"
    })


@graph_bp.route('/project/<project_id>/reset', methods=['POST'])
def reset_project(project_id: str):
    """
    Reset project state so the graph can be rebuilt.
    """
    project = ProjectManager.get_project(project_id)

    if not project:
        return jsonify({
            "success": False,
            "error": f"Project not found: {project_id}"
        }), 404

    # Reset back to the ontology-generated state.
    if project.ontology:
        project.status = ProjectStatus.ONTOLOGY_GENERATED
    else:
        project.status = ProjectStatus.CREATED

    project.graph_id = None
    project.graph_build_task_id = None
    project.error = None
    ProjectManager.save_project(project)

    return jsonify({
        "success": True,
        "message": f"Project reset: {project_id}",
        "data": project.to_dict()
    })


# ============== Endpoint 1: upload files and generate ontology ==============

@graph_bp.route('/ontology/generate', methods=['POST'])
def generate_ontology():
    """
    Endpoint 1: upload files and analyze them to generate an ontology.

    Request type: multipart/form-data

    Parameters:
        files: uploaded files (PDF/MD/TXT), multiple allowed
        simulation_requirement: simulation requirement description (required)
        project_name: project name (optional)
        additional_context: additional context (optional)

    Returns:
        {
            "success": true,
            "data": {
                "project_id": "proj_xxxx",
                "ontology": {
                    "entity_types": [...],
                    "edge_types": [...],
                    "analysis_summary": "..."
                },
                "files": [...],
                "total_text_length": 12345
            }
        }
    """
    try:
        logger.info("=== Starting ontology generation ===")

        # Read form fields.
        simulation_requirement = request.form.get('simulation_requirement', '')
        project_name = request.form.get('project_name', 'Unnamed Project')
        additional_context = request.form.get('additional_context', '')
        language = request.form.get('language', Config.LANGUAGE)
        enable_news = request.form.get('enable_news', 'false').lower() == 'true'

        logger.debug(f"Project name: {project_name}")
        logger.debug(f"Simulation requirement: {simulation_requirement[:100]}...")
        logger.debug(f"Enable news: {enable_news}")

        if not simulation_requirement:
            return jsonify({
                "success": False,
                "error": "Please provide simulation_requirement"
            }), 400

        # Read uploaded files.
        uploaded_files = request.files.getlist('files')
        if not uploaded_files or all(not f.filename for f in uploaded_files):
            return jsonify({
                "success": False,
                "error": "Please upload at least one document"
            }), 400

        # Create the project.
        project = ProjectManager.create_project(name=project_name)
        project.simulation_requirement = simulation_requirement
        project.enable_news = enable_news
        logger.info(f"Created project: {project.project_id}")

        # Save the files and extract text.
        document_texts = []
        all_text = ""

        for file in uploaded_files:
            if file and file.filename and allowed_file(file.filename):
                # Save the file into the project directory.
                file_info = ProjectManager.save_file_to_project(
                    project.project_id,
                    file,
                    file.filename
                )
                project.files.append({
                    "filename": file_info["original_filename"],
                    "size": file_info["size"]
                })

                # Extract text.
                text = FileParser.extract_text(file_info["path"])
                text = TextProcessor.preprocess_text(text)
                document_texts.append(text)
                all_text += f"\n\n=== {file_info['original_filename']} ===\n{text}"

        if not document_texts:
            ProjectManager.delete_project(project.project_id)
            return jsonify({
                "success": False,
                "error": "No documents were processed successfully. Check the file formats."
            }), 400

        # Save the extracted text.
        project.total_text_length = len(all_text)
        ProjectManager.save_extracted_text(project.project_id, all_text)
        logger.info(f"Text extraction complete: {len(all_text)} characters")

        # Generate the ontology.
        logger.info("Calling the LLM to generate the ontology...")
        generator = OntologyGenerator(language=language)
        ontology = generator.generate(
            document_texts=document_texts,
            simulation_requirement=simulation_requirement,
            additional_context=additional_context if additional_context else None
        )

        # Save the ontology to the project.
        entity_count = len(ontology.get("entity_types", []))
        edge_count = len(ontology.get("edge_types", []))
        logger.info(f"Ontology generated: {entity_count} entity types, {edge_count} edge types")

        project.ontology = {
            "entity_types": ontology.get("entity_types", []),
            "edge_types": ontology.get("edge_types", [])
        }
        project.analysis_summary = ontology.get("analysis_summary", "")
        project.status = ProjectStatus.ONTOLOGY_GENERATED
        ProjectManager.save_project(project)
        logger.info(f"=== Ontology generation complete === project_id={project.project_id}")

        return jsonify({
            "success": True,
            "data": {
                "project_id": project.project_id,
                "project_name": project.name,
                "ontology": project.ontology,
                "analysis_summary": project.analysis_summary,
                "files": project.files,
                "total_text_length": project.total_text_length
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            
        }), 500


# ============== Endpoint 2: build graph ==============

@graph_bp.route('/build', methods=['POST'])
def build_graph():
    """
    Endpoint 2: build a graph from project_id.

    Request (JSON):
        {
            "project_id": "proj_xxxx",  // required, returned by endpoint 1
            "graph_name": "Graph Name", // optional
            "chunk_size": 500,          // optional, default 500
            "chunk_overlap": 50         // optional, default 50
        }

    Returns:
        {
            "success": true,
            "data": {
                "project_id": "proj_xxxx",
                "task_id": "task_xxxx",
                "message": "Graph build task started"
            }
        }
    """
    try:
        logger.info("=== Starting graph build ===")

        # Validate configuration.
        errors = []
        if not Config.ZEP_API_KEY:
            errors.append("ZEP_API_KEY is not configured")
        if errors:
            logger.error(f"Configuration errors: {errors}")
            return jsonify({
                "success": False,
                "error": "Configuration error: " + "; ".join(errors)
            }), 500

        # Parse the request.
        data = request.get_json() or {}
        project_id = data.get('project_id')
        enable_deduplication = data.get('deduplicate', True)  # Default to True
        logger.debug(f"Request params: project_id={project_id}, deduplicate={enable_deduplication}")

        if not project_id:
            return jsonify({
                "success": False,
                "error": "Please provide project_id"
            }), 400

        # Load the project.
        project = ProjectManager.get_project(project_id)
        if not project:
            return jsonify({
                "success": False,
                "error": f"Project not found: {project_id}"
            }), 404

        # Validate the project state.
        force = data.get('force', False)  # Force rebuild

        if project.status == ProjectStatus.CREATED:
            return jsonify({
                "success": False,
                "error": "The project ontology has not been generated yet. Call /ontology/generate first."
            }), 400

        if project.status == ProjectStatus.GRAPH_BUILDING and not force:
            return jsonify({
                "success": False,
                "error": "Graph build is already in progress. To rebuild anyway, set force: true.",
                "task_id": project.graph_build_task_id
            }), 400

        # Reset state for a forced rebuild.
        if force and project.status in [ProjectStatus.GRAPH_BUILDING, ProjectStatus.FAILED, ProjectStatus.GRAPH_COMPLETED]:
            project.status = ProjectStatus.ONTOLOGY_GENERATED
            project.graph_id = None
            project.graph_build_task_id = None
            project.error = None

        # Resolve configuration.
        graph_name = data.get('graph_name', project.name or 'MiroFish Graph')
        chunk_size = data.get('chunk_size', project.chunk_size or Config.DEFAULT_CHUNK_SIZE)
        chunk_overlap = data.get('chunk_overlap', project.chunk_overlap or Config.DEFAULT_CHUNK_OVERLAP)
        enable_news = data.get('enable_news', project.enable_news)
        print(f"DEBUG: build_graph - enable_news from request: {data.get('enable_news')}")
        print(f"DEBUG: build_graph - enable_news from project: {project.enable_news}")
        print(f"DEBUG: build_graph - resolved enable_news: {enable_news}")

        # Persist the project settings.
        project.chunk_size = chunk_size
        project.chunk_overlap = chunk_overlap
        project.enable_news = enable_news

        # Load the extracted text.
        text = ProjectManager.get_extracted_text(project_id)
        if not text:
            return jsonify({
                "success": False,
                "error": "Extracted text content was not found"
            }), 400

        # Load the ontology.
        ontology = project.ontology
        if not ontology:
            return jsonify({
                "success": False,
                "error": "Ontology definition was not found"
            }), 400

        # Create the async task.
        task_manager = TaskManager()
        task_id = task_manager.create_task(f"Build graph: {graph_name}")
        logger.info(f"Created graph build task: task_id={task_id}, project_id={project_id}")

        # Update project state.
        project.status = ProjectStatus.GRAPH_BUILDING
        project.graph_build_task_id = task_id
        ProjectManager.save_project(project)

        # Launch the background task.
        def build_task():
            build_logger = get_logger('mirofish.build')
            try:
                build_logger.info(f"[{task_id}] Starting graph build...")
                task_manager.update_task(
                    task_id,
                    status=TaskStatus.PROCESSING,
                    message="Initializing graph builder..."
                )

                # Create the graph builder service.
                builder = GraphBuilderService(api_key=Config.ZEP_API_KEY)

                # Split text into chunks.
                task_manager.update_task(
                    task_id,
                    message="Splitting text into chunks...",
                    progress=5
                )
                chunks = TextProcessor.split_text(
                    text,
                    chunk_size=chunk_size,
                    overlap=chunk_overlap
                )
                total_chunks = len(chunks)

                # Create the graph.
                task_manager.update_task(
                    task_id,
                    message="Creating Zep graph...",
                    progress=10
                )
                graph_id = builder.create_graph(name=graph_name)

                # Persist graph_id on the project.
                project.graph_id = graph_id
                ProjectManager.save_project(project)

                # Apply the ontology.
                task_manager.update_task(
                    task_id,
                    message="Applying ontology definition...",
                    progress=15
                )
                builder.set_ontology(graph_id, ontology)

                # Fetch and add live news if enabled.
                if enable_news:
                    task_manager.update_task(
                        task_id,
                        message="Fetching and injecting live news...",
                        progress=20
                    )
                    print(f"DEBUG: build_task - enable_news is True, fetching news for query: {project.simulation_requirement}")
                    # Use the extracted text as context for news query generation
                    context_text = text if text else ProjectManager.get_extracted_text(project_id)
                    news_episode_uuid = builder.fetch_and_add_news(
                        graph_id, 
                        query=project.simulation_requirement,
                        context_text=context_text
                    )
                    print(f"DEBUG: build_task - news_episode_uuid result: {news_episode_uuid}")
                    if news_episode_uuid:
                        logger.info(f"[{task_id}] Added live news episode: {news_episode_uuid}")
                        # Wait for news episode to be processed (optional but recommended for consistency)
                        builder._wait_for_episodes([news_episode_uuid])
                
                # Add text batches. The callback signature is (msg, progress_ratio).
                def add_progress_callback(msg, progress_ratio):
                    progress = 15 + int(progress_ratio * 40)  # 15% - 55%
                    task_manager.update_task(
                        task_id,
                        message=msg,
                        progress=progress
                    )

                task_manager.update_task(
                    task_id,
                    message=f"Adding {total_chunks} text chunks...",
                    progress=15
                )

                episode_uuids = builder.add_text_batches(
                    graph_id,
                    chunks,
                    batch_size=3,
                    progress_callback=add_progress_callback
                )

                # Wait for Zep to finish processing each episode.
                task_manager.update_task(
                    task_id,
                    message="Waiting for Zep to process data...",
                    progress=55
                )

                def wait_progress_callback(msg, progress_ratio):
                    progress = 55 + int(progress_ratio * 35)  # 55% - 90%
                    task_manager.update_task(
                        task_id,
                        message=msg,
                        progress=progress
                    )

                builder._wait_for_episodes(episode_uuids, wait_progress_callback)

                # Fetch graph data.
                task_manager.update_task(
                    task_id,
                    message="Fetching graph data...",
                    progress=95
                )
                graph_data = builder.get_graph_data(graph_id)

                # Mark the project as completed.
                project.status = ProjectStatus.GRAPH_COMPLETED
                ProjectManager.save_project(project)

                node_count = graph_data.get("node_count", 0)
                edge_count = graph_data.get("edge_count", 0)
                build_logger.info(f"[{task_id}] Graph build complete: graph_id={graph_id}, nodes={node_count}, edges={edge_count}")

                # Run entity deduplication if enabled
                dedup_result = None
                if enable_deduplication:
                    try:
                        build_logger.info(f"[{task_id}] Starting entity deduplication...")
                        from ..services.entity_deduplicator import EntityDeduplicator
                        deduplicator = EntityDeduplicator()
                        dedup_report = deduplicator.deduplicate(graph_id=graph_id)
                        dedup_result = dedup_report.to_dict()
                        build_logger.info(
                            f"[{task_id}] Entity deduplication complete: "
                            f"found {dedup_report.groups_found} groups, "
                            f"removed {dedup_report.nodes_removed} nodes, "
                            f"migrated {dedup_report.edges_migrated} edges"
                        )
                    except Exception as dedup_err:
                        build_logger.warning(f"[{task_id}] Entity deduplication failed (not affecting graph build): {dedup_err}")

                # Mark the task complete.
                task_manager.update_task(
                    task_id,
                    status=TaskStatus.COMPLETED,
                    message="Graph build complete",
                    progress=100,
                    result={
                        "project_id": project_id,
                        "graph_id": graph_id,
                        "node_count": node_count,
                        "edge_count": edge_count,
                        "chunk_count": total_chunks,
                        "dedup_report": dedup_result
                    }
                )

            except Exception as e:
                # Mark the project as failed.
                build_logger.error(f"[{task_id}] Graph build failed: {str(e)}")
                build_logger.debug(traceback.format_exc())

                project.status = ProjectStatus.FAILED
                project.error = str(e)
                ProjectManager.save_project(project)

                task_manager.update_task(
                    task_id,
                    status=TaskStatus.FAILED,
                    message=f"Build failed: {str(e)}",
                    error=traceback.format_exc()
                )

        # Start the background thread.
        thread = threading.Thread(target=build_task, daemon=True)
        thread.start()

        return jsonify({
            "success": True,
            "data": {
                "project_id": project_id,
                "task_id": task_id,
                "message": "Graph build task started. Query progress via /task/{task_id}."
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            
        }), 500


# ============== Task query endpoints ==============

@graph_bp.route('/task/<task_id>', methods=['GET'])
def get_task(task_id: str):
    """
    Query task status.
    """
    task = TaskManager().get_task(task_id)

    if not task:
        return jsonify({
            "success": False,
            "error": f"Task not found: {task_id}"
        }), 404

    return jsonify({
        "success": True,
        "data": task.to_dict()
    })


@graph_bp.route('/tasks', methods=['GET'])
def list_tasks():
    """
    List all tasks.
    """
    tasks = TaskManager().list_tasks()

    return jsonify({
        "success": True,
        "data": [t.to_dict() for t in tasks],
        "count": len(tasks)
    })


# ============== Graph data endpoints ==============

@graph_bp.route('/data/<graph_id>', methods=['GET'])
def get_graph_data(graph_id: str):
    """
    Get graph data (nodes and edges).
    """
    try:
        if not Config.ZEP_API_KEY:
            return jsonify({
                "success": False,
                "error": "ZEP_API_KEY is not configured"
            }), 500

        builder = GraphBuilderService(api_key=Config.ZEP_API_KEY)
        graph_data = builder.get_graph_data(graph_id)

        return jsonify({
            "success": True,
            "data": graph_data
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            
        }), 500


@graph_bp.route('/delete/<graph_id>', methods=['DELETE'])
def delete_graph(graph_id: str):
    """
    Delete a Zep graph.
    """
    try:
        if not Config.ZEP_API_KEY:
            return jsonify({
                "success": False,
                "error": "ZEP_API_KEY is not configured"
            }), 500

        builder = GraphBuilderService(api_key=Config.ZEP_API_KEY)
        builder.delete_graph(graph_id)

        return jsonify({
            "success": True,
            "message": f"Graph deleted: {graph_id}"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            
        }), 500


@graph_bp.route('/deduplicate', methods=['POST'])
def deduplicate_graph():
    """
    Run entity deduplication on a graph.
    
    Request body (JSON):
    {
        "graph_id": "required - Zep graph ID",
        "dry_run": "optional - if true, only detect duplicates without merging"
    }
    
    Returns:
    {
        "success": true,
        "data": { ...DeduplicationReport... }
    }
    """
    try:
        data = request.get_json() or {}
        graph_id = data.get('graph_id')
        dry_run = data.get('dry_run', False)
        
        if not graph_id:
            return jsonify({
                "success": False,
                "error": "graph_id is required"
            }), 400
        
        if not Config.ZEP_API_KEY:
            return jsonify({
                "success": False,
                "error": "ZEP_API_KEY is not configured"
            }), 500
        
        from ..services.entity_deduplicator import EntityDeduplicator
        deduplicator = EntityDeduplicator()
        report = deduplicator.deduplicate(graph_id=graph_id, dry_run=dry_run)
        
        return jsonify({
            "success": True,
            "data": report.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Entity deduplication failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
