from fastapi.testclient import TestClient

from backend.app.dependencies import CSRF_COOKIE_NAME


PASSWORD = "correct horse battery staple"


def register(client: TestClient, email: str) -> dict:
    response = client.post("/auth/register", json={"email": email, "password": PASSWORD})
    assert response.status_code == 201
    return response.json()


def csrf_headers(client: TestClient) -> dict[str, str]:
    return {"X-CSRF-Token": client.cookies[CSRF_COOKIE_NAME]}


def test_multiple_workspaces_selection_and_membership_isolation(client) -> None:
    register(client, "owner@example.com")
    headers = csrf_headers(client)
    first = client.post("/workspaces", json={"name": "Workspace One"}, headers=headers)
    second = client.post("/workspaces", json={"name": "Workspace Two"}, headers=headers)
    assert first.status_code == second.status_code == 201

    guest = TestClient(client.app)
    with guest:
        register(guest, "guest@example.com")
        added = client.post(
            f"/workspaces/{first.json()['id']}/members",
            json={"email": "guest@example.com"},
            headers=headers,
        )
        assert added.status_code == 201
        assert added.json()["role"] == "member"

        visible = guest.get("/workspaces")
        assert visible.status_code == 200
        assert [item["id"] for item in visible.json()] == [first.json()["id"]]
        assert guest.get(f"/workspaces/{second.json()['id']}/members").status_code == 404
        assert guest.post(
            f"/workspaces/{second.json()['id']}/select",
            headers=csrf_headers(guest),
        ).status_code == 404

        selected = guest.post(
            f"/workspaces/{first.json()['id']}/select",
            headers=csrf_headers(guest),
        )
        assert selected.status_code == 200
        assert guest.get("/auth/me").json()["active_workspace_id"] == first.json()["id"]


def test_membership_roles_enforce_owner_admin_member_permissions(client) -> None:
    owner_user = register(client, "owner@example.com")
    headers = csrf_headers(client)
    workspace = client.post("/workspaces", json={"name": "Role Test"}, headers=headers).json()
    admin = TestClient(client.app)
    member = TestClient(client.app)
    recruit = TestClient(client.app)

    with admin, member, recruit:
        admin_user = register(admin, "admin@example.com")
        member_user = register(member, "member@example.com")
        register(recruit, "recruit@example.com")
        assert client.post(
            f"/workspaces/{workspace['id']}/members",
            json={"email": "admin@example.com", "role": "admin"},
            headers=headers,
        ).status_code == 201
        assert client.post(
            f"/workspaces/{workspace['id']}/members",
            json={"email": "member@example.com", "role": "member"},
            headers=headers,
        ).status_code == 201

        assert member.post(
            f"/workspaces/{workspace['id']}/members",
            json={"email": "owner@example.com"},
            headers=csrf_headers(member),
        ).status_code == 403
        assert member.patch(
            f"/workspaces/{workspace['id']}/members/{admin_user['id']}",
            json={"role": "member"},
            headers=csrf_headers(member),
        ).status_code == 403
        assert admin.patch(
            f"/workspaces/{workspace['id']}/members/{member_user['id']}",
            json={"role": "admin"},
            headers=csrf_headers(admin),
        ).status_code == 403
        assert admin.post(
            f"/workspaces/{workspace['id']}/members",
            json={"email": "recruit@example.com"},
            headers=csrf_headers(admin),
        ).status_code == 201
        assert admin.post(
            f"/workspaces/{workspace['id']}/members",
            json={"email": "recruit@example.com", "role": "admin"},
            headers=csrf_headers(admin),
        ).status_code == 403

        demoted = client.patch(
            f"/workspaces/{workspace['id']}/members/{admin_user['id']}",
            json={"role": "member"},
            headers=headers,
        )
        assert demoted.status_code == 200
        assert demoted.json()["role"] == "member"

        owner_update = client.patch(
            f"/workspaces/{workspace['id']}/members/{owner_user['id']}",
            json={"role": "member"},
            headers=headers,
        )
        assert owner_update.status_code == 403
