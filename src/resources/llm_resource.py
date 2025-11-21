from server import server as mcp


@mcp.resource("file://llm-docs/recipes/graphql-crud.md", name="datagateway-crud")
async def datagateway_crud() -> str:
    """datagateway-crud recipe

    This recipe provides a comprehensive guide on how to implement CRUD operations using DataGateway in a Blocks application.
    It covers the following key steps:
    1. Setting up DataGateway in your Blocks project.
    2. Creating and configuring schemas to define your data structure.
    3. Implementing Create, Read, Update, and Delete operations using GraphQL queries and mutations.
    4. Best practices for managing data and ensuring data integrity.
    5. Example code snippets to illustrate each operation.
    6. Tips for optimizing performance and handling errors effectively.
    7. Additional resources and documentation for further learning."""
    absolute_path = __file__.rsplit("/", 3)[0]
    with open(f"{absolute_path}/llm-docs/recipes/graphql-crud.md", "r") as f:
        return f.read()


@mcp.resource(
    "file://llm-docs/recipes/confirmation-modal-patterns.md",
    name="confirmation-modal-patterns",
)
async def confirmation_modal_patterns() -> str:
    """
    This resource provides a comprehensive guide on implementing confirmation modals in web applications.
    It covers best practices for designing user-friendly confirmation dialogs, including when to use them,
    how to structure the content, and how to handle user interactions effectively.
    The guide includes code examples and patterns for various scenarios, such as deleting items,
    submitting forms, and navigating away from unsaved changes.
    Additionally, it discusses accessibility considerations to ensure that confirmation modals are usable by all users.
    """
    absolute_path = __file__.rsplit("/", 3)[0]
    with open(
        f"{absolute_path}/llm-docs/recipes/confirmation-modal-patterns.md", "r"
    ) as f:
        return f.read()


@mcp.resource(
    "file://llm-docs/recipes/react-hook-form-integration.md",
    name="react-hook-form-integration",
)
async def react_hook_form_integration() -> str:
    """react-hook-form-integration recipe
    This recipe provides a comprehensive guide on how to integrate React Hook Form with your Blocks application.
    It covers the following key steps:
    1. Setting up React Hook Form in your project.
    2. Creating and managing form state using hooks.
    3. Implementing validation and error handling.
    4. Best practices for optimizing performance and user experience.
    5. Example code snippets to illustrate each concept.
    6. Tips for troubleshooting common issues.
    7. Additional resources and documentation for further learning."""
    absolute_path = __file__.rsplit("/", 3)[0]
    with open(
        f"{absolute_path}/llm-docs/recipes/react-hook-form-integration.md", "r"
    ) as f:
        return f.read()


@mcp.resource(
    "file://llm-docs/recipes/component-quick-reference.md",
    name="component-quick-reference",
)
async def component_catalog() -> str:
    """component-quick-reference recipe
    This recipe provides a quick reference guide for the various components available in the Blocks framework.
    It includes:
    1. A list of all components with a brief description of each.
    2. Code snippets demonstrating how to use each component.
    3. Best practices for component usage and composition.
    4. Tips for customizing and extending components.
    5. Links to detailed documentation for each component."""
    absolute_path = __file__.rsplit("/", 3)[0]
    with open(
        f"{absolute_path}/llm-docs/component-catalog/component-quick-reference.md",
        "r",
    ) as f:
        return f.read()


@mcp.resource(
    "file://llm-docs/recipes/selise-component-hierarchy.md",
    name="selise-component-hierarchy",
)
async def selise_component_hierarchy() -> str:
    """
    selise-component-hierarchy recipe
    This recipe provides a detailed overview of the component hierarchy used in Selise applications.
    It covers:
    1. The structure and organization of components within the Selise framework.
    2. Relationships and dependencies between different components.
    3. Guidelines for navigating and understanding the component tree.
    4. Best practices for component reuse and composition.
    5. Visual diagrams to illustrate the hierarchy and relationships.
    6. Tips for extending and customizing components within the hierarchy.
    7. Links to additional resources and documentation for further exploration.
    """
    absolute_path = __file__.rsplit("/", 3)[0]
    with open(
        f"{absolute_path}/llm-docs/component-catalog/selise-component-hierarchy.md",
        "r",
    ) as f:
        return f.read()
