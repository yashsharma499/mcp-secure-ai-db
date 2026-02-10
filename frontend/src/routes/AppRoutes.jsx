import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "../auth/ProtectedRoute";
import Login from "../pages/login/Login";
import Signup from "../pages/signup/Signup";
import UserLayout from "../layouts/UserLayout";
import AdminLayout from "../layouts/AdminLayout";
import ChatPage from "../pages/user/ChatPage";
import UsersPermissions from "../pages/admin/UsersPermissions";
import AuditLogs from "../pages/admin/AuditLogs";
import useAuth from "../auth/useAuth";

export default function AppRoutes() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <span className="text-sm text-slate-500 animate-pulse">Loading…</span>
      </div>
    );
  }

  return (
    <Routes>
      <Route
        path="/"
        element={
          user
            ? <Navigate to={user.role === "admin" ? "/admin" : "/app"} replace />
            : <Navigate to="/login" replace />
        }
      />

      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      <Route element={<ProtectedRoute allowedRoles={["user"]} />}>
        <Route path="/app" element={<UserLayout />}>
          <Route index element={<ChatPage />} />
        </Route>
      </Route>

      <Route element={<ProtectedRoute allowedRoles={["admin"]} />}>
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<Navigate to="permissions" replace />} />
          <Route path="permissions" element={<UsersPermissions />} />
          <Route path="audit" element={<AuditLogs />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
