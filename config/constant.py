class Constant:
    class Base:
        lbCreatedAt = "CreatedAt"
        lbUpdatedAt = "UpdatedAt"

    class Profile:
        lbTableId = "Uid"
        lbTableName = "Name"
        lbTableProfilePath = "Path"
        lbTableBrowserVersion = "Version"
        lbTableProxy = "Proxy"
        lbTableNote = "Note"
        lbTableAction = "Hành động"

class Base:
    header_labels_base = [
        Constant.Base.lbCreatedAt,
        Constant.Base.lbUpdatedAt
    ]

class TableHeaderLabel:
    header_labels_profile = [
        Constant.Profile.lbTableId,
        Constant.Profile.lbTableName,
        Constant.Profile.lbTableProfilePath,
        Constant.Profile.lbTableBrowserVersion,
        Constant.Profile.lbTableProxy,
        Constant.Profile.lbTableNote,
        Constant.Base.lbCreatedAt,
        Constant.Base.lbUpdatedAt,
        Constant.Profile.lbTableAction,
    ]