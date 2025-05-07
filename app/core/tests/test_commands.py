"""Test custom Django management commands"""
from unittest.mock import patch
# allows us to actually call the command we want to test
from django.core.management import call_command
# another error that we expect to happen when the db is not available
from django.db import OperationalError
# create unit tests for the command
from django.test import SimpleTestCase


# patch to check method check in wait_for_db.py
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands"""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready"""
        # check method return True if the database is ready
        patched_check.return_value = True
        # call the command
        call_command('wait_for_db')

        # assert that the check method was called once with the default db
        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """
        side_effect dùng để mô phỏng các giá trị hoặc lỗi
        mà hàm gốc sẽ trả về mỗi lần được gọi.
        Args:
            patched_check : là một mock object (do unittest.mock.patch tạo ra)
            thay thế cho function kiểm tra trạng thái database
        """

        # 2 times the error, 3 times the true, 3 times the error
        patched_check.side_effect = [OperationalError] * 2 + \
                                    [True] * 3 + \
                                    [OperationalError] * 3

        call_command('wait_for_db')

        # 3 do 2 lần lỗi và 1 lần thành công, những lần sau không được gọi
        # call_command chỉ tiếp tục cho đến khi database sẵn sàng, và ko chạy
        # thêm những lần True tiếp theo hay OperationalError sau đó nữa.
        self.assertEqual(patched_check.call_count, 3)
        patched_check.assert_called_with(databases=['default'])
