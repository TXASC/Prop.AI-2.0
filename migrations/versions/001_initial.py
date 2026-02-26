"""Initial migration: create NBA prop analytics tables"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('players',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('team', sa.String, nullable=False),
        sa.Column('external_ids', sa.JSON, nullable=True)
    )
    op.create_table('teams',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('abbrev', sa.String, nullable=False)
    )
    op.create_table('games',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('home_team_id', sa.String, nullable=False),
        sa.Column('away_team_id', sa.String, nullable=False),
        sa.Column('start_time', sa.DateTime, nullable=False),
        sa.Column('status', sa.String, nullable=False)
    )
    op.create_table('markets',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('game_id', sa.String, nullable=False),
        sa.Column('player_id', sa.String, nullable=False),
        sa.Column('stat_type', sa.String, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False)
    )
    op.create_table('lines',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('market_id', sa.String, nullable=False),
        sa.Column('source', sa.String, nullable=False),
        sa.Column('side', sa.String, nullable=False),
        sa.Column('line_value', sa.Float, nullable=False),
        sa.Column('price_american', sa.Integer, nullable=False),
        sa.Column('timestamp', sa.DateTime, nullable=False),
        sa.Column('latency_ms', sa.Integer, nullable=True)
    )
    op.create_table('projections',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('market_id', sa.String, nullable=False),
        sa.Column('model_version', sa.String, nullable=False),
        sa.Column('mean', sa.Float, nullable=False),
        sa.Column('stdev', sa.Float, nullable=False),
        sa.Column('timestamp', sa.DateTime, nullable=False),
        sa.Column('inputs_jsonb', sa.JSON, nullable=True)
    )
    op.create_table('edges',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('market_id', sa.String, nullable=False),
        sa.Column('model_version', sa.String, nullable=False),
        sa.Column('p_over', sa.Float, nullable=False),
        sa.Column('p_under', sa.Float, nullable=False),
        sa.Column('p_push', sa.Float, nullable=True),
        sa.Column('fair_odds_over', sa.Float, nullable=False),
        sa.Column('fair_odds_under', sa.Float, nullable=False),
        sa.Column('edge_over', sa.Float, nullable=False),
        sa.Column('edge_under', sa.Float, nullable=False),
        sa.Column('timestamp', sa.DateTime, nullable=False),
        sa.Column('freshness_score', sa.Float, nullable=False)
    )
    op.create_table('picks',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('user_tag', sa.String, nullable=False),
        sa.Column('market_id', sa.String, nullable=False),
        sa.Column('side', sa.String, nullable=False),
        sa.Column('stake', sa.Float, nullable=False),
        sa.Column('line_at_pick', sa.Float, nullable=False),
        sa.Column('price_at_pick', sa.Integer, nullable=False),
        sa.Column('picked_at', sa.DateTime, nullable=False),
        sa.Column('model_version', sa.String, nullable=False),
        sa.Column('projected_mean', sa.Float, nullable=False),
        sa.Column('p_hit', sa.Float, nullable=False)
    )
    op.create_table('results',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('market_id', sa.String, nullable=False),
        sa.Column('actual_value', sa.Float, nullable=False),
        sa.Column('settled_at', sa.DateTime, nullable=False),
        sa.Column('source', sa.String, nullable=False)
    )
    op.create_table('grades',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('pick_id', sa.String, nullable=False),
        sa.Column('won', sa.Boolean, nullable=False),
        sa.Column('profit', sa.Float, nullable=False),
        sa.Column('clv', sa.Float, nullable=False),
        sa.Column('abs_error', sa.Float, nullable=False),
        sa.Column('graded_at', sa.DateTime, nullable=False)
    )

def downgrade():
    op.drop_table('grades')
    op.drop_table('results')
    op.drop_table('picks')
    op.drop_table('edges')
    op.drop_table('projections')
    op.drop_table('lines')
    op.drop_table('markets')
    op.drop_table('games')
    op.drop_table('teams')
    op.drop_table('players')
