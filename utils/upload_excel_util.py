import time
from io import BytesIO

from sqlalchemy.orm import Session

from conf import config
from orm import crud
import pandas as pd
import numpy as np

from orm.db_model import cellxgene
from orm.schema import project_model
from orm.schema.response import ResponseMessage


def upload_file(db: Session, project_id: int, analysis_id: int, excel_id: str):
    # current_user_info = crud.get_user(
    #     db=db, filters=[cellxgene.User.email_address == current_admin_email_address]
    # )
    file_path = config.H5AD_FILE_PATH + "/" + excel_id
    with open(file_path, "rb") as file:
        project_content = file.read()
    project_excel_df = pd.ExcelFile(BytesIO(project_content))
    project_df = project_excel_df.parse("project_meta")
    biosample_df = project_excel_df.parse("biosample_meta")
    cell_proportion_df = project_excel_df.parse("calc_cell_cluster_proportion")
    gene_expression_df = project_excel_df.parse("cell_cluster_gene_expression")
    project_df = project_df.replace(np.nan, None)
    biosample_df = biosample_df.replace(np.nan, None)
    cell_proportion_df = cell_proportion_df.replace(np.nan, None)
    gene_expression_df = gene_expression_df.replace(np.nan, None)
    print(project_df)
    # cell_marker_file_id = await file_util.save_file(
    #     db=db,
    #     file=cell_marker_file,
    #     insert_user_id=current_user_info.id,
    #     insert=False,
    # )
    # umap_file_id = await file_util.save_file(
    #     db=db, file=umap_file, insert_user_id=current_user_info.id, insert=False
    # )
    # crud.update_analysis_for_transaction(
    #     db=db,
    #     filters=[cellxgene.Analysis.id == analysis_id],
    #     update_dict={
    #         "umap_id": umap_file_id,
    #         "cell_marker_id": cell_marker_file_id,
    #     },
    # )
    update_project_dict = project_df.to_dict("records")[0]
    analysis_id_info = crud.get_analysis(
        db=db,
        filters=[
            cellxgene.Analysis.id == analysis_id,
            cellxgene.Analysis.project_id == project_id,
        ],
    ).first()
    if not analysis_id_info:
        return ResponseMessage(
            status="0201", data={}, message="该analysis_id和project_id不存在关联"
        )
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
                cellxgene.BioSampleMeta(
                    **biosample_meta.model_dump(
                        mode="json", exclude={"id"}, exclude_none=True
                    )
                )
            )
        else:
            check_biosample_meta = crud.get_biosample(
                db=db,
                query_list=[cellxgene.BioSampleMeta],
                filters=[cellxgene.BioSampleMeta.id == biosample_meta.id],
            )
            if not check_biosample_meta:
                return ResponseMessage(
                    status="0201", data={}, message="biosample id 不存在"
                )
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
            cellxgene.BioSampleAnalysis.biosample_id
            == cellxgene.ProjectBioSample.biosample_id,
        ],
    )
    crud.create_biosample_analysis_for_transaction(
        db=db, insert_biosample_analysis_list=insert_biosample_analysis_model_list
    )
    for _, row in cell_proportion_df.iterrows():
        cell_proportion_meta = project_model.CellClusterProportionModel(**row.to_dict())
        cell_proportion_meta.biosample_id = (
            cell_proportion_meta.biosample_id
            if type(cell_proportion_meta.biosample_id) == int
            else int(inserted_biosample_id_dict.get(cell_proportion_meta.biosample_id))
        )
        cell_proportion_meta.analysis_id = analysis_id
        if cell_proportion_meta.biosample_id not in inserted_biosample_id_list:
            return ResponseMessage(
                status="0201", data={}, message="请选择biosample_meta中存在的biosample_id"
            )
        if type(cell_proportion_meta.calculated_cell_cluster_id) == str:
            check_insert_cell_proportion_id_list.append(
                cell_proportion_meta.calculated_cell_cluster_id
            )
            insert_cell_proportion_model_list.append(
                cellxgene.CalcCellClusterProportion(
                    **cell_proportion_meta.model_dump(
                        mode="json",
                        exclude={"calculated_cell_cluster_id"},
                        exclude_none=True,
                    ),
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
                return ResponseMessage(
                    status="0201", data={}, message="cell proportion id 不存在"
                )
            crud.update_cell_proportion_for_transaction(
                db=db,
                filters=[
                    cellxgene.CalcCellClusterProportion.calculated_cell_cluster_id
                    == cell_proportion_meta.calculated_cell_cluster_id
                ],
                update_dict=cell_proportion_meta.model_dump(
                    mode="json", exclude_none=True
                ),
            )
    inserted_cell_proportion_id_list = crud.create_cell_proprotion_for_transaction(
        db=db, insert_cell_proportion_model_list=insert_cell_proportion_model_list
    )
    inserted_cell_proportion_id_dict = dict(
        zip(check_insert_cell_proportion_id_list, inserted_cell_proportion_id_list)
    )
    for _, row in gene_expression_df.iterrows():
        gene_expression_meta = project_model.CellClusterGeneExpressionModel(
            **row.to_dict()
        )
        gene_expression_meta.calculated_cell_cluster_id = (
            gene_expression_meta.calculated_cell_cluster_id
            if type(gene_expression_meta.calculated_cell_cluster_id) == int
            else int(
                inserted_cell_proportion_id_dict.get(
                    gene_expression_meta.calculated_cell_cluster_id
                )
            )
        )
        if type(gene_expression_meta.id) == str:
            insert_gene_expression_model_list.append(
                cellxgene.CellClusterGeneExpression(
                    **gene_expression_meta.model_dump(
                        mode="json", exclude={"id"}, exclude_none=True
                    ),
                )
            )
        else:
            check_gene_expression_meta = crud.get_gene_expression(
                db=db,
                filters=[
                    cellxgene.CellClusterGeneExpression.id == gene_expression_meta.id
                ],
            )
            if not check_gene_expression_meta:
                return ResponseMessage(
                    status="0201", data={}, message="gene expression id 不存在"
                )
            crud.update_gene_expression_for_transaction(
                db=db,
                filters=[
                    cellxgene.CellClusterGeneExpression.id == gene_expression_meta.id
                ],
                update_dict=gene_expression_meta.model_dump(
                    mode="json", exclude_none=True
                ),
            )
    crud.create_gene_expression_for_transaction(
        db=db,
        insert_gene_expression_model_list=insert_gene_expression_model_list,
    )


def upload_file_v2(db: Session, project_id: int, analysis_id: int, excel_id: str):
    start_time = time.time()
    file_path = config.H5AD_FILE_PATH + "/" + excel_id
    with open(file_path, "rb") as file:
        project_content = file.read()
    species_meta_list = crud.get_species_list(db=db, query_list=[cellxgene.SpeciesMeta], filters=[])
    species_dict = {}
    for species_meta in species_meta_list:
        species_dict[species_meta.species] = species_meta.id
    project_excel_df = pd.ExcelFile(BytesIO(project_content))
    project_df = project_excel_df.parse("project_meta")
    analysis_df = project_excel_df.parse("analysis_meta")
    biosample_df = project_excel_df.parse("biosample_meta")
    donor_df = project_excel_df.parse("donor_meta")
    cell_proportion_df = project_excel_df.parse("calc_cell_cluster_proportion")
    pathway_score_df = project_excel_df.parse("pathway_score")
    gene_expression_df = project_excel_df.parse("gene_expression")
    analysis_df = analysis_df.replace(np.nan, None)
    analysis_df = analysis_df.replace("unknown", None)
    donor_df = donor_df.replace(np.nan, None)
    donor_df = donor_df.replace("unknown", None)
    biosample_df = biosample_df.replace(np.nan, None)
    biosample_df = biosample_df.replace("unknown", None)
    cell_proportion_df = cell_proportion_df.replace(np.nan, None)
    cell_proportion_df = cell_proportion_df.replace("unknown", None)
    pathway_score_df = pathway_score_df.replace(np.nan, None)
    pathway_score_df = pathway_score_df.replace("unknown", None)
    pathway_score_df["cell_type_name"] = pathway_score_df["calculated_cell_cluster_alias_id"].apply(lambda xx: xx.split('_')[3])
    gene_expression_df = gene_expression_df.replace(np.nan, None)
    gene_expression_df = gene_expression_df.replace("unknown", None)
    gene_expression_df = gene_expression_df.replace(np.inf, 3.91E+303)
    gene_expression_df['gene_symbol'] = gene_expression_df['gene_symbol'].astype(str)
    update_project_dict = project_df.to_dict("records")[0]
    update_analysis_dict = analysis_df.to_dict("records")[0]
    insert_donor_model_list = []
    insert_biosample_model_list = []
    insert_project_biosample_model_list = []
    insert_biosample_analysis_model_list = []
    insert_cell_proportion_model_list = []
    insert_pathway_model_list = []
    insert_gene_expression_model_list = []
    write_count = 10000
    check_donor_id_list = []
    del update_project_dict['project_id']
    crud.update_project_for_transaction(db=db, filters=[cellxgene.ProjectMeta.id == project_id], update_dict=update_project_dict)
    crud.update_analysis_for_transaction(db=db, filters=[cellxgene.Analysis.id == analysis_id], update_dict=update_analysis_dict)
    for _, row in donor_df.iterrows():
        donor_dict = row.to_dict()
        donor_meta = project_model.DonorModel(**donor_dict)
        check_donor_id_list.append(donor_dict['donor_id'])
        insert_donor_model_list.append(
            cellxgene.DonorMeta(
                **donor_meta.model_dump(
                    mode="json", exclude={"id"}, exclude_none=True
                )
            )
        )
    inserted_donor_id_list = crud.create_donor_meta_for_transaction(db=db, insert_donor_meta_list=insert_donor_model_list)
    inserted_donor_id_dict = dict(
        zip(check_donor_id_list, inserted_donor_id_list)
    )
    check_biosample_id_list = []
    biosample_df["species_id"] = biosample_df["species"].apply(lambda xx: species_dict[xx.strip()])
    biosample_df["donor_id"] = biosample_df["donor_id"].apply(lambda xx: int(inserted_donor_id_dict.get(xx, 0)))
    for _, row in biosample_df.iterrows():
        biosample_dict = row.to_dict()
        biosample_meta = project_model.BiosampleModel(**biosample_dict)
        check_biosample_id_list.append(biosample_dict['biosample_id'])
        # print(biosample_meta)
        insert_biosample_model_list.append(
                cellxgene.BioSampleMeta(
                    **biosample_meta.model_dump(
                        mode="json", exclude={"id"}, exclude_none=True
                    )
                )
            )
    inserted_biosample_id_list = crud.create_biosample_for_transaction(db=db, insert_biosample_model_list=insert_biosample_model_list)
    inserted_biosample_id_dict = dict(
        zip(check_biosample_id_list, inserted_biosample_id_list)
    )
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
    crud.create_project_biosample_for_transaction(
        db=db,
        insert_project_biosample_model_list=insert_project_biosample_model_list,
    )
    crud.create_biosample_analysis_for_transaction(
        db=db, insert_biosample_analysis_list=insert_biosample_analysis_model_list
    )
    cell_proportion_df["biosample_id"] = cell_proportion_df["biosample_id"].apply(lambda xx: int(inserted_biosample_id_dict.get(xx, 0)))
    for _, row in cell_proportion_df.iterrows():
        cell_proportion_meta = project_model.CellClusterProportionModel(**row.to_dict())
        cell_proportion_meta.analysis_id = analysis_id
        insert_cell_proportion_model_list.append(
            cellxgene.CalcCellClusterProportion(
                **cell_proportion_meta.model_dump(
                    mode="json", exclude={"calculated_cell_cluster_id"}, exclude_none=True
                )
            )
        )
    crud.create_cell_proprotion_for_transaction(
        db=db, insert_cell_proportion_model_list=insert_cell_proportion_model_list
    )
    pathway_score_df["species_id"] = pathway_score_df["species"].apply(lambda xx: species_dict[xx.strip()])
    pathway_score_df['biosample_id'] = pathway_score_df['biosample_id'].apply(lambda xx: inserted_biosample_id_dict.get(xx, 0))
    for _, row in pathway_score_df.iterrows():
        pathway_score_meta = project_model.PathwayScoreModel(**row.to_dict())
        pathway_score_meta.analysis_id = analysis_id
        # print(pathway_score_meta)
        insert_pathway_model_list.append(
                cellxgene.PathwayScore(
                    **pathway_score_meta.model_dump(
                        mode="json", exclude={"id"}, exclude_none=True
                    )
                )
            )
    pathway_insert_count = int(len(insert_pathway_model_list) / write_count)
    for i in range(1, pathway_insert_count + 1):
        crud.create_pathway_score_for_transaction(
            db=db, insert_pathway_meta_list=insert_pathway_model_list[write_count * (i - 1): write_count * i]
        )
    crud.create_pathway_score_for_transaction(
        db=db, insert_pathway_meta_list=insert_pathway_model_list[pathway_insert_count * write_count:]
    )
    # print('taken:', str(time.time() - start_time))
    for _, row in gene_expression_df.iterrows():
        gene_expression_meta = project_model.CellClusterGeneExpressionModel(**row.to_dict())
        gene_expression_meta.analysis_id = analysis_id
        # print(gene_expression_meta)
        insert_gene_expression_model_list.append(
                cellxgene.CellClusterGeneExpression(
                    **gene_expression_meta.model_dump(
                        mode="json", exclude={"id"}, exclude_none=True
                    )
                )
            )
    gene_expression_insert_count = int(len(insert_gene_expression_model_list) / write_count)
    for i in range(1, gene_expression_insert_count + 1):
        # print(write_count * (i - 1), write_count * i)
        crud.create_gene_expression_for_transaction(
            db=db, insert_gene_expression_model_list=insert_gene_expression_model_list[write_count * (i - 1): write_count * i]
        )
    crud.create_gene_expression_for_transaction(
        db=db, insert_gene_expression_model_list=insert_gene_expression_model_list[gene_expression_insert_count * write_count:]
    )
    db.commit()
    print('taken:', str(time.time() - start_time))


if __name__ == "__main__":
    from orm.dependencies import get_db

    upload_file_v2(db=next(get_db()), project_id=26, analysis_id=26, excel_id="update_file_test.xlsx")
