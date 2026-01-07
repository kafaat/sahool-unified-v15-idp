"""
SAHOOL Notification Service - Service Layer Tests
Comprehensive unit tests for notification business logic
Coverage: Service functions, repository operations, notification delivery, scheduling
"""

import pytest
from datetime import datetime, timedelta, time
from unittest.mock import AsyncMock, MagicMock, patch, call
from uuid import uuid4


@pytest.fixture
def mock_notification():
    """Create a mock notification object"""
    notif = MagicMock()
    notif.id = uuid4()
    notif.user_id = 'user-123'
    notif.tenant_id = 'tenant-1'
    notif.title = 'Test Notification'
    notif.title_ar = 'إشعار تجريبي'
    notif.body = 'Test body'
    notif.body_ar = 'نص تجريبي'
    notif.type = 'weather_alert'
    notif.priority = 'high'
    notif.channel = 'push'
    notif.status = 'pending'
    notif.created_at = datetime.utcnow()
    notif.expires_at = datetime.utcnow() + timedelta(hours=24)
    notif.data = {}
    notif.is_read = False
    notif.is_expired = False
    notif.action_url = None
    return notif


@pytest.fixture
def mock_farmer_profile():
    """Create a mock farmer profile"""
    return {
        'farmer_id': 'farmer-123',
        'name': 'Ahmed Ali',
        'name_ar': 'أحمد علي',
        'governorate': 'sanaa',
        'crops': ['tomato', 'coffee'],
        'phone': '+967771234567',
        'email': 'ahmed@example.com',
        'fcm_token': 'mock-fcm-token',
        'language': 'ar'
    }


class TestNotificationRepository:
    """Test NotificationRepository methods"""

    @pytest.mark.asyncio
    async def test_create_notification(self, mock_notification):
        """Test creating a notification in repository"""
        with patch('src.repository.Notification.create', new=AsyncMock(return_value=mock_notification)):
            from src.repository import NotificationRepository

            result = await NotificationRepository.create(
                user_id='user-123',
                title='Test',
                body='Test body',
                type='weather_alert',
                priority='high'
            )

            assert result.id == mock_notification.id
            assert result.user_id == 'user-123'
            assert result.type == 'weather_alert'

    @pytest.mark.asyncio
    async def test_get_by_id(self, mock_notification):
        """Test getting notification by ID"""
        with patch('src.repository.Notification.filter') as mock_filter:
            mock_filter.return_value.first = AsyncMock(return_value=mock_notification)
            from src.repository import NotificationRepository

            result = await NotificationRepository.get_by_id(mock_notification.id)
            assert result.id == mock_notification.id

    @pytest.mark.asyncio
    async def test_get_by_user(self, mock_notification):
        """Test getting notifications by user"""
        with patch('src.repository.Notification.filter') as mock_filter:
            mock_query = MagicMock()
            mock_query.filter = MagicMock(return_value=mock_query)
            mock_query.order_by = MagicMock(return_value=mock_query)
            mock_query.offset = MagicMock(return_value=mock_query)
            mock_query.limit = MagicMock(return_value=mock_query)
            mock_query.all = AsyncMock(return_value=[mock_notification])
            mock_filter.return_value = mock_query

            from src.repository import NotificationRepository

            result = await NotificationRepository.get_by_user('user-123', limit=10)
            assert len(result) == 1
            assert result[0].user_id == 'user-123'

    @pytest.mark.asyncio
    async def test_get_unread_count(self):
        """Test getting unread notification count"""
        with patch('src.repository.Notification.filter') as mock_filter:
            mock_query = MagicMock()
            mock_query.filter = MagicMock(return_value=mock_query)
            mock_query.count = AsyncMock(return_value=5)
            mock_filter.return_value = mock_query

            from src.repository import NotificationRepository

            count = await NotificationRepository.get_unread_count('user-123')
            assert count == 5

    @pytest.mark.asyncio
    async def test_mark_as_read(self, mock_notification):
        """Test marking notification as read"""
        with patch('src.repository.Notification.filter') as mock_filter:
            mock_query = MagicMock()
            mock_query.update = AsyncMock(return_value=1)
            mock_filter.return_value = mock_query

            from src.repository import NotificationRepository

            result = await NotificationRepository.mark_as_read(mock_notification.id)
            assert result is True

    @pytest.mark.asyncio
    async def test_mark_multiple_as_read(self):
        """Test marking multiple notifications as read"""
        notification_ids = [uuid4(), uuid4(), uuid4()]

        with patch('src.repository.Notification.filter') as mock_filter:
            mock_query = MagicMock()
            mock_query.update = AsyncMock(return_value=3)
            mock_filter.return_value = mock_query

            from src.repository import NotificationRepository

            count = await NotificationRepository.mark_multiple_as_read(notification_ids)
            assert count == 3

    @pytest.mark.asyncio
    async def test_update_status(self, mock_notification):
        """Test updating notification status"""
        with patch('src.repository.Notification.filter') as mock_filter:
            mock_query = MagicMock()
            mock_query.update = AsyncMock(return_value=1)
            mock_filter.return_value = mock_query

            from src.repository import NotificationRepository

            result = await NotificationRepository.update_status(
                mock_notification.id,
                status='sent',
                sent_at=datetime.utcnow()
            )
            assert result is True

    @pytest.mark.asyncio
    async def test_delete_notification(self, mock_notification):
        """Test deleting a notification"""
        with patch('src.repository.Notification.filter') as mock_filter:
            mock_query = MagicMock()
            mock_query.delete = AsyncMock(return_value=1)
            mock_filter.return_value = mock_query

            from src.repository import NotificationRepository

            result = await NotificationRepository.delete(mock_notification.id)
            assert result is True

    @pytest.mark.asyncio
    async def test_get_pending_notifications(self, mock_notification):
        """Test getting pending notifications"""
        with patch('src.repository.Notification.filter') as mock_filter:
            mock_query = MagicMock()
            mock_query.filter = MagicMock(return_value=mock_query)
            mock_query.order_by = MagicMock(return_value=mock_query)
            mock_query.limit = MagicMock(return_value=mock_query)
            mock_query.all = AsyncMock(return_value=[mock_notification])
            mock_filter.return_value = mock_query

            from src.repository import NotificationRepository

            result = await NotificationRepository.get_pending_notifications(limit=100)
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_create_bulk_notifications(self, mock_notification):
        """Test creating bulk notifications"""
        notifications_data = [
            {'user_id': 'user-1', 'title': 'Test 1', 'body': 'Body 1', 'type': 'alert'},
            {'user_id': 'user-2', 'title': 'Test 2', 'body': 'Body 2', 'type': 'alert'}
        ]

        with patch('src.repository.Notification.bulk_create', new=AsyncMock()):
            from src.repository import NotificationRepository

            result = await NotificationRepository.create_bulk(notifications_data)
            assert len(result) == 2


class TestNotificationChannelRepository:
    """Test NotificationChannelRepository methods"""

    @pytest.mark.asyncio
    async def test_create_channel(self):
        """Test creating notification channel"""
        mock_channel = MagicMock()
        mock_channel.id = uuid4()
        mock_channel.user_id = 'user-123'
        mock_channel.channel = 'email'
        mock_channel.address = 'test@example.com'
        mock_channel.verified = False
        mock_channel.enabled = True

        with patch('src.repository.NotificationChannel.filter') as mock_filter:
            mock_filter.return_value.first = AsyncMock(return_value=None)
            with patch('src.repository.NotificationChannel.create', new=AsyncMock(return_value=mock_channel)):
                from src.repository import NotificationChannelRepository

                result = await NotificationChannelRepository.create(
                    user_id='user-123',
                    channel='email',
                    address='test@example.com'
                )

                assert result.user_id == 'user-123'
                assert result.channel == 'email'

    @pytest.mark.asyncio
    async def test_get_user_channels(self):
        """Test getting user channels"""
        mock_channel = MagicMock()
        mock_channel.user_id = 'user-123'

        with patch('src.repository.NotificationChannel.filter') as mock_filter:
            mock_query = MagicMock()
            mock_query.filter = MagicMock(return_value=mock_query)
            mock_query.all = AsyncMock(return_value=[mock_channel])
            mock_filter.return_value = mock_query

            from src.repository import NotificationChannelRepository

            result = await NotificationChannelRepository.get_user_channels('user-123')
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_verify_channel(self):
        """Test verifying a channel"""
        mock_channel = MagicMock()
        mock_channel.verification_code = '123456'
        mock_channel.save = AsyncMock()

        with patch('src.repository.NotificationChannel.filter') as mock_filter:
            mock_filter.return_value.first = AsyncMock(return_value=mock_channel)

            from src.repository import NotificationChannelRepository

            result = await NotificationChannelRepository.verify_channel(
                uuid4(),
                verification_code='123456'
            )
            assert result is True
            assert mock_channel.verified is True

    @pytest.mark.asyncio
    async def test_delete_channel(self):
        """Test deleting a channel"""
        with patch('src.repository.NotificationChannel.filter') as mock_filter:
            mock_query = MagicMock()
            mock_query.delete = AsyncMock(return_value=1)
            mock_filter.return_value = mock_query

            from src.repository import NotificationChannelRepository

            result = await NotificationChannelRepository.delete_channel(uuid4())
            assert result is True


class TestNotificationPreferenceRepository:
    """Test NotificationPreferenceRepository methods"""

    @pytest.mark.asyncio
    async def test_create_or_update_preference(self):
        """Test creating or updating preference"""
        mock_pref = MagicMock()
        mock_pref.user_id = 'user-123'
        mock_pref.event_type = 'weather_alert'
        mock_pref.enabled = True
        mock_pref.channels = ['push', 'email']
        mock_pref.save = AsyncMock()

        with patch('src.repository.NotificationPreference.get_or_create', new=AsyncMock(return_value=(mock_pref, True))):
            from src.repository import NotificationPreferenceRepository

            result = await NotificationPreferenceRepository.create_or_update(
                user_id='user-123',
                event_type='weather_alert',
                channels=['push', 'email'],
                enabled=True
            )

            assert result.user_id == 'user-123'
            assert result.event_type == 'weather_alert'

    @pytest.mark.asyncio
    async def test_get_event_preference(self):
        """Test getting event preference"""
        mock_pref = MagicMock()
        mock_pref.user_id = 'user-123'
        mock_pref.event_type = 'weather_alert'

        with patch('src.repository.NotificationPreference.filter') as mock_filter:
            mock_query = MagicMock()
            mock_query.filter = MagicMock(return_value=mock_query)
            mock_query.first = AsyncMock(return_value=mock_pref)
            mock_filter.return_value = mock_query

            from src.repository import NotificationPreferenceRepository

            result = await NotificationPreferenceRepository.get_event_preference(
                'user-123',
                'weather_alert'
            )
            assert result.user_id == 'user-123'

    @pytest.mark.asyncio
    async def test_is_event_enabled(self):
        """Test checking if event is enabled"""
        mock_pref = MagicMock()
        mock_pref.enabled = True

        with patch('src.repository.NotificationPreference.filter') as mock_filter:
            mock_query = MagicMock()
            mock_query.filter = MagicMock(return_value=mock_query)
            mock_query.first = AsyncMock(return_value=mock_pref)
            mock_filter.return_value = mock_query

            from src.repository import NotificationPreferenceRepository

            result = await NotificationPreferenceRepository.is_event_enabled(
                'user-123',
                'weather_alert'
            )
            assert result is True

    @pytest.mark.asyncio
    async def test_get_preferred_channels(self):
        """Test getting preferred channels"""
        mock_pref = MagicMock()
        mock_pref.enabled = True
        mock_pref.channels = ['push', 'email']

        with patch('src.repository.NotificationPreference.filter') as mock_filter:
            mock_query = MagicMock()
            mock_query.filter = MagicMock(return_value=mock_query)
            mock_query.first = AsyncMock(return_value=mock_pref)
            mock_filter.return_value = mock_query

            from src.repository import NotificationPreferenceRepository

            result = await NotificationPreferenceRepository.get_preferred_channels(
                'user-123',
                'weather_alert'
            )
            assert result == ['push', 'email']


