from orm.db_model import cellxgene


cellxgene_table_dict = {
    "project":{
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
        "update_at": cellxgene.ProjectMeta.update_at
    }
}