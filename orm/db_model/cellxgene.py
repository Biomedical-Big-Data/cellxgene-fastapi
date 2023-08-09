from sqlalchemy import Column, DateTime, Integer, String, text, Double, TEXT, VARCHAR, INTEGER, ForeignKey, Table
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import declarative_base, relationship
from orm.database import cellxgene_engine

Base = declarative_base()
metadata = Base.metadata


project_biosample = Table(
    "project_biosample",
    metadata,
    Column("project_id", Integer, ForeignKey("project_meta.id")),
    Column("biosample_id", Integer, ForeignKey("biosample_meta.id"))
)

biosample_analysis = Table(
    "biosample_analysis",
    metadata,
    Column("analysis_id", Integer, ForeignKey("analysis.id")),
    Column("biosample_id", Integer, ForeignKey("biosample_meta.id"))
)


class ProjectMeta(Base):
    __tablename__ = "project_meta"

    # ID
    id = Column(Integer, primary_key=True)
    #
    integrated_project = Column(TINYINT(1))
    #
    title = Column(String(255))
    # 外部继承
    external_project_accesstion = Column(TEXT)
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
    # draft = Column(TINYINT(1), nullable=False)

    create_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )
    project_biosample_meta = relationship("BioSampleMeta", secondary=project_biosample, back_populates="biosample_project_meta", cascade="all")


