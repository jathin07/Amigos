import { axiosClient } from "../../../api/axiosClient";

export const authApi = {
  /**
   * Authenticate user credentials.
   * Expects payload: { email, password, remember_me }
   */
  login: async (email, password, rememberMe = false) => {
    const response = await axiosClient.post("/auth/login", {
      email,
      password,
      remember_me: rememberMe,
    });
    return response.data;
  },

  /**
   * Log out the current session.
   * Expects payload: { refresh_token }
   */
  logout: async (refreshToken) => {
    const response = await axiosClient.post("/auth/logout", {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  /**
   * Fetch current authenticated user profile.
   */
  getCurrentUser: async () => {
    const response = await axiosClient.get("/auth/me");
    return response.data;
  },

  /**
   * Request password reset link.
   * Expects payload: { email }
   */
  forgotPassword: async (email) => {
    const response = await axiosClient.post("/auth/forgot-password", {
      email,
    });
    return response.data;
  },

  /**
   * Reset forgotten password using reset token.
   * Expects payload: { token, new_password, confirm_password }
   */
  resetPassword: async (token, newPassword, confirmPassword) => {
    const response = await axiosClient.post("/auth/reset-password", {
      token,
      new_password: newPassword,
      confirm_password: confirmPassword,
    });
    return response.data;
  },

  /**
   * Change password for logged-in user.
   * Expects payload: { current_password, new_password, confirm_password }
   */
  changePassword: async (currentPassword, newPassword, confirmPassword) => {
    const response = await axiosClient.post("/auth/change-password", {
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword,
    });
    return response.data;
  },

  /**
   * Verify token validity.
   */
  verifyToken: async () => {
    const response = await axiosClient.get("/auth/verify");
    return response.data;
  }
};
export default authApi;
