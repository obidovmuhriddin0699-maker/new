"""AI agent tool permissions.

There is deliberately NO publish permission in this enum. Publishing is not an
agent tool at all: it is performed only by the backend publish service after a
human approval (PHASE 6/8). ``FORBIDDEN_FOR_AGENTS`` documents the names that
must never be granted, and ``grant`` refuses them even if requested via config.
"""

from enum import StrEnum


class AgentTool(StrEnum):
    READ_ANALYTICS = "READ_ANALYTICS"
    CREATE_CONTENT = "CREATE_CONTENT"
    EDIT_CONTENT = "EDIT_CONTENT"
    GENERATE_MEDIA = "GENERATE_MEDIA"
    CREATE_SCHEDULE = "CREATE_SCHEDULE"
    REQUEST_APPROVAL = "REQUEST_APPROVAL"


FORBIDDEN_FOR_AGENTS: frozenset[str] = frozenset(
    {"PUBLISH_TO_INSTAGRAM", "APPROVE_CONTENT", "MANAGE_OAUTH_TOKENS"}
)

DEFAULT_AGENT_TOOLS: frozenset[AgentTool] = frozenset(AgentTool)


class ForbiddenAgentPermissionError(PermissionError):
    pass


def grant(names: list[str]) -> frozenset[AgentTool]:
    """Build a permission set from names, rejecting forbidden or unknown ones."""
    tools: set[AgentTool] = set()
    for name in names:
        if name.upper() in FORBIDDEN_FOR_AGENTS:
            raise ForbiddenAgentPermissionError(f"{name} can never be granted to an AI agent")
        tools.add(AgentTool(name.upper()))
    return frozenset(tools)


def is_allowed(granted: frozenset[AgentTool], tool: str) -> bool:
    if tool.upper() in FORBIDDEN_FOR_AGENTS:
        return False
    try:
        return AgentTool(tool.upper()) in granted
    except ValueError:
        return False


# Tools granted to the content pipeline agents (PHASE 3). Deliberately excludes
# CREATE_SCHEDULE: scheduling is a human decision after approval.
PIPELINE_AGENT_TOOLS: frozenset[AgentTool] = frozenset(
    {
        AgentTool.READ_ANALYTICS,
        AgentTool.CREATE_CONTENT,
        AgentTool.EDIT_CONTENT,
        AgentTool.GENERATE_MEDIA,
        AgentTool.REQUEST_APPROVAL,
    }
)
