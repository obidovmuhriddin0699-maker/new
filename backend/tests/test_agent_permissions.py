import pytest

from app.agents.permissions import (
    DEFAULT_AGENT_TOOLS,
    AgentTool,
    ForbiddenAgentPermissionError,
    grant,
    is_allowed,
)


def test_publish_is_not_an_agent_tool():
    names = {t.value for t in AgentTool}
    assert "PUBLISH_TO_INSTAGRAM" not in names
    assert not any("PUBLISH" in n for n in names)


def test_default_tools():
    assert DEFAULT_AGENT_TOOLS == {
        AgentTool.READ_ANALYTICS,
        AgentTool.CREATE_CONTENT,
        AgentTool.EDIT_CONTENT,
        AgentTool.GENERATE_MEDIA,
        AgentTool.CREATE_SCHEDULE,
        AgentTool.REQUEST_APPROVAL,
    }


@pytest.mark.parametrize(
    "name", ["PUBLISH_TO_INSTAGRAM", "publish_to_instagram", "APPROVE_CONTENT"]
)
def test_forbidden_permissions_cannot_be_granted(name):
    with pytest.raises(ForbiddenAgentPermissionError):
        grant(["CREATE_CONTENT", name])


def test_is_allowed():
    tools = grant(["CREATE_CONTENT"])
    assert is_allowed(tools, "CREATE_CONTENT")
    assert not is_allowed(tools, "EDIT_CONTENT")
    assert not is_allowed(DEFAULT_AGENT_TOOLS, "PUBLISH_TO_INSTAGRAM")
    assert not is_allowed(DEFAULT_AGENT_TOOLS, "UNKNOWN")


def test_no_publish_endpoint_exists(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert not any("publish" in p.lower() for p in paths)
    # PHASE 2: the only approval endpoint is the human-only content approve route.
    assert [p for p in paths if "approve" in p.lower()] == ["/api/v1/contents/{content_id}/approve"]
