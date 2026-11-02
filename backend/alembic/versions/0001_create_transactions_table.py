"""create transactions table

Revision ID: 0001_create_transactions
Revises: 
Create Date: 2026-09-23 13:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001_create_transactions"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "transactions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("time", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("fraud_probability", sa.Float(), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("risk_label", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("amount > 0", name="chk_transactions_amount_positive"),
        sa.CheckConstraint("time >= 0", name="chk_transactions_time_non_negative"),
        sa.CheckConstraint(
            "fraud_probability >= 0.0 AND fraud_probability <= 1.0",
            name="chk_transactions_fraud_probability_range",
        ),
        sa.CheckConstraint(
            "risk_score >= 0 AND risk_score <= 100",
            name="chk_transactions_risk_score_range",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_transactions_id"), "transactions", ["id"], unique=False)
    op.create_index(
        op.f("ix_transactions_risk_label"), "transactions", ["risk_label"], unique=False
    )
    op.create_index(
        op.f("ix_transactions_risk_score"), "transactions", ["risk_score"], unique=False
    )
    op.create_index(
        op.f("ix_transactions_created_at"), "transactions", ["created_at"], unique=False
    )
    op.create_index(
        "ix_transactions_created_at_desc",
        "transactions",
        [sa.text("created_at DESC")],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_transactions_created_at_desc", table_name="transactions")
    op.drop_index(op.f("ix_transactions_created_at"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_risk_score"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_risk_label"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_id"), table_name="transactions")
    op.drop_table("transactions")
