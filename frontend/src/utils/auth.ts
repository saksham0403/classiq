import type { User, Token } from '../types';

export const saveAuth = (tokenData: Token): void => {
  localStorage.setItem('token', tokenData.access_token);
  localStorage.setItem('user', JSON.stringify(tokenData.user));
};

export const getAuth = (): { token: string | null; user: User | null } => {
  const token = localStorage.getItem('token');
  const userStr = localStorage.getItem('user');
  const user = userStr ? JSON.parse(userStr) : null;
  return { token, user };
};

export const clearAuth = (): void => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('token');
};

