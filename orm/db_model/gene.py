from sqlalchemy import Column, DateTime, Integer, String, text, Double
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import declarative_base
from orm.database import cellxgene_engine

Base = declarative_base()
metadata = Base.metadata


class MouseGene(Base):
    __tablename__ = "mouse_gene"
    __table_args__ = {"schema": "cellxgene"}

    # ID
    id = Column(Integer, primary_key=True)
    # 基因组 ID
    gene_ensemble_id = Column(String(255))
    # 品种
    species = Column(String(255))
    # FIXME 人类正源物
    ortholog_human = Column(String(255))
    # 项目描述
    gene_symbol = Column(String(255))
    # 基因符号
    gene_name = Column(String(255))
    # 别称
    alias = Column(String(255))
    # 基因生物
    gene_ontology = Column(String(255))
    # GPCR
    GPCR = Column(String(255))
    # TF
    TF = Column(String(255))
    # 表层
    surfaceome = Column(String(255))
    # 药物库目标药物
    drugbank_drugtarget = Column(String(255))
    # 表征
    phenotype = Column(String(255))

    create_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )


class MousePathwayScore(Base):
    __tablename__ = "mouse_pathway_score"
    __table_args__ = {"schema": "cellxgene"}
    # ID
    id = Column(Integer, primary_key=True)
    # 路径编号
    pathway_id = Column(String(255))
    # 路径源
    pathway_source = Column(String(255))
    # 路径名称
    pathway_name = Column(String(255))
    # 品种
    species = Column(String(255))
    # 基因组符号
    geneset_gene_symbols = Column(String(255))
    # 项目编号
    project_id = Column(String(255))
    # 生物样本 ID
    biosample_id = Column(String(255))
    # 细胞类型名称
    cell_type_name = Column(String(255))
    # 细胞集群标识
    cell_cluster_id = Column(String(255))
    # 得分函数
    score_function = Column(String(255))
    # 得分
    score = Column(Double)

    create_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )



class HumanGene(Base):
    __tablename__ = "human_gene"
    __table_args__ = {"schema": "cellxgene"}

    # ID
    id = Column(Integer, primary_key=True)
    # 基因组 ID
    gene_ensemble_id = Column(String(255))
    # 品种
    species = Column(String(255))
    # FIXME 鼠正源物
    ortholog_mouse = Column(String(255))
    # 项目描述
    gene_symbol = Column(String(255))
    # 基因符号
    gene_name = Column(String(255))
    # 别称
    alias = Column(String(255))
    # 基因生物
    gene_ontology = Column(String(255))
    # GPCR
    GPCR = Column(String(255))
    # TF
    TF = Column(String(255))
    # 表层
    surfaceome = Column(String(255))
    # 药物库目标药物
    drugbank_drugtarget = Column(String(255))
    # 表征
    phenotype = Column(String(255))

    create_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )


class HumanPathwayScore(Base):
    __tablename__ = "human_pathway_score"
    __table_args__ = {"schema": "cellxgene"}
    # ID
    id = Column(Integer, primary_key=True)
    # 路径编号
    pathway_id = Column(String(255))
    # 路径源
    pathway_source = Column(String(255))
    # 路径名称
    pathway_name = Column(String(255))
    # 品种
    species = Column(String(255))
    # 基因组符号
    geneset_gene_symbols = Column(String(255))
    # 项目编号
    project_id = Column(String(255))
    # 生物样本 ID
    biosample_id = Column(String(255))
    # 细胞类型名称
    cell_type_name = Column(String(255))
    # 细胞集群标识
    cell_cluster_id = Column(String(255))
    # 得分函数
    score_function = Column(String(255))
    # 得分
    score = Column(Double)

    create_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )


if __name__ == "__main__":
    MouseGene.metadata.create_all(cellxgene_engine)
