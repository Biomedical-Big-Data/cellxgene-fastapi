import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from orm.db_model import cellxgene
from orm import crud
from orm.dependencies import get_db
from orm.schema import project_model


def read_cell_txt():
    insert_taxonomy_model_list = []
    write_count = 1000
    with open("E:\\download\\cell.txt", "rb") as file:
        for line in file.readlines():
            # print(line)
            cell_taxonomy_list = line.decode().split("\t")
            # print(cell_taxonomy_list)
            insert_taxonomy_model_list.append(
                cellxgene.CellTaxonomy(
                    species=cell_taxonomy_list[0],
                    tissue_uberonontology_id=cell_taxonomy_list[1],
                    tissue_standard=cell_taxonomy_list[2],
                    ct_id=cell_taxonomy_list[3],
                    cell_standard=cell_taxonomy_list[4],
                    specific_cell_ontology_id=cell_taxonomy_list[5],
                    cell_marker=cell_taxonomy_list[6],
                    gene_entrezid=cell_taxonomy_list[7],
                    gene_alias=cell_taxonomy_list[8],
                    gene_ensemble_id=cell_taxonomy_list[9],
                    uniprot=cell_taxonomy_list[10],
                    pfam=cell_taxonomy_list[11],
                    go2=cell_taxonomy_list[12],
                    condition=cell_taxonomy_list[13],
                    disease_ontology_id=cell_taxonomy_list[14],
                    pmid=cell_taxonomy_list[15],
                    source=cell_taxonomy_list[16],
                    species_tax_id=cell_taxonomy_list[17],
                    species_alias=cell_taxonomy_list[18],
                    cell_alias_change=cell_taxonomy_list[19].replace("\n", ""),
                )
            )
    # print(len(insert_taxonomy_model_list))
    insert_count = int(len(insert_taxonomy_model_list) / write_count)
    # for i in range(1, insert_count):
    #     print(i, len(insert_taxonomy_model_list[write_count * (i - 1): write_count * i]))
    #     crud.create_taxonomy(db=next(get_db()), insert_taxonomy_model_list=insert_taxonomy_model_list[write_count * (i - 1): write_count * i])
    crud.create_taxonomy(
        db=next(get_db()),
        insert_taxonomy_model_list=insert_taxonomy_model_list[
            write_count * (insert_count - 1) : write_count * insert_count
        ],
    )


def read_excel():
    types = {
        "Gene_EnsembleID": str,
        "ortholog_human": str,
        "gene_symbol": str,
        "alias": str,
        "GPCR": str,
        "TF": str,
        "surfaceome": str,
        "drugbank_drugtarget": str,
        "phenotype": str,
    }
    excel_df = pd.read_excel(
        "C:\\Users\\yzw\\Documents\\WeChat Files\\wxid_5350063500712\\FileStorage\\File\\2023-08\\GeneTable.xlsx",
        sheet_name="Human gene table",
        dtype=types,
    )
    # print(excel_df)
    excel_df.fillna("", inplace=True)
    insert_gene_model_list = []
    for _, row in excel_df.iterrows():
        print(type(row["gene_name"]), row["gene_name"])
        insert_gene_model_list.append(
            cellxgene.GeneMeta(
                gene_ensemble_id=row["Gene_EnsembleID"],
                species_id=1,
                ortholog=None if not row["ortholog_human"] else row["ortholog_human"],
                gene_symbol=row["gene_symbol"],
                gene_name=None if row["gene_name"] == "NULL" else row["gene_name"],
                alias=None if row["alias"] == "NULL" else row["alias"],
                gene_ontology=None if row["alias"] == "NULL" else row["alias"],
                gpcr=None if row["GPCR"] == "NULL" else row["GPCR"],
                tf=None if row["TF"] == "NULL" else row["TF"],
                surfaceome=None if row["surfaceome"] == "NULL" else row["surfaceome"],
                drugbank_drugtarget=None
                if row["drugbank_drugtarget"] == "NULL"
                else row["drugbank_drugtarget"],
                phenotype=None if row["phenotype"] == "NULL" else row["phenotype"],
            )
        )
    crud.create_gene(db=next(get_db()), insert_gene_model_list=insert_gene_model_list)


