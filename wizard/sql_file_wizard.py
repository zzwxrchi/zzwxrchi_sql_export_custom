from datetime import datetime
from mimetypes import guess_type
from odoo import _, models, fields
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import logging
import json

class SqlFileWizard(models.TransientModel):
    _inherit = 'sql.file.wizard'

    def export_sql(self):
        self.ensure_one()
        # Check properties
        bad_props = [x for x in self.query_properties if not x["value"]]
        if bad_props:
            raise UserError(
                _("Please enter a values for the following properties : %s")
                % (",".join([x["string"] for x in bad_props]))
            )
        sql_export = self.sql_export_id
        # Manage Params
        variable_dict = {}
        now_tz = fields.Datetime.context_timestamp(sql_export, datetime.now())
        date = now_tz.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        for prop in self.query_properties:
            value = prop["value"]
            if prop["type"] == "selection" and isinstance(value, str):
                if 'selection' in prop:
                    try:
                        label = next(l for k, l in prop['selection'] if k == value)
                        if "=" in label:
                            value = label.split("=", 1)[0].strip()
                        else:
                            value = label  # Use full label if no "="
                    except StopIteration:
                        pass  # Keep original if no match
            elif prop["type"] == "tags" and isinstance(value, list):
                modified = []
                for v in value:
                    try:
                        label = next(l for k, l, _ in prop['tags'] if k == v)
                        if "=" in label:
                            modified.append(label.split("=", 1)[0].strip())
                        else:
                            modified.append(label)  # Use full label if no "="
                    except StopIteration:
                        modified.append(v)  # Keep original if no match
                value = modified
            # Assign to dict, with tuple for many2many/tags
            if prop["type"] in ("many2many", "tags"):
                variable_dict[prop["string"]] = tuple(value) if isinstance(value, list) else (value,)
            else:
                variable_dict[prop["string"]] = value

        # Log the full contents of self.query_properties for debugging
        #logging.getLogger(__name__).info("Query Properties Contents: %s", json.dumps(self.query_properties, indent=2, default=str))

        if "%(company_id)s" in sql_export.query:
            company_id = self.env.company.id
            variable_dict["company_id"] = company_id
        if "%(user_id)s" in sql_export.query:
            user_id = self.env.user.id
            variable_dict["user_id"] = user_id
        # Call different method depending on file_type since the logic will be
        # different
        method_name = "%s_get_data_from_query" % sql_export.file_format
        data = getattr(sql_export, method_name)(variable_dict)
        extension = sql_export._get_file_extension()
        self.write(
            {
                "binary_file": data,
                "file_name": "%(name)s_%(date)s.%(extension)s"
                % {"name": sql_export.name, "date": date, "extension": extension},
            }
        )
        # Bypass ORM to avoid changing the write_date/uid from sql query on a simple
        # execution. This also avoid error if user has no update right on the
        # sql.export object.
        self.env.cr.execute(
            """
            UPDATE sql_export
            SET last_execution_date = %s, last_execution_uid = %s
            WHERE id = %s
        """,
            (
                fields.Datetime.to_string(fields.Datetime.now()),
                self.env.user.id,
                sql_export.id,
            ),
        )
        self._get_field_attachment().sudo().write(
            {
                "name": self.file_name,
                "mimetype": guess_type(self.file_name)[0],
            }
        )
        action = {
            "name": "SQL Export",
            "type": "ir.actions.act_url",
            "url": "web/content/?model=%s&id=%d&filename_field=filename&"
            "field=binary_file&download=true&filename=%s"
            % (self._name, self.id, self.file_name),
            "target": "self",
        }
        return action
