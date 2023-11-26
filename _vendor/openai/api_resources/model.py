from TestAddOn._vendor.openai.api_resources.abstract import DeletableAPIResource, ListableAPIResource


class Model(ListableAPIResource, DeletableAPIResource):
    OBJECT_NAME = "models"
