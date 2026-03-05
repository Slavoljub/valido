"""
Company model for ValidoAI application
"""
from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, Enum, JSON, TIMESTAMP, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Company(Base):
    """Company model representing the companies table"""
    __tablename__ = 'companies'
    
    company_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='EN: Unique company ID | SR: Jedinstveni ID kompanije')
    name = Column(String(255), nullable=False, comment='EN: Company name | SR: Naziv kompanije')
    tax_id = Column(String(20), nullable=False, unique=True, comment='EN: Tax identification number | SR: Poreski identifikacioni broj')
    registration_number = Column(String(20), nullable=False, unique=True, comment='EN: Registration number | SR: Matični broj')
    address = Column(Text, nullable=True, comment='EN: Company address | SR: Adresa kompanije')
    city = Column(String(100), nullable=True, comment='EN: Company city | SR: Grad kompanije')
    postal_code = Column(String(20), nullable=True, comment='EN: Postal code | SR: Poštanski broj')
    country = Column(String(100), nullable=True, default='Serbia', comment='EN: Country | SR: Država')
    phone = Column(String(20), nullable=True, comment='EN: Company phone | SR: Telefon kompanije')
    email = Column(String(255), nullable=True, comment='EN: Company email | SR: Email kompanije')
    website = Column(String(255), nullable=True, comment='EN: Company website | SR: Web sajt kompanije')
    industry = Column(String(100), nullable=True, comment='EN: Industry sector | SR: Privredna grana')
    company_size = Column(Enum('micro', 'small', 'medium', 'large', name='company_size'), nullable=True, comment='EN: Company size | SR: Veličina kompanije')
    founded_date = Column(Date, nullable=True, comment='EN: Company founding date | SR: Datum osnivanja kompanije')
    is_active = Column(Boolean, nullable=True, default=True, comment='EN: Company active status | SR: Status aktivnosti kompanije')
    compliance_status = Column(Enum('compliant', 'non_compliant', 'pending_review', 'no_declarations', name='compliance_status'), 
                              nullable=True, default='no_declarations', comment='EN: Compliance status | SR: Status usklađenosti')
    metadata = Column(JSON, nullable=True, comment='EN: Additional company metadata | SR: Dodatni metapodaci kompanije')
    created_at = Column(TIMESTAMP, nullable=True, default=datetime.utcnow, comment='EN: Record creation timestamp | SR: Vreme kreiranja zapisa')
    updated_at = Column(TIMESTAMP, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow, comment='EN: Record update timestamp | SR: Vreme ažuriranja zapisa')
    
    def __repr__(self):
        return f"<Company(id={self.company_id}, name='{self.name}', tax_id='{self.tax_id}')>"
    
    def to_dict(self):
        """Convert Company object to dictionary"""
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        
        # Convert datetime objects to ISO format strings
        if self.founded_date:
            result['founded_date'] = self.founded_date.isoformat() if hasattr(self.founded_date, 'isoformat') else self.founded_date
        if self.created_at:
            result['created_at'] = self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else self.created_at
        if self.updated_at:
            result['updated_at'] = self.updated_at.isoformat() if hasattr(self.updated_at, 'isoformat') else self.updated_at
        
        # Parse JSON metadata if it exists
        if self.metadata:
            if isinstance(self.metadata, str):
                try:
                    result['metadata'] = json.loads(self.metadata)
                except:
                    result['metadata'] = self.metadata
            else:
                result['metadata'] = self.metadata
                
        return result
    
    @classmethod
    def from_dict(cls, data):
        """Create Company object from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in [c.name for c in cls.__table__.columns]})
