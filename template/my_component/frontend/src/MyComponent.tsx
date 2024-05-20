import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"
import { Input } from "baseui/input"
import { Card, StyledBody } from "baseui/card"
import Plot from 'react-plotly.js';

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


  public componentDidMount(): void {
    Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, this.onRender)
    Streamlit.setComponentReady()
    Streamlit.setFrameHeight(1000)
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
    // Arguments that are passed to the plugin in Python are accessible
    // via `this.props.args`. Here, we access the "name" arg.
    // const name = this.props.args["name"]

    // Streamlit sends us a theme object via props that we can use to ensure
    // that our component has visuals that match the active theme in a
    // streamlit app.
    const { theme } = this.props
    const style: React.CSSProperties = {}

    // Maintain compatibility with older versions of Streamlit that don't send
    // a theme object.
    if (theme) {
      // Use the theme object to style our button border. Alternatively, the
      // theme style is defined in CSS vars.
      const borderStyling = `1px solid ${
        this.state.isFocused ? theme.primaryColor : "gray"
      }`
      style.border = borderStyling
      style.outline = borderStyling
    }

    // Show a button and some text.
    // When the button is clicked, we'll increment our "numClicks" state
    // variable, and send its new value back to Streamlit, where it'll
    // be available to the Python program.
    return (
      <div>
      prompt {this.state.prompt} /prompt
      <div style={{ marginTop: "20px" }}>
      {this.state.renderables.map((renderable, index) => (
        
        <Card key={index}>
          <StyledBody>
          {renderable.type === "GRAPH" && (<Plot data={this.parseAndExtractData(renderable.content)} layout={this.parseAndExtractLayout(renderable.content)}/>)
          }
          {renderable.type === "TABLE" && renderable.content}
          {renderable.type === "RESPONSE_BOX" && renderable.content}
          </StyledBody>
        </Card>

      ))}
      
    </div>
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
