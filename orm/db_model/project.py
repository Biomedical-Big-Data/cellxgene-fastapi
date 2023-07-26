from sqlalchemy import Column, DateTime, Integer, String, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import declarative_base
from orm.database import cellxgene_engine

Base = declarative_base()
metadata = Base.metadata


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = {"schema": "cellxgene"}

    # ID
    id = Column(Integer, primary_key=True)
    # 捐赠者编号
    donor_number = Column(String(255))
    # 生物样本编号
    biosample_number = Column(String(255))
    # 细胞数
    cell_number = Column(String(255))
    # 项目描述
    description = Column(String(255))
    # 解剖实体
    anatomical_entity = Column(String(255))
    # 公布日期
    release_date = Column(DateTime)
    # 联系方式
    contact = Column(String(255))
    # 发布人
    publications = Column(TINYINT(1))
    # 贡献者
    contributors = Column(TINYINT(1))
    # 协作组织
    collaborating_organizations = Column(String(255))
    # 引文
    citation = Column(String(255))
    # 数据策展人
    data_curators = Column(String(255))
    # 草稿状态
    draft = Column(TINYINT(1), nullable=False)

    create_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )


if __name__ == "__main__":
    Project.metadata.create_all(cellxgene_engine)