class TestNotificationScheduler:
    """Test NotificationScheduler functionality"""

    @pytest.mark.asyncio
    async def test_schedule_notification(self):
        """Test scheduling a notification"""
        from src.notification_scheduler import NotificationScheduler, ScheduleFrequency
        from src.notification_types import NotificationPayload, NotificationPriority

        scheduler = NotificationScheduler()

        payload = NotificationPayload(
            notification_type='weather_alert',
            title='Test',
            body='Test body',
            title_ar='اختبار',
            body_ar='نص اختبار',
            priority=NotificationPriority.HIGH
        )

        scheduled_time = datetime.utcnow() + timedelta(hours=1)

        result = scheduler.schedule_notification(
            notification_id='notif-1',
            payload=payload,
            recipient_token='token-123',
            scheduled_time=scheduled_time,
            frequency=ScheduleFrequency.ONCE
        )

        assert result is True
        assert len(scheduler._queue) == 1

    @pytest.mark.asyncio
    async def test_schedule_batch(self):
        """Test scheduling batch of notifications"""
        from src.notification_scheduler import NotificationScheduler, ScheduleFrequency
        from src.notification_types import NotificationPayload, NotificationPriority

        scheduler = NotificationScheduler()

        payload = NotificationPayload(
            notification_type='weather_alert',
            title='Test',
            body='Test body',
            title_ar='اختبار',
            body_ar='نص اختبار',
            priority=NotificationPriority.HIGH
        )

        tokens = ['token-1', 'token-2', 'token-3']
        scheduled_time = datetime.utcnow() + timedelta(hours=1)

        count = scheduler.schedule_batch(
            payload=payload,
            recipient_tokens=tokens,
            scheduled_time=scheduled_time,
            frequency=ScheduleFrequency.ONCE
        )

        assert count == 3
        assert len(scheduler._queue) == 3

    def test_is_quiet_hours(self):
        """Test quiet hours detection"""
        from src.notification_scheduler import NotificationScheduler

        scheduler = NotificationScheduler(
            quiet_hours_start=time(22, 0),
            quiet_hours_end=time(6, 0)
        )

        # Test during quiet hours
        quiet_time = datetime.utcnow().replace(hour=23, minute=30)
        assert scheduler.is_quiet_hours(quiet_time) is True

        # Test outside quiet hours
        active_time = datetime.utcnow().replace(hour=10, minute=0)
        assert scheduler.is_quiet_hours(active_time) is False

    def test_can_send_to_user_rate_limiting(self):
        """Test rate limiting for user"""
        from src.notification_scheduler import NotificationScheduler

        scheduler = NotificationScheduler(rate_limit_per_minute=5)

        token = 'test-token'

        # Should allow first 5
        for _ in range(5):
            assert scheduler.can_send_to_user(token) is True
            scheduler.record_send(token)

        # Should block 6th
        assert scheduler.can_send_to_user(token) is False

    def test_cancel_notification(self):
        """Test cancelling scheduled notification"""
        from src.notification_scheduler import NotificationScheduler, ScheduleFrequency
        from src.notification_types import NotificationPayload, NotificationPriority

        scheduler = NotificationScheduler()

        payload = NotificationPayload(
            notification_type='weather_alert',
            title='Test',
            body='Test',
            title_ar='اختبار',
            body_ar='اختبار',
            priority=NotificationPriority.LOW
        )

        notification_id = 'notif-cancel'
        scheduler.schedule_notification(
            notification_id=notification_id,
            payload=payload,
            recipient_token='token',
            scheduled_time=datetime.utcnow() + timedelta(hours=1)
        )

        result = scheduler.cancel_notification(notification_id)
        assert result is True

    def test_get_stats(self):
        """Test getting scheduler statistics"""
        from src.notification_scheduler import NotificationScheduler

        scheduler = NotificationScheduler()
        stats = scheduler.get_stats()

        assert 'total_scheduled' in stats
        assert 'pending' in stats
        assert 'sent' in stats
        assert 'failed' in stats
        assert 'is_running' in stats


