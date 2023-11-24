from orm.schema.exception_model import BusinessException


def check_file_name(file_type: str, file_id: str):
    if file_type == "h5ad":
        if file_id is not None:
            name_list = file_id.split(".")
            if len(name_list) >= 2:
                if name_list[len(name_list) - 1] != "h5ad":
                    raise BusinessException(message="h5ad file should be .h5ad")
            else:
                raise BusinessException(message="wrong h5ad file")
    elif file_type in ["umap", "cell_marker", "pathway"]:
        if file_id is not None:
            name_list = file_id.split(".")
            if len(name_list) >= 2:
                if name_list[len(name_list) - 1] != "csv":
                    raise BusinessException(message="umap,cell_marker,pathway file should be .csv")
            else:
                raise BusinessException(message="umap,cell_marker,pathway file should be .csv")
    elif file_type == 'excel':
        if file_id is not None:
            name_list = file_id.split(".")
            if len(name_list) >= 2:
                if name_list[len(name_list) - 1] not in ["xlsx", "xls"]:
                    raise BusinessException(message="excel file should be .xlsx")
            else:
                raise BusinessException(message="excel file should be .xlsx")
    else:
        raise BusinessException(message="wrong file type")