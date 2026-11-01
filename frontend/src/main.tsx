import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import App from "./App";
import SubscribersPage from "./pages/SubscribersPage";
import ReactionsPage from "./pages/ReactionsPage";
import PostDetailsPage from "./pages/PostDetailsPage";
import PostListPage from "./pages/PostListPage";
import SearchResultsPage from "./pages/SearchResultsPage";
import TagsCloudPage from "./pages/TagsCloudPage";
import TopPostsPage from "./pages/TopPostsPage";
import SubscriberChangesPage from "./pages/SubscriberChangesPage";
import SubscriberDetailsPage from "./pages/SubscriberDetailsPage";
import SubscriberLifecyclePage from "./pages/SubscriberLifecyclePage";
import SummaryPage from "./pages/SummaryPage";
import "./index.css";
import { SMMetricsClient } from "./client/SMMetricsClient";

const client = new SMMetricsClient("http://127.0.0.1:8001");

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
        <Routes>
          <Route path="/" element={<App />}>
            <Route index element={<SummaryPage metricsClient={client} />} />
            <Route path="summary" element={<Navigate to="/" replace />} />
            <Route path="reactions" element={<ReactionsPage metricsClient={client} />} />
            <Route path="subscribers" element={<SubscribersPage metricsClient={client} />} />
            <Route path="subscribers/:id" element={<SubscriberDetailsPage metricsClient={client} />} />
            <Route path="subscriber-changes" element={<SubscriberChangesPage metricsClient={client} />} />
            <Route path="subscriber-lifecycle" element={<SubscriberLifecyclePage metricsClient={client} />} />
            <Route path="posts" element={<PostListPage metricsClient={client} />} />
            <Route path="search" element={<SearchResultsPage metricsClient={client} />} />
            <Route path="tags" element={<TagsCloudPage metricsClient={client} />} />
            <Route path="top" element={<TopPostsPage metricsClient={client} />} />
            <Route path="posts/:id" element={<PostDetailsPage metricsClient={client} />} />
          </Route>
        </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
