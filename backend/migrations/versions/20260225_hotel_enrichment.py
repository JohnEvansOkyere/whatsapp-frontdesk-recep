"""Add hotel-specific columns to services and bookings, add hotel business type.

Revision ID: a2b3c4d5e6f7
Revises: 8f69d917878c
Create Date: 2026-02-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY


revision = "a2b3c4d5e6f7"
down_revision = "8f69d917878c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add 'hotel' to businesstypeenum
    op.execute("ALTER TYPE businesstypeenum ADD VALUE IF NOT EXISTS 'hotel'")
    # Add 'no_show' to bookingstatusenum
    op.execute("ALTER TYPE bookingstatusenum ADD VALUE IF NOT EXISTS 'no_show'")

    # Service / Room-type enrichment
    op.add_column("services", sa.Column("image_url", sa.String(1024), nullable=True))
    op.add_column("services", sa.Column("max_occupancy", sa.Integer(), nullable=True))
    op.add_column("services", sa.Column("bed_type", sa.String(64), nullable=True))
    op.add_column("services", sa.Column("amenities", ARRAY(sa.String()), nullable=True))
    op.add_column("services", sa.Column("base_price_per_night", sa.Numeric(10, 2), nullable=True))
    op.add_column("services", sa.Column("room_count", sa.Integer(), nullable=True))
    op.add_column("services", sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))

    # Booking enrichment
    op.add_column("bookings", sa.Column("check_in_date", sa.Date(), nullable=True))
    op.add_column("bookings", sa.Column("check_out_date", sa.Date(), nullable=True))
    op.add_column("bookings", sa.Column("num_guests", sa.Integer(), nullable=True))
    op.add_column("bookings", sa.Column("num_nights", sa.Integer(), nullable=True))
    op.add_column("bookings", sa.Column("total_price", sa.Numeric(10, 2), nullable=True))
    op.add_column("bookings", sa.Column("guest_name", sa.String(255), nullable=True))
    op.add_column("bookings", sa.Column("guest_email", sa.String(255), nullable=True))
    op.add_column("bookings", sa.Column("guest_phone", sa.String(64), nullable=True))
    op.add_column("bookings", sa.Column("notes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("bookings", "notes")
    op.drop_column("bookings", "guest_phone")
    op.drop_column("bookings", "guest_email")
    op.drop_column("bookings", "guest_name")
    op.drop_column("bookings", "total_price")
    op.drop_column("bookings", "num_nights")
    op.drop_column("bookings", "num_guests")
    op.drop_column("bookings", "check_out_date")
    op.drop_column("bookings", "check_in_date")

    op.drop_column("services", "created_at")
    op.drop_column("services", "room_count")
    op.drop_column("services", "base_price_per_night")
    op.drop_column("services", "amenities")
    op.drop_column("services", "bed_type")
    op.drop_column("services", "max_occupancy")
    op.drop_column("services", "image_url")
