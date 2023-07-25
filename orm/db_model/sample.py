from sqlalchemy import Column, DateTime, Integer, String, text, Double, INTEGER
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base
from dataclasses import dataclass

Base = declarative_base()
metadata = Base.metadata


class BioSample(Base):
    __tablename__ = "biosample"
    __table_args__ = {"schema": "biosample"}

    # ID
    id = Column(Integer, primary_key=True)

    donor_number = Column(String(255))
    # 生物样本编号
    biosample_number = Column(String(255))
    # 外部继承
    external_acession = Column(String(255))
    # 生物样本类型
    biosample_type = Column(String(255))
    # 捐赠者 ID
    donor_id = Column(String(255))
    # bmi
    bmi = Column(DateTime)
    # 是否活体
    is_living = Column(String(255))
    # 样本收集时间
    sample_collection_time = Column(DateTime)
    # 地理区域
    geographical_region = Column(TINYINT(1))
    # 地理区域-本体标签
    geographical_region__ontology_label = Column(String(255))
    # 有机体年龄
    organism_age = Column(String(255))
    # 有机体年龄单位
    organism_age__unit = Column(String(255))
    # 有机体年龄单位标签
    organism_age__unit_label = Column(String(255))
    # TODO 鼠应变
    mouse_strain = Column(String(255))
    # TODO 鼠应变__本体_标签
    mouse_strain__ontology_label = Column(String(255))
    # TODO 持续时间
    culture_duration = Column(INTEGER)
    # 文化持续时间__单位
    culture_duration__unit = Column(String(255))
    # 文化持续时间__单位标签
    culture_duration__unit_label = Column(String(255))
    # 发展阶段
    development_stage = Column(String(255))
    # 发展阶段__本体_标签
    development_stage__ontology_label = Column(String(255))
    # 病症
    disease = Column(String(255))
    # 疾病__本体_标签
    disease__ontology_label = Column(String(255))
    # 疾病__细胞内病原体
    disease__intracellular_pathogen = Column(String(255))
    # 疾病__细胞内病原体__病理学__标签
    disease__intracellular_pathogen__ontology_label = Column(String(255))
    # 疾病__发病时间
    disease__time_since_onset = Column(INTEGER)
    # 疾病__发病时间__单位
    disease__time_since_onset__unit = Column(String(255))
    # 疾病__发病时间__单位标签
    disease__time_since_onset__unit_label = Column(String(255))
    # 疾病__治疗开始时间
    disease__time_since_treatment_start = Column(INTEGER)
    # 疾病__治疗开始时间__单位
    disease__time_since_treatment_start__unit = Column(String(255))
    # 疾病__治疗开始时间__单位标签
    disease__time_since_treatment_start__unit_label = Column(String(255))
    # 疾病__已治疗
    disease__treated = Column(String(255))
    # 疾病__治疗
    disease__treatment = Column(String(255))
    # 疫苗接种
    vaccination = Column(String(255))
    # 疫苗__佐剂
    vaccination__adjuvants = Column(String(255))
    # 疫苗接种__剂量
    vaccination__dosage = Column(String(255))
    # 疫苗接种__生理学_标签
    vaccination__ontology_label = Column(String(255))
    # 疫苗接种__路线
    vaccination__route = Column(String(255))
    # 接种时间
    vaccination__time_since = Column(String(255))
    # 接种__时间__起__单位
    vaccination__time_since__unit = Column(String(255))
    # 疫苗接种__时间__自__单位__标签
    vaccination__time_since__unit_label = Column(String(255))
    # 器官
    organ = Column(String(255))
    # 器官__生理学_标签
    organ__ontology_label = Column(String(255))
    # 器官区域
    organ_region = Column(String(255))
    # 器官区域标签
    organ_region__ontology_label = Column(String(255))
    # 基因扰动
    gene_perturbation = Column(String(255))
    # 基因扰动__方向
    gene_perturbation__direction = Column(String(255))
    # 基因扰动动力学
    gene_perturbation__dynamics = Column(String(255))
    # 基因扰动__方法
    gene_perturbation__method = Column(String(255))
    # 基因扰动__本体_标签
    gene_perturbation__ontology_label = Column(String(255))
    # 基因扰动__自时间
    gene_perturbation__time_since = Column(String(255))
    # 基因扰动__时间自__单位
    gene_perturbation__time_since__unit = Column(String(255))
    # 基因扰动__时间自__单位标签
    gene_perturbation__time_since__unit_label = Column(String(255))
    # 生物扰动
    biologies_perturbation = Column(String(255))
    # 生物扰动__浓度
    biologies_perturbation__concentration = Column(Double)
    # 生物扰动__浓度__单位
    biologies_perturbation__concentration__unit = Column(String(255))
    # 生物扰动__浓度__单位标签
    biologies_perturbation__concentration__unit_label = Column(String(255))
    # 生物扰动__本体_标签
    biologies_perturbation__ontology_label = Column(String(255))
    # 生物扰动__溶剂
    biologies_perturbation__solvent = Column(String(255))
    # 生物扰动__源
    biologies_perturbation__source = Column(String(255))
    # 生物扰动__开始时间
    biologies_perturbation__time_since = Column(String(255))
    # 生物扰动__时间自__单位
    biologies_perturbation__time_since__unit = Column(String(255))
    # 生物扰动__自__单位时间__标签
    biologies_perturbation__time_since__unit_label = Column(String(255))
    # 小分子扰动
    small_molecule_perturbation = Column(String(255))
    # 小分子扰动__浓度
    small_molecule_perturbation__concentration = Column(Double)
    # 小分子扰动__浓度__单位
    small_molecule_perturbation__concentration__unit = Column(String(255))
    # 小分子扰动__浓度__单位标签
    small_molecule_perturbation__concentration__unit_label = Column(String(255))
    # 小分子扰动__本体__标签
    small_molecule_perturbation__ontology_label = Column(String(255))
    # 小分子扰动__溶剂
    small_molecule_perturbation__solvent = Column(String(255))
    # 小分子扰动__源
    small_molecule_perturbation__source = Column(String(255))
    # 小分子扰动__自时间
    small_molecule_perturbation__time_since = Column(String(255))
    # 小分子扰动__自__单位时间
    small_molecule_perturbation__time_since__unit = Column(String(255))
    # 小分子扰动__自__单位__时间标签
    small_molecule_perturbation__time_since__unit_label = Column(String(255))
    # 其他扰动
    other_perturbation = Column(String(255))
    # 其他扰动__自时间
    other_perturbation__time_since = Column(Double)
    # 其他扰动__自__单位时间起
    other_perturbation__time_since__unit = Column(String(255))
    # 其他扰动__自__单位__时间标签
    other_perturbation__time_since__unit_label = Column(String(255))
    # 富集__细胞类型
    enrichment__cell_type = Column(String(255))
    # 富集__细胞类型__本体_标签
    enrichment__cell_type__ontology_label = Column(String(255))
    # 丰富__facs_标记
    enrichment__facs_markers = Column(String(255))
    # 浓缩方法
    enrichment_method = Column(String(255))
    # 保存方法
    preservation_method = Column(String(255))
    # 库准备协议
    library_preparation_protocol = Column(String(255))
    # 库准备协议__本体_标签
    library_preparation_protocol__ontology_label = Column(String(255))
    # 核酸源
    nucleic_acid_source = Column(String(255))
    # sequencing_instrument_manufacturer_model
    sequencing_instrument_manufacturer_model = Column(String(255))
    # 测序仪器制造商型号__本体_标签
    sequencing_instrument_manufacturer_model__ontology_label = Column(String(255))
    # 引子
    primer = Column(String(255))
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
    reference = Column(String(255))
    # 分析协议
    analysis_protocol = Column(String(255))

    create_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )


class Species(Base):
    id = Column(Integer, primary_key=True)
    biosample_id = Column(Integer)
    # 品种
    species = Column(String(255))
    # 物种__本体_标签
    species__ontology_label = Column(String(255))
    # 分类号
    taxon_id = Column(String(255))