class BioSampleMeta(Base):
    __tablename__ = "biosample_meta"

    # ID
    id = Column(Integer, primary_key=True)
    # 外部继承
    external_sample_accesstion = Column(TEXT)
    # 生物样本类型
    biosample_type = Column(String(255))
    # 种类 ID
    species_id = Column(Integer, ForeignKey("species_meta.id"))
    # 捐赠者 ID
    donor_id = Column(INTEGER, ForeignKey("donor_meta.id"))
    # bmi
    bmi = Column(String(255))
    # 是否活体
    is_living = Column(TINYINT(1))
    # 样本收集时间
    sample_collection_time = Column(DateTime)
    # 地理区域
    geographical_region = Column(String(255))
    # 有机体年龄
    organism_age = Column(INTEGER)
    # 有机体年龄单位
    organism_age__unit = Column(INTEGER)
    # TODO 鼠应变
    mouse_strain = Column(String(255))
    # TODO 持续时间
    culture_duration = Column(INTEGER)
    # 文化持续时间__单位
    culture_duration__unit = Column(INTEGER)
    # 发展阶段
    development_stage = Column(String(255))
    # 病症
    disease = Column(String(255))
    # 疾病__本体_标签
    disease__ontology_label = Column(TEXT)
    # 疾病__细胞内病原体
    disease__intracellular_pathogen = Column(String(255))
    # 疾病__细胞内病原体__病理学__标签
    disease__intracellular_pathogen__ontology_label = Column(TEXT)
    # 疾病__发病时间
    disease__time_since_onset = Column(DateTime)
    # 疾病__发病时间__单位
    disease__time_since_onset__unit = Column(INTEGER)
    # 疾病__发病时间__单位标签
    disease__time_since_onset__unit_label = Column(TEXT)
    # 疾病__治疗开始时间
    disease__time_since_treatment_start = Column(DateTime)
    # 疾病__治疗开始时间__单位
    disease__time_since_treatment_start__unit = Column(INTEGER)
    # 疾病__已治疗
    disease__treated = Column(TINYINT)
    # 疾病__治疗
    disease__treatment = Column(TEXT)
    # 疫苗接种
    vaccination = Column(String(255))
    # 疫苗__佐剂
    vaccination__adjuvants = Column(String(255))
    # 疫苗接种__剂量
    vaccination__dosage = Column(String(255))
    # 疫苗接种__路线
    vaccination__route = Column(String(255))
    # 接种时间
    vaccination__time_since = Column(DateTime)
    # 接种__时间__起__单位
    vaccination__time_since__unit = Column(INTEGER)
    # 器官
    organ = Column(String(255))
    # 器官区域
    organ_region = Column(String(255))
    # 基因扰动
    gene_perturbation = Column(String(255))
    # 基因扰动__方向
    gene_perturbation__direction = Column(String(255))
    # 基因扰动动力学
    gene_perturbation__dynamics = Column(String(255))
    # 基因扰动__方法
    gene_perturbation__method = Column(String(255))
    # 基因扰动__自时间
    gene_perturbation__time_since = Column(DateTime)
    # 基因扰动__时间自__单位
    gene_perturbation__time_since__unit = Column(INTEGER)
    # 生物扰动
    biologies_perturbation = Column(String(255))
    # 生物扰动__浓度
    biologies_perturbation__concentration = Column(Double)
    # 生物扰动__浓度__单位
    biologies_perturbation__concentration__unit = Column(INTEGER)
    # 生物扰动__溶剂
    biologies_perturbation__solvent = Column(String(255))
    # 生物扰动__源
    biologies_perturbation__source = Column(String(255))
    # 生物扰动__开始时间
    biologies_perturbation__time_since = Column(DateTime)
    # 生物扰动__时间自__单位
    biologies_perturbation__time_since__unit = Column(INTEGER)
    # 小分子扰动
    small_molecule_perturbation = Column(String(255))
    # 小分子扰动__浓度
    small_molecule_perturbation__concentration = Column(Double)
    # 小分子扰动__浓度__单位
    small_molecule_perturbation__concentration__unit = Column(INTEGER)
    # 小分子扰动__溶剂
    small_molecule_perturbation__solvent = Column(String(255))
    # 小分子扰动__源
    small_molecule_perturbation__source = Column(String(255))
    # 小分子扰动__自时间
    small_molecule_perturbation__time_since = Column(DateTime)
    # 小分子扰动__自__单位时间
    small_molecule_perturbation__time_since__unit = Column(INTEGER)
    # 其他扰动
    other_perturbation = Column(String(255))
    # 其他扰动__自时间
    other_perturbation__time_since = Column(DateTime)
    # 其他扰动__自__单位时间起
    other_perturbation__time_since__unit = Column(INTEGER)
    # 富集__细胞类型
    enrichment__cell_type = Column(String(255))
    # 丰富__facs_标记
    enrichment__facs_markers = Column(String(255))
    # 浓缩方法
    enrichment_method = Column(String(255))
    # 保存方法
    preservation_method = Column(String(255))
    # 库准备协议
    library_preparation_protocol = Column(String(255))
    # 核酸源
    nucleic_acid_source = Column(String(255))
    # sequencing_instrument_manufacturer_model
    sequencing_instrument_manufacturer_model = Column(String(255))
    # 引子
    primer = Column(TEXT)
    # 结束偏差
    end_bias = Column(String(255))
    # 尖峰浓度
    spike_in_concentration = Column(String(255))
    # 穗状包
    spike_in_kit = Column(String(255))
    # 读取长度
    strand = Column(String(255))
    read_length = Column(INTEGER)
    # 成对末端
    paired_ends = Column(String(255))
    # 细胞数
    number_of_cells = Column(INTEGER)
    # 参照
    number_of_reads = Column(INTEGER)

    create_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )
    biosample_donor_meta = relationship("DonorMeta", back_populates="donor_biosample_meta")
    biosample_project_meta = relationship("ProjectMeta", secondary=project_biosample, back_populates="project_biosample_meta", cascade="all")
    biosample_analysis_meta = relationship("Analysis", secondary=biosample_analysis, back_populates="analysis_biosample_meta")
    biosample_species_meta = relationship("SpeciesMeta", back_populates="species_biosample_meta")


class DonorMeta(Base):
    __tablename__ = "donor_meta"

    # ID
    id = Column(Integer, primary_key=True)
    sex = Column(String(255))
    # 种族
    ethnicity = Column(String(255))
    # 人种
    race = Column(String(255))
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
    donor_biosample_meta = relationship("BioSampleMeta", back_populates="biosample_donor_meta")


class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    h5ad_id = Column(String(255))
    reference = Column(String(255))
    analysis_protocol = Column(String(255))
    analysis_biosample_meta = relationship("BioSampleMeta", secondary=biosample_analysis, back_populates="biosample_analysis_meta")


class CalcCellClusterProportion(Base):
    __tablename__ = "calc_cell_cluster_proportion"
    # ID
    id = Column(Integer, primary_key=True)
    # 生物样品ID
    biosample_id = Column(Integer)
    # 细胞类型ID
    cell_type_id = Column(Integer, ForeignKey("cell_type_meta.id"))
    # 细胞类型ID比例
    cell_proportion = Column(Double)
    # 细胞类型ID数量
    cell_number = Column(Integer)
    # 细胞集群方法
    cell_cluster_method = Column(String(255))

    create_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )
    proportion_cell_type_meta = relationship("CellTypeMeta", back_populates="cell_type_proportion_meta")
    proportion_gene_expression = relationship("CellClusterGeneExpression", back_populates="gene_expression_proportion_meta")


