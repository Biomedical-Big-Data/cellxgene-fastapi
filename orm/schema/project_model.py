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
    integrated_project: int | None
    title: str | None
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
    status: int | None
    owner: int | None
    tag: str | None
    create_at: datetime
    update_at: datetime

    class Config:
        org_mode = True


class BiosampleModel(BaseModel):
    id: int
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
    create_at: datetime
    update_at: datetime

    class Config:
        org_mode = True


class AnalysisModel(BaseModel):
    id: int
    project_id: int | None
    h5ad_id: str | None
    reference: str | None
    analysis_protocol: str | None

    class Config:
        org_mode = True


class CellClusterProportionModel(BaseModel):
    id: int
    biosample_id: int | None
    analysis_id: int | None
    cell_type_id: int | None
    cell_proportion: float | None
    cell_number: int | None
    cell_cluster_method: str | None
    create_at: datetime
    update_at: datetime

    class Config:
        org_mode = True


class CellClusterGeneExpressionModel(BaseModel):
    id: int
    calculated_cell_cluster_id: int | None
    gene_id: int | None
    gene_symbol: str | None
    average_gene_expression: float | None
    cell_proportion_expression_the_gene: float | None
    cell_rank_gene_by_proportion: int | None
    cell_rank_gene_by_expression: int | None
    gene_rank_cell_by_expression: int | None
    gene_rank_cell_by_proportion: int | None
    suggested_surfaceome_protein_for_facs_sorting: str | None
    create_at: datetime
    update_at: datetime

    class Config:
        org_mode = True


class CellTypeModel(BaseModel):
    id: int
    species_id: int
    marker_gene_symbol: str | None
    cell_taxonomy_id: int | None
    cell_taxonomy_url: str | None
    cell_ontology_id: int | None
    cell_type_name: str | None
    cell_type_description: str | None
    cell_type_ontology_label: str | None
    create_at: datetime
    update_at: datetime

    class Config:
        org_mode = True


class GeneExpression(BaseModel):
    id: int
    calculated_cell_cluster_id: int
    gene_id: int | None
    gene_symbol: str | None
    average_gene_expression: float | None
    cell_proportion_expression_the_gene: float | None
    cell_rank_gene_by_proportion: int | None
    cell_rank_gene_by_expression: int | None
    gene_rank_cell_by_expression: int | None
    gene_rank_cell_by_proportion: int | None
    suggested_surfaceome_protein_for_facs_sorting: str | None
    create_at: datetime
    update_at: datetime

    class Config:
        org_mode = True


class GeneModel(BaseModel):
    id: int
    species_id: int
    ortholog: str | None
    gene_symbol: str | None
    gene_name: str | None
    alias: str | None
    gene_ontology: str | None
    GPCR: str | None
    TF: str | None
    surfaceome: str | None
    drugbank_drugtarget: str | None
    phenotype: str | None
    create_at: datetime
    update_at: datetime

    class Config:
        org_mode = True


if __name__ == "__main__":
    a = BiosampleModel()
    print(a.keys())
