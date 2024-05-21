FUNCTION_REWRITE_PROMPT = """<|im_start|>user

Please rewrite the following Python code so that it meets the following specifications:
  1. The code contains only a function definition and no extraneous text
  2. The function takes in one parameter called `conn`
  3. The function returns `fig` which is an instance of plotly.graph_objs.Figure
  4. Remove any fig.show() lines from the code
  5. In the line immediately after the dataframe is defined, rename its columns as such:
  dataframe.columns = dataframe.columns.str.lower()
  6. Make sure the function is properly formatted and executable without syntax errors

Below are some examples of acceptable outputs
---- Acceptable Example 1a ----
```
def plot_tracks(conn):
    df_tracks = pd.read_sql(
        '''SELECT tracks.trackid, genres.name AS genre 
            FROM tracks 
            LEFT JOIN genres on tracks.genreid = genres.genreid
        ''', conn
    )
    df_tracks.columns = df_tracks.columns.str.lower()
    tracks_per_genre = df_tracks.groupby('genre').size().reset_index(name='Count')
    fig = px.bar(tracks_per_genre, x='genre', y='Count', title='Number of Tracks per Genre')
    return fig
```
---- End Example 1a ----
---- Acceptable Example 2a ----
```
def plot_customer_states(conn):
    df_tracks = pd.read_sql(
        '''SELECT customerid, state AS state
            FROM customers
        ''', conn
    )
    df_tracks.columns = df_tracks.columns.str.lower()
    tracks_per_genre = df_tracks.groupby('state').size().reset_index(name='Count')
    fig = px.bar(tracks_per_genre, x='state', y='Count', title='Number of Customers per Sate')
    return fig
```
---- End Example 2a ----   
Below are some examples of unacceptable outputs
Example 1b is unacceptable because it misses the step where the columns are made lowercase
Example 2b is unacceptable because it shows the figure instead of returning it
---- Unacceptable Example 1b ----
```
def plot_tracks(conn):
    df_tracks = pd.read_sql(
        '''SELECT tracks.trackid, genres.name AS genre 
            FROM tracks 
            LEFT JOIN genres on tracks.genreid = genres.genreid
        ''', conn
    )
    tracks_per_genre = df_tracks.groupby('genre').size().reset_index(name='Count')
    fig = px.bar(tracks_per_genre, x='genre', y='Count', title='Number of Tracks per Genre')
    return fig
```
---- End Example 1b ----
---- Unacceptable Example 2b ----
```
def plot_customer_states(conn):
    df_tracks = pd.read_sql(
        '''SELECT customerid, state AS state
            FROM customers
        ''', conn
    )
    df_tracks.columns = df_tracks.columns.str.lower()
    tracks_per_genre = df_tracks.groupby('state').size().reset_index(name='Count')
    fig = px.bar(tracks_per_genre, x='state', y='Count', title='Number of Customers per Sate')
    fig.show()
```
---- End Example 2b ----  

Code to rewrite:

{prompt}

<|im_end|>
"""