import importlib
import os

import streamlit.components.v1 as components
import streamlit as st
import plotly.io as pio

from my_component.backend.interface.main import DataAnalystChat, get_database
from my_component.backend.interface.renderable import Renderable, RenderType
from my_component.backend.github import repo_actions
from my_component.backend.retrieval import retrieve_top_k
from my_component.backend import documents


# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = False

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _component_func = components.declare_component(
        # We give the component a simple, descriptive name ("my_component"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "my_component",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3001",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("my_component", path=build_dir)

# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.

def _reset_chat():
    st.cache_data.clear()
    st.cache_resource.clear()

def my_component(
        name:str,
        graphing_file_path:str,
        graphing_import_path:str,
        database_name:str,
        general_description:str,
        key: str=None):
    """Create a new instance of "my_component".

    Parameters
    ----------
    name: str
        The name of the thing we're saying hello to. The component will display
        the text "Hello, {name}!"
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    int
        The number of times the component's "Click Me" button has been clicked.
        (This is the value passed to `Streamlit.setComponentValue` on the
        frontend.)

    """
    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.
    da = DataAnalystChat(
        graphing_file_path=graphing_file_path,
        graphing_import_path=graphing_import_path,
        database_name=database_name,
        general_description=general_description
    )
    col1, col2 = st.columns([0.8,0.2])
    with col1:
        input_prompt = st.text_input("How can I help you?", label_visibility="collapsed", placeholder="Ask something")
    with col2:
        reset_chat = st.button("Reset Chat", on_click=_reset_chat)
    renderables = []
    # if input_prompt:
        # renderables = da.run(prompt=input_prompt)
        # _component_func(
        #     name=name,
        #     key=key,
        #     renderables=[r.to_dict() for r in renderables],
        #     prompt=input_prompt
        # )
    renderables = [Renderable(type=RenderType.NEW_GRAPH, content="", code="testing", function_name="test")]
    new_graphs = [r for r in renderables if r.type.value == "NEW_GRAPH"]
    repo_name = os.environ.get('REPO_NAME')
    repo_owner = os.environ.get('REPO_OWNER')
    github_token = os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN')

    if all([new_graphs, repo_name, repo_owner, github_token]):

        @st.experimental_dialog("New Graphs Created!")
        def create_pr(code_block):
            st.write(f"""Want to add this to the code base? Please create a title for this graph and hit submit to create a pull request:
```{code_block}```""")
            pr_title = st.text_input("Tile: ")
            if st.button("Submit"):
                if not pr_title:
                    st.write("Please give the graph a title")
                else:
                    try:
                        pr_url = repo_actions.create_new_graphing_pr(repo_name=repo_name,
                                                            repo_owner=repo_owner,
                                                            token=github_token,
                                                            graphing_file_full_path=graphing_file_path,
                                                            graph_title=pr_title,
                                                            new_code=code_block)
                        st.success(f'Success! See PR at [{pr_url}]({pr_url})')
                    except Exception as e:
                        st.error(f"There was an error creating this PR: {str(e)}")
        st.write(":mailbox: You got new graphs!")
        for index, record in enumerate(new_graphs):
            if st.button(record.function_name):
                create_pr(record.code)

    st.divider()

    docs = documents.python_to_docs(graphing_file_path)
    n_graphs_to_display = 6
    input_prompt = None
    if input_prompt:
        top_k_docs = retrieve_top_k(query=input_prompt, docs=docs, k=n_graphs_to_display)
    else:
        top_k_docs = docs[:n_graphs_to_display]
    if top_k_docs:
        top_k_function_names = documents.extract_function_names(top_k_docs)
        db = get_database(database_name)
        conn = db.connect()
        imported_graphing_library = importlib.import_module(graphing_import_path)
        to_render = []
        for func_name in top_k_function_names:
            func = eval(f'imported_graphing_library.{func_name}')
            fig = func(conn)
            fig.update_layout(width=300, height=300)
            to_render.append(Renderable(type=RenderType.GRAPH, content=pio.to_json(fig)))
    _component_func(
        name=name,
        key=None,
        renderables=[r.to_dict() for r in to_render],
        prompt=input_prompt
    )