import React from "react"
import ReactDOM from "react-dom"
import AIAssistant from "./AIAssistant"

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
    <AIAssistant />
  </ThemeProvider>
  </StyletronProvider>
  </React.StrictMode>,
  document.getElementById("root")
)
