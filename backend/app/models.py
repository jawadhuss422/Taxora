from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./taxora.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    supplier_name = Column(String, default="")
    invoice_number = Column(String, default="")
    invoice_date = Column(String, default="")
    due_date = Column(String, default="")
    description = Column(String, default="")
    subtotal = Column(String, default="")
    sales_tax = Column(String, default="")
    withholding_tax = Column(String, default="")
    total_amount = Column(String, default="")
    currency = Column(String, default="")
    payment_method = Column(String, default="")
    transaction_type = Column(String, default="other")
    tax_rate = Column(String, default="")
    tax_amount = Column(Float, default=0.0)
    fbr_section = Column(String, default="")
    status = Column(String, default="extracted")
    created_at = Column(DateTime, default=datetime.utcnow)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()