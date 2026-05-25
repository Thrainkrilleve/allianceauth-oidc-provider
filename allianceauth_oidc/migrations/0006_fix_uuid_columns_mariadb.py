# Fix Django 5.2 + MariaDB 10.7+ UUID column compatibility.
#
# Django 5.2 introduced has_native_uuid_field support for MariaDB >= 10.7.
# When this feature flag is active, Django passes uuid.UUID objects (with hyphens)
# directly to the database driver instead of converting to 32-char hex strings.
# Columns originally created as char(32) by older django-oauth-toolkit migrations
# are too short for the 36-char hyphenated UUID format and raise:
#   DataError: (1406, "Data too long for column '...' at row 1")
#
# This migration converts the affected oauth2_provider columns from char(32)
# to MariaDB's native uuid type so the DB and Django agree on the format.
# On non-MariaDB backends (MySQL < 8.0.13, SQLite, PostgreSQL) this is a no-op.

from django.db import migrations, connection


def _is_mariadb_with_native_uuid(apps, schema_editor):
    """Return True only when the backend actually needs this fix."""
    db = schema_editor.connection
    return getattr(db, "mysql_is_mariadb", False) and getattr(
        db, "mysql_version", (0,)
    ) >= (10, 7)


def fix_uuid_columns(apps, schema_editor):
    if not _is_mariadb_with_native_uuid(apps, schema_editor):
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "ALTER TABLE oauth2_provider_idtoken "
            "MODIFY COLUMN jti uuid NOT NULL"
        )
        cursor.execute(
            "ALTER TABLE oauth2_provider_refreshtoken "
            "MODIFY COLUMN token_family uuid NULL"
        )


def reverse_uuid_columns(apps, schema_editor):
    if not _is_mariadb_with_native_uuid(apps, schema_editor):
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "ALTER TABLE oauth2_provider_idtoken "
            "MODIFY COLUMN jti char(32) NOT NULL"
        )
        cursor.execute(
            "ALTER TABLE oauth2_provider_refreshtoken "
            "MODIFY COLUMN token_family char(32) NULL"
        )


class Migration(migrations.Migration):
    dependencies = [
        ("allianceauth_oidc", "0005_alter_allianceauthapplication_authorization_grant_type"),
        ("oauth2_provider", "0013_alter_application_authorization_grant_type_device"),
    ]

    operations = [
        migrations.RunPython(fix_uuid_columns, reverse_code=reverse_uuid_columns),
    ]
