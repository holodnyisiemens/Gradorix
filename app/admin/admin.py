from sqladmin import ModelView
from wtforms import PasswordField
from wtforms.validators import Optional, Length
from app.core.database import Base
from app.models.user import User
from app.auth.password import hash_password


class UserAdmin(ModelView, model=User):
    column_list = ["id", "username", "email", "role", "is_active"]
    column_details_exclude_list = ["password_hash"]
    form_excluded_columns = ["password_hash"]
    
    async def scaffold_form(self, form_rules):
        """Add password field to the form."""
        form_class = await super().scaffold_form(form_rules)
        form_class.password = PasswordField(
            "Password",
            validators=[Optional(), Length(min=6, max=72)],
            # render_kw={"placeholder": "enter new password"},"}
        )
        return form_class

    async def on_model_change(self, data, model, is_created, request):
        """Hash the password before saving if it's provided."""
        if "password" in data and data["password"]:
            data["password_hash"] = hash_password(data["password"])
            del data["password"]
        elif "password" in data:
            del data["password"]


def register_all_models(admin):
    admin.add_view(UserAdmin)
    
    for model in Base.registry.mappers:
        model_class = model.class_
        
        if model_class == User:
            continue

        class GenericAdmin(ModelView, model=model_class):
            column_list = "__all__"

        admin.add_view(GenericAdmin)
