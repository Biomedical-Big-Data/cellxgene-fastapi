from pydantic import BaseModel, ConfigDict
from typing import List, ClassVar
from datetime import datetime


class SpeciesModel(BaseModel):
    id: int
    species: str | None
    species_ontology_label: str | None

    class Config:
        org_mode = True


class DonorModel(BaseModel):
    id: int
    sex: str | None
    ethnicity: str | None
    race: str | None
    mhc_genotype: str | None
    alcohol_history: str | None
    medications: str | None
    nutritional_state: str | None
    smoking_history: str | None
    test_results: str | None
    create_at: datetime
    update_at: datetime

    class Config:
        org_mode = True


class ProjectModel(BaseModel):
    id: int
    project_alias_id: str | None
    integrated_project: int | None
    title: str | None
    donor_number: int | None
    biosample_number: int | None
    external_project_accesstion: str | None
    cell_number: str | None
    description: str | None
    anatomical_entity: str | None
    release_date: str | None
    contact: str | None
    publications: int | None
    contributors: int | None
    collaborating_organizations: str | None
    citation: str | None
    data_curators: str | None
    is_publish: int | None
    is_private: int | None
    owner: int | None
    tags: str | None
    create_at: datetime | None
    update_at: datetime | None

    class Config:
        org_mode = True


class BiosampleModel(BaseModel):
    id: int | str
    external_sample_accesstion: str | None
    biosample_type: str | None
    species_id: int | None
    donor_id: int | None
    bmi: float | None
    is_living: int | None
    sample_collection_time: str | None
    geographical_region: str | None
    organism_age: int | None
    organism_age_unit: int | None
    mouse_strain: str | None
    culture_duration: int | None
    culture_duration_unit: int | None
    development_stage: str | None
    disease: str | None
    disease_ontology_label: str | None
    disease_intracellular_pathogen: str | None
    disease_intracellular_pathogen_ontology_label: str | None
    disease_time_since_onset: str | None
    disease_time_since_onset_unit: int | None
    disease_time_since_onset_unit_label: str | None
    disease_time_since_treatment_start: str | None
    disease_time_since_treatment_start_unit: int | None
    disease_treated: int | None
    disease_treatment: str | None
    vaccination: str | None
    vaccination_adjuvants: str | None
    vaccination_dosage: str | None
    vaccination_route: str | None
    vaccination_time_since: str | None
    vaccination_time_since_unit: int | None
    organ: str | None
    organ_region: str | None
    gene_perturbation: str | None
    gene_perturbation_direction: str | None
    gene_perturbation_dynamics: str | None
    gene_perturbation_method: str | None
    gene_perturbation_time_since: str | None
    gene_perturbation_time_since_unit: int | None
    biologies_perturbation: str | None
    biologies_perturbation_concentration: float | None
    biologies_perturbation_concentration_unit: int | None
    biologies_perturbation_solvent: str | None
    biologies_perturbation_source: str | None
    biologies_perturbation_time_since: str | None
    biologies_perturbation_time_since_unit: int | None
    small_molecule_perturbation: str | None
    small_molecule_perturbation_concentration: float | None
    small_molecule_perturbation_concentration_unit: int | None
    small_molecule_perturbation_solvent: str | None
    small_molecule_perturbation_source: str | None
    small_molecule_perturbation_time_since: str | None
    small_molecule_perturbation_time_since_unit: int | None
    other_perturbation: str | None
    other_perturbation_time_since: str | None
    other_perturbation_time_since_unit: int | None
    enrichment_cell_type: str | None
    enrichment_facs_markers: str | None
    enrichment_method: str | None
    preservation_method: str | None
    library_preparation_protocol: str | None
    nucleic_acid_source: str | None
    sequencing_instrument_manufacturer_model: str | None
    primer: str | None
    end_bias: str | None
    spike_in_concentration: str | None
    spike_in_kit: str | None
    strand: str | None
    read_length: int | None
    paired_ends: str | None
    number_of_cells: int | None
    number_of_reads: int | None
    create_at: datetime | None = None
    update_at: datetime | None = None

    class Config:
        org_mode = True


class AnalysisModel(BaseModel):
    id: int
    project_id: int | None
    h5ad_id: str | None
    umap_id: str | None
    cell_marker_id: str | None
    pathway_id: str | None
    other_file_ids: str | None
    reference: str | None
    analysis_protocol: str | None
    create_at: datetime
    update_at: datetime

    class Config:
        org_mode = True


