import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"
import { FlexGrid, FlexGridItem } from 'baseui/flex-grid';
import { Block } from 'baseui/block';
import Plot from 'react-plotly.js';
import './styles.css';

interface Renderable {
  type: string
  content: string
}

interface State {
  isFocused: boolean
  value: string
  renderables: Renderable[]
  prompt: string
}

/**
 * This is a React-based component template. The `render()` function is called
 * automatically when your component should be re-rendered.
 */
class MyComponent extends StreamlitComponentBase<State> {
  public state: { 
    isFocused: boolean; 
    value: string; 
    renderables: Renderable[]
    prompt: string } 
    = { isFocused: false, value: "", renderables: [], prompt: "" };


  getBorderColor(type: string) {
    switch (type) {
      case 'GRAPH':
        return 'black';
      case 'TABLE':
        return 'black';
      case 'RESPONSE_BOX':
        return 'green';
        case 'NEW_GRAPH':
          return 'gold';
      default:
        return 'black';
    }
  }
  
  public componentDidMount(): void {
    Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, this.onRender)
    Streamlit.setComponentReady()
    const container = document.getElementById('container-id') // Replace with your container ID
    if (container) {
      const height = container.offsetHeight
      Streamlit.setFrameHeight(height)
    }
  }

  public componentWillUnmount(): void {
    Streamlit.events.removeEventListener(Streamlit.RENDER_EVENT, this.onRender)
  }
  
  private onRender = (event: any): void => {
    const { renderables, prompt } = event.detail.args
    if (renderables) {
      this.setState({ renderables })
    }
    if (prompt) {
      this.setState({ prompt })
    }
  }

  private parseAndExtractData = (input: string): any => {
    try {
      const json = JSON.parse(input);
      return json.data;
    } catch (error) {
      console.error("Invalid JSON string:", error);
      return null;
    }
  };

  private parseAndExtractLayout = (input: string): any => {
    try {
      const json = JSON.parse(input);
      return json.layout;
    } catch (error) {
      console.error("Invalid JSON string:", error);
      return null;
    }
  };

  public render = (): ReactNode => {

    const { theme } = this.props
    const style: React.CSSProperties = {}

    if (theme) {
      const borderStyling = `1px solid ${
        this.state.isFocused ? theme.primaryColor : "gray"
      }`
      style.border = borderStyling
      style.outline = borderStyling
    }

    return (
      <div id="container-id">
        <FlexGrid
        flexGridColumnCount={2}
        flexGridColumnGap="scale100"
        flexGridRowGap="scale100"
    >
        {this.state.renderables.map((renderable, index) => (
            <FlexGridItem key={index}>
                <Block
                    padding="scale200"
                    overrides={{
                        Block: {
                            style: {
                                borderRadius: '8px',
                                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                                border: `2px solid ${this.getBorderColor(renderable.type)}`,
                                height: '300px',
                                width: '90%',
                                margin: '0px',
                                overflow: 'auto',
                                display: 'flex',
                                flexDirection: 'row',
                                justifyContent: 'flex-start',
                                alignItems: 'flex-start'
                            },
                        },
                    }}
                >
                    {(renderable.type === "GRAPH" || renderable.type === "NEW_GRAPH") && (
                        <Plot
                            data={this.parseAndExtractData(renderable.content)}
                            layout={this.parseAndExtractLayout(renderable.content)}
                            style={{ width: '100%', height: '400px' }}
                        />
                    )}
                    {renderable.type === "TABLE" && <p className="p">{renderable.content}</p>}
                    {renderable.type === "RESPONSE_BOX" && renderable.content}
                </Block>
            </FlexGridItem>
        ))}
    </FlexGrid>
    </div>
    )
  }
}




// "withStreamlitConnection" is a wrapper function. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
//
// You don't need to edit withStreamlitConnection (but you're welcome to!).
export default withStreamlitConnection(MyComponent)
