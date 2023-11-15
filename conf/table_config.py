from orm.db_model import cellxgene


cellxgene_table_dict = {
    "project_meta": {
        "id": cellxgene.ProjectMeta.id,
        "project_alias_id": cellxgene.ProjectMeta.project_alias_id,
        "integrated_project": cellxgene.ProjectMeta.integrated_project,
        "title": cellxgene.ProjectMeta.title,
        "donor_number": cellxgene.ProjectMeta.donor_number,
        "biosample_number": cellxgene.ProjectMeta.biosample_number,
        "external_project_accesstion": cellxgene.ProjectMeta.external_project_accesstion,
        "cell_number": cellxgene.ProjectMeta.cell_number,
        "description": cellxgene.ProjectMeta.description,
        "anatomical_entity": cellxgene.ProjectMeta.anatomical_entity,
        "release_date": cellxgene.ProjectMeta.release_date,
        "contact": cellxgene.ProjectMeta.contact,
        "publications": cellxgene.ProjectMeta.publications,
        "contributors": cellxgene.ProjectMeta.contributors,
        "collaborating_organizations": cellxgene.ProjectMeta.collaborating_organizations,
        "citation": cellxgene.ProjectMeta.citation,
        "data_curators": cellxgene.ProjectMeta.data_curators,
        "is_publish": cellxgene.ProjectMeta.is_publish,
        "is_private": cellxgene.ProjectMeta.is_private,
        "owner": cellxgene.ProjectMeta.owner,
        "tags": cellxgene.ProjectMeta.tags,
        "create_at": cellxgene.ProjectMeta.create_at,
        "update_at": cellxgene.ProjectMeta.update_at,
    },
    "biosample_meta": {
        "id": cellxgene.BioSampleMeta.id,
        "external_sample_accesstion": cellxgene.BioSampleMeta.external_sample_accesstion,
        "biosample_type": cellxgene.BioSampleMeta.biosample_type,
        "species_id": cellxgene.BioSampleMeta.species_id,
        "donor_id": cellxgene.BioSampleMeta.donor_id,
        "bmi": cellxgene.BioSampleMeta.bmi,
        "is_living": cellxgene.BioSampleMeta.is_living,
        "sample_collection_time": cellxgene.BioSampleMeta.sample_collection_time,
        "geographical_region": cellxgene.BioSampleMeta.geographical_region,
        "organism_age": cellxgene.BioSampleMeta.organism_age,
        "organism_age_unit": cellxgene.BioSampleMeta.organism_age_unit,
        "mouse_strain": cellxgene.BioSampleMeta.mouse_strain,
        "culture_duration": cellxgene.BioSampleMeta.culture_duration,
        "culture_duration_unit": cellxgene.BioSampleMeta.culture_duration_unit,
        "development_stage": cellxgene.BioSampleMeta.development_stage,
        "disease": cellxgene.BioSampleMeta.disease,
        "disease_ontology_label": cellxgene.BioSampleMeta.disease_ontology_label,
        "disease_intracellular_pathogen": cellxgene.BioSampleMeta.disease_intracellular_pathogen,
        "disease_intracellular_pathogen_ontology_label": cellxgene.BioSampleMeta.disease_intracellular_pathogen_ontology_label,
        "disease_time_since_onset": cellxgene.BioSampleMeta.disease_time_since_onset,
        "disease_time_since_onset_unit": cellxgene.BioSampleMeta.disease_time_since_onset_unit,
        "disease_time_since_onset_unit_label": cellxgene.BioSampleMeta.disease_time_since_onset_unit_label,
        "disease_time_since_treatment_start": cellxgene.BioSampleMeta.disease_time_since_treatment_start,
        "disease_time_since_treatment_start_unit": cellxgene.BioSampleMeta.disease_time_since_treatment_start_unit,
        "disease_treated": cellxgene.BioSampleMeta.disease_treated,
        "disease_treatment": cellxgene.BioSampleMeta.disease_treatment,
        "vaccination": cellxgene.BioSampleMeta.vaccination,
        "vaccination_adjuvants": cellxgene.BioSampleMeta.vaccination_adjuvants,
        "vaccination_dosage": cellxgene.BioSampleMeta.vaccination_dosage,
        "vaccination_route": cellxgene.BioSampleMeta.vaccination_route,
        "vaccination_time_since": cellxgene.BioSampleMeta.vaccination_time_since,
        "vaccination_time_since_unit": cellxgene.BioSampleMeta.vaccination_time_since_unit,
        "organ": cellxgene.BioSampleMeta.organ,
        "organ_region": cellxgene.BioSampleMeta.organ_region,
        "gene_perturbation": cellxgene.BioSampleMeta.gene_perturbation,
        "gene_perturbation_direction": cellxgene.BioSampleMeta.gene_perturbation_direction,
        "gene_perturbation_dynamics": cellxgene.BioSampleMeta.gene_perturbation_dynamics,
        "gene_perturbation_method": cellxgene.BioSampleMeta.gene_perturbation_method,
        "gene_perturbation_time_since": cellxgene.BioSampleMeta.gene_perturbation_time_since,
        "gene_perturbation_time_since_unit": cellxgene.BioSampleMeta.gene_perturbation_time_since_unit,
        "biologies_perturbation": cellxgene.BioSampleMeta.biologies_perturbation,
        "biologies_perturbation_concentration": cellxgene.BioSampleMeta.biologies_perturbation_concentration,
        "biologies_perturbation_concentration_unit": cellxgene.BioSampleMeta.biologies_perturbation_concentration_unit,
        "biologies_perturbation_solvent": cellxgene.BioSampleMeta.biologies_perturbation_solvent,
        "biologies_perturbation_source": cellxgene.BioSampleMeta.biologies_perturbation_source,
        "biologies_perturbation_time_since": cellxgene.BioSampleMeta.biologies_perturbation_time_since,
        "biologies_perturbation_time_since_unit": cellxgene.BioSampleMeta.biologies_perturbation_time_since_unit,
        "small_molecule_perturbation": cellxgene.BioSampleMeta.small_molecule_perturbation,
        "small_molecule_perturbation_concentration": cellxgene.BioSampleMeta.small_molecule_perturbation_concentration,
        "small_molecule_perturbation_concentration_unit": cellxgene.BioSampleMeta.small_molecule_perturbation_concentration_unit,
        "small_molecule_perturbation_solvent": cellxgene.BioSampleMeta.small_molecule_perturbation_solvent,
        "small_molecule_perturbation_source": cellxgene.BioSampleMeta.small_molecule_perturbation_source,
        "small_molecule_perturbation_time_since": cellxgene.BioSampleMeta.small_molecule_perturbation_time_since,
        "small_molecule_perturbation_time_since_unit": cellxgene.BioSampleMeta.small_molecule_perturbation_time_since_unit,
        "other_perturbation": cellxgene.BioSampleMeta.other_perturbation,
        "other_perturbation_time_since": cellxgene.BioSampleMeta.other_perturbation_time_since,
        "other_perturbation_time_since_unit": cellxgene.BioSampleMeta.other_perturbation_time_since_unit,
        "enrichment_cell_type": cellxgene.BioSampleMeta.enrichment_cell_type,
        "enrichment_facs_markers": cellxgene.BioSampleMeta.enrichment_facs_markers,
        "enrichment_method": cellxgene.BioSampleMeta.enrichment_method,
        "preservation_method": cellxgene.BioSampleMeta.preservation_method,
        "library_preparation_protocol": cellxgene.BioSampleMeta.library_preparation_protocol,
        "nucleic_acid_source": cellxgene.BioSampleMeta.nucleic_acid_source,
        "sequencing_instrument_manufacturer_model": cellxgene.BioSampleMeta.sequencing_instrument_manufacturer_model,
        "primer": cellxgene.BioSampleMeta.primer,
        "end_bias": cellxgene.BioSampleMeta.end_bias,
        "spike_in_concentration": cellxgene.BioSampleMeta.spike_in_concentration,
        "spike_in_kit": cellxgene.BioSampleMeta.spike_in_kit,
        "strand": cellxgene.BioSampleMeta.strand,
        "read_length": cellxgene.BioSampleMeta.read_length,
        "paired_ends": cellxgene.BioSampleMeta.paired_ends,
        "number_of_cells": cellxgene.BioSampleMeta.number_of_cells,
        "number_of_reads": cellxgene.BioSampleMeta.number_of_reads,
        "create_at": cellxgene.BioSampleMeta.create_at,
        "update_at": cellxgene.BioSampleMeta.update_at,
    },
    "analysis_meta": {
        "id": cellxgene.Analysis.id,
        "project_id": cellxgene.Analysis.project_id,
        "h5ad_id": cellxgene.Analysis.h5ad_id,
        "umap_id": cellxgene.Analysis.umap_id,
        "cell_marker_id": cellxgene.Analysis.cell_marker_id,
        "pathway_id": cellxgene.Analysis.pathway_id,
        "other_file_ids": cellxgene.Analysis.other_file_ids,
        "reference": cellxgene.Analysis.reference,
        "analysis_protocol": cellxgene.Analysis.analysis_protocol,
        "create_at": cellxgene.Analysis.create_at,
        "update_at": cellxgene.Analysis.update_at,
    },
    "cell_proportion_meta": {
        "calculated_cell_cluster_id": cellxgene.CalcCellClusterProportion.calculated_cell_cluster_id,
        "calculated_cell_cluster_alias_id": cellxgene.CalcCellClusterProportion.calculated_cell_cluster_alias_id,
        "biosample_id": cellxgene.CalcCellClusterProportion.biosample_id,
        "analysis_id": cellxgene.CalcCellClusterProportion.analysis_id,
        "cell_type_id": cellxgene.CalcCellClusterProportion.cell_type_id,
        "cell_proportion": cellxgene.CalcCellClusterProportion.cell_proportion,
        "cell_number": cellxgene.CalcCellClusterProportion.cell_number,
        "cell_cluster_method": cellxgene.CalcCellClusterProportion.cell_cluster_method,
        "create_at": cellxgene.CalcCellClusterProportion.create_at,
        "update_at": cellxgene.CalcCellClusterProportion.update_at,
    },
    "gene_expression_meta": {
        "id": cellxgene.CellClusterGeneExpression.id,
        "calculated_cell_cluster_alias_id": cellxgene.CellClusterGeneExpression.calculated_cell_cluster_alias_id,
        "cell_type_id": cellxgene.CellClusterGeneExpression.cell_type_id,
        "analysis_id": cellxgene.CellClusterGeneExpression.analysis_id,
        "gene_ensemble_id": cellxgene.CellClusterGeneExpression.gene_ensemble_id,
        "gene_symbol": cellxgene.CellClusterGeneExpression.gene_symbol,
        "average_gene_expression": cellxgene.CellClusterGeneExpression.average_gene_expression,
        "cell_proportion_expression_the_gene": cellxgene.CellClusterGeneExpression.cell_proportion_expression_the_gene,
        "cell_rank_gene_by_proportion": cellxgene.CellClusterGeneExpression.cell_rank_gene_by_proportion,
        "cell_rank_gene_by_expression": cellxgene.CellClusterGeneExpression.cell_rank_gene_by_expression,
        "gene_rank_cell_by_expression": cellxgene.CellClusterGeneExpression.gene_rank_cell_by_expression,
        "gene_rank_cell_by_proportion": cellxgene.CellClusterGeneExpression.gene_rank_cell_by_proportion,
        "suggested_surfaceome_protein_for_facs_sorting": cellxgene.CellClusterGeneExpression.suggested_surfaceome_protein_for_facs_sorting,
        "create_at": cellxgene.CellClusterGeneExpression.create_at,
        "update_at": cellxgene.CellClusterGeneExpression.update_at,
    },
    "cell_type_meta": {
        "id": cellxgene.CellTypeMeta.id,
        "cell_type_id": cellxgene.CellTypeMeta.cell_type_id,
        "species_id": cellxgene.CellTypeMeta.species_id,
        "marker_gene_symbol": cellxgene.CellTypeMeta.marker_gene_symbol,
        "cell_taxonomy_id": cellxgene.CellTypeMeta.cell_taxonomy_id,
        "cell_taxonomy_url": cellxgene.CellTypeMeta.cell_taxonomy_url,
        "cell_ontology_id": cellxgene.CellTypeMeta.cell_ontology_id,
        "cell_type_name": cellxgene.CellTypeMeta.cell_type_name,
        "cell_type_description": cellxgene.CellTypeMeta.cell_type_description,
        "cell_type_ontology_label": cellxgene.CellTypeMeta.cell_type_ontology_label,
        "create_at": cellxgene.CellTypeMeta.create_at,
        "update_at": cellxgene.CellTypeMeta.update_at,
    },
    "gene_meta": {
        "gene_ensemble_id": cellxgene.GeneMeta.gene_ensemble_id,
        "species_id": cellxgene.GeneMeta.species_id,
        "ortholog": cellxgene.GeneMeta.ortholog,
        "gene_symbol": cellxgene.GeneMeta.gene_symbol,
        "gene_name": cellxgene.GeneMeta.gene_name,
        "alias": cellxgene.GeneMeta.alias,
        "gene_ontology": cellxgene.GeneMeta.gene_ontology,
        "gpcr": cellxgene.GeneMeta.gpcr,
        "tf": cellxgene.GeneMeta.tf,
        "surfaceome": cellxgene.GeneMeta.surfaceome,
        "drugbank_drugtarget": cellxgene.GeneMeta.drugbank_drugtarget,
        "phenotype": cellxgene.GeneMeta.phenotype,
        "create_at": cellxgene.GeneMeta.create_at,
        "update_at": cellxgene.GeneMeta.update_at,
    },
}