class TestNotificationDelivery:
    """Test notification delivery functions"""

    @pytest.mark.asyncio
    async def test_send_sms_notification(self, mock_notification, mock_farmer_profile):
        """Test sending SMS notification"""
        with patch('src.main.FARMER_PROFILES', {'farmer-123': mock_farmer_profile}):
            with patch('src.main.get_sms_client') as mock_sms_client:
                mock_client = MagicMock()
                mock_client._initialized = True
                mock_client.send_sms = AsyncMock(return_value='msg-123')
                mock_sms_client.return_value = mock_client

                with patch('src.main.NotificationRepository.update_status', new=AsyncMock()):
                    with patch('src.main.NotificationLogRepository.create_log', new=AsyncMock()):
                        from src.main import send_sms_notification

                        await send_sms_notification(mock_notification, 'farmer-123')
                        assert mock_client.send_sms.called

    @pytest.mark.asyncio
    async def test_send_email_notification(self, mock_notification, mock_farmer_profile):
        """Test sending email notification"""
        with patch('src.main.FARMER_PROFILES', {'farmer-123': mock_farmer_profile}):
            with patch('src.main.get_email_client') as mock_email_client:
                mock_client = MagicMock()
                mock_client._initialized = True
                mock_client.send_email = AsyncMock(return_value='email-123')
                mock_email_client.return_value = mock_client

                with patch('src.main.NotificationRepository.update_status', new=AsyncMock()):
                    with patch('src.main.NotificationLogRepository.create_log', new=AsyncMock()):
                        from src.main import send_email_notification

                        await send_email_notification(mock_notification, 'farmer-123')
                        assert mock_client.send_email.called

    @pytest.mark.asyncio
    async def test_send_push_notification(self, mock_notification, mock_farmer_profile):
        """Test sending push notification"""
        with patch('src.main.FARMER_PROFILES', {'farmer-123': mock_farmer_profile}):
            with patch('src.main.get_firebase_client') as mock_firebase_client:
                mock_client = MagicMock()
                mock_client._initialized = True
                mock_client.send_notification = MagicMock(return_value='push-123')
                mock_firebase_client.return_value = mock_client

                with patch('src.main.NotificationRepository.update_status', new=AsyncMock()):
                    with patch('src.main.NotificationLogRepository.create_log', new=AsyncMock()):
                        from src.main import send_push_notification

                        await send_push_notification(mock_notification, 'farmer-123')
                        assert mock_client.send_notification.called


class TestNotificationHelpers:
    """Test helper functions"""

    def test_determine_recipients_by_criteria(self):
        """Test recipient determination"""
        from src.main import determine_recipients_by_criteria, FARMER_PROFILES

        # Mock farmer profiles
        mock_profiles = {
            'farmer-1': MagicMock(governorate='sanaa', crops=['tomato', 'wheat']),
            'farmer-2': MagicMock(governorate='taiz', crops=['coffee']),
            'farmer-3': MagicMock(governorate='sanaa', crops=['tomato'])
        }

        with patch.dict('src.main.FARMER_PROFILES', mock_profiles):
            # Test by governorate
            recipients = determine_recipients_by_criteria(
                target_governorates=['sanaa']
            )
            assert 'farmer-1' in recipients
            assert 'farmer-3' in recipients
            assert 'farmer-2' not in recipients

    def test_get_weather_alert_message(self):
        """Test weather alert message generation"""
        from src.main import get_weather_alert_message, Governorate

        title, title_ar, body, body_ar = get_weather_alert_message(
            'frost',
            Governorate.SANAA
        )

        assert 'Frost' in title
        assert 'صقيع' in title_ar
        assert len(body) > 0
        assert len(body_ar) > 0


class TestPreferencesService:
    """Test PreferencesService functionality"""

    @pytest.mark.asyncio
    async def test_check_if_should_send(self):
        """Test checking if notification should be sent"""
        mock_pref = MagicMock()
        mock_pref.enabled = True
        mock_pref.channels = ['push', 'email']

        with patch('src.preferences_service.NotificationPreferenceRepository.get_event_preference', new=AsyncMock(return_value=mock_pref)):
            from src.preferences_service import PreferencesService

            should_send, channels = await PreferencesService.check_if_should_send(
                user_id='user-123',
                event_type='weather_alert'
            )

            assert should_send is True
            assert 'push' in channels
            assert 'email' in channels

    @pytest.mark.asyncio
    async def test_check_if_should_send_disabled(self):
        """Test when event is disabled"""
        mock_pref = MagicMock()
        mock_pref.enabled = False

        with patch('src.preferences_service.NotificationPreferenceRepository.get_event_preference', new=AsyncMock(return_value=mock_pref)):
            from src.preferences_service import PreferencesService

            should_send, channels = await PreferencesService.check_if_should_send(
                user_id='user-123',
                event_type='weather_alert'
            )

            assert should_send is False
            assert len(channels) == 0