class CellClusterProportionModel(BaseModel):
    calculated_cell_cluster_id: int | str
    biosample_id: int | str | None
    analysis_id: int | None = None
    cell_type_id: int | None
    cell_proportion: float | None
    cell_number: int | None
    cell_cluster_method: str | None
    create_at: datetime | None = None
    update_at: datetime | None = None

    class Config:
        org_mode = True


class CellClusterGeneExpressionModel(BaseModel):
    id: int | str
    calculated_cell_cluster_id: int | str | None
    gene_ensemble_id: str | None
    gene_symbol: str | None
    average_gene_expression: float | None
    cell_proportion_expression_the_gene: float | None
    cell_rank_gene_by_proportion: int | None
    cell_rank_gene_by_expression: int | None
    gene_rank_cell_by_expression: int | None
    gene_rank_cell_by_proportion: int | None
    suggested_surfaceome_protein_for_facs_sorting: str | None
    create_at: datetime | None = None
    update_at: datetime | None = None

    class Config:
        org_mode = True


class CellTypeModel(BaseModel):
    cell_type_id: int
    cell_type_alias_id: str | None
    species_id: int
    marker_gene_symbol: str | None
    cell_taxonomy_id: str | None
    cell_taxonomy_url: str | None
    cell_ontology_id: str | None
    cell_type_name: str | None
    cell_type_description: str | None
    cell_type_ontology_label: str | None
    create_at: datetime
    update_at: datetime

    class Config:
        org_mode = True


class GeneModel(BaseModel):
    gene_ensemble_id: str
    species_id: int
    ortholog: str | None
    gene_symbol: str | None
    gene_name: str | None
    alias: str | None
    gene_ontology: str | None
    gpcr: str | None
    tf: str | None
    surfaceome: str | None
    drugbank_drugtarget: str | None
    phenotype: str | None
    create_at: datetime
    update_at: datetime

    class Config:
        org_mode = True


class CellTaxonomyModel(BaseModel):
    id: int
    species: str | None
    tissue_uberonontology_id: str | None
    tissue_standard: str | None
    ct_id: str | None
    cell_standard: str | None
    specific_cell_ontology_id: str | None
    cell_marker: str | None
    gene_entrezid: str | None
    gene_alias: str | None
    gene_ensemble_id: str | None
    uniprot: str | None
    pfam: str | None
    go2: str | None
    condition: str | None
    disease_ontology_id: str | None
    pmid: str | None
    source: str | None
    species_tax_id: str | None
    species_alias: str | None
    cell_alias_change: str | None
    create_at: datetime
    update_at: datetime

    class Config:
        org_mode = True


class FileLibraryModel(BaseModel):
    file_id: str
    file_name: str
    upload_user_id: int
    create_at: datetime
    update_at: datetime

    class Config:
        org_mode = True


class ProjectBiosampleModel(BaseModel):
    id: int
    project_id: int
    biosample_id: int

    class Config:
        org_mode = True


class BiosampleAnalysisModel(BaseModel):
    id: int
    biosample_id: int
    analysis_id: int

    class Config:
        org_mode = True


class TransferProjectModel(BaseModel):
    transfer_to_email_address: str


class CopyToProjectModel(BaseModel):
    copy_to_email_address: str


class UpdateProjectModel(BaseModel):
    project_status: int


class PathwayScoreModel(BaseModel):
    id: int
    pathway_source: str | None
    pathway_name: str | None
    species_id: int | None
    geneset_gene_symbols: str | None
    analysis_id: int | None
    biosample_id: int | None
    cell_type_name: str | None
    calculated_cell_cluster_id: int | None
    score_function: str | None
    score: float | None
    create_at: datetime
    update_at: datetime

    class Config:
        org_mode = True


class ProjectCreateModel(BaseModel):
    title: str
    description: str
    h5ad_id: str
    umap_id: str | None = None
    cell_marker_id: str | None = None
    pathway_id: str | None = None
    other_file_ids: str | None = (None,)
    tags: str
    members: list
    is_publish: int
    is_private: int
    species_id: int
    organ: str


class TransferHistoryModel(BaseModel):
    id: int
    project_id: int
    old_owner: int
    new_owner: int
    create_at: datetime
    update_at: datetime

    class Config:
        org_mode = True



if __name__ == "__main__":
    a = BiosampleModel()
    print(a.keys())
