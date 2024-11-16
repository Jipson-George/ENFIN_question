"""seed_data

Revision ID: 1137156da157
Revises: 16802114a6fa
Create Date: 2024-11-16 18:19:57.730148

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1137156da157'
down_revision: Union[str, None] = '16802114a6fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


"""expanded_seed_data

Revision ID: expanded_seed_rev1
Revises: your_previous_revision
Create Date: 2024-01-01
"""

def upgrade():
    conn = op.get_bind()

    # More Users with diverse timezones
    conn.execute(
        sa.text("""
        INSERT INTO users (id, timezone, name) VALUES
        (1, 'UTC+0', 'John Doe'),
        (2, 'UTC-5', 'Jane Smith'),
        (3, 'UTC+1', 'Mike Johnson'),
        (4, 'UTC+5:30', 'Priya Patel'),
        (5, 'UTC-8', 'Sarah Wilson'),
        (6, 'UTC+9', 'Takeshi Yamamoto'),
        (7, 'UTC+2', 'Maria Garcia'),
        (8, 'UTC-3', 'Carlos Silva'),
        (9, 'UTC+8', 'Li Wei'),
        (10, 'UTC+3', 'Alex Kumar')
        """)
    )

    # Extensive Weekly Availability
    conn.execute(
        sa.text("""
        INSERT INTO weekly_availability (user_id, day_of_week, start_time, end_time) VALUES
        
        (1, 1, '09:00:00', '17:00:00'),
        (1, 2, '09:00:00', '17:00:00'),
        (1, 3, '09:00:00', '17:00:00'),
        (1, 4, '09:00:00', '17:00:00'),
        (1, 5, '09:00:00', '17:00:00'),
        (2, 1, '13:00:00', '21:00:00'),
        (2, 2, '13:00:00', '21:00:00'),
        (2, 3, '13:00:00', '21:00:00'),
        (2, 4, '13:00:00', '21:00:00'),
        (3, 1, '06:00:00', '14:00:00'),
        (3, 2, '06:00:00', '14:00:00'),
        (3, 3, '06:00:00', '14:00:00'),
        (4, 1, '09:00:00', '13:00:00'),
        (4, 1, '15:00:00', '19:00:00'),
        (4, 3, '09:00:00', '13:00:00'),
        (4, 3, '15:00:00', '19:00:00'),
        (5, 6, '10:00:00', '18:00:00'),
        (5, 7, '10:00:00', '18:00:00'),
        (6, 1, '08:00:00', '16:00:00'),
        (6, 3, '10:00:00', '18:00:00'),
        (6, 5, '12:00:00', '20:00:00')
        """)
    )

    # Specific Availability for next month
    conn.execute(
        sa.text("""
        INSERT INTO specific_availability (user_id, date, start_time, end_time) VALUES
        (1, '2024-02-01', '10:00:00', '15:00:00'),
        (1, '2024-02-02', '09:00:00', '17:00:00'),
        (2, '2024-02-01', '14:00:00', '20:00:00'),
        (3, '2024-02-03', '07:00:00', '15:00:00'),
        (4, '2024-02-04', '09:00:00', '18:00:00'),
        (5, '2024-02-05', '11:00:00', '19:00:00'),
        (6, '2024-02-06', '08:00:00', '16:00:00'),
        (7, '2024-02-07', '10:00:00', '18:00:00'),
        (8, '2024-02-08', '09:00:00', '17:00:00'),
        (9, '2024-02-09', '13:00:00', '21:00:00'),
        (10, '2024-02-10', '07:00:00', '15:00:00')
        """)
    )

    # Scheduled Events
    conn.execute(
        sa.text("""
        INSERT INTO scheduled_events (user_id, start_datetime, end_datetime) VALUES
        (1, '2024-02-01 10:30:00', '2024-02-01 11:30:00'),
        (1, '2024-02-01 14:00:00', '2024-02-01 15:00:00'),
        (2, '2024-02-01 15:00:00', '2024-02-01 16:00:00'),
        (3, '2024-02-03 08:00:00', '2024-02-03 09:00:00'),
        (4, '2024-02-04 10:00:00', '2024-02-04 11:00:00'),
        (5, '2024-02-05 12:00:00', '2024-02-05 13:00:00'),
        (6, '2024-02-06 09:00:00', '2024-02-06 10:00:00'),
        (7, '2024-02-07 11:00:00', '2024-02-07 12:00:00'),
        (8, '2024-02-08 14:00:00', '2024-02-08 15:00:00'),
        (9, '2024-02-09 16:00:00', '2024-02-09 17:00:00'),
        (10, '2024-02-10 08:00:00', '2024-02-10 09:00:00')
        """)
    )

def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM scheduled_events"))
    conn.execute(sa.text("DELETE FROM specific_availability"))
    conn.execute(sa.text("DELETE FROM weekly_availability"))
    conn.execute(sa.text("DELETE FROM users"))

