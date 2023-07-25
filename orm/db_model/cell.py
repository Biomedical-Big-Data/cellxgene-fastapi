from sqlalchemy import Column, DateTime, Integer, String, text, Double
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base
from dataclasses import dataclass

Base = declarative_base()
metadata = Base.metadata


class CellTypeMeta(Base):
    __tablename__ = "cell_type_meta"
    __table_args__ = {"schema": "cell_type_meta"}

    # ID
    id = Column(Integer, primary_key=True)
    # 生物样品ID
    biosample_id = Column(Integer)
    # 标记符号
    marker_gene_symbol = Column(String(255))
    # 细胞分类标识
    cell_taxonomy_id = Column(String(255))
    # 细胞分类URL
    cell_taxonomy_url = Column(String(255))
    # 细胞本体 ID
    cell_ontology_id = Column(String(255))
    # 细胞类型名称
    cell_type_name = Column(String(255))
    # 细胞类型描述
    cell_type_description = Column(String(255))
    # 细胞类型__本体_标签
    cell_type__ontology_label = Column(String(255))

    create_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )


class CellClusterProportion(Base):
    __tablename__ = "cell_cluster_proportion"
    __table_args__ = {"schema": "cell_cluster_proportion"}
    # ID
    id = Column(Integer, primary_key=True)
    # 生物样品ID
    biosample_id = Column(Integer)
    # 细胞类型ID
    cell_type_id = Column(String(255))
    # 细胞类型ID比例
    cell_type_id_proportion = Column(Double)
    # 细胞类型ID数量
    cell_type_id_number = Column(Integer)
    # 细胞集群方法
    cell_cluster_method = Column(String(255))
    # 细胞集群标识
    cell_cluster_id = Column(String(255))

    create_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )


class CellClusterGeneExpression(Base):
    __tablename__ = "cell_cluster_gene_expression"
    __table_args__ = {"schema": "cell_cluster_gene_expression"}
    # ID
    id = Column(Integer, primary_key=True)
    # 细胞集群ID
    cell_cluster_id = Column(String(255))
    # 基因组ID
    gene_ensemble_id = Column(String(255))
    # 基因符号
    gene_symbol = Column(String(255))
    # 平均基因表达式
    average_gene_expression = Column(Double)
    # 基因的细胞表达比例
    cell_proportion_expression_the_gene = Column(Double)
    # 细胞按比例排序
    cell_rank_gene_by_proportion = Column(Integer)
    # 细胞表达式的基因排名
    cell_rank_gene_by_expression = Column(Integer)
    # 逐个表达的基因排名
    gene_rank_cell_by_expression = Column(Integer)
    # 基因按比例排序
    gene_rank_cell_by_proportion = Column(Integer)
    # 用于 FACS 排序的建议表面组蛋白质
    suggested_surfaceome_protein_for_facs_sorting = Column(String(255))
