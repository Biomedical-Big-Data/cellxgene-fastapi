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
            check_insert_biosample_id_list,
            update_biosample_id_list,
        ) = ([], [], [])
        insert_project_biosample_model_list, insert_biosample_analysis_model_list = (
            [],
            [],
        )
        (
            insert_cell_proportion_model_list,
            check_insert_cell_proportion_id_list,
        ) = ([], [])
        insert_gene_expression_model_list = []
        for _, row in biosample_df.iterrows():
            biosample_meta = project_model.BiosampleModel(**row.to_dict())
            if type(biosample_meta.id) == str:
                check_insert_biosample_id_list.append(biosample_meta.id)
                insert_biosample_model_list.append(
                    cellxgene.BioSampleMeta(**biosample_meta.model_dump(mode="json", exclude={"id"}, exclude_none=True))
                )
            else:
                check_biosample_meta = crud.get_biosample(
                    db=db, filters=[cellxgene.BioSampleMeta.id == biosample_meta.id]
                )
                if not check_biosample_meta:
                    return "biosample id 不存在"
                update_biosample_id_list.append(biosample_meta.id)
                crud.update_biosample_for_transaction(
                    db=db,
                    filters=[cellxgene.BioSampleMeta.id == biosample_meta.id],
                    update_dict=biosample_meta.model_dump(mode="json", exclude_none=True),
                )
        inserted_biosample_id_list = crud.create_biosample_for_transaction(
            db=db, insert_biosample_model_list=insert_biosample_model_list
        )
        inserted_biosample_id_dict = dict(
            zip(check_insert_biosample_id_list, inserted_biosample_id_list)
        )
        inserted_biosample_id_list.extend(update_biosample_id_list)
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
                cellxgene.ProjectBioSample.project_id == project_id,
                cellxgene.BioSampleAnalysis.biosample_id == cellxgene.ProjectBioSample.biosample_id,
            ],
        )
        crud.create_biosample_analysis_for_transaction(
            db=db, insert_biosample_analysis_list=insert_biosample_analysis_model_list
        )
        for _, row in cell_proportion_df.iterrows():
            cell_proportion_meta = project_model.CellClusterProportionModel(**row.to_dict())
            cell_proportion_meta.biosample_id = cell_proportion_meta.biosample_id if type(cell_proportion_meta.biosample_id) == int else int(inserted_biosample_id_dict.get(cell_proportion_meta.biosample_id))
            cell_proportion_meta.analysis_id = analysis_id
            if cell_proportion_meta.biosample_id not in inserted_biosample_id_list:
                print("请选择biosample_meta中存在的biosample_id")
                return
            if type(cell_proportion_meta.calculated_cell_cluster_id) == str:
                check_insert_cell_proportion_id_list.append(
                    cell_proportion_meta.calculated_cell_cluster_id
                )
                insert_cell_proportion_model_list.append(
                    cellxgene.CalcCellClusterProportion(
                        **cell_proportion_meta.model_dump(mode="json", exclude={"calculated_cell_cluster_id"}, exclude_none=True),
                        ),
                    )
            else:
                check_cell_proportion_meta = crud.get_cell_proportion(
                    db=db,
                    filters=[
                        cellxgene.CalcCellClusterProportion.calculated_cell_cluster_id
                        == cell_proportion_meta.calculated_cell_cluster_id
                    ],
                )
                if not check_cell_proportion_meta:
                    return "cell proportion id 不存在"
                crud.update_cell_proportion_for_transaction(
                    db=db,
                    filters=[
                        cellxgene.CalcCellClusterProportion.calculated_cell_cluster_id
                        == cell_proportion_meta.calculated_cell_cluster_id
                    ],
                    update_dict=cell_proportion_meta.model_dump(mode="json", exclude_none=True),
                )
        inserted_cell_proportion_id_list = crud.create_cell_proprotion_for_transaction(
            db=db, insert_cell_proportion_model_list=insert_cell_proportion_model_list
        )
        inserted_cell_proportion_id_dict = dict(
            zip(check_insert_cell_proportion_id_list, inserted_cell_proportion_id_list)
        )
        for _, row in gene_expression_df.iterrows():
            gene_expression_meta = project_model.CellClusterGeneExpressionModel(**row.to_dict())
            gene_expression_meta.calculated_cell_cluster_id = gene_expression_meta.calculated_cell_cluster_id if type(
                gene_expression_meta.calculated_cell_cluster_id) == int else int(
                inserted_cell_proportion_id_dict.get(gene_expression_meta.calculated_cell_cluster_id))
            if type(gene_expression_meta.id) == str:
                insert_gene_expression_model_list.append(
                    cellxgene.CellClusterGeneExpression(
                        **gene_expression_meta.model_dump(mode="json", exclude={"id"},
                                                          exclude_none=True),
                    )
                )
            else:
                check_gene_expression_meta = crud.get_gene_expression(
                    db=db,
                    filters=[
                        cellxgene.CellClusterGeneExpression.id
                        == gene_expression_meta.id
                    ],
                )
                if not check_gene_expression_meta:
                    return "gene expression id 不存在"
                crud.update_gene_expression_for_transaction(
                    db=db,
                    filters=[
                        cellxgene.CellClusterGeneExpression.id
                        == gene_expression_meta.id
                    ],
                    update_dict=gene_expression_meta.model_dump(mode="json", exclude_none=True),
                )
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
