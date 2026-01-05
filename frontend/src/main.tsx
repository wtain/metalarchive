import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App";
import SubscribersPage from "./pages/SubscribersPage";
import ReactionsPage from "./pages/ReactionsPage";
import PostDetailsPage from "./pages/PostDetailsPage";
import PostListPage from "./pages/PostListPage";
import TopPostsPage from "./pages/TopPostsPage";
import "./index.css";
import { SMMetricsClient } from "./client/SMMetricsClient";

const client = new SMMetricsClient("http://127.0.0.1:8001");

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
        <Routes>
          <Route path="/" element={<App />}>
            <Route path="reactions" element={<ReactionsPage metricsClient={client} />} />
            <Route index path="subscribers" element={<SubscribersPage metricsClient={client} />} />
            <Route path="posts" element={<PostListPage metricsClient={client} />} />
            <Route path="top" element={<TopPostsPage metricsClient={client} />} />
            <Route path="posts/:id" element={<PostDetailsPage metricsClient={client} />} />
          </Route>
        </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
