import React from "react";
import ReactDOM from "react-dom/client";
import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";
import App from "./App.jsx";
import "./styles.css";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#14591D",
    },
    secondary: {
      main: "#D1495B",
    },
    background: {
      default: "#f2f3f0",
    },
  },
  typography: {
    fontFamily: "'Palatino Linotype', 'Book Antiqua', Palatino, serif",
    h2: {
      fontWeight: 700,
      letterSpacing: "0.04em",
    },
  },
});

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
