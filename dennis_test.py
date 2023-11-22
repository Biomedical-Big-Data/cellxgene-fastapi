import pandas as pd
import json
import numpy as np
from sqlalchemy import literal, null
from sqlalchemy.orm import Session, aliased

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
    crud.create_gene_for_transaction(db=next(get_db()), insert_gene_model_list=insert_gene_model_list)


def import_relation_json():
    with open(
        "/Users/dennis/Documents/celltype_relationship.json", "r", encoding="utf-8"
    ) as f:
        content = json.load(f)
    # print(content)
    insert_list = []
    for ct_dict in content:
        # print(ct_dict)
        insert_list.append(
            cellxgene.CellTaxonomyRelation(
                cl_id=ct_dict["id"],
                cl_pid=ct_dict.get("pId", ""),
                name=ct_dict.get("name", ""),
            )
        )
    print(insert_list)
    crud.create_cell_taxonomy_relation(db=next(get_db()), insert_model_list=insert_list)


def get_relation():
    with open("./conf/celltype_relationship.json", "r", encoding="utf-8") as f:
        total_relation_list = json.load(f)
    # print(content)
    filter_list = [
        cellxgene.CellTaxonomy.specific_cell_ontology_id
        == cellxgene.CellTaxonomyRelation.cl_id,
        cellxgene.CellTaxonomy.cell_marker == "Lgals7",
    ]
    # crud.get_cell_taxonomy_relation_test1(db=next(get_db()), query_list=[], filters=filter_list)
    # print(res)
    cell_taxonomy_relation_model_list = crud.get_cell_taxonomy_relation(
        db=next(get_db()),
        query_list=[cellxgene.CellTaxonomyRelation],
        filters=filter_list,
    ).all()
    res = []
    for cell_taxonomy_relation_model in cell_taxonomy_relation_model_list:
        relation_dict = {"cl_id": cell_taxonomy_relation_model.cl_id}
        parent_dict = get_parent_id(
            total_relation_list, cell_taxonomy_relation_model.cl_id, {}
        )
        relation_dict["parent_dict"] = parent_dict
        res.append(relation_dict)
    print(res)
    # print(len(res))
    # for i in res:
    #     # print(i.cl_id, i.cl_pid, i.name, i.parents)
    #     for j in i.parent:
    #         print(i.cl_id, i.cl_pid, j.cl_id, j.cl_pid, j.name)
    #     print('------')


# def get_parent_id(relation_list, cl_id, parent_dict):
#     for i in relation_list:
#         if i.get("id") == cl_id:
#             parent_dict["cl_id"] = i.get("id")
#             parent_dict["parent_dict"] = {}
#             get_parent_id(relation_list, i.get("pId"), parent_dict["parent_dict"])
#         if i.get("id") == "CL:0000000":
#             return parent_dict


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


def create_cell_type_meta(db: Session):
    file_path = "/Users/dennis/Documents/cell_type.csv"
    file_data_df = pd.read_csv(file_path)
    file_data_df = file_data_df.replace(np.nan, None)
    # print(file_data_df)
    species_meta_list = crud.get_species_list(
        db=db, query_list=[cellxgene.SpeciesMeta], filters=[]
    )
    species_dict = {}
    for species_meta in species_meta_list:
        species_dict[species_meta.species] = species_meta.id
    print(species_dict)
    insert_list = []
    for _, row in file_data_df.iterrows():
        cell_type_id = row["ct_id"]
        species_id = species_dict.get(row["species"])
        marker_gene_symbol_list = row["marker_gene_symbol"].split(',')
        marker_gene_symbol_list = list(set(marker_gene_symbol_list))
        marker_gene_symbol = ','.join(marker_gene_symbol_list)
        cell_taxonomy_id = row["ct_id"]
        cell_taxonomy_url = (
            "https://ngdc.cncb.ac.cn/celltaxonomy/celltype/" + row["ct_id"]
        )
        cell_ontology_id = row["specific_cell_ontology_id"]
        cell_type_name = row["cell_standard"]
        insert_list.append(
            cellxgene.CellTypeMeta(
                cell_type_id=cell_type_id,
                species_id=species_id,
                marker_gene_symbol=marker_gene_symbol,
                cell_taxonomy_id=cell_taxonomy_id,
                cell_taxonomy_url=cell_taxonomy_url,
                cell_ontology_id=cell_ontology_id,
                cell_type_name=cell_type_name,
            )
        )
    print(len(insert_list))
    crud.create_cell_type_meta(db=db, insert_cell_type_model_list=insert_list)


