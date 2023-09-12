import pandas as pd
import json
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


def import_relation_json():
    with open("D:\\项目文档\\cellxgene\\celltype_relationship.json", "r", encoding="utf-8") as f:
        content = json.load(f)
    # print(content)
    insert_list = []
    for ct_dict in content:
        # print(ct_dict)
        insert_list.append(cellxgene.CellTaxonomyRelation(cl_id=ct_dict['id'], cl_pid=ct_dict.get('pId', ''), name=ct_dict.get('name', '')))
    print(insert_list)
    crud.create_cell_taxonomy_relation(db=next(get_db()), insert_model_list=insert_list)


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
    pass
    import_relation_json()
    # excel_test()
    # read_update_file(next(get_db()))
    # read_cell_txt()
    # read_excel()
    # dennis_test()
