/**
 * Helper files shared across the project
 */

export const formatDateTime = (dateString: string): string => {
  return new Date(dateString).toLocaleString();
};
