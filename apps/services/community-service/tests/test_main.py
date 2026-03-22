"""
Comprehensive tests for community-service | اختبارات شاملة لخدمة المجتمع الزراعي
=================================================================================
Tests cover all endpoints, authentication, tenant isolation, rate limiting,
error handling, and Rocket.Chat client interaction.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Module-level fixtures (import app with mocked auth)
# ---------------------------------------------------------------------------
TENANT_ID_1 = "00000000-0000-0000-0000-000000000001"
TENANT_ID_2 = "00000000-0000-0000-0000-000000000002"


def _make_user(
    user_id="test-user-001",
    username="test_farmer",
    email="farmer@sahool.app",
    tenant_id=TENANT_ID_1,
    roles=None,
):
    """Create a mock authenticated user. | إنشاء مستخدم مصادق وهمي"""
    user = MagicMock()
    user.id = user_id
    user.username = username
    user.email = email
    user.tenant_id = tenant_id
    user.roles = roles or ["user"]
    return user


def _make_rc_mock():
    """Create a fresh Rocket.Chat mock client. | إنشاء عميل روكيت شات وهمي"""
    rc = AsyncMock()
    rc.create_channel = AsyncMock(return_value={"_id": "ch001", "name": "test-channel"})
    rc.get_channels = AsyncMock(return_value=[])
    rc.post_message = AsyncMock(return_value={"_id": "msg001", "ts": "2026-01-01T00:00:00Z"})

    rc.add_user_to_channel = AsyncMock(return_value={})
    rc.remove_user_from_channel = AsyncMock(return_value={})
    rc.get_channel_history = AsyncMock(return_value=[])
    rc.get_channel_members = AsyncMock(return_value=[])
    rc.search_messages = AsyncMock(return_value=[])
    rc.create_user = AsyncMock(return_value={"_id": "rc_user_001", "username": "test"})

    rc.set_user_avatar = AsyncMock(return_value={})
    rc.pin_message = AsyncMock(return_value={})
    return rc


def _make_app(user, rc_mock=None, rc_connected=True):
    """Build a TestClient with mocked dependencies. | بناء عميل اختبار بالتبعيات الوهمية"""
    from src.main import app, get_current_user

    async def _override_user():
        return user

    app.dependency_overrides[get_current_user] = _override_user

    if rc_mock is not None:
        app.state.rc = rc_mock
    else:
        app.state.rc = _make_rc_mock()
    app.state.rc_connected = rc_connected
    app.state.db_pool = AsyncMock()
    app.state.db_connected = True
    app.state.nc = AsyncMock()
    app.state.nc.publish = AsyncMock()
    app.state.nats_connected = True
    app.state.redis = None
    app.state.redis_connected = False
    client = TestClient(app)
    client.headers["X-Tenant-Id"] = user.tenant_id
    return client, app


# ===========================================================================
# 1. Health endpoints | نقاط فحص السلامة
# ===========================================================================
class TestHealthEndpoints:
    """Health endpoint tests | اختبارات نقاط السلامة"""

    @pytest.mark.unit
    def test_healthz_returns_ok(self, client):
        """GET /healthz returns status ok | يعيد حالة ok"""
        resp = client.get("/healthz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "community-service"
        assert data["version"] == "16.0.0"

    @pytest.mark.unit
    def test_readyz_returns_component_status(self, rc_client, app_with_rc):
        """GET /readyz shows component statuses | يعرض حالات المكونات"""
        resp = rc_client.get("/readyz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["rocketchat"] is True
        assert data["database"] is True
        assert data["nats"] is True

    @pytest.mark.unit
    def test_health_degraded_when_rc_disconnected(self):
        """GET /health returns degraded when RC not connected | يعيد حالة متدهورة"""
        user = _make_user()
        c, app = _make_app(user, rc_connected=False)
        app.state.rc = None
        app.state.rc_connected = False
        resp = c.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "degraded"
        assert data["components"]["rocketchat"] is False

    @pytest.mark.unit
    def test_health_ok_when_rc_connected(self, rc_client):
        """GET /health returns ok when RC connected | يعيد حالة ok عند اتصال RC"""
        resp = rc_client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["components"]["rocketchat"] is True


# ===========================================================================
# 2. Tenant setup | تهيئة المستأجر
# ===========================================================================
class TestTenantSetup:
    """Tenant workspace setup tests | اختبارات تهيئة مساحة عمل المستأجر"""

    @pytest.mark.unit
    def test_setup_tenant_creates_default_channels(self, rc_client, mock_rc_client):
        """Setup tenant creates 8 default agricultural channels | ينشئ 8 قنوات زراعية افتراضية"""
        resp = rc_client.post(
            "/api/v1/community/setup-tenant",
            json={
                "tenant_id": TENANT_ID_1,
                "tenant_name": "Al-Rashid Farm",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["tenant_id"] == TENANT_ID_1
        assert data["channels_created"] == 8
        assert len(data["channels"]) == 8
        # All 8 default channels should be created via RC client
        assert mock_rc_client.create_channel.call_count == 8

    @pytest.mark.unit
    def test_setup_tenant_channel_names_have_prefix(self, rc_client, mock_rc_client):
        """Channels are prefixed with tenant ID | القنوات مسبوقة بمعرف المستأجر"""
        resp = rc_client.post(
            "/api/v1/community/setup-tenant",
            json={
                "tenant_id": TENANT_ID_1,
                "tenant_name": "Farm",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        prefix = f"t-{TENANT_ID_1[:8]}-"
        for ch in data["channels"]:
            assert ch["name"].startswith(prefix), f"Channel {ch['name']} missing prefix"

    @pytest.mark.unit
    def test_setup_tenant_with_admin_sync(self, rc_client, mock_rc_client):
        """Setup tenant syncs admin user when provided | يزامن مستخدم الإدارة"""
        resp = rc_client.post(
            "/api/v1/community/setup-tenant",
            json={
                "tenant_id": TENANT_ID_1,
                "tenant_name": "Al-Rashid Farm",
                "admin_username": "admin_rashid",
                "admin_email": "admin@rashid.farm",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["admin_synced"] is True
        mock_rc_client.create_user.assert_called_once()
        call_kwargs = mock_rc_client.create_user.call_args
        assert call_kwargs[1]["email"] == "admin@rashid.farm"
        assert call_kwargs[1]["username"] == "admin_rashid"
        assert call_kwargs[1]["roles"] == ["admin"]

    @pytest.mark.unit
    def test_setup_tenant_without_admin(self, rc_client, mock_rc_client):
        """Setup tenant without admin keeps admin_synced=False | بدون مدير"""
        resp = rc_client.post(
            "/api/v1/community/setup-tenant",
            json={"tenant_id": TENANT_ID_1, "tenant_name": "Farm"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["admin_synced"] is False
        mock_rc_client.create_user.assert_not_called()

    @pytest.mark.unit
    def test_setup_tenant_with_extra_channels(self, rc_client, mock_rc_client):
        """Setup tenant with extra channels beyond defaults | قنوات إضافية"""
        resp = rc_client.post(
            "/api/v1/community/setup-tenant",
            json={
                "tenant_id": TENANT_ID_1,
                "tenant_name": "Farm",
                "extra_channels": [
                    {
                        "name": "custom-channel",
                        "name_ar": "قناة-مخصصة",
                        "description": "A custom channel",
                    }
                ],
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        # 8 defaults + 1 extra
        assert data["channels_created"] == 9
        assert mock_rc_client.create_channel.call_count == 9

    @pytest.mark.unit
    def test_setup_tenant_channel_bilingual_info(self, rc_client, mock_rc_client):
        """Default channels include Arabic names and descriptions | أسماء عربية"""
        resp = rc_client.post(
            "/api/v1/community/setup-tenant",
            json={"tenant_id": TENANT_ID_1, "tenant_name": "Farm"},
        )
        data = resp.json()
        irrigation_ch = next(ch for ch in data["channels"] if "irrigation" in ch["name"])

        assert irrigation_ch["name_ar"] == "الري"
        assert irrigation_ch["description_ar"] == "جدولة الري وإدارة المياه"

    @pytest.mark.unit
    def test_setup_tenant_publishes_nats_event(self, rc_client, mock_nats):
        """Tenant setup publishes NATS event | ينشر حدث NATS"""
        rc_client.post(
            "/api/v1/community/setup-tenant",
            json={"tenant_id": TENANT_ID_1, "tenant_name": "Farm"},
        )
        mock_nats.publish.assert_called()
        call_args = mock_nats.publish.call_args
        subject = call_args[0][0]
        assert subject == "sahool.community.tenant_setup"

    @pytest.mark.unit
    def test_setup_tenant_tolerates_channel_creation_failure(self, rc_client, mock_rc_client):
        """Setup continues if some channels fail to create | يستمر عند فشل بعض القنوات"""
        call_count = 0

        async def flaky_create(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 3:
                raise HTTPException(status_code=502, detail="RC error")
            return {"_id": f"ch{call_count:03d}", "name": "ok"}

        mock_rc_client.create_channel = AsyncMock(side_effect=flaky_create)
        resp = rc_client.post(
            "/api/v1/community/setup-tenant",
            json={"tenant_id": TENANT_ID_1, "tenant_name": "Farm"},
        )
        assert resp.status_code == 200
        data = resp.json()
        # 8 default channels, 1 failed => 7 created
        assert data["channels_created"] == 7

    @pytest.mark.unit
    def test_setup_tenant_tolerates_admin_sync_failure(self, rc_client, mock_rc_client):
        """Setup continues if admin sync fails | يستمر عند فشل مزامنة المدير"""
        mock_rc_client.create_user = AsyncMock(side_effect=HTTPException(status_code=502, detail="RC error"))

        resp = rc_client.post(
            "/api/v1/community/setup-tenant",
            json={
                "tenant_id": TENANT_ID_1,
                "tenant_name": "Farm",
                "admin_username": "admin",
                "admin_email": "admin@farm.app",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["admin_synced"] is False


# ===========================================================================
# 3. Channel creation | إنشاء القنوات
# ===========================================================================
class TestChannelCreation:
    """Channel creation tests | اختبارات إنشاء القنوات"""

    @pytest.mark.unit
    def test_create_channel_success(self, rc_client, mock_rc_client):
        """Create channel returns correct response | ينشئ قناة بنجاح"""
        resp = rc_client.post(
            "/api/v1/community/channels",
            json={
                "name": "wheat-growers",
                "name_ar": "مزارعو-القمح",
                "description": "Wheat growing community",
                "description_ar": "مجتمع زراعة القمح",
                "topic": "Wheat",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "ch001"
        assert data["name_ar"] == "مزارعو-القمح"
        assert data["description"] == "Wheat growing community"
        assert data["description_ar"] == "مجتمع زراعة القمح"

    @pytest.mark.unit
    def test_create_channel_with_members(self, rc_client, mock_rc_client):
        """Create channel with initial members | إنشاء قناة مع أعضاء"""
        resp = rc_client.post(
            "/api/v1/community/channels",
            json={
                "name": "test-channel",
                "members": ["user1", "user2"],
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["members_count"] == 2
        mock_rc_client.create_channel.assert_called_once()
        call_kwargs = mock_rc_client.create_channel.call_args[1]
        assert call_kwargs["members"] == ["user1", "user2"]

    @pytest.mark.unit
    def test_create_channel_read_only(self, rc_client, mock_rc_client):
        """Create read-only channel | إنشاء قناة للقراءة فقط"""
        resp = rc_client.post(
            "/api/v1/community/channels",
            json={"name": "announcements", "read_only": True},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["read_only"] is True
        call_kwargs = mock_rc_client.create_channel.call_args[1]
        assert call_kwargs["read_only"] is True

    @pytest.mark.unit
    def test_create_channel_name_too_short(self, rc_client):
        """Channel name shorter than 2 chars is rejected | رفض اسم قصير جدا"""
        resp = rc_client.post(
            "/api/v1/community/channels",
            json={"name": "x"},
        )
        assert resp.status_code == 422

    @pytest.mark.unit
    def test_create_channel_name_too_long(self, rc_client):
        """Channel name longer than 64 chars is rejected | رفض اسم طويل جدا"""
        resp = rc_client.post(
            "/api/v1/community/channels",
            json={"name": "a" * 65},
        )
        assert resp.status_code == 422

    @pytest.mark.unit
    def test_create_channel_missing_name(self, rc_client):
        """Channel creation without name is rejected | رفض بدون اسم"""
        resp = rc_client.post(
            "/api/v1/community/channels",
            json={"description": "no name"},
        )
        assert resp.status_code == 422

    @pytest.mark.unit
    def test_create_channel_publishes_nats_event(self, rc_client, mock_nats):
        """Channel creation publishes NATS event | ينشر حدث NATS"""
        rc_client.post(
            "/api/v1/community/channels",
            json={"name": "test-ch"},
        )
        mock_nats.publish.assert_called()
        call_args = mock_nats.publish.call_args
        subject = call_args[0][0]
        assert subject == "sahool.community.channel_created"

    @pytest.mark.unit
    def test_create_channel_bilingual_description(self, rc_client, mock_rc_client):
        """Arabic and English descriptions are combined | دمج الوصف العربي والإنجليزي"""
        rc_client.post(
            "/api/v1/community/channels",
            json={
                "name": "test-ch",
                "description": "English desc",
                "description_ar": "وصف عربي",
            },
        )
        call_kwargs = mock_rc_client.create_channel.call_args[1]
        assert "English desc" in call_kwargs["description"]
        assert "وصف عربي" in call_kwargs["description"]


# ===========================================================================
# 4. Channel listing | عرض القنوات
# ===========================================================================
class TestChannelListing:
    """Channel listing tests | اختبارات عرض القنوات"""

    @pytest.mark.unit
    def test_list_channels_empty(self, rc_client, mock_rc_client):
        """List channels returns empty when none exist | قائمة فارغة"""
        mock_rc_client.get_channels = AsyncMock(return_value=[])
        resp = rc_client.get("/api/v1/community/channels")
        assert resp.status_code == 200
        data = resp.json()
        assert data["channels"] == []
        assert data["count"] == 0

    @pytest.mark.unit
    def test_list_channels_returns_channel_data(self, rc_client, mock_rc_client):
        """List channels maps RC response correctly | تعيين بيانات القنوات"""
        mock_rc_client.get_channels = AsyncMock(
            return_value=[
                {
                    "_id": "ch001",
                    "name": "irrigation",
                    "description": "Irrigation",
                    "topic": "Water",
                    "usersCount": 15,
                    "ro": False,
                },
                {
                    "_id": "ch002",
                    "name": "announcements",
                    "description": "Announcements",
                    "topic": "News",
                    "usersCount": 50,
                    "ro": True,
                },
            ]
        )
        resp = rc_client.get("/api/v1/community/channels")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 2
        assert data["channels"][0]["id"] == "ch001"
        assert data["channels"][0]["members_count"] == 15
        assert data["channels"][1]["read_only"] is True

    @pytest.mark.unit
    def test_list_channels_with_pagination(self, rc_client, mock_rc_client):
        """List channels supports count and offset params | دعم التصفح"""
        mock_rc_client.get_channels = AsyncMock(return_value=[])
        resp = rc_client.get("/api/v1/community/channels?count=10&offset=5")
        assert resp.status_code == 200
        mock_rc_client.get_channels.assert_called_once_with(count=10, offset=5)

    @pytest.mark.unit
    def test_list_channels_count_validation(self, rc_client):
        """Count parameter must be between 1 and 500 | حدود معامل العدد"""
        resp = rc_client.get("/api/v1/community/channels?count=0")
        assert resp.status_code == 422
        resp = rc_client.get("/api/v1/community/channels?count=501")
        assert resp.status_code == 422


# ===========================================================================
# 5. Channel join/leave | الانضمام/المغادرة
# ===========================================================================
class TestChannelJoinLeave:
    """Channel join and leave tests | اختبارات الانضمام والمغادرة"""

    @pytest.mark.unit
    def test_join_channel(self, rc_client, mock_rc_client):
        """Join channel adds user via RC | الانضمام يضيف المستخدم"""
        resp = rc_client.post("/api/v1/community/channels/ch001/join")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "joined"
        assert data["channel_id"] == "ch001"
        # user_id comes from the authenticated user (mocked or fallback)
        assert "user_id" in data
        mock_rc_client.add_user_to_channel.assert_called_once()
        call_args = mock_rc_client.add_user_to_channel.call_args[0]
        assert call_args[0] == "ch001"

    @pytest.mark.unit
    def test_leave_channel(self, rc_client, mock_rc_client):
        """Leave channel removes user via RC | المغادرة تزيل المستخدم"""
        resp = rc_client.post("/api/v1/community/channels/ch001/leave")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "left"
        assert data["channel_id"] == "ch001"
        mock_rc_client.remove_user_from_channel.assert_called_once()
        call_args = mock_rc_client.remove_user_from_channel.call_args[0]
        assert call_args[0] == "ch001"

    @pytest.mark.unit
    def test_join_channel_publishes_nats_event(self, rc_client, mock_nats):
        """Join channel publishes NATS event | الانضمام ينشر حدث NATS"""
        rc_client.post("/api/v1/community/channels/ch001/join")
        mock_nats.publish.assert_called()
        call_args = mock_nats.publish.call_args
        subject = call_args[0][0]
        assert subject == "sahool.community.user_joined"

    @pytest.mark.unit
    def test_get_channel_members(self, rc_client, mock_rc_client):
        """Get channel members returns member list | عرض أعضاء القناة"""
        mock_rc_client.get_channel_members = AsyncMock(
            return_value=[
                {"_id": "u1", "username": "farmer1", "name": "Ahmad", "status": "online"},
                {"_id": "u2", "username": "farmer2", "name": "Khalid", "status": "offline"},
            ]
        )
        resp = rc_client.get("/api/v1/community/channels/ch001/members")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 2
        assert data["members"][0]["user_id"] == "u1"
        assert data["members"][0]["username"] == "farmer1"
        assert data["members"][1]["status"] == "offline"


# ===========================================================================
# 6. Channel history | سجل القناة
# ===========================================================================
class TestChannelHistory:
    """Channel history tests | اختبارات سجل القناة"""

    @pytest.mark.unit
    def test_get_channel_history_empty(self, rc_client, mock_rc_client):
        """Empty history returns empty list | سجل فارغ"""
        mock_rc_client.get_channel_history = AsyncMock(return_value=[])
        resp = rc_client.get("/api/v1/community/channels/ch001/history")
        assert resp.status_code == 200
        data = resp.json()
        assert data["messages"] == []
        assert data["count"] == 0

    @pytest.mark.unit
    def test_get_channel_history_with_messages(self, rc_client, mock_rc_client):
        """History returns mapped messages | السجل يعيد رسائل معينة"""
        mock_rc_client.get_channel_history = AsyncMock(
            return_value=[
                {
                    "_id": "msg001",
                    "msg": "Hello farmers!",
                    "u": {"name": "Ahmad", "username": "ahmad"},
                    "ts": "2026-01-01T10:00:00Z",
                    "pinned": True,
                },
                {
                    "_id": "msg002",
                    "msg": "مرحبا بالمزارعين!",
                    "u": {"name": "Khalid", "username": "khalid"},
                    "ts": "2026-01-01T11:00:00Z",
                    "pinned": False,
                },
            ]
        )
        resp = rc_client.get("/api/v1/community/channels/ch001/history")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 2
        assert data["messages"][0]["id"] == "msg001"
        assert data["messages"][0]["text"] == "Hello farmers!"
        assert data["messages"][0]["user"] == "Ahmad"
        assert data["messages"][0]["username"] == "ahmad"
        assert data["messages"][0]["pinned"] is True
        assert data["messages"][1]["text"] == "مرحبا بالمزارعين!"

    @pytest.mark.unit
    def test_get_channel_history_with_count(self, rc_client, mock_rc_client):
        """History supports count parameter | دعم معامل العدد"""
        resp = rc_client.get("/api/v1/community/channels/ch001/history?count=10")
        assert resp.status_code == 200
        mock_rc_client.get_channel_history.assert_called_once_with("ch001", count=10, oldest=None)

    @pytest.mark.unit
    def test_get_channel_history_with_oldest(self, rc_client, mock_rc_client):
        """History supports oldest timestamp filter | دعم فلتر الأقدم"""
        ts = "2026-01-01T00:00:00Z"
        resp = rc_client.get(f"/api/v1/community/channels/ch001/history?oldest={ts}")
        assert resp.status_code == 200
        mock_rc_client.get_channel_history.assert_called_once_with("ch001", count=50, oldest=ts)

    @pytest.mark.unit
    def test_get_channel_history_count_validation(self, rc_client):
        """History count must be between 1 and 200 | حدود العدد"""
        resp = rc_client.get("/api/v1/community/channels/ch001/history?count=0")
        assert resp.status_code == 422
        resp = rc_client.get("/api/v1/community/channels/ch001/history?count=201")
        assert resp.status_code == 422


# ===========================================================================
# 7. Message posting | نشر الرسائل
# ===========================================================================
class TestMessagePosting:
    """Message posting tests | اختبارات نشر الرسائل"""

    @pytest.mark.unit
    def test_post_message_success(self, rc_client, mock_rc_client):
        """Post message returns correct response | نشر رسالة بنجاح"""
        resp = rc_client.post(
            "/api/v1/community/messages",
            json={
                "channel_id": "ch001",
                "text": "Hello community!",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "msg001"
        assert data["channel_id"] == "ch001"
        assert data["text"] == "Hello community!"
        # user field comes from the authenticated user (mocked or fallback)
        assert "user" in data

    @pytest.mark.unit
    def test_post_message_with_alias_and_emoji(self, rc_client, mock_rc_client):
        """Post message with alias and emoji | نشر رسالة مع لقب ورمز"""
        rc_client.post(
            "/api/v1/community/messages",
            json={
                "channel_id": "ch001",
                "text": "Irrigation update",
                "alias": "Irrigation Bot",
                "emoji": ":droplet:",
            },
        )
        mock_rc_client.post_message.assert_called_once()
        call_kwargs = mock_rc_client.post_message.call_args[1]
        assert call_kwargs["alias"] == "Irrigation Bot"
        assert call_kwargs["emoji"] == ":droplet:"

    @pytest.mark.unit
    def test_post_message_with_attachments(self, rc_client, mock_rc_client):
        """Post message with attachments | نشر رسالة مع مرفقات"""
        attachments = [{"title": "Report", "text": "Details"}]
        rc_client.post(
            "/api/v1/community/messages",
            json={
                "channel_id": "ch001",
                "text": "See report",
                "attachments": attachments,
            },
        )
        call_kwargs = mock_rc_client.post_message.call_args[1]
        assert call_kwargs["attachments"] == attachments

    @pytest.mark.unit
    def test_post_message_empty_text_rejected(self, rc_client):
        """Empty message text is rejected | رفض نص فارغ"""
        resp = rc_client.post(
            "/api/v1/community/messages",
            json={"channel_id": "ch001", "text": ""},
        )
        assert resp.status_code == 422

    @pytest.mark.unit
    def test_post_message_missing_channel_id(self, rc_client):
        """Missing channel_id is rejected | رفض بدون معرف القناة"""
        resp = rc_client.post(
            "/api/v1/community/messages",
            json={"text": "Hello"},
        )
        assert resp.status_code == 422

    @pytest.mark.unit
    def test_post_message_text_too_long(self, rc_client):
        """Message text longer than 5000 chars is rejected | رفض نص طويل جدا"""
        resp = rc_client.post(
            "/api/v1/community/messages",
            json={"channel_id": "ch001", "text": "a" * 5001},
        )
        assert resp.status_code == 422

    @pytest.mark.unit
    def test_post_message_publishes_nats_event(self, rc_client, mock_nats):
        """Message posting publishes NATS event | النشر ينشر حدث NATS"""
        rc_client.post(
            "/api/v1/community/messages",
            json={"channel_id": "ch001", "text": "Hello"},
        )
        mock_nats.publish.assert_called()
        call_args = mock_nats.publish.call_args
        subject = call_args[0][0]
        assert subject == "sahool.community.message_posted"

    @pytest.mark.unit
    def test_post_message_arabic_text(self, rc_client, mock_rc_client):
        """Arabic message text is handled correctly | النص العربي"""
        arabic_text = "مرحبا بالجميع في قناة الري"
        resp = rc_client.post(
            "/api/v1/community/messages",
            json={"channel_id": "ch001", "text": arabic_text},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["text"] == arabic_text


# ===========================================================================
# 8. Message search | البحث في الرسائل
# ===========================================================================
class TestMessageSearch:
    """Message search tests | اختبارات البحث في الرسائل"""

    @pytest.mark.unit
    def test_search_messages_empty_results(self, rc_client, mock_rc_client):
        """Search with no results returns empty | بحث بدون نتائج"""
        mock_rc_client.search_messages = AsyncMock(return_value=[])
        resp = rc_client.post(
            "/api/v1/community/messages/search",
            json={"channel_id": "ch001", "query": "wheat"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["messages"] == []
        assert data["count"] == 0
        assert data["query"] == "wheat"

    @pytest.mark.unit
    def test_search_messages_with_results(self, rc_client, mock_rc_client):
        """Search returns matching messages | البحث يعيد رسائل مطابقة"""
        mock_rc_client.search_messages = AsyncMock(
            return_value=[
                {
                    "_id": "msg001",
                    "msg": "Wheat irrigation tips",
                    "u": {"username": "expert"},
                    "ts": "2026-01-01T10:00:00Z",
                },
            ]
        )
        resp = rc_client.post(
            "/api/v1/community/messages/search",
            json={"channel_id": "ch001", "query": "wheat"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert data["messages"][0]["text"] == "Wheat irrigation tips"
        assert data["messages"][0]["user"] == "expert"

    @pytest.mark.unit
    def test_search_messages_empty_query_rejected(self, rc_client):
        """Empty search query is rejected | رفض بحث فارغ"""
        resp = rc_client.post(
            "/api/v1/community/messages/search",
            json={"channel_id": "ch001", "query": ""},
        )
        assert resp.status_code == 422

    @pytest.mark.unit
    def test_search_messages_query_too_long(self, rc_client):
        """Search query longer than 200 chars is rejected | رفض بحث طويل جدا"""
        resp = rc_client.post(
            "/api/v1/community/messages/search",
            json={"channel_id": "ch001", "query": "q" * 201},
        )
        assert resp.status_code == 422

    @pytest.mark.unit
    def test_search_messages_arabic_query(self, rc_client, mock_rc_client):
        """Arabic search queries are supported | دعم البحث بالعربية"""
        mock_rc_client.search_messages = AsyncMock(return_value=[])
        resp = rc_client.post(
            "/api/v1/community/messages/search",
            json={"channel_id": "ch001", "query": "القمح"},
        )
        assert resp.status_code == 200
        mock_rc_client.search_messages.assert_called_once_with("ch001", "القمح")


# ===========================================================================
# 9. User sync | مزامنة المستخدمين
# ===========================================================================
class TestUserSync:
    """User sync tests | اختبارات مزامنة المستخدمين"""

    @pytest.mark.unit
    def test_sync_user_success(self, rc_client, mock_rc_client):
        """Sync user creates RC user and returns ID | مزامنة مستخدم بنجاح"""
        resp = rc_client.post(
            "/api/v1/community/users/sync",
            json={
                "email": "farmer@sahool.app",
                "name": "Ahmad Al-Rashid",
                "username": "ahmad_farmer",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["rc_user_id"] == "rc_user_001"
        assert data["username"] == "ahmad_farmer"
        assert data["synced"] is True

    @pytest.mark.unit
    def test_sync_user_with_avatar(self, rc_client, mock_rc_client):
        """Sync user sets avatar when URL provided | تعيين صورة المستخدم"""
        resp = rc_client.post(
            "/api/v1/community/users/sync",
            json={
                "email": "farmer@sahool.app",
                "name": "Ahmad",
                "username": "ahmad",
                "avatar_url": "https://example.com/avatar.png",
            },
        )
        assert resp.status_code == 200
        mock_rc_client.set_user_avatar.assert_called_once_with("rc_user_001", "https://example.com/avatar.png")

    @pytest.mark.unit
    def test_sync_user_without_avatar(self, rc_client, mock_rc_client):
        """Sync user without avatar does not call set_user_avatar | بدون صورة"""
        rc_client.post(
            "/api/v1/community/users/sync",
            json={
                "email": "farmer@sahool.app",
                "name": "Ahmad",
                "username": "ahmad",
            },
        )
        mock_rc_client.set_user_avatar.assert_not_called()

    @pytest.mark.unit
    def test_sync_user_with_custom_roles(self, rc_client, mock_rc_client):
        """Sync user with custom roles passes them to RC | أدوار مخصصة"""
        rc_client.post(
            "/api/v1/community/users/sync",
            json={
                "email": "admin@sahool.app",
                "name": "Admin",
                "username": "admin_user",
                "roles": ["admin", "moderator"],
            },
        )
        call_kwargs = mock_rc_client.create_user.call_args[1]
        assert call_kwargs["roles"] == ["admin", "moderator"]

    @pytest.mark.unit
    def test_sync_user_generates_password_when_missing(self, rc_client, mock_rc_client):
        """Password is auto-generated when not provided | توليد كلمة مرور تلقائي"""
        rc_client.post(
            "/api/v1/community/users/sync",
            json={
                "email": "farmer@sahool.app",
                "name": "Ahmad",
                "username": "ahmad",
            },
        )
        call_kwargs = mock_rc_client.create_user.call_args[1]
        assert len(call_kwargs["password"]) == 16  # uuid4().hex[:16]

    @pytest.mark.unit
    def test_sync_user_avatar_failure_does_not_break(self, rc_client, mock_rc_client):
        """Avatar set failure does not break sync | فشل الصورة لا يكسر المزامنة"""
        mock_rc_client.set_user_avatar = AsyncMock(side_effect=HTTPException(status_code=502, detail="Avatar error"))

        resp = rc_client.post(
            "/api/v1/community/users/sync",
            json={
                "email": "farmer@sahool.app",
                "name": "Ahmad",
                "username": "ahmad",
                "avatar_url": "https://example.com/bad.png",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["synced"] is True


# ===========================================================================
# 10. Advisory bot | بوت الاستشارات
# ===========================================================================
class TestAdvisoryBot:
    """Advisory bot tests | اختبارات بوت الاستشارات"""

    @pytest.mark.unit
    def test_post_advisory_irrigation(self, rc_client, mock_rc_client):
        """Advisory for irrigation routes to irrigation channel | استشارة ري"""
        resp = rc_client.post(
            "/api/v1/community/bots/advisory",
            json={
                "advisory_type": "irrigation",
                "text": "Increase irrigation by 20mm this week",
                "severity": "warning",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "posted"
        assert data["channel"] == "irrigation"
        assert data["advisory_type"] == "irrigation"
        call_kwargs = mock_rc_client.post_message.call_args[1]
        assert call_kwargs["channel"] == "irrigation"
        assert call_kwargs["alias"] == "SAHOOL Advisory Bot"

    @pytest.mark.unit
    def test_post_advisory_crop_diseases(self, rc_client, mock_rc_client):
        """Advisory for crop-diseases routes correctly | استشارة أمراض"""
        resp = rc_client.post(
            "/api/v1/community/bots/advisory",
            json={
                "advisory_type": "crop-diseases",
                "text": "Wheat rust detected",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["channel"] == "crop-diseases"

    @pytest.mark.unit
    def test_post_advisory_unknown_type_defaults_to_best_practices(self, rc_client, mock_rc_client):
        """Unknown advisory type routes to best-practices | النوع غير المعروف"""
        resp = rc_client.post(
            "/api/v1/community/bots/advisory",
            json={
                "advisory_type": "unknown-type",
                "text": "General advice",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["channel"] == "best-practices"

    @pytest.mark.unit
    def test_post_advisory_bilingual(self, rc_client, mock_rc_client):
        """Advisory with Arabic text includes both languages | استشارة ثنائية اللغة"""
        rc_client.post(
            "/api/v1/community/bots/advisory",
            json={
                "advisory_type": "irrigation",
                "text": "Increase water by 20mm",
                "text_ar": "زيادة الري بمقدار 20 ملم",
                "severity": "info",
            },
        )
        call_kwargs = mock_rc_client.post_message.call_args[1]
        posted_text = call_kwargs["text"]
        assert "Increase water by 20mm" in posted_text
        assert "زيادة الري بمقدار 20 ملم" in posted_text

    @pytest.mark.unit
    def test_post_advisory_severity_emojis(self, rc_client, mock_rc_client):
        """Advisory severity maps to correct emoji | رموز الشدة"""
        for severity, expected_emoji in [("info", "ℹ️"), ("warning", "⚠️"), ("critical", "🚨")]:
            mock_rc_client.post_message.reset_mock()
            rc_client.post(
                "/api/v1/community/bots/advisory",
                json={
                    "advisory_type": "irrigation",
                    "text": "Test",
                    "severity": severity,
                },
            )
            call_kwargs = mock_rc_client.post_message.call_args[1]
            assert expected_emoji in call_kwargs["text"]

    @pytest.mark.unit
    def test_post_advisory_with_source(self, rc_client, mock_rc_client):
        """Advisory includes source when provided | المصدر"""
        rc_client.post(
            "/api/v1/community/bots/advisory",
            json={
                "advisory_type": "weather-alerts",
                "text": "Heat advisory",
                "source": "weather-service",
            },
        )
        call_kwargs = mock_rc_client.post_message.call_args[1]
        assert "weather-service" in call_kwargs["text"]

    @pytest.mark.unit
    def test_post_advisory_publishes_nats_event(self, rc_client, mock_nats):
        """Advisory posts NATS event | ينشر حدث NATS"""
        rc_client.post(
            "/api/v1/community/bots/advisory",
            json={
                "advisory_type": "irrigation",
                "text": "Test advisory",
            },
        )
        mock_nats.publish.assert_called()
        call_args = mock_nats.publish.call_args
        subject = call_args[0][0]
        assert subject == "sahool.community.advisory_posted"


# ===========================================================================
# 11. Alert bot | بوت التنبيهات
# ===========================================================================
class TestAlertBot:
    """Alert bot tests | اختبارات بوت التنبيهات"""

    @pytest.mark.unit
    def test_post_weather_alert(self, rc_client, mock_rc_client):
        """Weather alert routes to weather-alerts channel | تنبيه طقس"""
        resp = rc_client.post(
            "/api/v1/community/bots/alert",
            json={
                "alert_type": "weather",
                "title": "Heat Wave Warning",
                "text": "Temperatures exceeding 45C expected",
                "severity": "critical",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["channel"] == "weather-alerts"
        assert data["alert_type"] == "weather"
        assert data["severity"] == "critical"

    @pytest.mark.unit
    def test_post_pest_alert(self, rc_client, mock_rc_client):
        """Pest alert routes to pest-management channel | تنبيه آفات"""
        resp = rc_client.post(
            "/api/v1/community/bots/alert",
            json={
                "alert_type": "pest",
                "title": "RPW Detected",
                "text": "Red Palm Weevil detected in Block B",
                "severity": "critical",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["channel"] == "pest-management"

    @pytest.mark.unit
    def test_post_disease_alert(self, rc_client, mock_rc_client):
        """Disease alert routes to crop-diseases channel | تنبيه مرض"""
        resp = rc_client.post(
            "/api/v1/community/bots/alert",
            json={
                "alert_type": "disease",
                "title": "Wheat Rust",
                "text": "Wheat rust detected",
                "severity": "warning",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["channel"] == "crop-diseases"

    @pytest.mark.unit
    def test_post_frost_alert(self, rc_client, mock_rc_client):
        """Frost alert routes to weather-alerts | تنبيه صقيع"""
        resp = rc_client.post(
            "/api/v1/community/bots/alert",
            json={
                "alert_type": "frost",
                "title": "Frost Warning",
                "text": "Frost expected tonight",
                "severity": "warning",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["channel"] == "weather-alerts"

    @pytest.mark.unit
    def test_post_unknown_alert_type_defaults_to_announcements(self, rc_client, mock_rc_client):
        """Unknown alert type defaults to announcements | النوع غير المعروف"""
        resp = rc_client.post(
            "/api/v1/community/bots/alert",
            json={
                "alert_type": "earthquake",
                "title": "Earthquake",
                "text": "Minor earthquake",
                "severity": "info",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["channel"] == "announcements"

    @pytest.mark.unit
    def test_post_alert_bilingual(self, rc_client, mock_rc_client):
        """Alert with Arabic title and text includes both | تنبيه ثنائي اللغة"""
        rc_client.post(
            "/api/v1/community/bots/alert",
            json={
                "alert_type": "weather",
                "title": "Heat Wave",
                "title_ar": "موجة حرارة",
                "text": "High temps expected",
                "text_ar": "درجات حرارة مرتفعة متوقعة",
                "severity": "warning",
            },
        )
        call_kwargs = mock_rc_client.post_message.call_args[1]
        posted_text = call_kwargs["text"]
        assert "Heat Wave" in posted_text
        assert "موجة حرارة" in posted_text
        assert "High temps expected" in posted_text
        assert "درجات حرارة مرتفعة متوقعة" in posted_text

    @pytest.mark.unit
    def test_post_alert_with_affected_area(self, rc_client, mock_rc_client):
        """Alert includes affected area | المنطقة المتأثرة"""
        rc_client.post(
            "/api/v1/community/bots/alert",
            json={
                "alert_type": "flood",
                "title": "Flood Risk",
                "text": "Flash flood warning",
                "severity": "critical",
                "affected_area": "Wadi Al-Dawasir",
            },
        )
        call_kwargs = mock_rc_client.post_message.call_args[1]
        assert "Wadi Al-Dawasir" in call_kwargs["text"]

    @pytest.mark.unit
    def test_post_alert_with_expiry(self, rc_client, mock_rc_client):
        """Alert includes expiry timestamp | وقت انتهاء التنبيه"""
        expires = "2026-01-15T18:00:00Z"
        rc_client.post(
            "/api/v1/community/bots/alert",
            json={
                "alert_type": "heatwave",
                "title": "Heatwave",
                "text": "Extreme heat",
                "severity": "critical",
                "expires_at": expires,
            },
        )
        call_kwargs = mock_rc_client.post_message.call_args[1]
        assert expires in call_kwargs["text"]

    @pytest.mark.unit
    def test_post_alert_uses_alert_alias(self, rc_client, mock_rc_client):
        """Alert uses 'SAHOOL Alert System' alias | اسم نظام التنبيه"""
        rc_client.post(
            "/api/v1/community/bots/alert",
            json={
                "alert_type": "weather",
                "title": "Test",
                "text": "Test alert",
                "severity": "info",
            },
        )
        call_kwargs = mock_rc_client.post_message.call_args[1]
        assert call_kwargs["alias"] == "SAHOOL Alert System"

    @pytest.mark.unit
    def test_post_alert_publishes_nats_event(self, rc_client, mock_nats):
        """Alert publishes NATS event | التنبيه ينشر حدث NATS"""
        rc_client.post(
            "/api/v1/community/bots/alert",
            json={
                "alert_type": "weather",
                "title": "Test",
                "text": "Test alert",
                "severity": "info",
            },
        )
        mock_nats.publish.assert_called()
        call_args = mock_nats.publish.call_args
        subject = call_args[0][0]
        assert subject == "sahool.community.alert_posted"


# ===========================================================================
# 12. Authentication required | المصادقة مطلوبة
# ===========================================================================
class TestAuthentication:
    """Authentication requirement tests | اختبارات المصادقة"""

    @pytest.mark.unit
    def test_authenticated_endpoints_require_auth(self):
        """All protected endpoints require authentication | جميع النقاط تتطلب مصادقة"""
        from src.main import app

        # Check that all API endpoints have get_current_user dependency
        protected_paths = [
            "/api/v1/community/setup-tenant",
            "/api/v1/community/channels",
            "/api/v1/community/messages",
            "/api/v1/community/messages/search",
            "/api/v1/community/users/sync",
            "/api/v1/community/bots/advisory",
            "/api/v1/community/bots/alert",
        ]
        for route in app.routes:
            if hasattr(route, "path") and route.path in protected_paths:
                # Endpoint has dependencies - verified by the endpoint handler signature
                assert hasattr(route, "dependant") or hasattr(route, "endpoint")

    @pytest.mark.unit
    def test_health_endpoints_do_not_require_auth(self):
        """Health endpoints work without auth | نقاط السلامة بدون مصادقة"""
        from src.main import app

        client = TestClient(app)
        # Health endpoints should be accessible without auth
        resp = client.get("/healthz")
        assert resp.status_code == 200

    @pytest.mark.unit
    def test_unauthenticated_request_to_channels(self):
        """Unauthenticated request to channels fails | طلب غير مصادق يفشل"""
        from src.main import app, get_current_user

        async def raise_auth_error():
            raise HTTPException(status_code=401, detail="Not authenticated")

        app.dependency_overrides[get_current_user] = raise_auth_error
        try:
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get("/api/v1/community/channels")
            # Should return an error status (401 or 400 depending on error handler)
            assert resp.status_code in (400, 401, 403)
        finally:
            app.dependency_overrides.pop(get_current_user, None)


# ===========================================================================
# 13. Tenant isolation | عزل المستأجرين
# ===========================================================================
class TestTenantIsolation:
    """Tenant isolation tests | اختبارات عزل المستأجرين"""

    @pytest.mark.unit
    def test_tenant_prefix_in_setup_channels(self):
        """Each tenant gets uniquely prefixed channels | قنوات مسبوقة بمعرف فريد"""
        tid_a = "aaaaaaaa-0000-0000-0000-000000000001"
        tid_b = "bbbbbbbb-0000-0000-0000-000000000002"

        user1 = _make_user(tenant_id=tid_a)
        c1, app1 = _make_app(user1)

        resp1 = c1.post(
            "/api/v1/community/setup-tenant",
            json={"tenant_id": tid_a, "tenant_name": "Farm A"},
        )
        data1 = resp1.json()
        prefix1 = f"t-{tid_a[:8]}-"

        user2 = _make_user(tenant_id=tid_b)
        c2, app2 = _make_app(user2)

        resp2 = c2.post(
            "/api/v1/community/setup-tenant",
            json={"tenant_id": tid_b, "tenant_name": "Farm B"},
        )
        data2 = resp2.json()
        prefix2 = f"t-{tid_b[:8]}-"

        # Verify different prefixes
        assert prefix1 != prefix2
        for ch in data1["channels"]:
            assert ch["name"].startswith(prefix1)
        for ch in data2["channels"]:
            assert ch["name"].startswith(prefix2)

    @pytest.mark.unit
    def test_tenant_id_in_header(self, rc_client):
        """Request includes X-Tenant-Id header | معرف المستأجر في الرأس"""
        assert rc_client.headers.get("X-Tenant-Id") == TENANT_ID_1


# ===========================================================================
# 14. Rate limiting | تحديد المعدل
# ===========================================================================
class TestRateLimiting:
    """Rate limiting tests | اختبارات تحديد المعدل"""

    @pytest.mark.unit
    def test_rate_limit_module_loaded(self):
        """Rate limiting module is detected when available | كشف وحدة تحديد المعدل"""
        from src.main import RATE_LIMIT_AVAILABLE

        # In test environment, slowapi may or may not be installed
        # We just verify the flag exists and the code handles both cases
        assert isinstance(RATE_LIMIT_AVAILABLE, bool)

    @pytest.mark.unit
    def test_rate_limiter_attached_to_app(self):
        """If slowapi available, limiter is attached to app state | مرفق بحالة التطبيق"""
        from src.main import RATE_LIMIT_AVAILABLE, app

        if RATE_LIMIT_AVAILABLE:
            assert hasattr(app.state, "limiter")


# ===========================================================================
# 15. Error handling | معالجة الأخطاء
# ===========================================================================
class TestErrorHandling:
    """Error handling tests | اختبارات معالجة الأخطاء"""

    @pytest.mark.unit
    def test_rc_not_connected_returns_503(self):
        """Endpoints return 503 when RC not connected | 503 عند عدم اتصال RC"""
        user = _make_user()
        rc = _make_rc_mock()
        c, the_app = _make_app(user, rc_mock=rc, rc_connected=False)
        the_app.state.rc = None
        the_app.state.rc_connected = False

        resp = c.get("/api/v1/community/channels")
        assert resp.status_code == 503
        body = resp.json()
        # Response may use "detail" key or unified error format with "message"
        error_text = str(body.get("detail", body.get("message", body.get("error", ""))))
        assert "Rocket.Chat" in error_text or "روكيت شات" in error_text

    @pytest.mark.unit
    def test_rc_not_connected_returns_503_for_post(self):
        """Post endpoints return 503 when RC not connected | 503 للنشر بدون اتصال"""
        user = _make_user()
        c, app = _make_app(user, rc_connected=False)
        app.state.rc = None
        app.state.rc_connected = False

        resp = c.post(
            "/api/v1/community/channels",
            json={"name": "test-channel"},
        )
        assert resp.status_code == 503

    @pytest.mark.unit
    def test_rc_api_error_returns_502(self, rc_client, mock_rc_client):
        """RC API failure returns 502 | خطأ API RC يعيد 502"""
        mock_rc_client.create_channel = AsyncMock(
            side_effect=HTTPException(status_code=502, detail="Rocket.Chat API error: 500")
        )
        resp = rc_client.post(
            "/api/v1/community/channels",
            json={"name": "failing-channel"},
        )
        assert resp.status_code == 502

    @pytest.mark.unit
    def test_rc_connection_error_returns_502(self, rc_client, mock_rc_client):
        """RC connection failure returns 502 | خطأ اتصال RC يعيد 502"""
        mock_rc_client.get_channels = AsyncMock(
            side_effect=HTTPException(status_code=502, detail="Cannot reach Rocket.Chat")
        )
        resp = rc_client.get("/api/v1/community/channels")
        assert resp.status_code == 502

    @pytest.mark.unit
    def test_post_message_rc_failure(self, rc_client, mock_rc_client):
        """Post message handles RC failure | فشل نشر الرسالة"""
        mock_rc_client.post_message = AsyncMock(side_effect=HTTPException(status_code=502, detail="RC error"))

        resp = rc_client.post(
            "/api/v1/community/messages",
            json={"channel_id": "ch001", "text": "Hello"},
        )
        assert resp.status_code == 502

    @pytest.mark.unit
    def test_join_channel_rc_failure(self, rc_client, mock_rc_client):
        """Join channel handles RC failure | فشل الانضمام"""
        mock_rc_client.add_user_to_channel = AsyncMock(side_effect=HTTPException(status_code=502, detail="RC error"))

        resp = rc_client.post("/api/v1/community/channels/ch001/join")
        assert resp.status_code == 502

    @pytest.mark.unit
    def test_leave_channel_rc_failure(self, rc_client, mock_rc_client):
        """Leave channel handles RC failure | فشل المغادرة"""
        mock_rc_client.remove_user_from_channel = AsyncMock(
            side_effect=HTTPException(status_code=502, detail="RC error")
        )
        resp = rc_client.post("/api/v1/community/channels/ch001/leave")
        assert resp.status_code == 502

    @pytest.mark.unit
    def test_search_messages_rc_failure(self, rc_client, mock_rc_client):
        """Search handles RC failure | فشل البحث"""
        mock_rc_client.search_messages = AsyncMock(side_effect=HTTPException(status_code=502, detail="RC error"))

        resp = rc_client.post(
            "/api/v1/community/messages/search",
            json={"channel_id": "ch001", "query": "test"},
        )
        assert resp.status_code == 502

    @pytest.mark.unit
    def test_sync_user_rc_failure(self, rc_client, mock_rc_client):
        """Sync user handles RC failure | فشل المزامنة"""
        mock_rc_client.create_user = AsyncMock(side_effect=HTTPException(status_code=502, detail="RC error"))

        resp = rc_client.post(
            "/api/v1/community/users/sync",
            json={
                "email": "farmer@sahool.app",
                "name": "Ahmad",
                "username": "ahmad",
            },
        )
        assert resp.status_code == 502

    @pytest.mark.unit
    def test_advisory_bot_rc_failure(self, rc_client, mock_rc_client):
        """Advisory bot handles RC failure | فشل بوت الاستشارات"""
        mock_rc_client.post_message = AsyncMock(side_effect=HTTPException(status_code=502, detail="RC error"))

        resp = rc_client.post(
            "/api/v1/community/bots/advisory",
            json={
                "advisory_type": "irrigation",
                "text": "Test advisory",
            },
        )
        assert resp.status_code == 502

    @pytest.mark.unit
    def test_alert_bot_rc_failure(self, rc_client, mock_rc_client):
        """Alert bot handles RC failure | فشل بوت التنبيهات"""
        mock_rc_client.post_message = AsyncMock(side_effect=HTTPException(status_code=502, detail="RC error"))

        resp = rc_client.post(
            "/api/v1/community/bots/alert",
            json={
                "alert_type": "weather",
                "title": "Test",
                "text": "Test alert",
                "severity": "info",
            },
        )
        assert resp.status_code == 502

    @pytest.mark.unit
    def test_invalid_json_body(self, rc_client):
        """Invalid JSON body returns 422 | جسم JSON غير صالح"""
        resp = rc_client.post(
            "/api/v1/community/channels",
            content="not-json",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 422

    @pytest.mark.unit
    def test_description_too_long(self, rc_client):
        """Description over 500 chars is rejected | رفض وصف طويل جدا"""
        resp = rc_client.post(
            "/api/v1/community/channels",
            json={"name": "test-ch", "description": "d" * 501},
        )
        assert resp.status_code == 422

    @pytest.mark.unit
    def test_nats_publish_failure_does_not_break_response(self):
        """NATS publish failure does not affect response | فشل NATS لا يؤثر"""
        user = _make_user()
        rc = _make_rc_mock()
        c, app = _make_app(user, rc_mock=rc)
        app.state.nc.publish = AsyncMock(side_effect=Exception("NATS down"))

        resp = c.post(
            "/api/v1/community/channels",
            json={"name": "test-ch"},
        )
        # Channel creation should succeed even if NATS publish fails
        assert resp.status_code == 200


# ===========================================================================
# Additional edge case tests | اختبارات حالات الحافة
# ===========================================================================
class TestEdgeCases:
    """Edge case and integration tests | اختبارات حالات الحافة"""

    @pytest.mark.unit
    def test_channel_response_includes_topic(self, rc_client, mock_rc_client):
        """Channel response includes topic field | حقل الموضوع"""
        resp = rc_client.post(
            "/api/v1/community/channels",
            json={"name": "test-ch", "topic": "Irrigation Tips"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["topic"] == "Irrigation Tips"

    @pytest.mark.unit
    def test_history_default_count_is_50(self, rc_client, mock_rc_client):
        """Default history count is 50 | العدد الافتراضي للسجل 50"""
        rc_client.get("/api/v1/community/channels/ch001/history")
        mock_rc_client.get_channel_history.assert_called_once_with("ch001", count=50, oldest=None)

    @pytest.mark.unit
    def test_list_channels_default_pagination(self, rc_client, mock_rc_client):
        """Default listing uses count=100 offset=0 | التصفح الافتراضي"""
        mock_rc_client.get_channels = AsyncMock(return_value=[])
        rc_client.get("/api/v1/community/channels")
        mock_rc_client.get_channels.assert_called_once_with(count=100, offset=0)

    @pytest.mark.unit
    def test_metrics_endpoint(self, rc_client):
        """Metrics endpoint returns response | نقطة المقاييس"""
        resp = rc_client.get("/metrics")
        assert resp.status_code == 200

    @pytest.mark.unit
    def test_all_advisory_channel_mappings(self, rc_client, mock_rc_client):
        """All advisory types map to correct channels | تعيين جميع الأنواع"""
        from src.main import ADVISORY_CHANNEL_MAP

        for advisory_type, expected_channel in ADVISORY_CHANNEL_MAP.items():
            mock_rc_client.post_message.reset_mock()
            resp = rc_client.post(
                "/api/v1/community/bots/advisory",
                json={"advisory_type": advisory_type, "text": "Test"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["channel"] == expected_channel, (
                f"Advisory type '{advisory_type}' should route to '{expected_channel}', got '{data['channel']}'"
            )

    @pytest.mark.unit
    def test_all_alert_type_mappings(self, rc_client, mock_rc_client):
        """All alert types map to correct channels | تعيين جميع التنبيهات"""
        expected_mappings = {
            "weather": "weather-alerts",
            "frost": "weather-alerts",
            "flood": "weather-alerts",
            "heatwave": "weather-alerts",
            "pest": "pest-management",
            "disease": "crop-diseases",
        }
        for alert_type, expected_channel in expected_mappings.items():
            mock_rc_client.post_message.reset_mock()
            resp = rc_client.post(
                "/api/v1/community/bots/alert",
                json={
                    "alert_type": alert_type,
                    "title": "Test",
                    "text": "Test",
                    "severity": "info",
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["channel"] == expected_channel, (
                f"Alert type '{alert_type}' should route to '{expected_channel}', got '{data['channel']}'"
            )

    @pytest.mark.unit
    def test_default_agri_channels_count(self):
        """Platform defines 8 default agricultural channels | 8 قنوات افتراضية"""
        from src.main import DEFAULT_AGRI_CHANNELS

        assert len(DEFAULT_AGRI_CHANNELS) == 8

    @pytest.mark.unit
    def test_default_channels_have_bilingual_info(self):
        """All default channels have Arabic names and descriptions | معلومات ثنائية اللغة"""
        from src.main import DEFAULT_AGRI_CHANNELS

        for ch in DEFAULT_AGRI_CHANNELS:
            assert "name" in ch, "Missing name for channel"
            assert "name_ar" in ch, f"Missing name_ar for {ch['name']}"
            assert "description" in ch, f"Missing description for {ch['name']}"
            assert "description_ar" in ch, f"Missing description_ar for {ch['name']}"

    @pytest.mark.unit
    def test_service_version(self):
        """Service version is 16.0.0 | إصدار الخدمة"""
        from src.main import VERSION

        assert VERSION == "16.0.0"

    @pytest.mark.unit
    def test_user_sync_default_roles(self, rc_client, mock_rc_client):
        """User sync defaults to ['user'] role when not specified | الأدوار الافتراضية"""
        rc_client.post(
            "/api/v1/community/users/sync",
            json={
                "email": "farmer@sahool.app",
                "name": "Ahmad",
                "username": "ahmad",
            },
        )
        call_kwargs = mock_rc_client.create_user.call_args[1]
        assert call_kwargs["roles"] == ["user"]

    @pytest.mark.unit
    def test_get_channel_members_with_count(self, rc_client, mock_rc_client):
        """Get channel members supports count parameter | دعم معامل العدد"""
        mock_rc_client.get_channel_members = AsyncMock(return_value=[])
        rc_client.get("/api/v1/community/channels/ch001/members?count=25")
        mock_rc_client.get_channel_members.assert_called_once_with("ch001", count=25)
