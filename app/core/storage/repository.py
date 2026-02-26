
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nba:nba_pw@localhost:5432/nba_props")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# ORM models
class Market(Base):
    __tablename__ = "markets"
    id = Column(String, primary_key=True)
    game_id = Column(String)
    player_id = Column(String)
    stat_type = Column(String)
    created_at = Column(DateTime)

class Line(Base):
    __tablename__ = "lines"
    id = Column(String, primary_key=True)
    market_id = Column(String)
    source = Column(String)
    side = Column(String)
    line_value = Column(Float)
    price_american = Column(Integer)
    timestamp = Column(DateTime)
    latency_ms = Column(Integer)

class Projection(Base):
    __tablename__ = "projections"
    id = Column(String, primary_key=True)
    market_id = Column(String)
    model_version = Column(String)
    mean = Column(Float)
    stdev = Column(Float)
    timestamp = Column(DateTime)
    inputs_jsonb = Column(JSON)

class Edge(Base):
    __tablename__ = "edges"
    id = Column(String, primary_key=True)
    market_id = Column(String)
    model_version = Column(String)
    p_over = Column(Float)
    p_under = Column(Float)
    p_push = Column(Float)
    fair_odds_over = Column(Float)
    fair_odds_under = Column(Float)
    edge_over = Column(Float)
    edge_under = Column(Float)
    timestamp = Column(DateTime)
    freshness_score = Column(Float)

class Pick(Base):
    __tablename__ = "picks"
    id = Column(String, primary_key=True)
    user_tag = Column(String)
    market_id = Column(String)
    side = Column(String)
    stake = Column(Float)
    line_at_pick = Column(Float)
    price_at_pick = Column(Integer)
    picked_at = Column(DateTime)
    model_version = Column(String)
    projected_mean = Column(Float)
    p_hit = Column(Float)

class Result(Base):
    __tablename__ = "results"
    id = Column(String, primary_key=True)
    market_id = Column(String)
    actual_value = Column(Float)
    settled_at = Column(DateTime)
    source = Column(String)

class Grade(Base):
    __tablename__ = "grades"
    id = Column(String, primary_key=True)
    pick_id = Column(String)
    won = Column(Boolean)
    profit = Column(Float)
    clv = Column(Float)
    abs_error = Column(Float)
    graded_at = Column(DateTime)

class NBARepository:
    def __init__(self):
        self.session = Session()

    def store_markets(self, markets):
        for m in markets:
            market = Market(**m)
            self.session.add(market)
        self.session.commit()

    def store_lines(self, lines):
        for l in lines:
            line = Line(**l)
            self.session.add(line)
        self.session.commit()

    def store_projections(self, projections):
        for p in projections:
            proj = Projection(**p)
            self.session.add(proj)
        self.session.commit()

    def store_edges(self, edges):
        for e in edges:
            edge = Edge(**e)
            self.session.add(edge)
        self.session.commit()

    def store_pick(self, pick):
        self.session.add(Pick(**pick))
        self.session.commit()

    def store_results(self, results):
        for r in results:
            result = Result(**r)
            self.session.add(result)
        self.session.commit()

    def store_grades(self, grades):
        for g in grades:
            grade = Grade(**g)
            self.session.add(grade)
        self.session.commit()

    def store_raw_response(self, response, date):
        # TODO: Store compressed raw API response for audit (implement as needed)
        pass

    # Retrieval methods (examples)
    def get_markets(self, date):
        return self.session.query(Market).filter(Market.created_at == date).all()

    def get_lines(self, market_id):
        return self.session.query(Line).filter(Line.market_id == market_id).all()

    def get_picks(self, date):
        return self.session.query(Pick).filter(Pick.picked_at == date).all()

    def get_results(self, date):
        return self.session.query(Result).filter(Result.settled_at == date).all()
