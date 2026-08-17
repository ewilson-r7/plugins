import insightconnect_plugin_runtime
from .schema import UpdateUrlsOfUrlCategoryInput, UpdateUrlsOfUrlCategoryOutput, Input, Output, Component

# Custom imports below
from insightconnect_plugin_runtime.helper import clean
from icon_zscaler.util.helpers import (
    convert_dict_keys_to_camel_case,
    find_custom_url_category_by_name,
    filter_dict_keys,
    find_url_category_by_id,
)
from icon_zscaler.util.constants import URL_CATEGORY_UPDATE_ACTIONS, URL_CATEGORORIES_NAMES, Cause, Assistance
from insightconnect_plugin_runtime.exceptions import PluginException


class UpdateUrlsOfUrlCategory(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super().__init__(
            name="update_urls_of_url_category",
            description=Component.DESCRIPTION,
            input=UpdateUrlsOfUrlCategoryInput(),
            output=UpdateUrlsOfUrlCategoryOutput(),
        )

    def run(self, params={}):
        url_category_name = params.get(Input.URLCATEGORYNAME)
        custom_urls = [url for url in params.get(Input.CUSTOMURLS, []) or [] if url]
        db_categorized_urls = [url for url in params.get(Input.DBCATEGORIZEDURLS, []) or [] if url]
        action = params.get(Input.ACTION)
        activate_configuration = params.get(Input.ACTIVATE_CONFIGURATION, False)

        if not custom_urls and not db_categorized_urls:
            raise PluginException(
                cause=Cause.URL_LIST_NOT_PROVIDED,
                assistance=Assistance.VERIFY_INPUT,
            )

        # Try predefined category first
        predefined_id = URL_CATEGORORIES_NAMES.get(url_category_name)

        if predefined_id:
            # Predefined category - look up by ID from the full list
            url_category = find_url_category_by_id(predefined_id, self.connection.zia_client.list_url_categories())
            url_category_id = url_category.get("id")
            url_category_data_to_send = filter_dict_keys(url_category, ["keywordsRetainingParentCategory"])
        else:
            # Custom category - search by name
            custom_url_category = find_custom_url_category_by_name(
                url_category_name, self.connection.zia_client.list_url_categories(custom_only=True)
            )
            url_category_id = custom_url_category.get("id")
            url_category_data_to_send = filter_dict_keys(
                custom_url_category, ["configuredName", "description", "scopes", "keywordsRetainingParentCategory"]
            )

        if custom_urls:
            url_category_data_to_send["urls"] = custom_urls
        if db_categorized_urls:
            url_category_data_to_send["dbCategorizedUrls"] = db_categorized_urls

        updated_category = convert_dict_keys_to_camel_case(
            self.connection.zia_client.update_urls_in_url_category(
                url_category_id, URL_CATEGORY_UPDATE_ACTIONS.get(action), url_category_data_to_send
            )
        )

        status = None
        if activate_configuration:
            self.connection.zia_client.activate_configuration()
            status = self.connection.zia_client.get_status().json().get("status")

        return clean({
            Output.URLCATEGORY: updated_category,
            Output.STATUS: status,
        })
