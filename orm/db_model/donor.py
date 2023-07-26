from sqlalchemy import Column, DateTime, Integer, String, text, Double
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base
from dataclasses import dataclass

Base = declarative_base()
metadata = Base.metadata


class DonorMeta(Base):
    __tablename__ = "donor_meta"
    __table_args__ = {"schema": "donor_meta"}

    # ID
    id = Column(Integer, primary_key=True)
    # 性别
    sex = Column(String(255))
    # 种族
    ethnicity = Column(String(255))
    # 种族__本体__标签
    ethnicity__ontology_label = Column(String(255))
    # 人种
    race = Column(String(255))
    # 种族__本体__标签
    race__ontology_label = Column(String(255))
    # 基因型
    mhc_genotype = Column(String(255))
    # 酒精历史
    alcohol_history = Column(String(255))
    # 药物
    medications = Column(String(255))
    # 营养状态
    nutritional_state = Column(String(255))
    # 吸烟历史
    smoking_history = Column(String(255))
    # 测试结果
    test_results = Column(String(255))

    create_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )