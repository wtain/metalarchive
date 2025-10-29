import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App";
import SubscribersPage from "./pages/SubscribersPage";
import ReactionsPage from "./pages/ReactionsPage";
import PostDetailsPage from "./pages/PostDetailsPage";
import PostListPage from "./pages/PostListPage";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
        <Routes>
          <Route path="/" element={<App />}>
            <Route path="reactions" element={<ReactionsPage />} />
            <Route index path="subscribers" element={<SubscribersPage />} />
            <Route path="posts" element={<PostListPage />} />
            <Route path="posts/:id" element={<PostDetailsPage />} />
          </Route>
        </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
