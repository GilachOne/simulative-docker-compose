"""Run with the application's dependencies installed (or inside its image)."""
import os
from pathlib import Path
import subprocess
import sys
import unittest

APP_DIR = Path(__file__).resolve().parents[1] / 'app'
if not (APP_DIR / 'app.py').exists():
    APP_DIR = Path('/app')


class ConfigTests(unittest.TestCase):
    def load(self, changes=None, code='import app'):
        env = {k: v for k, v in os.environ.items() if not k.startswith('DB_')}
        env.update(DB_NAME='test_db', DB_USER='test_user', DB_PASSWORD='private-test-value')
        for key, value in (changes or {}).items():
            if value is None:
                env.pop(key, None)
            else:
                env[key] = value
        return subprocess.run([sys.executable, '-c', code], cwd=APP_DIR,
                              env=env, text=True, capture_output=True)

    def test_required_variables_name_missing_setting(self):
        for name in ('DB_NAME', 'DB_USER', 'DB_PASSWORD'):
            for value in (None, '', '   '):
                with self.subTest(name=name, value=value):
                    result = self.load({name: value})
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(f'Переменная {name} должна быть установлена', result.stderr)
                    self.assertNotIn('private-test-value', result.stderr)

    def test_blank_optional_variables_use_defaults(self):
        result = self.load({'DB_HOST': ' ', 'DB_PORT': ''},
                           'import app; print(app.DB_HOST, app.DB_PORT)')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'postgres 5432')

    def test_invalid_port_has_clear_error(self):
        for port in ('abc', '0', '65536'):
            with self.subTest(port=port):
                result = self.load({'DB_PORT': port})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('DB_PORT должна быть целым числом от 1 до 65535', result.stderr)
                self.assertNotIn('private-test-value', result.stderr)

    def test_explicit_port_and_password_are_preserved(self):
        result = self.load({'DB_PORT': '5544', 'DB_PASSWORD': ' pass with spaces '},
                           "import app; assert app.DB_PORT == 5544; assert app.DB_PASSWORD == ' pass with spaces '")
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
