"""Tests for legacy_users service."""
import time
from typing import Optional
from unittest import mock, TestCase
from datetime import datetime
from pytz import timezone

from .. import exceptions, sessions, util, models, cookies

from .util import temporary_db

EASTERN = timezone('US/Eastern')


class TestCreateSession(TestCase):
    """Tests for public function :func:`.`."""

    @mock.patch(f'{sessions.__name__}.util.get_session_duration')
    def test_create(self, mock_get_session_duration):
        """Accept a :class:`.User` and returns a :class:`.Session`."""
        mock_get_session_duration.return_value = 36000
        user = sessions.domain.User(
            user_id="1",
            username='theuser',
            email='the@user.com',
        )
        auths = sessions.domain.Authorizations(classic=6)
        ip_address = '127.0.0.1'
        remote_host = 'foo-host.foo.com'
        tracking = "1.foo"
        with temporary_db():
            user_session, cookie = sessions.create(user, auths, ip_address,
                                                   remote_host, tracking)

            self.assertIsInstance(user_session, sessions.domain.Session)
            tapir_session = sessions._load(user_session.session_id)
            self.assertIsNotNone(user_session, 'verifying we have a session')
            if tapir_session is not None:
                self.assertEqual(
                    tapir_session.session_id,
                    int(user_session.session_id),
                    "Returned session has correct session id."
                )
                self.assertEqual(tapir_session.user_id, int(user.user_id),
                                 "Returned session has correct user id.")
                self.assertEqual(tapir_session.end_time, 0,
                                 "End time is 0 (no end time)")


class TestInvalidateSession(TestCase):
    """Tests for public function :func:`.invalidate`."""

    @mock.patch(f'{cookies.__name__}.util.get_session_duration')
    def test_invalidate(self, mock_get_duration):
        """The session is invalidated by setting `end_time`."""
        mock_get_duration.return_value = 36000
        session_id = "424242424"
        user_id = "12345"
        ip = "127.0.0.1"
        capabilities = 6
        start = datetime.now(tz=EASTERN)

        with temporary_db() as db_session:
            cookie = cookies.pack(session_id, user_id, ip, start, capabilities)
            with util.transaction() as db_session:
                tapir_session = models.DBSession(
                    session_id=session_id,
                    user_id=12345,
                    last_reissue=util.epoch(start),
                    start_time=util.epoch(start),
                    end_time=0
                )
                db_session.add(tapir_session)

            sessions.invalidate(cookie)
            tapir_session = sessions._load(session_id)
            time.sleep(1)
            self.assertGreaterEqual(util.now(), tapir_session.end_time)

    @mock.patch(f'{cookies.__name__}.util.get_session_duration')
    def test_invalidate_nonexistant_session(self, mock_get_duration):
        """An exception is raised if the session doesn't exist."""
        mock_get_duration.return_value = 36000
        with temporary_db():
            with self.assertRaises(exceptions.UnknownSession):
                sessions.invalidate('1:1:10.10.10.10:1531145500:4')