def read_update_file(db: Session):
    analysis_id = 1
    excel_df = pd.ExcelFile("D:\\项目文档\\cellxgene\\项目更新.xlsx")
    project_df = excel_df.parse("project_meta")
    biosample_df = excel_df.parse("biosample_meta")
    cell_proportion_df = excel_df.parse("calc_cell_cluster_proportion")
    gene_expression_df = excel_df.parse("cell_cluster_gene_expression")
    project_df = project_df.replace(np.nan, None)
    print(project_df)
    biosample_df = biosample_df.replace(np.nan, None)
    cell_proportion_df = cell_proportion_df.replace(np.nan, None)
    gene_expression_df = gene_expression_df.replace(np.nan, None)
    # print(project_df.to_dict('records')[0])
    try:
        update_project_dict = project_df.to_dict("records")[0]
        project_id = update_project_dict.get("id")
        analysis_id_info = crud.get_analysis(
            db=db,
            filters=[
                cellxgene.Analysis.id == analysis_id,
                cellxgene.Analysis.project_id == project_id,
            ],
        ).first()
        if not analysis_id_info:
            print("该analysis_id和project_id不存在关联")
            return
        update_project_filter_list = [cellxgene.ProjectMeta.id == project_id]
        crud.update_project_for_transaction(
            db=db, filters=update_project_filter_list, update_dict=update_project_dict
        )
        (
            insert_biosample_model_list,
            check_biosample_id_list,
            check_insert_biosample_id_list,
            update_biosample_id_list,
        ) = ([], [], [], [])
        insert_project_biosample_model_list, insert_biosample_analysis_model_list = (
            [],
            [],
        )
        (
            insert_cell_proportion_model_list,
            check_cell_proportion_id_list,
            check_insert_cell_proportion_id_list,
        ) = ([], [], [])
        insert_gene_expression_model_list = []
        for _, row in biosample_df.iterrows():
            biosample_meta = project_model.BiosampleModel(**row.to_dict())
            check_biosample_id_list.append(biosample_meta.id)
            # print(str(biosample_meta['id']).isdigit())
            if type(biosample_meta.id == str):
                check_insert_biosample_id_list.append(str(biosample_meta["id"]))
                insert_biosample_model_list.append(
                    cellxgene.BioSampleMeta(
                        external_sample_accesstion=biosample_meta[
                            "external_sample_accesstion"
                        ],
                        biosample_type=biosample_meta["biosample_type"],
                        species_id=biosample_meta["species_id"],
                        donor_id=biosample_meta["donor_id"],
                        bmi=biosample_meta["bmi"],
                        is_living=biosample_meta["is_living"],
                        sample_collection_time=biosample_meta["sample_collection_time"],
                        geographical_region=biosample_meta["geographical_region"],
                        organism_age=biosample_meta["organism_age"],
                        organism_age_unit=biosample_meta["organism_age_unit"],
                        mouse_strain=biosample_meta["mouse_strain"],
                        culture_duration=biosample_meta["culture_duration"],
                        culture_duration_unit=biosample_meta["culture_duration_unit"],
                        development_stage=biosample_meta["development_stage"],
                        disease=biosample_meta["disease"],
                        disease_ontology_label=biosample_meta["disease_ontology_label"],
                        disease_intracellular_pathogen=biosample_meta[
                            "disease_intracellular_pathogen"
                        ],
                        disease_intracellular_pathogen_ontology_label=biosample_meta[
                            "disease_intracellular_pathogen_ontology_label"
                        ],
                        disease_time_since_onset=biosample_meta[
                            "disease_time_since_onset"
                        ],
                        disease_time_since_onset_unit=biosample_meta[
                            "disease_time_since_onset_unit"
                        ],
                        disease_time_since_onset_unit_label=biosample_meta[
                            "disease_time_since_onset_unit_label"
                        ],
                        disease_time_since_treatment_start=biosample_meta[
                            "disease_time_since_treatment_start"
                        ],
                        disease_time_since_treatment_start_unit=biosample_meta[
                            "disease_time_since_treatment_start_unit"
                        ],
                        disease_treated=biosample_meta["disease_treated"],
                        disease_treatment=biosample_meta["disease_treatment"],
                        vaccination=biosample_meta["vaccination"],
                        vaccination_adjuvants=biosample_meta["vaccination_adjuvants"],
                        vaccination_dosage=biosample_meta["vaccination_dosage"],
                        vaccination_route=biosample_meta["vaccination_route"],
                        vaccination_time_since=biosample_meta["vaccination_time_since"],
                        vaccination_time_since_unit=biosample_meta[
                            "vaccination_time_since_unit"
                        ],
                        organ=biosample_meta["organ"],
                        organ_region=biosample_meta["organ_region"],
                        gene_perturbation=biosample_meta["gene_perturbation"],
                        gene_perturbation_direction=biosample_meta[
                            "gene_perturbation_direction"
                        ],
                        gene_perturbation_dynamics=biosample_meta[
                            "gene_perturbation_dynamics"
                        ],
                        gene_perturbation_method=biosample_meta[
                            "gene_perturbation_method"
                        ],
                        gene_perturbation_time_since=biosample_meta[
                            "gene_perturbation_time_since"
                        ],
                        gene_perturbation_time_since_unit=biosample_meta[
                            "gene_perturbation_time_since_unit"
                        ],
                        biologies_perturbation=biosample_meta["biologies_perturbation"],
                        biologies_perturbation_concentration=biosample_meta[
                            "biologies_perturbation_concentration"
                        ],
                        biologies_perturbation_concentration_unit=biosample_meta[
                            "biologies_perturbation_concentration_unit"
                        ],
                        biologies_perturbation_solvent=biosample_meta[
                            "biologies_perturbation_solvent"
                        ],
                        biologies_perturbation_source=biosample_meta[
                            "biologies_perturbation_source"
                        ],
                        biologies_perturbation_time_since=biosample_meta[
                            "biologies_perturbation_time_since"
                        ],
                        biologies_perturbation_time_since_unit=biosample_meta[
                            "biologies_perturbation_time_since_unit"
                        ],
                        small_molecule_perturbation=biosample_meta[
                            "small_molecule_perturbation"
                        ],
                        small_molecule_perturbation_concentration=biosample_meta[
                            "small_molecule_perturbation_concentration"
                        ],
                        small_molecule_perturbation_concentration_unit=biosample_meta[
                            "small_molecule_perturbation_concentration_unit"
                        ],
                        small_molecule_perturbation_solvent=biosample_meta[
                            "small_molecule_perturbation_solvent"
                        ],
                        small_molecule_perturbation_source=biosample_meta[
                            "small_molecule_perturbation_source"
                        ],
                        small_molecule_perturbation_time_since=biosample_meta[
                            "small_molecule_perturbation_time_since"
                        ],
                        small_molecule_perturbation_time_since_unit=biosample_meta[
                            "small_molecule_perturbation_time_since_unit"
                        ],
                        other_perturbation=biosample_meta["other_perturbation"],
                        other_perturbation_time_since=biosample_meta[
                            "other_perturbation_time_since"
                        ],
                        other_perturbation_time_since_unit=biosample_meta[
                            "other_perturbation_time_since_unit"
                        ],
                        enrichment_cell_type=biosample_meta["enrichment_cell_type"],
                        enrichment_facs_markers=biosample_meta[
                            "enrichment_facs_markers"
                        ],
                        enrichment_method=biosample_meta["enrichment_method"],
                        preservation_method=biosample_meta["preservation_method"],
                        library_preparation_protocol=biosample_meta[
                            "library_preparation_protocol"
                        ],
                        nucleic_acid_source=biosample_meta["nucleic_acid_source"],
                        sequencing_instrument_manufacturer_model=biosample_meta[
                            "sequencing_instrument_manufacturer_model"
                        ],
                        primer=biosample_meta["primer"],
                        end_bias=biosample_meta["end_bias"],
                        spike_in_concentration=biosample_meta["spike_in_concentration"],
                        spike_in_kit=biosample_meta["spike_in_kit"],
                        strand=biosample_meta["strand"],
                        read_length=biosample_meta["read_length"],
                        paired_ends=biosample_meta["paired_ends"],
                        number_of_cells=biosample_meta["number_of_cells"],
                        number_of_reads=biosample_meta["number_of_reads"],
                    )
                )
            else:
                print('1111')
                check_biosample_meta = crud.get_biosample(
                    db=db, filters=[cellxgene.BioSampleMeta.id == biosample_meta["id"]]
                )
                if not check_biosample_meta:
                    return "biosample id 不存在"
                update_biosample_id_list.append(int(biosample_meta["id"]))
                crud.update_biosample_for_transaction(
                    db=db,
                    filters=[cellxgene.BioSampleMeta.id == biosample_meta["id"]],
                    update_dict=biosample_meta.to_dict(),
                )
        inserted_biosample_id_list = crud.create_biosample_for_transaction(
            db=db, insert_biosample_model_list=insert_biosample_model_list
        )
        inserted_biosample_id_dict = dict(
            zip(check_insert_biosample_id_list, inserted_biosample_id_list)
        )
        inserted_biosample_id_list.extend(update_biosample_id_list)
        print(inserted_biosample_id_list)
        for inserted_biosample_id in inserted_biosample_id_list:
            insert_project_biosample_model_list.append(
                cellxgene.ProjectBioSample(
                    project_id=project_id, biosample_id=inserted_biosample_id
                )
            )
            insert_biosample_analysis_model_list.append(
                cellxgene.BioSampleAnalysis(
                    biosample_id=inserted_biosample_id, analysis_id=analysis_id
                )
            )
        need_delete_biosample_model_list = crud.get_project_biosample(
            db=db, filters=[cellxgene.ProjectBioSample.project_id == project_id]
        ).all()
        need_delete_biosample_id_list = []
        for need_delete_biosample_model in need_delete_biosample_model_list:
            need_delete_biosample_id_list.append(
                need_delete_biosample_model.biosample_id
            )
        print(need_delete_biosample_id_list)
        crud.delete_project_biosample_for_transaction(
            db=db, filters=[cellxgene.ProjectBioSample.project_id == project_id]
        )
        crud.create_project_biosample_for_transaction(
            db=db,
            insert_project_biosample_model_list=insert_project_biosample_model_list,
        )
        crud.delete_biosample_analysis_for_transaction(
            db=db,
            filters=[
                cellxgene.BioSampleAnalysis.analysis_id == analysis_id,
                cellxgene.BioSampleAnalysis.biosample_id.in_(
                    need_delete_biosample_id_list
                ),
            ],
        )
        crud.create_biosample_analysis_for_transaction(
            db=db, insert_biosample_analysis_list=insert_biosample_analysis_model_list
        )
        for _, cell_proportion_meta in cell_proportion_df.iterrows():
            check_cell_proportion_id_list.append(
                cell_proportion_meta.get("calculated_cell_cluster_id")
            )
            if cell_proportion_meta.get("biosample_id") not in check_biosample_id_list:
                print("请选择biosample_meta中存在的biosample_id")
            if not cell_proportion_meta.get("calculated_cell_cluster_id").isdigit():
                check_insert_cell_proportion_id_list.append(
                    cell_proportion_meta.get("calculated_cell_cluster_id")
                )
                insert_cell_proportion_model_list.append(
                    cellxgene.CalcCellClusterProportion(
                        biosample_id=cell_proportion_meta.get("biosample_id")
                        if cell_proportion_meta.get("biosample_id").isdigit()
                        else inserted_biosample_id_dict.get(
                            cell_proportion_meta.get("biosample_id")
                        ),
                        analysis_id=analysis_id,
                        cell_type_id=cell_proportion_meta.get("cell_type_id"),
                        cell_proportion=cell_proportion_meta.get("cell_proportion"),
                        cell_number=cell_proportion_meta.get("cell_number"),
                        cell_cluster_method=cell_proportion_meta.get(
                            "cell_cluster_method"
                        ),
                    )
                )
            else:
                check_cell_proportion_meta = crud.get_cell_proportion(
                    db=db,
                    filters=[
                        cellxgene.CalcCellClusterProportion.calculated_cell_cluster_id
                        == cell_proportion_meta["calculated_cell_cluster_id"]
                    ],
                )
                if not check_cell_proportion_meta:
                    return "cell proportion id 不存在"
                crud.update_cell_proportion_for_transaction(
                    db=db,
                    filters=[
                        cellxgene.CalcCellClusterProportion.calculated_cell_cluster_id
                        == cell_proportion_meta["calculated_cell_cluster_id"]
                    ],
                    update_dict=cell_proportion_meta.to_dict(),
                )
        inserted_cell_proportion_id_list = crud.create_cell_proprotion_for_transaction(
            db=db, insert_cell_proportion_model_list=insert_cell_proportion_model_list
        )
        inserted_cell_proportion_id_dict = dict(
            zip(check_insert_cell_proportion_id_list, inserted_cell_proportion_id_list)
        )
        for _, gene_expression_meta in gene_expression_df.iterrows():
            if not gene_expression_meta["gene_expression_id"].isdigit():
                insert_gene_expression_model_list.append(
                    cellxgene.CellClusterGeneExpression(
                        calculated_cell_cluster_id=gene_expression_meta.get(
                            "calculated_cell_cluster_id"
                        )
                        if gene_expression_meta.get(
                            "calculated_cell_cluster_id"
                        ).isdigit()
                        else inserted_cell_proportion_id_dict.get(
                            gene_expression_meta.get("calculated_cell_cluster_id")
                        ),
                        gene_id=gene_expression_meta["gene_id"],
                        gene_symbol=gene_expression_meta["gene_symbol"],
                        average_gene_expression=gene_expression_meta[
                            "average_gene_expression"
                        ],
                        cell_proportion_expression_the_gene=gene_expression_meta[
                            "cell_proportion_expression_the_gene"
                        ],
                        cell_rank_gene_by_proportion=gene_expression_meta[
                            "cell_rank_gene_by_proportion"
                        ],
                        cell_rank_gene_by_expression=gene_expression_meta[
                            "cell_rank_gene_by_expression"
                        ],
                        gene_rank_cell_by_expression=gene_expression_meta[
                            "gene_rank_cell_by_expression"
                        ],
                        gene_rank_cell_by_proportion=gene_expression_meta[
                            "gene_rank_cell_by_proportion"
                        ],
                        suggested_surfaceome_protein_for_facs_sorting=gene_expression_meta[
                            "suggested_surfaceome_protein_for_facs_sorting"
                        ],
                    )
                )
            else:
                check_gene_expression_meta = crud.get_gene_expression(
                    db=db,
                    filters=[
                        cellxgene.CellClusterGeneExpression.id
                        == gene_expression_meta.get("gene_expression_id"),
                        gene_expression_meta["gene_expression_id"],
                    ],
                )
                if not check_gene_expression_meta:
                    return "gene expression id 不存在"
                crud.update_gene_expression_for_transaction(
                    db=db,
                    filters=[
                        cellxgene.CellClusterGeneExpression.id
                        == gene_expression_meta["gene_expression_id"]
                    ],
                    update_dict=gene_expression_meta.to_dict(),
                )
        if insert_gene_expression_model_list:
            crud.create_gene_expression_for_transaction(
                db=db,
                insert_gene_expression_model_list=insert_gene_expression_model_list,
            )
    except Exception as e:
        print(e)
    else:
        db.commit()


def dennis_test():
    a = "c1"
    if a.isalnum():
        print("111")
    else:
        print("2222")


def excel_test():
    import openpyxl

    wb = openpyxl.load_workbook("D:\\项目文档\\cellxgene\\项目更新.xlsx")  # 获取表格文件对象
    # 指定表单（sheet）
    project_meta_sheet = wb["project_meta"]
    project_meta_list = list(project_meta_sheet.values)
    print(type(project_meta_list), project_meta_list)
    for i in range(1, len(project_meta_list)):
        print(type(project_meta_list[i]), project_meta_list[i])
        project_meta = cellxgene.ProjectMeta(project_meta_list[i])
        print(project_meta)


if __name__ == "__main__":
    # excel_test()
    read_update_file(next(get_db()))
    # read_cell_txt()
    # read_excel()
    # dennis_test()
