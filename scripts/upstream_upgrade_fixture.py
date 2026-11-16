"""Synthetic data fixture for the disposable upstream beta.9 Docker upgrade check.

Run this file with each image's own Python and application modules. Never point
it at an operator's data directory: ``seed`` requires an empty account table.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone

import bcrypt
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

import app
from app.core.config.settings import get_settings
from app.core.crypto import TokenEncryptor
from app.db.migrate import check_schema_drift, inspect_migration_state
from app.db.migration_url import to_sync_database_url
from app.db.models import (
    Account,
    AccountStatus,
    ApiKey,
    ApiKeyAccountAssignment,
    DashboardRoleRecord,
    DashboardSettings,
    DashboardUser,
    RequestLog,
    UsageHistory,
)

ACCOUNT_ID = "upgrade-fixture-account"
USER_ID = "upgrade-fixture-user"
KEY_ID = "upgrade-fixture-api-key"
PASSWORD = "Only-a-disposable-upgrade-test-123!"
API_KEY = "sk-clb-upgrade-fixture-not-a-real-secret"
TOTP_SECRET = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
SOURCE_VERSION = "1.25.0-beta.9"

# Full rows protect all existing account/key/auth/history fields. Only settings
# use a projection: upstream has already retired two overflow configuration
# columns in the target's existing migrations.
SNAPSHOT_QUERIES = {
    "accounts": "SELECT * FROM accounts ORDER BY id",
    "api_keys": "SELECT * FROM api_keys ORDER BY id",
    "api_key_accounts": "SELECT * FROM api_key_accounts ORDER BY api_key_id, account_id",
    "dashboard_users": "SELECT * FROM dashboard_users ORDER BY id",
    "usage_history": "SELECT * FROM usage_history ORDER BY id",
    "request_logs": "SELECT * FROM request_logs ORDER BY id",
    "dashboard_settings": (
        "SELECT id, sticky_threads_enabled, prohibit_fast_mode, upstream_stream_transport "
        "FROM dashboard_settings ORDER BY id"
    ),
}


def snapshot() -> dict[str, str]:
    settings = get_settings()
    result = {"encryption.key": hashlib.sha256(settings.encryption_key_file.read_bytes()).hexdigest()}
    database_path = settings.data_dir / "store.db"
    with sqlite3.connect(database_path.as_uri() + "?mode=ro", uri=True) as connection:
        for name, query in SNAPSHOT_QUERIES.items():
            rows = connection.execute(query).fetchall()
            assert rows, f"Missing fixture rows: {name}"
            result[name] = hashlib.sha256(repr(rows).encode()).hexdigest()
    return result


def seed() -> None:
    assert app.__version__ == SOURCE_VERSION, (app.__version__, SOURCE_VERSION)
    settings = get_settings()
    baseline_path = settings.data_dir / "upstream-upgrade-fixture.json"
    assert not baseline_path.exists(), "Refusing to overwrite an existing fixture"
    encryptor = TokenEncryptor()
    engine = create_engine(to_sync_database_url(settings.database_url))
    try:
        with Session(engine) as session:
            assert session.scalar(select(Account.id).limit(1)) is None, "Fixture requires an empty account table"
            role = session.scalars(select(DashboardRoleRecord).where(DashboardRoleRecord.slug == "admin")).one()
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            session.add(
                Account(
                    id=ACCOUNT_ID,
                    email="upgrade@example.invalid",
                    alias="Original upstream account",
                    plan_type="plus",
                    status=AccountStatus.PAUSED,
                    access_token_encrypted=encryptor.encrypt("fixture-access-token"),
                    refresh_token_encrypted=encryptor.encrypt("fixture-refresh-token"),
                    id_token_encrypted=encryptor.encrypt("fixture-id-token"),
                    last_refresh=now,
                )
            )
            session.add(
                DashboardUser(
                    id=USER_ID,
                    username="upgrade-admin",
                    role_id=role.id,
                    password_hash=bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt()).decode(),
                    totp_secret_encrypted=encryptor.encrypt(TOTP_SECRET),
                )
            )
            session.flush()
            session.add(
                ApiKey(
                    id=KEY_ID,
                    name="Original upstream key",
                    key_hash=hashlib.sha256(API_KEY.encode()).hexdigest(),
                    key_prefix="sk-clb-upgrade",
                    owner_user_id=USER_ID,
                    account_assignment_scope_enabled=True,
                    allowed_models='["gpt-5.6-sol"]',
                )
            )
            session.flush()
            session.add(ApiKeyAccountAssignment(api_key_id=KEY_ID, account_id=ACCOUNT_ID))
            session.add(
                UsageHistory(
                    account_id=ACCOUNT_ID,
                    recorded_at=now,
                    window="primary",
                    used_percent=23.5,
                    input_tokens=1234,
                    output_tokens=567,
                )
            )
            session.add(
                RequestLog(
                    account_id=ACCOUNT_ID,
                    api_key_id=KEY_ID,
                    request_id="upstream-upgrade-fixture-request",
                    requested_at=now,
                    model="gpt-5.6-sol",
                    status="success",
                    input_tokens=1234,
                    output_tokens=567,
                    cost_usd=0.125,
                )
            )
            dashboard = session.get(DashboardSettings, 1)
            assert dashboard is not None, "Original startup did not create dashboard settings"
            dashboard.sticky_threads_enabled = False
            dashboard.prohibit_fast_mode = True
            dashboard.upstream_stream_transport = "http"
            session.commit()
    finally:
        engine.dispose()
    baseline_path.write_text(json.dumps(snapshot(), sort_keys=True), encoding="utf-8")
    print(f"Seeded original {SOURCE_VERSION}: encrypted account, scoped API key, dashboard auth/settings and history")


def verify(expected_version: str) -> None:
    assert app.__version__ == expected_version, (app.__version__, expected_version)
    settings = get_settings()
    expected = json.loads((settings.data_dir / "upstream-upgrade-fixture.json").read_text(encoding="utf-8"))
    actual = snapshot()
    assert actual == expected, f"Data changed: {[name for name in expected if actual.get(name) != expected[name]]}"
    state = inspect_migration_state(settings.database_url)
    assert not state.needs_upgrade and not state.unknown_revisions, state
    drift = check_schema_drift(settings.database_url)
    assert not drift, drift
    engine = create_engine(to_sync_database_url(settings.database_url))
    try:
        with Session(engine) as session:
            account = session.get(Account, ACCOUNT_ID)
            user = session.get(DashboardUser, USER_ID)
            key = session.get(ApiKey, KEY_ID)
            assert account is not None and user is not None and key is not None
            encryptor = TokenEncryptor()
            assert encryptor.decrypt(account.access_token_encrypted) == "fixture-access-token"
            assert encryptor.decrypt(account.refresh_token_encrypted) == "fixture-refresh-token"
            assert encryptor.decrypt(account.id_token_encrypted) == "fixture-id-token"
            assert user.totp_secret_encrypted is not None and user.password_hash is not None
            assert encryptor.decrypt(user.totp_secret_encrypted) == TOTP_SECRET
            assert bcrypt.checkpw(PASSWORD.encode(), user.password_hash.encode())
            assert key.key_hash == hashlib.sha256(API_KEY.encode()).hexdigest()
            assert key.is_active and key.owner_user_id == USER_ID and key.account_assignment_scope_enabled
            assert session.get(ApiKeyAccountAssignment, (KEY_ID, ACCOUNT_ID)) is not None
    finally:
        engine.dispose()
    print(f"Upgrade verified: {SOURCE_VERSION} -> {expected_version}; data, credentials and schema preserved")


if __name__ == "__main__":
    if sys.argv[1:] == ["seed"]:
        seed()
    elif len(sys.argv) == 3 and sys.argv[1] == "verify":
        verify(sys.argv[2])
    else:
        raise SystemExit("usage: upstream_upgrade_fixture.py seed | verify VERSION")
