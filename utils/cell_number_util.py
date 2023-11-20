from conf import config
from sqlalchemy import func
from sqlalchemy.orm import Session
from orm import crud


from orm.db_model import cellxgene


def get_cell_taxonomy_tree_cell_number(db: Session):
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
    cell_type_meta_dict, cl_id_dict = {}, {}
    for cell_type_meta in cell_type_meta_list:
        cell_type_meta_dict[
            cell_type_meta.cell_type_id
        ] = cell_type_meta.cell_ontology_id if cell_type_meta.cell_ontology_id else 0
        if cell_type_meta.cell_ontology_id:
            cl_id_dict[cell_type_meta.cell_ontology_id] = cell_type_meta.cell_type_id
    # print(cell_type_meta_dict)
    cell_taxonomy_relation_model_list = crud.get_cell_taxonomy_relation_tree(
        db=db, filters=[], public_filter_list=[]
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
    exist_cl_id_list = []
    for cell_proportion_meta in cell_proportion_list:
        cl_id = cell_type_meta_dict.get(cell_proportion_meta[0])
        if cl_id:
            exist_cl_id_list.append(cl_id)
            cell_number = cell_proportion_meta[1]
            # print("cl_id", cl_id, cell_number)
            get_parent_cell_number(
                cell_taxonomy_relation_list, cl_id, cell_number, cell_proportion_dict
            )
        # print('------', cell_proportion_dict)
    # print(cell_proportion_dict, cell_proportion_dict.get("CL:0000000"))
    return cell_proportion_dict, exist_cl_id_list, cl_id_dict
    # for i in range(0, len(cell_taxonomy_relation_list)):
    #     # print(cell_taxonomy_relation_list[i]["cl_id"], cell_proportion_dict.get(cell_taxonomy_relation_list[i]["cl_id"], 0))
    #     cell_taxonomy_relation_list[i]["cell_number"] = cell_proportion_dict.get(cell_taxonomy_relation_list[i]["cl_id"], 0)
    # print(cell_taxonomy_relation_list)


def get_parent_cell_number(relation_list, cl_id, cell_number, parent_dict):
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
            get_parent_cell_number(
                relation_list, i.get("cl_pid"), cell_number, parent_dict
            )


if __name__ == "__main__":
    from orm.dependencies import get_db

    get_cell_taxonomy_tree_cell_number(db=next(get_db()))