class CellTypeMeta(Base):
    __tablename__ = "cell_type_meta"

    # ID
    id = Column(Integer, primary_key=True)
    # 物种ID
    species_id = Column(Integer, ForeignKey("species_meta.id"))
    # 标记符号
    marker_gene_symbol = Column(String(255))
    # 细胞分类标识
    cell_taxonomy_id = Column(Integer)
    # 细胞分类URL
    cell_taxonomy_url = Column(String(255))
    # 细胞本体 ID
    cell_ontology_id = Column(Integer)
    # 细胞类型名称
    cell_type_name = Column(String(255))
    # 细胞类型描述
    cell_type_description = Column(String(255))
    # 细胞类型__本体_标签
    cell_type__ontology_label = Column(TEXT)

    create_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )
    cell_type_proportion_meta = relationship("CalcCellClusterProportion", back_populates="proportion_cell_type_meta")
    cell_type_species_meta = relationship("SpeciesMeta", back_populates="species_cell_type_meta")


class CellClusterGeneExpression(Base):
    __tablename__ = "cell_cluster_gene_expression"
    # ID
    id = Column(Integer, primary_key=True)
    # 细胞集群ID
    calculated_cell_cluster_id = Column(Integer, ForeignKey("calc_cell_cluster_proportion.id"))
    # 基因组ID
    gene_id = Column(Integer, ForeignKey("gene_meta.id"))
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

    create_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )
    gene_expression_proportion_meta = relationship("CalcCellClusterProportion", back_populates="proportion_gene_expression")
    gene_expression_gene_meta = relationship("GeneMeta", back_populates="gene_gene_expression_meta")


class SpeciesMeta(Base):
    __tablename__ = "species_meta"

    id = Column(Integer, primary_key=True)
    # 品种
    species = Column(String(255))
    # 物种__本体_标签
    species__ontology_label = Column(TEXT)
    species_cell_type_meta = relationship("CellTypeMeta", back_populates="cell_type_species_meta")
    species_gene_meta = relationship("GeneMeta", back_populates="gene_species_meta")
    species_biosample_meta = relationship("BioSampleMeta", back_populates="biosample_species_meta")


class GeneMeta(Base):
    __tablename__ = "gene_meta"

    # ID
    id = Column(Integer, primary_key=True)
    # 品种
    species_id = Column(Integer, ForeignKey("species_meta.id"))
    # 人类正源物
    ortholog = Column(String(255))
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
    gene_species_meta = relationship("SpeciesMeta", back_populates="species_gene_meta")
    gene_gene_expression_meta = relationship("CellClusterGeneExpression", back_populates="gene_expression_gene_meta")


class PathwayScore(Base):
    __tablename__ = "pathway_score"
    # ID
    id = Column(Integer, primary_key=True)
    # 路径源
    pathway_source = Column(String(255))
    # 路径名称
    pathway_name = Column(String(255))
    # 品种
    species_id = Column(Integer, ForeignKey("species_meta.id"))
    # 基因组符号
    geneset_gene_symbols = Column(String(255))
    # 项目编号
    project_id = Column(Integer, ForeignKey("project_meta.id"))
    # 生物样本 ID
    biosample_id = Column(Integer, ForeignKey("biosample_meta.id"))
    # 细胞类型名称
    cell_type_name = Column(String(255))
    # 细胞集群标识
    calculated_cell_cluster_id = Column(Integer, ForeignKey("calc_cell_cluster_proportion.id"))
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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_name = Column(String(255), nullable=False, unique=True)
    email_address = Column(VARCHAR(255), nullable=False, unique=True)
    organization = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    user_password = Column(String(255), nullable=False)
    state = Column(TINYINT(1), nullable=False)
    create_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )

    def to_dict(self):
        return {
            "user_name": self.user_name,
            "email_address": self.email_address,
            "organization": self.organization,
            "state": self.state,
            "create_at": self.create_at,
            "update_at": self.update_at,
        }


if __name__ == "__main__":
    metadata.create_all(cellxgene_engine)