import React from "react"
import ReactDOM from "react-dom"
import MyComponent from "./MyComponent"

import { ThemeProvider, createTheme, lightThemePrimitives } from "baseui";
import { Provider as StyletronProvider } from "styletron-react";
import { Client as Styletron } from "styletron-engine-atomic";


const engine = new Styletron();

const theme = createTheme({
  ...lightThemePrimitives,
  primaryFontFamily: "Arial",
});

ReactDOM.render(
  <React.StrictMode>
  <StyletronProvider value={engine}>
    <ThemeProvider theme={theme}>
    <MyComponent />
  </ThemeProvider>
  </StyletronProvider>
  </React.StrictMode>,
  document.getElementById("root")
)
