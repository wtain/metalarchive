import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App";
import SubscribersPage from "./pages/SubscribersPage";
import ReactionsPage from "./pages/ReactionsPage";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App>
        <Routes>
          <Route path="/" element={<SubscribersPage />} />
          <Route path="/reactions" element={<ReactionsPage />} />
        </Routes>
      </App>
    </BrowserRouter>
  </React.StrictMode>
);
