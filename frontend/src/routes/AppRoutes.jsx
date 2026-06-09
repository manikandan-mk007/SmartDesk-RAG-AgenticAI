import { Navigate, Route, Routes } from "react-router-dom";

import AdminLayout from "../layouts/AdminLayout";
import AgentLayout from "../layouts/AgentLayout";
import UserLayout from "../layouts/UserLayout";

import ProtectedRoute from "./ProtectedRoute";
import RoleRoute from "./RoleRoute";

import HomePage from "../pages/user/HomePage";
import LoginPage from "../pages/user/LoginPage";
import RegisterPage from "../pages/user/RegisterPage";
import TicketPage from "../pages/user/TicketPage";

import AgentDashboardPage from "../pages/agent/AgentDashboardPage";
import AgentQueuePage from "../pages/agent/AgentQueuePage";
import AgentTicketChatPage from "../pages/agent/AgentTicketChatPage";

import AdminDashboardPage from "../pages/admin/AdminDashboardPage";
import AdminReportsPage from "../pages/admin/AdminReportsPage";
import AgentManagementPage from "../pages/admin/AgentManagementPage";
import FAQManagementPage from "../pages/admin/FAQManagementPage";
import KBManagementPage from "../pages/admin/KBManagementPage";
import UserManagementPage from "../pages/admin/UserManagementPage";

function Placeholder({ title }) {
  return (
    <div className="sd-card pad">
      <h1 className="sd-heading-md">{title}</h1>
      <p className="sd-body sd-muted sd-mt-2">
        This page will be connected in the next integration step.
      </p>
    </div>
  );
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<UserLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route
          path="/tickets"
          element={
            <ProtectedRoute>
              <RoleRoute allowedRoles={["USER"]}>
                <TicketPage />
              </RoleRoute>
            </ProtectedRoute>
          }
        />

        <Route
          path="/tickets/:id"
          element={
            <ProtectedRoute>
              <RoleRoute allowedRoles={["USER"]}>
                <TicketPage />
              </RoleRoute>
            </ProtectedRoute>
          }
        />
      </Route>

      <Route
        path="/agent"
        element={
          <ProtectedRoute>
            <RoleRoute allowedRoles={["AGENT", "ADMIN"]}>
              <AgentLayout />
            </RoleRoute>
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/agent/dashboard" replace />} />
        <Route path="dashboard" element={<AgentDashboardPage />} />
        <Route path="queue" element={<AgentQueuePage />} />
        <Route path="tickets/:id" element={<AgentTicketChatPage />} />
        <Route path="knowledge" element={<Placeholder title="Agent Knowledge" />} />
        <Route path="reports" element={<Placeholder title="Agent Reports" />} />
      </Route>

      <Route
        path="/admin"
        element={
          <ProtectedRoute>
            <RoleRoute allowedRoles={["ADMIN"]}>
              <AdminLayout />
            </RoleRoute>
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/admin/dashboard" replace />} />
        <Route path="dashboard" element={<AdminDashboardPage />} />
        <Route path="users" element={<UserManagementPage />} />
        <Route path="agents" element={<AgentManagementPage />} />
        <Route path="faqs" element={<FAQManagementPage />} />
        <Route path="kb" element={<KBManagementPage />} />
        <Route path="reports" element={<AdminReportsPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}