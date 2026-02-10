import agentApi from "./agentAxios";

export const sendChatMessage = async ({ message, user_id }) => {
  const payload = {
    message: message.trim(),
    user_id
  };

  const { data } = await agentApi.post("/chat", payload);

  return data;
};


export const fetchMyPermissions = async () => {
  const { data } = await agentApi.get("/me/permissions");
  return data;
};
