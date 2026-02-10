import api from "./axios";

export const fetchUsers = async () => {
  const { data } = await api.get("/admin/users");
  return data;
};

export const fetchUserPermissions = async (userId) => {
  const params = {};
  if (userId) params.user_id = userId;

  const { data } = await api.get("/admin/permissions", { params });
  return data;
};

export const upsertUserPermission = async ({
  userId,
  tableName,
  canRead,
  canWrite,
  allowedColumns
}) => {
  const payload = {
    user_id: userId,
    table_name: tableName,
    can_read: Boolean(canRead),
    can_write: Boolean(canWrite),
    allowed_columns: Array.isArray(allowedColumns) ? allowedColumns : []
  };

  const { data } = await api.post("/admin/permissions", payload);
  return data;
};


export const deleteUserPermission = async (permissionId) => {
  await api.delete(`/admin/permissions/${permissionId}`);
};

export const fetchAuditLogs = async ({ userId, limit = 100 } = {}) => {
  const params = {};

  if (userId) params.user_id = userId;
  if (limit) params.limit = limit;

  const { data } = await api.get(
    "/mcp/tools/audit_query_history",
    { params }
  );

  return data;
};
