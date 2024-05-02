from sqlalchemy import Column, Enum, Text, ForeignKey, Integer, DateTime, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from form_models._database import ServiceObject, db


class FormModel(ServiceObject, db.Model):
    __tablename__ = "tmp_form_model"

    name = Column(Text)
    description = Column(Text)
    subcategory = Column(Integer)

