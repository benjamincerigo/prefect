"""
Reduced schemas for accepting API actions
"""
from prefect.orion.schemas.core import State, Flow, FlowRun, TaskRun

FlowCreate = Flow.subclass(
    name="FlowCreate",
    include_fields=["name", "tags", "parameters"],
)

FlowRunCreate = FlowRun.subclass(
    name="FlowRunCreate",
    include_fields=[
        "flow_id",
        "flow_version",
        "parameters",
        "parent_task_run_id",
        "context",
        "tags",
        "flow_run_metadata",
    ],
)

StateCreate = State.subclass(
    name="StateCreate",
    include_fields=[
        "type",
        "name",
        "timestamp",
        "message",
        "data",
        "state_details",
    ],
)

TaskRunCreate = TaskRun.subclass(
    name="TaskRunCreate",
    include_fields=[
        "flow_run_id",
        "task_key",
        "dynamic_key",
        "cache_key",
        "cache_expiration",
        "task_version",
        "empirical_policy",
        "tags",
        "task_inputs",
        "upstream_task_run_ids",
        "task_run_metadata",
    ],
)
