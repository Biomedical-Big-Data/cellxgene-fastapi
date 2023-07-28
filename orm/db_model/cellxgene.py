from sqlalchemy import Column, DateTime, Integer, String, text, Double, TEXT, VARCHAR, INTEGER, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()
metadata = Base.metadata


class CellTypeMeta(Base):
    __tablename__ = "cell_type_meta"

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
    cell_type__ontology_label = Column(TEXT)

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


class DonorMeta(Base):
    __tablename__ = "donor_meta"

    # ID
    id = Column(Integer, primary_key=True)
    # 性别
    sex = Column(String(255))
    # 种族
    ethnicity = Column(String(255))
    # 种族__本体__标签
    ethnicity__ontology_label = Column(TEXT)
    # 人种
    race = Column(String(255))
    # 种族__本体__标签
    race__ontology_label = Column(TEXT)
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


class MouseGene(Base):
    __tablename__ = "mouse_gene"

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


class Project(Base):
    __tablename__ = "projects"

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


class BioSample(Base):
    __tablename__ = "biosample"

    # ID
    id = Column(Integer, primary_key=True)

    donor_number = Column(INTEGER)
    # 生物样本编号
    biosample_number = Column(INTEGER)
    # 外部继承
    external_acession = Column(TEXT)
    # 生物样本类型
    biosample_type = Column(String(255))
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
    # 地理区域-本体标签
    geographical_region__ontology_label = Column(TEXT)
    # 有机体年龄
    organism_age = Column(INTEGER)
    # 有机体年龄单位
    organism_age__unit = Column(INTEGER)
    # 有机体年龄单位标签
    organism_age__unit_label = Column(TEXT)
    # TODO 鼠应变
    mouse_strain = Column(String(255))
    # TODO 鼠应变__本体_标签
    mouse_strain__ontology_label = Column(TEXT)
    # TODO 持续时间
    culture_duration = Column(INTEGER)
    # 文化持续时间__单位
    culture_duration__unit = Column(INTEGER)
    # 文化持续时间__单位标签
    culture_duration__unit_label = Column(TEXT)
    # 发展阶段
    development_stage = Column(String(255))
    # 发展阶段__本体_标签
    development_stage__ontology_label = Column(TEXT)
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
    # 疾病__治疗开始时间__单位标签
    disease__time_since_treatment_start__unit_label = Column(TEXT)
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
    # 疫苗接种__生理学_标签
    vaccination__ontology_label = Column(TEXT)
    # 疫苗接种__路线
    vaccination__route = Column(String(255))
    # 接种时间
    vaccination__time_since = Column(DateTime)
    # 接种__时间__起__单位
    vaccination__time_since__unit = Column(INTEGER)
    # 疫苗接种__时间__自__单位__标签
    vaccination__time_since__unit_label = Column(TEXT)
    # 器官
    organ = Column(String(255))
    # 器官__生理学_标签
    organ__ontology_label = Column(TEXT)
    # 器官区域
    organ_region = Column(String(255))
    # 器官区域标签
    organ_region__ontology_label = Column(TEXT)
    # 基因扰动
    gene_perturbation = Column(String(255))
    # 基因扰动__方向
    gene_perturbation__direction = Column(String(255))
    # 基因扰动动力学
    gene_perturbation__dynamics = Column(String(255))
    # 基因扰动__方法
    gene_perturbation__method = Column(String(255))
    # 基因扰动__本体_标签
    gene_perturbation__ontology_label = Column(TEXT)
    # 基因扰动__自时间
    gene_perturbation__time_since = Column(DateTime)
    # 基因扰动__时间自__单位
    gene_perturbation__time_since__unit = Column(INTEGER)
    # 基因扰动__时间自__单位标签
    gene_perturbation__time_since__unit_label = Column(TEXT)
    # 生物扰动
    biologies_perturbation = Column(String(255))
    # 生物扰动__浓度
    biologies_perturbation__concentration = Column(Double)
    # 生物扰动__浓度__单位
    biologies_perturbation__concentration__unit = Column(INTEGER)
    # 生物扰动__浓度__单位标签
    biologies_perturbation__concentration__unit_label = Column(TEXT)
    # 生物扰动__本体_标签
    biologies_perturbation__ontology_label = Column(TEXT)
    # 生物扰动__溶剂
    biologies_perturbation__solvent = Column(String(255))
    # 生物扰动__源
    biologies_perturbation__source = Column(String(255))
    # 生物扰动__开始时间
    biologies_perturbation__time_since = Column(DateTime)
    # 生物扰动__时间自__单位
    biologies_perturbation__time_since__unit = Column(INTEGER)
    # 生物扰动__自__单位时间__标签
    biologies_perturbation__time_since__unit_label = Column(TEXT)
    # 小分子扰动
    small_molecule_perturbation = Column(String(255))
    # 小分子扰动__浓度
    small_molecule_perturbation__concentration = Column(Double)
    # 小分子扰动__浓度__单位
    small_molecule_perturbation__concentration__unit = Column(INTEGER)
    # 小分子扰动__浓度__单位标签
    small_molecule_perturbation__concentration__unit_label = Column(TEXT)
    # 小分子扰动__本体__标签
    small_molecule_perturbation__ontology_label = Column(TEXT)
    # 小分子扰动__溶剂
    small_molecule_perturbation__solvent = Column(String(255))
    # 小分子扰动__源
    small_molecule_perturbation__source = Column(String(255))
    # 小分子扰动__自时间
    small_molecule_perturbation__time_since = Column(DateTime)
    # 小分子扰动__自__单位时间
    small_molecule_perturbation__time_since__unit = Column(INTEGER)
    # 小分子扰动__自__单位__时间标签
    small_molecule_perturbation__time_since__unit_label = Column(TEXT)
    # 其他扰动
    other_perturbation = Column(String(255))
    # 其他扰动__自时间
    other_perturbation__time_since = Column(DateTime)
    # 其他扰动__自__单位时间起
    other_perturbation__time_since__unit = Column(INTEGER)
    # 其他扰动__自__单位__时间标签
    other_perturbation__time_since__unit_label = Column(TEXT)
    # 富集__细胞类型
    enrichment__cell_type = Column(String(255))
    # 富集__细胞类型__本体_标签
    enrichment__cell_type__ontology_label = Column(TEXT)
    # 丰富__facs_标记
    enrichment__facs_markers = Column(String(255))
    # 浓缩方法
    enrichment_method = Column(String(255))
    # 保存方法
    preservation_method = Column(String(255))
    # 库准备协议
    library_preparation_protocol = Column(String(255))
    # 库准备协议__本体_标签
    library_preparation_protocol__ontology_label = Column(TEXT)
    # 核酸源
    nucleic_acid_source = Column(String(255))
    # sequencing_instrument_manufacturer_model
    sequencing_instrument_manufacturer_model = Column(String(255))
    # 测序仪器制造商型号__本体_标签
    sequencing_instrument_manufacturer_model__ontology_label = Column(TEXT)
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
    reference = Column(TEXT)
    # 分析协议
    analysis_protocol = Column(TEXT)

    create_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )
    donor_msg = relationship("DonorMeta")


class Species(Base):
    __tablename__ = "species"

    id = Column(Integer, primary_key=True)
    biosample_id = Column(Integer)
    # 品种
    species = Column(String(255))
    # 物种__本体_标签
    species__ontology_label = Column(TEXT)
    # 分类号
    taxon_id = Column(String(255))


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