def cell_taxonomy_tree(db: Session):
    from conf import config
    from sqlalchemy import and_, or_, distinct, func

    proportion_filter_list = [
        cellxgene.ProjectMeta.is_private == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
        cellxgene.ProjectMeta.is_publish
        == config.ProjectStatus.PROJECT_STATUS_IS_PUBLISH,
        cellxgene.ProjectMeta.id == cellxgene.Analysis.project_id,
        cellxgene.Analysis.id == cellxgene.CalcCellClusterProportion.analysis_id,
    ]
    cell_proportion_list = (
        crud.get_cell_proportion(
            db=db,
            query_list=[
                cellxgene.CalcCellClusterProportion.cell_type_id,
                func.sum(cellxgene.CalcCellClusterProportion.cell_number),
            ],
            filters=proportion_filter_list,
        )
        .group_by(cellxgene.CalcCellClusterProportion.cell_type_id)
        .all()
    )
    cell_type_meta_list = (
        crud.get_cell_type_meta(
            db=db,
            query_list=[
                cellxgene.CellTypeMeta.cell_type_id,
                cellxgene.CellTypeMeta.cell_ontology_id,
            ],
            filters=[],
        )
        .distinct()
        .all()
    )
    cell_type_meta_dict = {}
    for cell_type_meta in cell_type_meta_list:
        cell_type_meta_dict[
            cell_type_meta.cell_type_id
        ] = cell_type_meta.cell_ontology_id
    # print(cell_type_meta_dict)
    cell_taxonomy_relation_model_list = crud.get_cell_taxonomy_relation_tree(
        db=db, filters=[]
    )
    cell_taxonomy_relation_list = []
    cell_proportion_dict = {}
    for cell_taxonomy_relation_model in cell_taxonomy_relation_model_list:
        cell_taxonomy_relation_list.append(
            {
                "cl_id": cell_taxonomy_relation_model[0],
                "cl_pid": cell_taxonomy_relation_model[2],
                "name": cell_taxonomy_relation_model[1],
            }
        )
    # print(cell_proportion_list)
    for cell_proportion_meta in cell_proportion_list:
        cl_id = cell_type_meta_dict.get(cell_proportion_meta[0])
        cell_number = cell_proportion_meta[1]
        # print("cl_id", cl_id, cell_number)
        get_parent_id(
            cell_taxonomy_relation_list, cl_id, cell_number, cell_proportion_dict
        )
        # print('------', cell_proportion_dict)
    # print(cell_proportion_dict)
    for i in range(0, len(cell_taxonomy_relation_list)):
        cell_taxonomy_relation_list[i]["cell_number"] = cell_proportion_dict.get(
            cell_taxonomy_relation_list[i]["cl_id"], 0
        )
    print(cell_taxonomy_relation_list)


def get_parent_id(relation_list, cl_id, cell_number, parent_dict):
    for i in relation_list:
        if i.get("cl_id") == cl_id:
            # print("parent", i.get("cl_id"), i.get("cl_pid"), cell_number)
            # print(type(parent_dict), parent_dict)
            if cl_id not in parent_dict.keys():
                parent_dict[cl_id] = {}
                parent_dict[cl_id] = cell_number
            else:
                parent_dict[cl_id] += cell_number
            if i.get("cl_pid") == "CL:0000000":
                if "CL:0000000" not in parent_dict.keys():
                    parent_dict["CL:0000000"] = {}
                    parent_dict["CL:0000000"] = cell_number
                else:
                    parent_dict["CL:0000000"] += cell_number
                break
            get_parent_id(relation_list, i.get("cl_pid"), cell_number, parent_dict)


def get_file_name(db: Session, excel_id: str):
    file_name = crud.get_file_info(db=db, query_list=[cellxgene.FileLibrary], filters=[cellxgene.FileLibrary.file_id == excel_id]).first().file_name
    print(file_name)


if __name__ == "__main__":
    pass
    # get_file_name(db=next(get_db()), excel_id='84bb8e668bfb4323819ca89abc0b0137.xlsx')
    # cell_taxonomy_tree(next(get_db()))
    create_cell_type_meta(next(get_db()))
    # get_relation()
    # import_relation_json()
    # excel_test()
    # read_update_file(next(get_db()))
    # read_cell_txt()
    # read_excel()
    # dennis_test()
